# utils/exceptions.py

# ======================
# Base application error
# ======================

from __future__ import annotations


class TaskNotFoundError(Exception):
    """
    Raised when a task does not exist.
    Domain-level exception (no HTTP knowledge).
    """
    pass


class ForbiddenTaskAccessError(Exception):
    """
    Raised when a user tries to access a task
    they do not own.
    """
    pass


class InvalidPaginationError(Exception):
    """
    Raised when pagination parameters
    violate business rules.
    """
    pass




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

class TokenError(SecurityError):
    """ Invalid , Expired or reused token"""
    pass