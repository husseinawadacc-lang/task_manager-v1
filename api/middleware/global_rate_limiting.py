from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from core.security.rate_limiter import global_rate_limiter
from utils.exceptions import RateLimitError
from utils.logger import get_logger

logger = get_logger(__name__)


class GlobalRateLimitMiddleware(BaseHTTPMiddleware):

    EXCLUDED_PATHS = {
        "/docs",
        "/openapi.json",
        "/redoc",
    }

    async def dispatch(self, request: Request, call_next):

        # =========================================
        # 1️⃣ Skip docs & login
        # =========================================
        if (
            request.url.path in self.EXCLUDED_PATHS
            or request.url.path.startswith("/api/v1/auth/login")
        ):
            return await call_next(request)

        # =========================================
        # 2️⃣ Extract client IP (proxy-safe)
        # =========================================
        client_ip = request.headers.get(
            "X-Forwarded-For",
            request.client.host if request.client else "unknown"
        )

        # =========================================
        # 3️⃣ Build key
        # =========================================
        key = f"global:{client_ip}"

        # =========================================
        # 4️⃣ Apply rate limit
        # =========================================
        try:
            global_rate_limiter.check_and_add(key)

        except RateLimitError:

            logger.warning(
                "Global rate limit exceeded",
                extra={
                    "ip": client_ip,
                    "path": request.url.path,
                },
            )

            # 🔥 مهم: سيب exception handler يتعامل
            raise RateLimitError("Too many requests")

        # =========================================
        # 5️⃣ Continue
        # =========================================
        return await call_next(request)