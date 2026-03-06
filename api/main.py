from fastapi import FastAPI
from api.v1.router import api_router
from api.exceptions import (
    validation_error_handler,
    conflict_error_handler,
    authentication_error_handler,
    permission_denied_handler,
    not_found_handler,
    security_error_handler,
    weak_password_handler,
    token_error_handler,
    task_not_found_handler,
    forbidden_task_handler,
    invalid_pagination_handler,
)

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

app = FastAPI(title="task manger")

# ---------- Register Handlers ----------

app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(ConflictError, conflict_error_handler)
app.add_exception_handler(AuthenticationError, authentication_error_handler)
app.add_exception_handler(PermissionDeniedError, permission_denied_handler)
app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(SecurityError, security_error_handler)
app.add_exception_handler(WeakPasswordError, weak_password_handler)
app.add_exception_handler(TokenError, token_error_handler)

# Task-specific
app.add_exception_handler(TaskNotFoundError, task_not_found_handler)
app.add_exception_handler(ForbiddenTaskAccessError, forbidden_task_handler)
app.add_exception_handler(InvalidPaginationError, invalid_pagination_handler)

# =====================================================
# Routers
# =====================================================
app.include_router(api_router,prefix="/api/v1")
