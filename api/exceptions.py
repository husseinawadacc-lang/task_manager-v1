from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import status

from utils.exceptions import (
    AppError,
    ValidationError,
    ConflictError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    SecurityError,
)


def register_exception_handlers(app):
    """
    Register application-level exception handlers.

    ⚠️ IMPORTANT:
    - We DO NOT catch FastAPI / Pydantic validation errors (422)
    - We ONLY handle our custom domain exceptions
    """

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ConflictError)
    async def conflict_error_handler(request: Request, exc: ConflictError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
        )

    @app.exception_handler(PermissionDeniedError)
    async def permission_error_handler(request: Request, exc: PermissionDeniedError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(exc)},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(SecurityError)
    async def security_error_handler(request: Request, exc: SecurityError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)},
        )

    # ❌ لا تكتب handler لـ Exception أو AppError عام