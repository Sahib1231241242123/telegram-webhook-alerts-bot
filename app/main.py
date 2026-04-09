from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from telegram import Update
from telegram.ext import Application

from app.core.config import get_settings
from app.core.container import AppContainer
from app.core.logging import configure_logging, get_logger
from app.handlers.register import register_handlers
from app.repositories.json_alerts_repository import JsonAlertsRepository
from app.repositories.json_orders_repository import JsonOrdersRepository
from app.services.alerts_service import AlertsService
from app.services.message_sanitizer import MessageSanitizer
from app.services.rate_limiter import RateLimiter
from app.services.report_service import ReportService

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger("app.main")

base_dir = Path(__file__).resolve().parent.parent
fixtures_dir = base_dir / "fixtures"

orders_repo = JsonOrdersRepository(fixtures_dir / "orders.json")
alerts_repo = JsonAlertsRepository(fixtures_dir / "alerts.json")

container = AppContainer(
    report_service=ReportService(orders_repo),
    alerts_service=AlertsService(alerts_repo),
    rate_limiter=RateLimiter(settings.rate_limit_calls, settings.rate_limit_window_sec),
    message_sanitizer=MessageSanitizer(settings.max_message_len),
)

telegram_app = Application.builder().token(settings.bot_token).updater(None).build()
register_handlers(telegram_app, container)


def create_fastapi_app(enable_lifespan: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if not enable_lifespan:
            yield
            return

        await telegram_app.initialize()
        await telegram_app.start()
        await telegram_app.bot.set_webhook(settings.webhook_full_url)
        logger.info(
            "webhook_set",
            user_id=None,
            action="startup",
            alert_id=None,
            url=settings.webhook_full_url,
        )
        try:
            yield
        finally:
            await telegram_app.bot.delete_webhook(drop_pending_updates=False)
            await telegram_app.stop()
            await telegram_app.shutdown()
            logger.info("shutdown_complete", user_id=None, action="shutdown", alert_id=None)

    application = FastAPI(title="Telegram Bot MVP", lifespan=lifespan)

    @application.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.post(settings.webhook_path)
    async def webhook(request: Request) -> dict[str, bool]:
        try:
            payload = await request.json()
        except Exception as exc:  # pragma: no cover - defensive branch
            logger.warning("webhook_bad_json", user_id=None, action="webhook", alert_id=None)
            raise HTTPException(status_code=400, detail="Invalid JSON body.") from exc

        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Invalid update payload.")

        try:
            update = Update.de_json(payload, telegram_app.bot)
        except Exception as exc:
            logger.warning("webhook_bad_update", user_id=None, action="webhook", alert_id=None)
            raise HTTPException(status_code=400, detail="Malformed Telegram update.") from exc

        await telegram_app.update_queue.put(update)
        return {"ok": True}

    return application


app = create_fastapi_app(enable_lifespan=True)
