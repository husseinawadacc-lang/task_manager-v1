"""
conftest.py
===========

Central testing infrastructure for the entire project.

Goals
-----
- Provide a realistic testing environment
- Use real services (no mocking business logic)
- Keep tests isolated from production configuration
- Provide reusable fixtures for:

    - users
    - authentication
    - tokens
    - tasks
    - rate limiting
    - password reset
    - pagination

Important
---------
This file MUST NOT modify production code.
It only configures the environment for testing.
"""

# ============================================================
# 1️⃣ TEST ENVIRONMENT CONFIGURATION
# ============================================================
# These variables MUST be set before importing the application.

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("PASSWORD_PEPPER", "test-password-pepper")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:password@localhost:5432/testdb"
)

# ============================================================
# 2️⃣ STANDARD LIBRARIES
# ============================================================

from datetime import datetime, timedelta, timezone

# ============================================================
# 3️⃣ THIRD-PARTY LIBRARIES
# ============================================================

import pytest
from fastapi.testclient import TestClient
from jose import jwt

# ============================================================
# 4️⃣ APPLICATION IMPORTS
# ============================================================

from api.main import app

from core.config import get_settings
from core.auth.jwt import create_access_token
from core.auth.token import hash_token, generate_refresh_token

from core.enums.role import UserRole

from core.security.rate_limiter import login_rate_limiter, RateLimiter

from storage.memory_storage import MemoryStorage

from services.auth_service import AuthService
from services.task_service import TaskService
from services.token_services import TokenService
from services.password_policy_service import PasswordPolicyService
from services.unit_of_work import UnitOfWork

from api.deps.services_dep import (
    get_storage,
    get_auth_service,
    get_task_service,
)

from db.session import engine
from db.base import Base

settings = get_settings()

# ============================================================
# 5️⃣ DATABASE SETUP FOR TESTS
# ============================================================

@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """
    Create database tables before running tests
    and drop them after the session ends.
    """

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


# ============================================================
# 6️⃣ STORAGE LAYER
# ============================================================

@pytest.fixture
def storage():
    """
    In-memory storage used for tests.

    Advantages
    ----------
    - very fast
    - deterministic
    - no external dependency
    """
    return MemoryStorage()


# ============================================================
# 7️⃣ UNIT OF WORK
# ============================================================

@pytest.fixture
def uow():
    """
    Provide UnitOfWork instance for transaction management.
    """
    return UnitOfWork()


# ============================================================
# 8️⃣ SERVICES
# ============================================================

@pytest.fixture
def password_policy():
    """Password validation service"""
    return PasswordPolicyService()


@pytest.fixture
def token_service(storage, uow):
    """Token service using MemoryStorage"""
    return TokenService(storage=storage, uow=uow)


@pytest.fixture
def auth_service(storage, password_policy, uow, token_service):
    """
    AuthService wired exactly like production
    but using in-memory storage.
    """
    return AuthService(
        storage=storage,
        password_policy=password_policy,
        uow=uow,
        token_service=token_service,
    )


@pytest.fixture
def task_service(storage, uow):
    """Task business logic service"""
    return TaskService(storage=storage, uow=uow)


# ============================================================
# 9️⃣ RATE LIMITER RESET
# ============================================================

@pytest.fixture(autouse=True)
def reset_login_rate_limiter():
    """
    Reset login rate limiter before every test.

    Prevents cross-test interference.
    """
    login_rate_limiter.reset_all()


# ============================================================
# 🔟 TEST CLIENT
# ============================================================

@pytest.fixture
def client(storage, auth_service, task_service):
    """
    FastAPI TestClient with dependency overrides.
    """

    app.dependency_overrides[get_storage] = lambda: storage
    app.dependency_overrides[get_auth_service] = lambda: auth_service
    app.dependency_overrides[get_task_service] = lambda: task_service

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ============================================================
# 11️⃣ USERS
# ============================================================

@pytest.fixture
def user(auth_service):
    """Regular user"""
    return auth_service.register(
        email="user@test.com",
        password="StrongPass1!",
    )


