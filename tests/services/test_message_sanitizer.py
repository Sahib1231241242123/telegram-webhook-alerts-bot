from app.services.message_sanitizer import MessageSanitizer


def test_message_sanitizer_truncates_long_text() -> None:
    sanitizer = MessageSanitizer(30)
    result = sanitizer.sanitize("x" * 100)
    assert len(result) <= 30
    assert "сокращено" in result


def test_message_sanitizer_keeps_short_text() -> None:
    sanitizer = MessageSanitizer(50)
    text = "короткий текст"
    assert sanitizer.sanitize(text) == text
