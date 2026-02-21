"""
conftest.py
============

This file defines the COMPLETE testing infrastructure for the project.

Goals:
- Mirror real application behavior
- Avoid mocking business logic
- Isolate tests from production
- Support auth, tokens, rate-limit, tasks, permissions

NO production code is modified by this file.
"""

# =================================================
# MUST be first — before any project import
# =================================================
import os

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("PASSWORD_PEPPER", "test-password-pepper")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

# =================================================
# Now safe imports
# =================================================

# -------------------------------------------------
# Standard library
# -------------------------------------------------

from datetime import datetime, timedelta, timezone

# -------------------------------------------------
# Third-party
# -------------------------------------------------
import pytest
from fastapi.testclient import TestClient
from jose import jwt

# -------------------------------------------------
# Application imports
# -------------------------------------------------
from api.main import app

from core.config import get_settings
from storage.memory_storage import MemoryStorage

from services.auth_s import AuthService
from services.task_s import TaskService

from api.deps.services import (
    get_storage,
    get_auth_service,
    get_task_service,
)

from utils.jwt_utils import create_access_token
from core.enums.user_role import UserRole
from utils.rate_limiter import login_rate_limiter
from utils.rate_limiter import RateLimiter

# =================================================
# for test window_seconds, we use a short duration to speed up tests
# =================================================
test_login_rate_limiter = RateLimiter(max_attempts=5, window_seconds=1)  # 1 second window for testing
# =================================================
# 1️⃣ Environment variables (same as production)
# =================================================

@pytest.fixture(scope="session", autouse=True)
def _set_test_env():
    """
    Ensure ALL required environment variables exist.

    We do NOT mock settings.
    We load real settings, but with test-safe values.
    """
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    os.environ.setdefault("PASSWORD_PEPPER", "test-password-pepper")
    os.environ.setdefault("JWT_ALGORITHM", "HS256")



# =================================================
# 3️⃣ Storage layer (shared in-memory DB)
# =================================================

@pytest.fixture(scope="session")
def storage():
    """
    Single MemoryStorage instance for the test session.

    Why?
    - Matches real storage interface
    - Fast
    - Deterministic
    """
    return MemoryStorage()

@pytest.fixture(autouse=True)
def clear_storage(storage):
    """
    Clear storage before each test to ensure test isolation.
    """
    storage.clear()


# =================================================
# 4️⃣ Services layer (REAL services)
# =================================================

@pytest.fixture(scope="session")
def auth_service(storage):
    """
    AuthService wired exactly like production,
    but using MemoryStorage.
    """
    return AuthService(
        storage=storage,
        
    )


@pytest.fixture(scope="session")
def task_service(storage):
    """
    TaskService with same storage as auth.
    """
    return TaskService(storage=storage)

# =================================================
# rate limiter (shared instance to track attempts)
# =================================================
@pytest.fixture(autouse=True)
def reset_login_rate_limiter():
    """ensure the rate limiter is reset before each test 
    to avoid cross-test interference."""
    login_rate_limiter.reset_all()

# =================================================
# 5️⃣ FastAPI dependency overrides
# =================================================

@pytest.fixture(scope="session", autouse=True)
def override_dependencies(storage, auth_service, task_service):
    """
    Override FastAPI dependencies so:
    - API uses MemoryStorage
    - API uses REAL services
    """
    app.dependency_overrides[get_storage] = lambda: storage
    app.dependency_overrides[get_auth_service] = lambda: auth_service
    app.dependency_overrides[get_task_service] = lambda: task_service

    yield

    app.dependency_overrides.clear()


# =================================================
# 6️⃣ Test client
# =================================================

@pytest.fixture()
def client():
    """
    FastAPI TestClient with overridden deps.
    """
    with TestClient(app) as c:
        yield c


# =================================================
# 7️⃣ Users (REAL domain users)
# =================================================

@pytest.fixture()
def user(auth_service):
    """
    Normal user with valid password rules.
    """
    return auth_service.register(
        username="testuser",
        email="user@test.com",
        password="StrongPass1!",
        role=UserRole.USER,
    )


@pytest.fixture()
def admin(auth_service):
    """
    Admin user.
    """
    return auth_service.register(
        username="adminuser",
        email="admin@test.com",
        password="StrongPass1!",
        role=UserRole.ADMIN,
    )


@pytest.fixture()
def other_user(auth_service):
    """
    Another normal user (ownership testing).
    """
    return auth_service.register(
        username="otheruser",
        email="other@test.com",
        password="StrongPass1!",
        role="user",
    )


# =================================================
# 8️⃣ Auth headers (JWT access tokens)
# =================================================

@pytest.fixture()
def user_headers(user):
    """
    Authorization header for normal user.
    """
    token = create_access_token(subject=str(user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_headers(admin):
    """
    Authorization header for admin.
    """
    token = create_access_token(admin.id)
    return {"Authorization": f"Bearer {token}"}


# =================================================
# 9️⃣ Expired token (ATTACK / FAILURE CASE)
# =================================================

@pytest.fixture()
def expired_token(settings, user):
    """
    Create an EXPIRED JWT.

    IMPORTANT:
    - This logic lives ONLY in tests
    - jwt_utils remains clean
    """
    payload = {
        "sub": str(user.id),
        "iat": datetime.now(timezone.utc) - timedelta(minutes=10),
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
        "type": "access",
    }
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


@pytest.fixture()
def expired_headers(expired_token):
    return {"Authorization": f"Bearer {expired_token}"}


# =================================================
# 🔟 Tasks (ownership & permissions)
# =================================================

@pytest.fixture()
def user_task(task_service, user):
    """
    Task owned by normal user.
    """
    return task_service.create_task(
        title="User Task",
        description="Owned by user",
        owner_id=user.id,
    )


@pytest.fixture()
def other_user_task(task_service, other_user):
    """
    Task owned by another user.
    """
    return task_service.create_task(
        title="Other User Task",
        description="Owned by other user",
        owner_id=other_user.id,
    )