@pytest.fixture
def admin(auth_service, uow):
    """Admin user"""

    user = auth_service.register(
        email="admin@test.com",
        password="StrongPass1!",
    )

    user.role = UserRole.ADMIN

    with uow as session:
        auth_service.storage.update_user(session=session, user=user)

    return user


@pytest.fixture
def other_user(auth_service):
    """Second user for ownership tests"""

    return auth_service.register(
        email="other@test.com",
        password="StrongPass1!",
    )


# ============================================================
# 12️⃣ AUTHORIZATION HEADERS
# ============================================================

@pytest.fixture
def user_headers(user):
    """JWT access header for normal user"""

    token = create_access_token(subject=str(user.id))

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(admin):
    """JWT access header for admin"""

    token = create_access_token(subject=str(admin.id))

    return {"Authorization": f"Bearer {token}"}


# ============================================================
# 13️⃣ TOKEN FIXTURES
# ============================================================

@pytest.fixture
def valid_access_headers(user, token_service):

    tokens = token_service.issue_tokens(user.id)

    return {"Authorization": f"Bearer {tokens.access_token}"}


@pytest.fixture
def valid_refresh_headers(user, token_service):

    tokens = token_service.issue_tokens(user.id)

    return {"Authorization": f"Bearer {tokens.refresh_token}"}

@pytest.fixture
def expired_refresh_headers(user, uow, storage):

    raw_refresh_token = generate_refresh_token()

    token_hash = hash_token(raw_refresh_token)

    with uow as session:

        storage.create_refresh_token(
            session=session,
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            family_id="test-family"
        )

    payload = {
        "sub": str(user.id),
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=1),
    }

    jwt_token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return {
        "Authorization": f"Bearer {jwt_token}"
    }

@pytest.fixture
def expired_user_headers(user):
    """Expired JWT token"""

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user.id),
        "type": "access",
        "iat": now - timedelta(minutes=10),
        "exp": now - timedelta(minutes=5),
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return {"Authorization": f"Bearer {token}"}


# ============================================================
# 14️⃣ PASSWORD RESET TOKENS
# ============================================================

@pytest.fixture
def valid_password_reset_token(storage, uow, user):

    raw_token = "valid-reset-token"

    with uow as session:

        storage.create_password_reset_token(
            session=session,
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        )

    return raw_token

@pytest.fixture
def expired_password_reset_token(storage, uow, user):
    """
    Create a password reset token that is already expired.
    """

    raw_token = "expired-reset-token"

    token_hash = hash_token(raw_token)

    with uow as session:

        storage.create_password_reset_token(
            session=session,
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1)
        )

    return raw_token

@pytest.fixture
def used_password_reset_token(storage, uow, user):

    raw_token = "used-reset-token"
    token_hash = hash_token(raw_token)

    with uow as session:

        token_id = storage.create_password_reset_token(
            session=session,
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        )

        storage.mark_password_reset_token_used(
            session=session,
            token_id=token_id
        )

    return raw_token


# ============================================================
# 15️⃣ TASK FIXTURES
# ============================================================

@pytest.fixture
def user_task(task_service, user):
    """Task owned by the main user"""

    return task_service.create_task(
        title="User Task",
        description="Owned by user",
        owner_id=user.id,
    )


@pytest.fixture
def other_user_task(task_service, other_user):
    """Task owned by another user"""

    return task_service.create_task(
        title="Other User Task",
        description="Owned by other user",
        owner_id=other_user.id,
    )


@pytest.fixture
def many_tasks(task_service, user):
    """
    Generate many tasks for pagination tests.
    """

    tasks = []

    for i in range(30):

        task = task_service.create_task(
            title=f"Task {i}",
            description="Pagination test",
            owner_id=user.id,
        )

        tasks.append(task)

    return tasks


# ============================================================
# 16️⃣ LOGIN PAYLOAD
# ============================================================

@pytest.fixture
def valid_login_payload(auth_service):
    """Valid login payload"""

    user = auth_service.register(
        email="user@example.com",
        password="StrongPass1!",
    )

    return {
        "email": user.email,
        "password": "StrongPass1!",
    }