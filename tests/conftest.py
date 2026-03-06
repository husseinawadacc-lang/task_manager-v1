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
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:password@localhost:5432/testdb"
)
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
from services.unit_of_work import UnitOfWork
from services.token_services import TokenService
from api.deps.services import (
    get_storage,
    get_auth_service,
    get_task_service,)
from utils.security import hash_reset_token,hash_password
from utils.token import  generate_refresh_token,hash_refresh_token
from services.password_policy_s import PasswordPolicyService
from utils.jwt_utils import create_access_token
from core.enums.user_role import UserRole
from utils.rate_limiter import login_rate_limiter
from utils.rate_limiter import RateLimiter
from services.unit_of_work import UnitOfWork
from db.session import SessionLocal

# =================================================
# for test window_seconds, we use a short duration to speed up tests
# =================================================
test_login_rate_limiter = RateLimiter(max_attempts=5, window_seconds=1)  # 1 second window for testing
settings = get_settings()
# =================================================
# 1️⃣ Environment variables (same as production)
# =================================================


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
from db.session import engine
from db.base import Base


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """
    Create all tables before running integration tests.
    """

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)



@pytest.fixture
def storage():
    """
    Single MemoryStorage instance for the test session.

    Why?
    - Matches real storage interface
    - Fast
    - Deterministic
    """
    return MemoryStorage()

@pytest.fixture
def uow():
   """
   provide a unitofwork instance for tests
   transaction mangement is handeled internally
   """
   return UnitOfWork()
    
# =================================================
# 4️⃣ Services layer (REAL services)
# =================================================
@pytest.fixture
def auth_service(storage,password_policy,uow,token_service):
    """
    AuthService wired exactly like production,
    but using MemoryStorage.
    """
    return AuthService(
        storage=storage,
        password_policy=password_policy,
        uow=uow,
        token_service=token_service,
            )

@pytest.fixture
def task_service(storage,uow):
    """
    TaskService with same storage as auth.
    """
    return TaskService(storage=storage,
                       uow =uow
                       )

@pytest.fixture
def token_service(storage,uow):
    """
    token service for tests
    """
    return TokenService(
        storage=storage,
        uow=uow,
    )

# =================================================
# rate limiter (shared instance to track attempts)
# =================================================
@pytest.fixture(autouse=True)
def reset_login_rate_limiter():
    """ensure the rate limiter is reset before each test 
    to avoid cross-test interference."""
    login_rate_limiter.reset_all()



# =================================================
# 6️⃣ Test client
# =================================================
@pytest.fixture()
def client(storage, auth_service, task_service):
    app.dependency_overrides[get_storage] = lambda: storage
    app.dependency_overrides[get_auth_service] = lambda: auth_service
    app.dependency_overrides[get_task_service] = lambda: task_service

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

# =================================================
# 7️⃣ Users (REAL domain users)
# =================================================

@pytest.fixture()
def user(auth_service):
    """
    Normal user with valid password rules.
    """
    return auth_service.register(
        email="user@test.com",
        password="StrongPass1!",
            )
   

@pytest.fixture()
def admin(auth_service,uow):
    """
    Admin user.
    """
    user=auth_service.register(
        email="admin@test.com",
        password="StrongPass1!",
            )
    user.role = UserRole.ADMIN
    with uow as session:
      auth_service.storage.update_user(user=user,session=session)        
    return user


@pytest.fixture()
def other_user(auth_service):
    """
    Another normal user (ownership testing).
    """
    return auth_service.register(
        email="other@test.com",
        password="StrongPass1!",
        
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
    token = create_access_token(subject= str(admin.id))
    return {"Authorization": f"Bearer {token}"}


# =================================================
# 9️⃣ Expired token (ATTACK / FAILURE CASE)
# =================================================
@pytest.fixture
def valid_password_reset_token(storage,uow, user):
    raw_token = "valid-reset-token-123"
    token_hash = hash_reset_token(raw_token)

    with uow as session:

        storage.create_password_reset_token(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            session=session
        )

    return raw_token

@pytest.fixture
def expired_password_reset_token(storage,uow, user):
    raw_token = "expired-reset-token"
    token_hash = hash_reset_token(raw_token)

    with uow as session:

        storage.create_password_reset_token(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            session=session
        )
    return raw_token

@pytest.fixture
def used_password_reset_token(storage, uow, user):

    raw_token = "used-reset-token"
    token_hash = hash_reset_token(raw_token)

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

@pytest.fixture()
def expired_user_headers(user):
    """
    Authorization header with EXPIRED access token
    for an existing user.
    """

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user.id),
        "type": "access",
        "iat": now - timedelta(minutes=10),
        "exp": now - timedelta(minutes=5),  # ⛔ expired
    }

    expired_token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return {
        "Authorization": f"Bearer {expired_token}"
    }


@pytest.fixture
def valid_refresh_headers(user,uow, storage):
    # 1️⃣ أنشئ JWT refresh token
    payload = {
        "sub": str(user.id),
        "type": "refresh",
        "exp": datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }

    jwt_token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    # 2️⃣ hash الـ JWT نفسه (مش raw string)
    token_hash = hash_refresh_token(jwt_token)

    # 3️⃣ خزّنه في storage
    with uow as session:
        storage.create_refresh_token(
        session=session,    
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    # 4️⃣ رجّعه في الهيدر
    return {
        "Authorization": f"Bearer {jwt_token}"
    }

@pytest.fixture
def expired_refresh_headers(user,uow, storage):
    raw_refresh_token = generate_refresh_token()
    token_hash = hash_refresh_token(raw_refresh_token)
    
    with uow as session :
        storage.create_refresh_token(
        session= session,    
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
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



@pytest.fixture
def many_tasks(task_service, user):
    """
    Create multiple tasks for a single user.
    Used for pagination & performance tests.
    """
    tasks = []

    for i in range(30):
        task = task_service.create_task(
            title=f"Task {i}",
            description="Pagination test task",
            owner_id=user.id,
        )
        tasks.append(task)

    return tasks
#=================================
#=== password policy
#=================================
@pytest.fixture
def password_policy():
    return PasswordPolicyService()


@pytest.fixture
def valid_login_payload(auth_service):
    """
    Valid login payload for an existing user.
    """
    user = auth_service.register(
        email="user@example.com",
        password="StrongPass1!",
    )

    return {
        "email": user.email,
        "password": "StrongPass1!",
    }