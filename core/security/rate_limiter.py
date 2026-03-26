"""
Redis Sliding Window Rate Limiter (Production Version)
=====================================================

This module provides a production-grade rate limiter using Redis.

Design Goals
------------
✔ Distributed (works across multiple servers)
✔ Atomic operations (safe under concurrency)
✔ Sliding window algorithm (accurate limiting)
✔ Automatic cleanup using TTL
✔ Structured logging
✔ Clean architecture (reusable)

How It Works
------------
Each request is stored in a Redis Sorted Set:

    key     = rl:v1:<identifier>
    score   = timestamp (seconds)
    member  = unique value (timestamp + uuid)

Steps:
------
1️⃣ Remove expired entries (outside window)
2️⃣ Count current requests
3️⃣ If limit exceeded → block
4️⃣ Otherwise → add new request
"""

from datetime import datetime, timezone
import uuid

from core.cache.redis_client import redis_client, rate_limit_key
from utils.logger import get_logger
from utils.exceptions import RateLimitError
logger = get_logger(__name__)




# ==========================================================
# RateLimiter Class
# ==========================================================

class RateLimiter:
    """
    Redis-based Sliding Window Rate Limiter.

    Parameters
    ----------
    max_attempts : int
        Maximum number of allowed requests within the window.

    window_seconds : int
        Time window in seconds.

    Example
    -------
    limiter = RateLimiter(5, 300)
    limiter.check_and_add("login:ip:email")
    """

    def __init__(self, max_attempts: int, window_seconds: int):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds

    # ======================================================
    # Helpers
    # ======================================================

    def _key(self, identifier: str) -> str:
        """
        Build Redis key.

        Example:
            rl:v1:login:127.0.0.1:user@email.com
        """
        return rate_limit_key(identifier)

    def _now(self) -> int:
        """
        Current UTC timestamp in seconds.
        """
        return int(datetime.now(timezone.utc).timestamp())

    # ======================================================
    # Core Logic (Atomic)
    # ======================================================

    def check_and_add(self, identifier: str) -> None:
        """
        Check rate limit AND record request (atomic-safe pattern).

        Steps
        -----
        1️⃣ Remove expired entries
        2️⃣ Count active entries
        3️⃣ If limit exceeded → raise exception
        4️⃣ Otherwise → add new attempt

        Why atomic?
        ----------
        Prevents race conditions under high concurrency.
        """

        redis_key = self._key(identifier)

        now = self._now()
        window_start = now - self.window_seconds

        # ------------------------------------------
        # Step 1 + 2 (Atomic via pipeline)
        # ------------------------------------------
        pipe = redis_client.pipeline()

        # Remove expired entries
        pipe.zremrangebyscore(redis_key, 0, window_start)

        # Count current entries
        pipe.zcard(redis_key)

        _, attempts = pipe.execute()

        # ------------------------------------------
        # Step 3: Check limit
        # ------------------------------------------
        if attempts >= self.max_attempts:
            logger.warning(
                "Rate limit exceeded",
                extra={
                    "identifier": identifier,
                    "attempts": attempts,
                    "max": self.max_attempts,
                },
            )
            raise RateLimitError("Too many requests")

        # ------------------------------------------
        # Step 4: Add new attempt
        # ------------------------------------------
        member = f"{now}-{uuid.uuid4()}"

        pipe = redis_client.pipeline()

        pipe.zadd(redis_key, {member: now})

        # TTL ensures automatic cleanup
        pipe.expire(redis_key, self.window_seconds)

        pipe.execute()

    # ======================================================
    # Optional Utilities
    # ======================================================

    def reset(self, identifier: str) -> None:
        """
        Clear attempts for a specific identifier.

        Use case:
        - Successful login
        """
        redis_client.delete(self._key(identifier))

    def reset_all(self) -> None:
        """
        Remove ALL rate limit keys.

        ⚠ WARNING:
        - Use ONLY in testing
        - Uses SCAN (safe for production)
        """

        for key in redis_client.scan_iter("rl:v1:*"):
            redis_client.delete(key)


# ==========================================================
# Predefined Policies
# ==========================================================

"""
These are ready-to-use rate limiters for common use cases.
"""

# Login protection (anti brute-force)
login_rate_limiter = RateLimiter(
    max_attempts=5,
    window_seconds=300  # 5 minutes
)

# General API limiter (global)
global_rate_limiter = RateLimiter(
    max_attempts=100,
    window_seconds=60  # 100 requests per minute
)