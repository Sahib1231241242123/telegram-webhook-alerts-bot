from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from app.core.container import AppContainer
from app.handlers.commands import CommandHandlers
from app.schemas.alert import AlertRecord
from app.schemas.order import OrderRecord
from app.services.alerts_service import AlertsService
from app.services.message_sanitizer import MessageSanitizer
from app.services.rate_limiter import RateLimiter
from app.services.report_service import ReportService


class OrdersRepoStub:
    async def get_orders(self) -> list[OrderRecord]:
        return [
            OrderRecord(
                order_id="1",
                sku="SKU-A",
                revenue=100.0,
                margin=20.0,
                created_at=datetime.now(UTC) - timedelta(hours=2),
            )
        ]


class AlertsRepoStub:
    def __init__(self, active: bool = True):
        self._active = active

    async def get_alerts(self) -> list[AlertRecord]:
        status = "active" if self._active else "resolved"
        return [
            AlertRecord(
                id="AL-1",
                title="Alert 1",
                severity="high",
                status=status,
                reasoning="r",
                expected_impact="i",
            )
        ]


class FakeMessage:
    def __init__(self):
        self.last_text = ""
        self.reply_markup = None

    async def reply_text(self, text: str, reply_markup=None) -> None:
        self.last_text = text
        self.reply_markup = reply_markup


def make_update(user_id: int, message: FakeMessage):
    return SimpleNamespace(effective_user=SimpleNamespace(id=user_id), effective_message=message)


def make_handlers(active_alert: bool = True, limit: int = 50) -> CommandHandlers:
    container = AppContainer(
        report_service=ReportService(OrdersRepoStub()),
        alerts_service=AlertsService(AlertsRepoStub(active=active_alert)),
        rate_limiter=RateLimiter(max_calls=limit, window_seconds=20),
        message_sanitizer=MessageSanitizer(2000),
    )
    return CommandHandlers(container)


@pytest.mark.asyncio
async def test_report_command_returns_formatted_report() -> None:
    handlers = make_handlers()
    message = FakeMessage()
    await handlers.report(make_update(11, message), SimpleNamespace(user_data={}))
    assert "Отчет" in message.last_text
    assert "Top-3 SKU" in message.last_text


@pytest.mark.asyncio
async def test_alerts_command_returns_active_alerts() -> None:
    handlers = make_handlers(active_alert=True)
    message = FakeMessage()
    await handlers.alerts(make_update(12, message), SimpleNamespace(user_data={}))
    assert "Активные алерты" in message.last_text
    assert message.reply_markup is not None


@pytest.mark.asyncio
async def test_alerts_command_handles_empty_alerts() -> None:
    handlers = make_handlers(active_alert=False)
    message = FakeMessage()
    await handlers.alerts(make_update(13, message), SimpleNamespace(user_data={}))
    assert "Активных алертов нет" in message.last_text


@pytest.mark.asyncio
async def test_rate_limit_guard_for_commands() -> None:
    handlers = make_handlers(limit=1)
    message = FakeMessage()
    update = make_update(14, message)
    await handlers.report(update, SimpleNamespace(user_data={}))
    await handlers.report(update, SimpleNamespace(user_data={}))
    assert "Слишком много запросов" in message.last_text


@pytest.mark.asyncio
async def test_language_command_shows_keyboard() -> None:
    handlers = make_handlers()
    message = FakeMessage()
    context = SimpleNamespace(user_data={})
    await handlers.language(make_update(15, message), context)
    assert "Выберите язык" in message.last_text
    assert message.reply_markup is not None
