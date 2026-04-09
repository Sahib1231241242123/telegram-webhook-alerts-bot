from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from app.core.container import AppContainer
from app.handlers.callbacks import CallbackHandlers
from app.handlers.commands import CommandHandlers
from app.handlers.errors import telegram_error_handler


def register_handlers(application: Application, container: AppContainer) -> None:
    command_handlers = CommandHandlers(container)
    callback_handlers = CallbackHandlers(container)

    application.add_handler(CommandHandler("start", command_handlers.start))
    application.add_handler(CommandHandler("language", command_handlers.language))
    application.add_handler(CommandHandler("report", command_handlers.report))
    application.add_handler(CommandHandler("alerts", command_handlers.alerts))
    application.add_handler(CallbackQueryHandler(callback_handlers.handle))
    application.add_error_handler(telegram_error_handler)
