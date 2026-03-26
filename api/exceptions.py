from fastapi import Request, status
from fastapi.responses import JSONResponse

from utils.exceptions import (
    ValidationError,
    ConflictError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    SecurityError,
    WeakPasswordError,
    TokenError,
    TaskNotFoundError,
    ForbiddenTaskAccessError,
    InvalidPaginationError,
    RateLimitError,
)

from utils.logger import get_logger

"""
Global Exception Handlers (Production Version)
=============================================

Rules
-----
✔ Only domain exceptions
✔ No override for FastAPI validation
✔ No generic catching (except 500 fallback)
✔ Centralized HTTP mapping
✔ Structured logging
"""

logger = get_logger("exceptions")


# ==========================================================
# 422 Validation
# ==========================================================
async def validation_error_handler(request: Request, exc: ValidationError):

    logger.info(
        "Validation error",
        extra={
            "path": request.url.path,
            "method": request.method,
            "detail": str(exc),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )


# ==========================================================
# 409 Conflict
# ==========================================================
async def conflict_error_handler(request: Request, exc: ConflictError):

    logger.warning(
        "Conflict error",
        extra={
            "path": request.url.path,
            "method": request.method,
            "detail": str(exc),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


# ==========================================================
# 401 Authentication
# ==========================================================
async def authentication_error_handler(request: Request, exc: AuthenticationError):

    logger.warning(
        "Authentication failed",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


async def token_error_handler(request: Request, exc: TokenError):

    logger.warning(
        "Invalid token",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


# ==========================================================
# 403 Permission
# ==========================================================
async def permission_denied_handler(request: Request, exc: PermissionDeniedError):

    logger.warning(
        "Permission denied",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc)},
    )


async def forbidden_task_handler(request: Request, exc: ForbiddenTaskAccessError):

    logger.warning(
        "Forbidden task access",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "Not allowed to access this task"},
    )


# ==========================================================
# 404 Not Found (Anti-IDOR friendly)
# ==========================================================
async def not_found_handler(request: Request, exc: NotFoundError):

    logger.info(
        "Resource not found",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def task_not_found_handler(request: Request, exc: TaskNotFoundError):

    logger.info(
        "Task not found",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Task not found"},
    )


# ==========================================================
# 422 Security
# ==========================================================
async def security_error_handler(request: Request, exc: SecurityError):

    logger.error(
        "Security violation",
        extra={
            "path": request.url.path,
            "method": request.method,
            "detail": str(exc),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error" : "validation_error" ,"detail": str(exc)},
    )


async def invalid_pagination_handler(request: Request, exc: InvalidPaginationError):

    logger.info(
        "Invalid pagination",
        extra={
            "path": request.url.path,
            "method": request.method,
            "detail": str(exc),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error" : "validation_error" ,"detail": str(exc)},
    )


# ==========================================================
# 400 Weak Password
# ==========================================================
async def weak_password_handler(request: Request, exc: WeakPasswordError):

    logger.info(
        "Weak password",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Password does not meet security requirements"},
    )


# ==========================================================
# 429 Rate Limit (Global + Login)
# ==========================================================
async def rate_limit_handler(request: Request, exc: RateLimitError):

    logger.warning(
        "Rate limit exceeded",
        extra={
            "path": request.url.path,
            "method": request.method,
            "detail": str(exc),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": str(exc),
        },
    )


# ==========================================================
# 500 Fallback (VERY IMPORTANT 🔥)
# ==========================================================
async def unhandled_exception_handler(request: Request, exc: Exception):

    logger.error(
        "Unhandled exception",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error": str(exc),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
        },
    )