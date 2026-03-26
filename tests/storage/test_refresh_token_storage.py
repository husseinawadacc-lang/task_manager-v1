
#test work
#create_refresh_token
#get_refresh_token

import pytest
from datetime import datetime, timedelta, timezone

from storage.memory_storage import MemoryStorage
from utils.exceptions import NotFoundError


def test_create_and_get_refresh_token():

    storage = MemoryStorage()

    token_hash = "hash123"
    expires = datetime.now(timezone.utc) + timedelta(days=7)

    token_id = storage.create_refresh_token(
        session=None,
        user_id=1,
        token_hash=token_hash,
        expires_at=expires,
        family_id="family-1",
    )

    record = storage.get_refresh_token(
        session=None,
        token_hash=token_hash
    )

    assert record.id == token_id
    assert record.user_id == 1
    assert record.revoked is False
    assert record.used is False

# test revoke refresh token work

def test_revoke_single_refresh_token():

    storage = MemoryStorage()

    token_hash = "hash123"
    expires = datetime.now(timezone.utc) + timedelta(days=7)

    token_id = storage.create_refresh_token(
        session=None,
        user_id=1,
        token_hash=token_hash,
        expires_at=expires,
        family_id="family-1",
    )

    storage.revoke_refresh_token(
        session=None,
        token_id=token_id
    )

    record = storage.get_refresh_token(
        session=None,
        token_hash=token_hash
    )

    assert record.revoked is True

    # test revoke token family


def test_revoke_token_family():

    storage = MemoryStorage()

    expires = datetime.now(timezone.utc) + timedelta(days=7)

    storage.create_refresh_token(
        session=None,
        user_id=1,
        token_hash="hash1",
        expires_at=expires,
        family_id="family-1",
    )

    storage.create_refresh_token(
        session=None,
        user_id=1,
        token_hash="hash2",
        expires_at=expires,
        family_id="family-1",
    )

    storage.revoke_token_family(
        session=None,
        family_id="family-1"
    )

    token1 = storage.get_refresh_token(session=None, token_hash="hash1")
    token2 = storage.get_refresh_token(session=None, token_hash="hash2")

    assert token1.revoked is True
    assert token2.revoked is True

#test revoke token by user

def test_revoke_tokens_by_user():

    storage = MemoryStorage()

    expires = datetime.now(timezone.utc) + timedelta(days=7)

    storage.create_refresh_token(
        session=None,
        user_id=1,
        token_hash="hash1",
        expires_at=expires,
        family_id="family-1",
    )

    storage.create_refresh_token(
        session=None,
        user_id=1,
        token_hash="hash2",
        expires_at=expires,
        family_id="family-2",
    )

    storage.revoke_tokens_by_user(
        session=None,
        user_id=1
    )

    token1 = storage.get_refresh_token(session=None, token_hash="hash1")
    token2 = storage.get_refresh_token(session=None, token_hash="hash2")

    assert token1.revoked is True
    assert token2.revoked is True        

