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
)

"""
Global Exception Handlers

Design Rules:
- Only handle domain-level exceptions.
- Do NOT override FastAPI/Pydantic 422 validation.
- Do NOT catch generic Exception or AppError.
- HTTP mapping lives here only.
"""


# ---------- 422 Domain Validation ----------

async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )


# ---------- 409 Conflict ----------

async def conflict_error_handler(request: Request, exc: ConflictError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


# ---------- 401 Authentication ----------

async def authentication_error_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


async def token_error_handler(request: Request, exc: TokenError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


# ---------- 403 Permission ----------

async def permission_denied_handler(request: Request, exc: PermissionDeniedError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc)},
    )


async def forbidden_task_handler(request: Request, exc: ForbiddenTaskAccessError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "Not allowed to access this task"},
    )


# ---------- 404 Not Found ----------

async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def task_not_found_handler(request: Request, exc: TaskNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Task not found"},
    )


# ---------- 422 Security ----------

async def security_error_handler(request: Request, exc: SecurityError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )


async def invalid_pagination_handler(request: Request, exc: InvalidPaginationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )


# ---------- 400 Weak Password ----------

async def weak_password_handler(request: Request, exc: WeakPasswordError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Password does not meet security requirements"},
    )