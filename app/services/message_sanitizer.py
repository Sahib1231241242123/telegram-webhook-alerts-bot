class MessageSanitizer:
    def __init__(self, max_len: int):
        self._max_len = max_len

    def sanitize(self, text: str) -> str:
        if len(text) <= self._max_len:
            return text
        safe_tail = "\n\n... [сообщение сокращено]"
        allowed = self._max_len - len(safe_tail)
        return text[: max(allowed, 0)] + safe_tail
