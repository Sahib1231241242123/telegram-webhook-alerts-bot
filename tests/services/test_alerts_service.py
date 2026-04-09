import pytest

from app.core.errors import NotFoundError
from app.schemas.alert import AlertRecord
from app.services.alerts_service import AlertsService


class AlertsRepoStub:
    def __init__(self, alerts: list[AlertRecord]):
        self._alerts = alerts

    async def get_alerts(self) -> list[AlertRecord]:
        return self._alerts


def _alerts() -> list[AlertRecord]:
    return [
        AlertRecord(
            id="A-1",
            title="Alert 1",
            severity="high",
            status="active",
            reasoning="why",
            expected_impact="impact",
        ),
        AlertRecord(
            id="A-2",
            title="Alert 2",
            severity="low",
            status="resolved",
            reasoning="why2",
            expected_impact="impact2",
        ),
    ]


@pytest.mark.asyncio
async def test_get_active_alerts() -> None:
    service = AlertsService(AlertsRepoStub(_alerts()))
    active = await service.get_active_alerts()
    assert len(active) == 1
    assert active[0].id == "A-1"


@pytest.mark.asyncio
async def test_confirm_and_reject_remove_from_active() -> None:
    service = AlertsService(AlertsRepoStub(_alerts()))
    await service.confirm_alert("A-1")
    assert await service.get_active_alerts() == []
    await service.reject_alert("A-1")
    assert await service.get_active_alerts() == []


@pytest.mark.asyncio
async def test_get_details_and_not_found() -> None:
    service = AlertsService(AlertsRepoStub(_alerts()))
    details = await service.get_alert_details("A-1")
    assert "impact" in details.expected_impact
    with pytest.raises(NotFoundError):
        await service.get_alert_details("missing")
