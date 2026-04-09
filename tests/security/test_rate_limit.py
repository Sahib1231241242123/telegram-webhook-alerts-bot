import pytest

from app.core.errors import RateLimitError
from app.services.rate_limiter import RateLimiter


def test_rate_limit_blocks_after_threshold() -> None:
    limiter = RateLimiter(max_calls=2, window_seconds=60)
    limiter.check(1)
    limiter.check(1)
    with pytest.raises(RateLimitError):
        limiter.check(1)


def test_rate_limit_is_per_user() -> None:
    limiter = RateLimiter(max_calls=1, window_seconds=60)
    limiter.check(1)
    limiter.check(2)
