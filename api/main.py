from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.v1.router import api_router
from api.middleware.request_logger import RequestLoggingMiddleware
from api.middleware.global_rate_limiting import GlobalRateLimitMiddleware
from fastapi.middleware.cors import CORSMiddleware
from api.middleware.request_id import RequestIDMiddleware
from db.init_db import init_db
from core.cache.redis_client import check_redis_connection

# Exception handlers
from api.exceptions import *
from utils.exceptions import *


# =====================================================
# Lifespan
# =====================================================
@asynccontextmanager
async def lifespan(app: FastAPI):

    init_db()
    check_redis_connection()  # 🔥 مهم

    yield


# =====================================================
# App
# =====================================================
app = FastAPI(
    title="TaskForge API",
    version="1.0.0",
    description="TaskForge - Smart Task Management SaaS",
    lifespan=lifespan
)


# =====================================================
# Middleware (ORDER MATTERS 🔥)
# =====================================================

# 1️⃣ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2️⃣ Rate Limiting
app.add_middleware(GlobalRateLimitMiddleware)

# 3️⃣ Logging
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestLoggingMiddleware)


# =====================================================
# Exception Handlers
# =====================================================

app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(ConflictError, conflict_error_handler)
app.add_exception_handler(AuthenticationError, authentication_error_handler)
app.add_exception_handler(PermissionDeniedError, permission_denied_handler)
app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(SecurityError, security_error_handler)
app.add_exception_handler(WeakPasswordError, weak_password_handler)
app.add_exception_handler(TokenError, token_error_handler)

# Task
app.add_exception_handler(TaskNotFoundError, task_not_found_handler)
app.add_exception_handler(ForbiddenTaskAccessError, forbidden_task_handler)
app.add_exception_handler(InvalidPaginationError, invalid_pagination_handler)

# Rate limit
app.add_exception_handler(RateLimitError, rate_limit_handler)

# 🔥 LAST
app.add_exception_handler(Exception, unhandled_exception_handler)


# =====================================================
# Routers
# =====================================================
app.include_router(api_router, prefix="/api/v1")