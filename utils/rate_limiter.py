# utils/ratelimiter.py
from datetime import datetime, timedelta,timezone


class RateLimitExceeded(Exception):
    pass


class RateLimiter:
    def __init__(self, max_attempts: int, window_seconds: int):
        self.max_attempts = max_attempts
        self.window = timedelta(seconds=window_seconds)
        self.attempts: dict[str, list[datetime]] = {}

    def _now(self) -> datetime:
        return datetime.now( timezone.utc)

    def check(self, key: str) -> None:
        now = self._now()
        attempts = self.attempts.get(key, [])

        # تنظيف المحاولات القديمة
        attempts = [
            ts for ts in attempts
            if now - ts <= self.window
        ]
        self.attempts[key] = attempts

        if len(attempts) >= self.max_attempts:
            raise RateLimitExceeded("Too many attempts")

    def add_attempt(self, key: str) -> None:
        self.attempts.setdefault(key, []).append(self._now())

    def reset(self, key: str) -> None:
        self.attempts.pop(key, None)

    def reset_all(self) -> None:
        self.attempts.clear()    

    # =====================================
# Rate limit policies
# =====================================

login_rate_limiter = RateLimiter(max_attempts=5, window_seconds=300)  # 5 attempts every 5 minutes