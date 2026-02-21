# utils/exceptions.py

# ======================
# Base application error
# ======================
class AppError(Exception):
    """Base application error"""
    pass


# ======================
# Validation & business
# ======================
class ValidationError(AppError):
    """Invalid input or state"""
    pass


class ConflictError(AppError):
    """Conflict errors (e.g. email already exists)"""
    pass


class NotFoundError(AppError):
    """Resource not found"""
    pass


# ======================
# Authentication / Authorization
# ======================
class AuthenticationError(AppError):
    """Invalid authentication credentials"""
    pass


class PermissionDeniedError(AppError):
    """User does not have permission"""
    pass


# ======================
# Security (subset of AppError)
# ======================
class SecurityError(AppError):
    """Security related errors"""
    pass


class WeakPasswordError(SecurityError):
    """Password does not meet strength requirements"""
    pass