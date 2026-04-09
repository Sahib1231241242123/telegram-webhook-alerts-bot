from telegram.ext import ContextTypes

from app.core.i18n import get_user_language, translate
from app.core.logging import get_logger

logger = get_logger("handlers.errors")


async def telegram_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = None
    if getattr(update, "effective_user", None):
        user_id = update.effective_user.id
    logger.error(
        "telegram_handler_failed",
        user_id=user_id,
        action="error_handler",
        alert_id=None,
        exc_info=context.error,
    )

    if getattr(update, "effective_message", None):
        language = get_user_language(getattr(context, "user_data", {}))
        await update.effective_message.reply_text(translate("internal_error", language))
