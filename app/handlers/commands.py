from telegram import Update
from telegram.ext import ContextTypes

from app.core.container import AppContainer
from app.core.errors import DataValidationError, RateLimitError
from app.core.i18n import get_user_language, translate
from app.core.logging import get_logger
from app.keyboards.alerts_keyboard import build_alerts_keyboard
from app.keyboards.language_keyboard import build_language_keyboard
from app.services.alerts_service import AlertsService
from app.services.report_service import ReportService


class CommandHandlers:
    def __init__(self, container: AppContainer):
        self._container = container
        self._logger = get_logger("handlers.commands")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id if update.effective_user else 0
        self._logger.info("command_received", user_id=user_id, action="start", alert_id=None)
        lang = get_user_language(context.user_data)
        await self._reply(update, translate("start", lang))

    async def language(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id if update.effective_user else 0
        self._logger.info("command_received", user_id=user_id, action="language", alert_id=None)
        lang = get_user_language(context.user_data)
        await self._reply(
            update,
            translate("language_prompt", lang),
            reply_markup=build_language_keyboard(),
        )

    async def report(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id if update.effective_user else 0
        self._logger.info("command_received", user_id=user_id, action="report", alert_id=None)
        lang = get_user_language(context.user_data)
        if not await self._allow_request(update, context, user_id, "report"):
            return

        try:
            report = await self._container.report_service.build_report()
            text = ReportService.format_report(report, lang)
        except DataValidationError:
            self._logger.error(
                "report_data_invalid",
                user_id=user_id,
                action="report",
                alert_id=None,
            )
            text = translate("report_data_unavailable", lang)

        await self._reply(update, text)

    async def alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id if update.effective_user else 0
        self._logger.info("command_received", user_id=user_id, action="alerts", alert_id=None)
        lang = get_user_language(context.user_data)
        if not await self._allow_request(update, context, user_id, "alerts"):
            return

        try:
            alerts = await self._container.alerts_service.get_active_alerts()
            text = AlertsService.format_alerts(alerts, lang)
        except DataValidationError:
            self._logger.error(
                "alerts_data_invalid",
                user_id=user_id,
                action="alerts",
                alert_id=None,
            )
            alerts = []
            text = translate("alerts_data_unavailable", lang)

        keyboard = build_alerts_keyboard(alerts, lang) if alerts else None
        await self._reply(update, text, reply_markup=keyboard)

    async def _allow_request(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_id: int,
        action: str,
    ) -> bool:
        try:
            self._container.rate_limiter.check(user_id)
            return True
        except RateLimitError:
            self._logger.warning("rate_limited", user_id=user_id, action=action, alert_id=None)
            lang = get_user_language(context.user_data)
            await self._reply(update, translate("rate_limited", lang))
            return False

    async def _reply(self, update: Update, text: str, reply_markup=None) -> None:
        safe_text = self._container.message_sanitizer.sanitize(text)
        if update.effective_message:
            await update.effective_message.reply_text(safe_text, reply_markup=reply_markup)
