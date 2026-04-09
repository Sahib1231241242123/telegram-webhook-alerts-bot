from app.core.container import AppContainer
from app.handlers.register import register_handlers
from app.services.message_sanitizer import MessageSanitizer
from app.services.rate_limiter import RateLimiter


class DummyApp:
    def __init__(self):
        self.handlers = []
        self.error_handler = None

    def add_handler(self, handler):
        self.handlers.append(handler)

    def add_error_handler(self, handler):
        self.error_handler = handler


class DummyService:
    async def get_orders(self):
        return []

    async def get_alerts(self):
        return []


def test_register_handlers() -> None:
    app = DummyApp()
    container = AppContainer(
        report_service=DummyService(),
        alerts_service=DummyService(),
        rate_limiter=RateLimiter(5, 10),
        message_sanitizer=MessageSanitizer(100),
    )
    register_handlers(app, container)
    assert len(app.handlers) == 5
    assert app.error_handler is not None
