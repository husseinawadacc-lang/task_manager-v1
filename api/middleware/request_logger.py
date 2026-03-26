import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from utils.logger import get_logger

logger = get_logger("request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        request_id = str(uuid.uuid4())  # 🔥 trace id
        start = time.time()

        # 🔥 لو عندك auth middleware
        user_id = getattr(request.state, "user_id", None)

        try:
            response = await call_next(request)

            duration = round((time.time() - start) * 1000)

            logger.info(
                "Request processed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "duration_ms": duration,
                    "user_id": user_id,
                },
            )

            return response

        except Exception as e:

            duration = round((time.time() - start) * 1000)

            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration,
                    "user_id": user_id,
                    "error": str(e),
                },
            )

            raise