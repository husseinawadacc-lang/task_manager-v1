import pytest
from datetime import datetime, timedelta, timezone

from storage.memory_storage import MemoryStorage
from services.token_services import TokenService
from services.unit_of_work import UnitOfWork
from core.auth.token import hash_token


@pytest.fixture
def storage():
    return MemoryStorage()


@pytest.fixture
def uow():
    return UnitOfWork()


@pytest.fixture
def token_service(storage, uow):
    return TokenService(storage, uow)


@pytest.fixture
def refresh_token_record(storage):

    token_hash = hash_token("test-refresh-token")

    expires = datetime.now(timezone.utc) + timedelta(days=7)

    token_id = storage.create_refresh_token(
        session=None,
        user_id=1,
        token_hash=token_hash,
        expires_at=expires,
        family_id="family-1"
    )

    return {
        "raw": "test-refresh-token",
        "hash": token_hash,
        "id": token_id,
        "family_id": "family-1",
        "user_id": 1
    }

def test_revoke_refresh_token(token_service, storage, refresh_token_record):

    token_service.revoke_refresh_token(refresh_token_record["raw"])

    record = storage.get_refresh_token(
        session=None,
        token_hash=refresh_token_record["hash"]
    )

    assert record.revoked is True


def test_revoke_token_family(token_service, storage):

    expires = datetime.now(timezone.utc) + timedelta(days=7)

    storage.create_refresh_token(
        session=None,
        user_id=1,
        token_hash="hash1",
        expires_at=expires,
        family_id="family-A"
    )

    storage.create_refresh_token(
        session=None,
        user_id=1,
        token_hash="hash2",
        expires_at=expires,
        family_id="family-A"
    )

    token_service.revoke_token_family("family-A")

    token1 = storage.get_refresh_token(session=None, token_hash="hash1")
    token2 = storage.get_refresh_token(session=None, token_hash="hash2")

    assert token1.revoked is True
    assert token2.revoked is True


def test_logout_revokes_family(token_service, storage, refresh_token_record):

    token_service.logout(refresh_token_record["raw"])

    record = storage.get_refresh_token(
        session=None,
        token_hash=refresh_token_record["hash"]
    )

    assert record.revoked is True


def test_logout_all_revokes_all_user_tokens(token_service, storage):

    expires = datetime.now(timezone.utc) + timedelta(days=7)

    storage.create_refresh_token(
        session=None,
        user_id=1,
        token_hash="hashA",
        expires_at=expires,
        family_id="family1"
    )

    storage.create_refresh_token(
        session=None,
        user_id=1,
        token_hash="hashB",
        expires_at=expires,
        family_id="family2"
    )

    token_service.logout_all(user_id=1)

    tokenA = storage.get_refresh_token(session=None, token_hash="hashA")
    tokenB = storage.get_refresh_token(session=None, token_hash="hashB")

    assert tokenA.revoked is True
    assert tokenB.revoked is True    




def test_refresh_after_logout_fails(client, valid_refresh_headers):

    client.post("/api/v1/auth/logout", headers=valid_refresh_headers)

    response = client.post(
        "/api/v1/auth/refresh",
        headers=valid_refresh_headers
    )
    print("HEADERS:", valid_refresh_headers)

    assert response.status_code == 401


from core.cache.token_blacklist import blacklist_token, is_token_blacklisted


def test_token_blacklist():

    jti = "test-jti"

    blacklist_token(jti, ttl=60)

    assert is_token_blacklisted(jti) is True

def test_blacklist_fail_safe(client, user_headers):

    response = client.get(
        "/api/v1/auth/me",
        headers=user_headers
    )

    assert response.status_code == 200

def test_login_logging(client, valid_login_payload):

    response = client.post(
        "/api/v1/auth/login",
        json=valid_login_payload
    )

    assert response.status_code == 200            