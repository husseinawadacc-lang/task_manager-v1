"""
SQLAlchemy Integration Tests
============================

Goal of these tests
-------------------

Verify that the SQLAlchemy database layer works correctly.

These tests check:

1️⃣ Database connection
2️⃣ Session lifecycle
3️⃣ Transaction commit
4️⃣ Transaction rollback
5️⃣ CRUD operations
6️⃣ Storage compatibility with BaseStorage contract

Important:
----------
These are integration tests (not unit tests).

They interact with the REAL database using SQLAlchemy.
"""

import pytest

from services.unit_of_work import UnitOfWork
from storage.st_factory import get_storage
from models.user import User


# ==========================================================
# Fixture: storage
# ==========================================================

@pytest.fixture
def storage():
    """
    Provide storage implementation.

    In production:
        PostgreSQLStorage

    In tests:
        could still be PostgreSQL but isolated DB.
    """
    return get_storage()


# ==========================================================
# Test 1 — Database connection
# ==========================================================

def test_database_session_creation():
    """
    GIVEN a UnitOfWork instance
    WHEN opening a session
    THEN a valid SQLAlchemy session should be created
    """

    uow = UnitOfWork()

    with uow as session:
        # pseudo:
        # verify that SQLAlchemy session exists
        assert session is not None


# ==========================================================
# Test 2 — Insert user (commit)
# ==========================================================

def test_create_user_commit(storage):
    """
    GIVEN a new user object
    WHEN creating the user in storage
    AND transaction commits
    THEN user should be persisted in database
    """

    uow = UnitOfWork()

    user = User(
        id=None,
        email="sqlalchemy@test.com",
        password_hash="hashed",
        role="user",
        is_active=True,
        is_verified=False,
    )

    # ---- Transaction begin
    with uow as session:

        storage.create_user(
            session=session,
            user=user
        )

    # ---- Transaction committed

    # verify user exists
    with uow as session:

        loaded_user = storage.get_user_by_email(
            session=session,
            email="sqlalchemy@test.com"
        )

        assert loaded_user.email == "sqlalchemy@test.com"


# ==========================================================
# Test 3 — Rollback test
# ==========================================================

def test_transaction_rollback(storage):
    """
    GIVEN a database transaction
    WHEN an error occurs
    THEN transaction should rollback
    AND no data should be persisted
    """

    uow = UnitOfWork()

    user = User(
        id=None,
        email="rollback@test.com",
        password_hash="hashed",
        role="user",
        is_active=True,
        is_verified=False,
    )

    try:

        with uow as session:

            storage.create_user(
                session=session,
                user=user
            )

            # simulate unexpected error
            raise RuntimeError("force rollback")

    except RuntimeError:
        pass

    # verify user NOT saved
    with uow as session:

        with pytest.raises(Exception):

            storage.get_user_by_email(
                session=session,
                email="rollback@test.com"
            )


# ==========================================================
# Test 4 — Update user
# ==========================================================

def test_update_user(storage):
    """
    GIVEN an existing user
    WHEN updating fields
    THEN changes should persist
    """

    uow = UnitOfWork()

    user = User(
        id=None,
        email="update@test.com",
        password_hash="hash",
        role="user",
        is_active=True,
        is_verified=False,
    )

    with uow as session:

        storage.create_user(
            session=session,
            user=user
        )

    # update user
    with uow as session:

        db_user = storage.get_user_by_email(
            session=session,
            email="update@test.com"
        )

        db_user.is_active = False

        storage.update_user(
            session=session,
            user=db_user
        )

    # verify update
    with uow as session:

        updated = storage.get_user_by_email(
            session=session,
            email="update@test.com"
        )

        assert updated.is_active is False


# ==========================================================
# Test 5 — Verify isolation between transactions
# ==========================================================

def test_transaction_isolation(storage):
    """
    GIVEN a transaction that inserts data
    WHEN transaction not committed yet
    THEN other transactions should not see the data
    """

    uow = UnitOfWork()

    user = User(
        id=None,
        email="isolation@test.com",
        password_hash="hash",
        role="user",
        is_active=True,
        is_verified=False,
    )

    # open transaction but do not exit context
    with uow as session:

        storage.create_user(
            session=session,
            user=user
        )

        # open another transaction
        other_uow = UnitOfWork()

        with other_uow as other_session:

            with pytest.raises(Exception):

                storage.get_user_by_email(
                    session=other_session,
                    email="isolation@test.com"
                )


# ==========================================================
# Test 6 — Verify session closing
# ==========================================================

def test_session_closed_after_uow():
    """
    GIVEN a UnitOfWork block
    WHEN exiting the context
    THEN session must be closed
    """

    uow = UnitOfWork()

    with uow as session:
        pass

    # pseudo:
    # after  exit
    # SQLAlchemy session should have no activa trandaction

    assert not session.in_transaction() 