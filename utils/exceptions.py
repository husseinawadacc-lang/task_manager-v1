class AppError(Exception):
    """Base application error"""
    pass

class ForbiddenError(Exception):
    """
    Raised when user tries to access forbidden resource
    """
    pass

class RateLimitError(Exception):
    """
    Raised when a user exceeds allowed rate limits.

    Used for:
    - login brute-force protection
    - API abuse prevention
    """

    def __init__(self, message: str = "Too many requests, please try again later"):
        self.message = message
        super().__init__(self.message)
# ======================
# Validation & business
# ======================

class ValidationError(AppError):
    pass


class ConflictError(AppError):
    pass


class NotFoundError(AppError):
    pass


# ======================
# Authentication / Authorization
# ======================

class AuthenticationError(AppError):
    pass


class PermissionDeniedError(AppError):
    pass


# ======================
# Security
# ======================

class SecurityError(AppError):
    pass


class WeakPasswordError(SecurityError):
    pass


class TokenError(SecurityError):
    pass


# ======================
# Domain errors
# ======================

class TaskNotFoundError(AppError):
    pass


class ForbiddenTaskAccessError(AppError):
    pass


class InvalidPaginationError(AppError):
    pass
