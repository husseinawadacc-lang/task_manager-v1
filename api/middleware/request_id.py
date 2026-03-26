import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from utils.request_context import request_id_ctx


class RequestIDMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        # 1️⃣ generate request id
        request_id = str(uuid.uuid4())

        # 2️⃣ store in context
        request_id_ctx.set(request_id)

        # 3️⃣ attach to request (optional)
        request.state.request_id = request_id

        response = await call_next(request)

        # 4️⃣ add header (important)
        response.headers["X-Request-ID"] = request_id

        return response