from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta

from app.core.errors import RateLimitError


class RateLimiter:
    def __init__(self, max_calls: int, window_seconds: int):
        self._max_calls = max_calls
        self._window = timedelta(seconds=window_seconds)
        self._buckets: dict[int, deque[datetime]] = defaultdict(deque)

    def check(self, user_id: int) -> None:
        now = datetime.now(UTC)
        bucket = self._buckets[user_id]
        while bucket and now - bucket[0] > self._window:
            bucket.popleft()
        if len(bucket) >= self._max_calls:
            raise RateLimitError("Too many requests. Try later.")
        bucket.append(now)
