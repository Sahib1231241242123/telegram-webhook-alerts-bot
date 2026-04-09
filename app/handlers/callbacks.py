from telegram import Update
from telegram.ext import ContextTypes

from app.core.container import AppContainer
from app.core.errors import DataValidationError, NotFoundError, RateLimitError
from app.core.i18n import SUPPORTED_LANGUAGES, get_user_language, set_user_language, translate
from app.core.logging import get_logger
from app.handlers import fsm
from app.keyboards.alerts_keyboard import build_alerts_keyboard, build_back_to_alerts_keyboard
from app.keyboards.language_keyboard import build_language_keyboard
from app.schemas.callbacks import CallbackAction, CallbackPayload
from app.services.alerts_service import AlertsService


class CallbackHandlers:
    def __init__(self, container: AppContainer):
        self._container = container
        self._logger = get_logger("handlers.callbacks")

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        user_id = update.effective_user.id if update.effective_user else 0
        if query is None:
            return

        await query.answer()
        lang = get_user_language(context.user_data)
        try:
            self._container.rate_limiter.check(user_id)
        except RateLimitError:
            self._logger.warning("rate_limited", user_id=user_id, action="callback", alert_id=None)
            await query.edit_message_text(translate("callback_rate_limited", lang))
            return

        try:
            payload = CallbackPayload.unpack(query.data or "")
        except DataValidationError:
            self._logger.warning(
                "malformed_callback",
                user_id=user_id,
                action="invalid_callback",
                alert_id=None,
            )
            await query.edit_message_text(translate("invalid_callback", lang))
            return

        self._logger.info(
            "callback_received",
            user_id=user_id,
            action=payload.action.value,
            alert_id=payload.alert_id,
        )

        if payload.action == CallbackAction.SET_LANG:
            await self._handle_set_language(query, context, payload.alert_id)
            return
        if payload.action == CallbackAction.CONFIRM:
            await self._handle_confirm(query, context, payload.alert_id)
            return
        if payload.action == CallbackAction.REJECT:
            await self._handle_reject(query, context, payload.alert_id)
            return
        if payload.action == CallbackAction.DETAILS:
            await self._handle_details(query, context, payload.alert_id)
            return
        if payload.action == CallbackAction.BACK:
            await self._handle_back(query, context, payload.alert_id)
            return

        await query.edit_message_text(translate("unknown_callback_action", lang))

    async def _handle_set_language(
        self,
        query,
        context: ContextTypes.DEFAULT_TYPE,
        language_code: str,
    ) -> None:
        if language_code not in SUPPORTED_LANGUAGES:
            await query.edit_message_text(
                translate("invalid_callback", get_user_language(context.user_data))
            )
            return
        lang = set_user_language(context.user_data, language_code)
        await query.edit_message_text(
            translate("language_changed", lang),
            reply_markup=build_language_keyboard(),
        )

    async def _handle_confirm(
        self,
        query,
        context: ContextTypes.DEFAULT_TYPE,
        alert_id: str,
    ) -> None:
        lang = get_user_language(context.user_data)
        try:
            await self._container.alerts_service.confirm_alert(alert_id)
            alerts = await self._container.alerts_service.get_active_alerts()
            prefix = (
                f"✅ Alert [{alert_id}] confirmed."
                if lang == "en"
                else f"✅ Алерт [{alert_id}] подтвержден."
            )
            text = f"{prefix}\n\n{AlertsService.format_alerts(alerts, lang)}"
            keyboard = build_alerts_keyboard(alerts, lang) if alerts else None
            await query.edit_message_text(
                self._container.message_sanitizer.sanitize(text),
                reply_markup=keyboard,
            )
        except NotFoundError:
            await query.edit_message_text(translate("alert_not_found", lang))

    async def _handle_reject(
        self,
        query,
        context: ContextTypes.DEFAULT_TYPE,
        alert_id: str,
    ) -> None:
        lang = get_user_language(context.user_data)
        try:
            await self._container.alerts_service.reject_alert(alert_id)
            alerts = await self._container.alerts_service.get_active_alerts()
            prefix = (
                f"❌ Alert [{alert_id}] rejected."
                if lang == "en"
                else f"❌ Алерт [{alert_id}] отклонен."
            )
            text = f"{prefix}\n\n{AlertsService.format_alerts(alerts, lang)}"
            keyboard = build_alerts_keyboard(alerts, lang) if alerts else None
            await query.edit_message_text(
                self._container.message_sanitizer.sanitize(text),
                reply_markup=keyboard,
            )
        except NotFoundError:
            await query.edit_message_text(translate("alert_not_found", lang))

    async def _handle_details(
        self,
        query,
        context: ContextTypes.DEFAULT_TYPE,
        alert_id: str,
    ) -> None:
        lang = get_user_language(context.user_data)
        try:
            alert = await self._container.alerts_service.get_alert_details(alert_id)
            fsm.set_details_state(context.user_data, alert_id)
            text = self._container.alerts_service.format_alert_details(alert, lang)
            await query.edit_message_text(
                self._container.message_sanitizer.sanitize(text),
                reply_markup=build_back_to_alerts_keyboard(alert_id, lang),
            )
        except NotFoundError:
            await query.edit_message_text(translate("alert_not_found", lang))

    async def _handle_back(
        self,
        query,
        context: ContextTypes.DEFAULT_TYPE,
        alert_id: str,
    ) -> None:
        lang = get_user_language(context.user_data)
        if fsm.is_details_state(context.user_data):
            fsm.reset_state(context.user_data)
        alerts = await self._container.alerts_service.get_active_alerts()
        text = AlertsService.format_alerts(alerts, lang)
        keyboard = build_alerts_keyboard(alerts, lang) if alerts else None
        await query.edit_message_text(
            self._container.message_sanitizer.sanitize(text),
            reply_markup=keyboard,
        )
