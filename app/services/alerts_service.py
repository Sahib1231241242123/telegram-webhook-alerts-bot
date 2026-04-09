from app.core.errors import NotFoundError
from app.repositories.interfaces import AlertsRepository
from app.schemas.alert import AlertRecord


class AlertsService:
    def __init__(self, alerts_repo: AlertsRepository):
        self._alerts_repo = alerts_repo
        self._status_overrides: dict[str, str] = {}

    async def get_active_alerts(self) -> list[AlertRecord]:
        alerts = await self._alerts_repo.get_alerts()
        active: list[AlertRecord] = []
        for alert in alerts:
            status = self._status_overrides.get(alert.id, alert.status)
            if status == "active":
                active.append(alert)
        return active

    async def get_alert_details(self, alert_id: str) -> AlertRecord:
        alerts = await self._alerts_repo.get_alerts()
        for alert in alerts:
            if alert.id == alert_id:
                return alert
        raise NotFoundError("Alert not found.")

    async def confirm_alert(self, alert_id: str) -> None:
        await self._ensure_exists(alert_id)
        self._status_overrides[alert_id] = "confirmed"

    async def reject_alert(self, alert_id: str) -> None:
        await self._ensure_exists(alert_id)
        self._status_overrides[alert_id] = "rejected"

    async def _ensure_exists(self, alert_id: str) -> None:
        _ = await self.get_alert_details(alert_id)

    @staticmethod
    def format_alerts(alerts: list[AlertRecord], language: str = "ru") -> str:
        if not alerts:
            return "🔕 No active alerts." if language == "en" else "🔕 Активных алертов нет."
        rows = [f"• [{item.id}] {item.title} (severity: {item.severity})" for item in alerts]
        header = "🚨 Active alerts:\n\n" if language == "en" else "🚨 Активные алерты:\n\n"
        return header + "\n".join(rows)

    @staticmethod
    def format_alert_details(alert: AlertRecord, language: str = "ru") -> str:
        if language == "en":
            return (
                f"ℹ️ Alert details [{alert.id}]\n\n"
                f"Title: {alert.title}\n"
                f"Reasoning: {alert.reasoning}\n"
                f"Expected impact: {alert.expected_impact}"
            )
        return (
            f"ℹ️ Детали алерта [{alert.id}]\n\n"
            f"Название: {alert.title}\n"
            f"Reasoning: {alert.reasoning}\n"
            f"Expected impact: {alert.expected_impact}"
        )
