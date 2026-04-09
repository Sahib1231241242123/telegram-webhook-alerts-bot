from types import SimpleNamespace

import pytest

from app.core.container import AppContainer
from app.handlers.callbacks import CallbackHandlers
from app.handlers.fsm import CURRENT_ALERT_KEY, FSM_STATE_KEY
from app.schemas.alert import AlertRecord
from app.schemas.callbacks import CallbackAction, CallbackPayload
from app.services.alerts_service import AlertsService
from app.services.message_sanitizer import MessageSanitizer
from app.services.rate_limiter import RateLimiter


class AlertsRepoStub:
    async def get_alerts(self) -> list[AlertRecord]:
        return [
            AlertRecord(
                id="AL-1",
                title="Alert",
                severity="high",
                status="active",
                reasoning="reason",
                expected_impact="impact",
            )
        ]


class DummyReportService:
    async def build_report(self):
        return None


class FakeQuery:
    def __init__(self, data: str):
        self.data = data
        self.answered = False
        self.edited_text = ""

    async def answer(self) -> None:
        self.answered = True

    async def edit_message_text(self, text: str, reply_markup=None) -> None:
        self.edited_text = text


def make_handler() -> CallbackHandlers:
    container = AppContainer(
        report_service=DummyReportService(),
        alerts_service=AlertsService(AlertsRepoStub()),
        rate_limiter=RateLimiter(max_calls=50, window_seconds=10),
        message_sanitizer=MessageSanitizer(2000),
    )
    return CallbackHandlers(container)


@pytest.mark.asyncio
async def test_callback_malformed_data() -> None:
    handler = make_handler()
    query = FakeQuery("bad-data")
    update = SimpleNamespace(callback_query=query, effective_user=SimpleNamespace(id=1))
    context = SimpleNamespace(user_data={})

    await handler.handle(update, context)
    assert query.answered is True
    assert "Некорректный callback" in query.edited_text


@pytest.mark.asyncio
async def test_callback_details_and_back_flow() -> None:
    handler = make_handler()
    details_payload = CallbackPayload(action=CallbackAction.DETAILS, alert_id="AL-1").pack()
    details_query = FakeQuery(details_payload)
    update = SimpleNamespace(callback_query=details_query, effective_user=SimpleNamespace(id=10))
    context = SimpleNamespace(user_data={})

    await handler.handle(update, context)
    assert context.user_data[FSM_STATE_KEY] == "DETAILS_VIEW"
    assert context.user_data[CURRENT_ALERT_KEY] == "AL-1"
    assert "Reasoning" in details_query.edited_text

    back_payload = CallbackPayload(action=CallbackAction.BACK, alert_id="AL-1").pack()
    back_query = FakeQuery(back_payload)
    back_update = SimpleNamespace(callback_query=back_query, effective_user=SimpleNamespace(id=10))
    await handler.handle(back_update, context)
    assert FSM_STATE_KEY not in context.user_data
    assert "Активные алерты" in back_query.edited_text


@pytest.mark.asyncio
async def test_callback_confirm_edits_message() -> None:
    handler = make_handler()
    payload = CallbackPayload(action=CallbackAction.CONFIRM, alert_id="AL-1").pack()
    query = FakeQuery(payload)
    update = SimpleNamespace(callback_query=query, effective_user=SimpleNamespace(id=50))
    context = SimpleNamespace(user_data={})

    await handler.handle(update, context)
    assert "подтвержден" in query.edited_text


@pytest.mark.asyncio
async def test_callback_set_language() -> None:
    handler = make_handler()
    payload = CallbackPayload(action=CallbackAction.SET_LANG, alert_id="en").pack()
    query = FakeQuery(payload)
    update = SimpleNamespace(callback_query=query, effective_user=SimpleNamespace(id=51))
    context = SimpleNamespace(user_data={})

    await handler.handle(update, context)
    assert context.user_data["language"] == "en"
    assert "Language switched" in query.edited_text
