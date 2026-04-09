from types import SimpleNamespace

import pytest

from app.handlers.errors import telegram_error_handler


class FakeMessage:
    def __init__(self):
        self.text = ""

    async def reply_text(self, text: str) -> None:
        self.text = text


@pytest.mark.asyncio
async def test_error_handler_replies_to_user() -> None:
    update = SimpleNamespace(effective_user=SimpleNamespace(id=1), effective_message=FakeMessage())
    context = SimpleNamespace(error=RuntimeError("boom"))
    await telegram_error_handler(update, context)
    assert "ошибка" in update.effective_message.text.lower()


@pytest.mark.asyncio
async def test_error_handler_ignores_non_update() -> None:
    context = SimpleNamespace(error=RuntimeError("boom"))
    await telegram_error_handler(object(), context)
