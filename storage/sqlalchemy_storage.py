"""
SQLAlchemyStorage
=================

This storage implementation uses SQLAlchemy ORM.

Important architectural rules:

1) Storage NEVER controls transactions
   - No commit
   - No rollback

2) Transaction lifecycle is handled by UnitOfWork.

3) Storage only performs:
   - queries
   - inserts
   - updates
   - deletes

4) flush() is used instead of commit() to obtain generated IDs.
"""

from datetime import datetime
from typing import List

from sqlalchemy import select, func

from storage.base_st import (
    BaseStorage,
    PasswordResetTokenRecord,
    RefreshTokenRecord
)

from models.user import User
from models.task import Task

from db.models.user import UserORM
from db.models.task import TaskORM
from db.models.password_reset import PasswordResetTokenORM
from db.models.refresh_token import RefreshTokenORM

from utils.exceptions import NotFoundError


class SQLAlchemyStorage(BaseStorage):

    # ==========================================================
    # USER OPERATIONS
    # ==========================================================

    def create_user(self, *, session, user: User) -> User:
        """
        Persist new user.
        """

        orm_user = UserORM(
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
        )

        session.add(orm_user)

        # flush sends SQL but does NOT commit
        session.flush()

        # copy generated id back to domain model
        user.id = orm_user.id

        return user

    # ----------------------------------------------------------

    def update_user(self, *, session, user: User) -> User:
        """
        Update existing user.
        """

        stmt = select(UserORM).where(UserORM.id == user.id)

        orm_user = session.execute(stmt).scalar_one_or_none()

        if not orm_user:
            raise NotFoundError("User not found")

        orm_user.email = user.email
        orm_user.role = user.role
        orm_user.is_active = user.is_active

        session.flush()

        return user

    # ----------------------------------------------------------

    def get_user_by_id(self, *, session, user_id: int) -> User:

        stmt = select(UserORM).where(UserORM.id == user_id)

        orm_user = session.execute(stmt).scalar_one_or_none()

        if not orm_user:
            raise NotFoundError("User not found")

        return User(
            id=orm_user.id,
            email=orm_user.email,
            password_hash=orm_user.password_hash,
            role=orm_user.role,
            is_active=orm_user.is_active,
            created_at=orm_user.created_at,
        )

    # ----------------------------------------------------------

    def get_user_by_email(self, *, session, email: str) -> User:

        stmt = select(UserORM).where(UserORM.email == email)

        orm_user = session.execute(stmt).scalar_one_or_none()

        if not orm_user:
            raise NotFoundError("User not found")

        return User(
            id=orm_user.id,
            email=orm_user.email,
            password_hash=orm_user.password_hash,
            role=orm_user.role,
            is_active=orm_user.is_active,
            created_at=orm_user.created_at,
        )

    # ----------------------------------------------------------

    def update_user_password(
        self,
        *,
        session,
        user_id: int,
        password_hash: str
    ) -> None:

        stmt = select(UserORM).where(UserORM.id == user_id)

        orm_user = session.execute(stmt).scalar_one_or_none()

        if not orm_user:
            raise NotFoundError("User not found")

        orm_user.password_hash = password_hash

        session.flush()

    # ==========================================================
    # TASK OPERATIONS
    # ==========================================================

    def create_task(
        self,
        *,
        session,
        title: str,
        description: str,
        owner_id: int
    ) -> Task:

        orm_task = TaskORM(
            title=title,
            description=description,
            owner_id=owner_id,
            completed=False,
            created_at=datetime.utcnow(),
        )

        session.add(orm_task)

        session.flush()

        return Task(
            id=orm_task.id,
            title=orm_task.title,
            description=orm_task.description,
            owner_id=orm_task.owner_id,
            completed=orm_task.completed,
            created_at=orm_task.created_at,
        )

    # ----------------------------------------------------------

    def get_task(self, *, session, task_id: int) -> Task:

        stmt = select(TaskORM).where(TaskORM.id == task_id)

        orm_task = session.execute(stmt).scalar_one_or_none()

        if not orm_task:
            raise NotFoundError("Task not found")

        return Task(
            id=orm_task.id,
            title=orm_task.title,
            description=orm_task.description,
            owner_id=orm_task.owner_id,
            completed=orm_task.completed,
            created_at=orm_task.created_at,
        )

    # ----------------------------------------------------------

    def update_task(
        self,
        *,
        session,
        task_id: int,
        title: str | None,
        description: str | None,
        completed: bool | None
    ) -> Task:

        stmt = select(TaskORM).where(TaskORM.id == task_id)

        orm_task = session.execute(stmt).scalar_one_or_none()

        if not orm_task:
            raise NotFoundError("Task not found")

        if title is not None:
            orm_task.title = title

        if description is not None:
            orm_task.description = description

        if completed is not None:
            orm_task.completed = completed

        session.flush()

        return Task(
            id=orm_task.id,
            title=orm_task.title,
            description=orm_task.description,
            owner_id=orm_task.owner_id,
            completed=orm_task.completed,
            created_at=orm_task.created_at,
        )

    # ----------------------------------------------------------

    def delete_task(self, *, session, task_id: int) -> None:

        stmt = select(TaskORM).where(TaskORM.id == task_id)

        orm_task = session.execute(stmt).scalar_one_or_none()

        if not orm_task:
            raise NotFoundError("Task not found")

        session.delete(orm_task)

    # ==========================================================
    # PAGINATION
    # ==========================================================

    def list_tasks(
        self,
        *,
        session,
        owner_id: int,
        limit: int,
        offset: int
    ) -> List[Task]:

        stmt = (
            select(TaskORM)
            .where(TaskORM.owner_id == owner_id)
            .limit(limit)
            .offset(offset)
        )

        tasks = session.execute(stmt).scalars().all()

        return [
            Task(
                id=t.id,
                title=t.title,
                description=t.description,
                owner_id=t.owner_id,
                completed=t.completed,
                created_at=t.created_at,
            )
            for t in tasks
        ]

    # ----------------------------------------------------------

    def count_tasks(self, *, session, owner_id: int) -> int:

        stmt = select(func.count()).where(TaskORM.owner_id == owner_id)

        return session.execute(stmt).scalar_one()

    # ==========================================================
    # PASSWORD RESET TOKENS
    # ==========================================================

    def create_password_reset_token(
        self,
        *,
        session,
        user_id: int,
        token_hash: str,
        expires_at: datetime
    ) -> int:

        orm_token = PasswordResetTokenORM(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False,
        )

        session.add(orm_token)

        session.flush()

        return orm_token.id

    # ----------------------------------------------------------

    def get_password_reset_token(
        self,
        *,
        session,
        token_hash: str
    ) -> PasswordResetTokenRecord:

        stmt = select(PasswordResetTokenORM).where(
            PasswordResetTokenORM.token_hash == token_hash
        )

        orm_token = session.execute(stmt).scalar_one_or_none()

        if not orm_token:
            raise NotFoundError("Reset token not found")

        return PasswordResetTokenRecord(
            id=orm_token.id,
            user_id=orm_token.user_id,
            token_hash=orm_token.token_hash,
            expires_at=orm_token.expires_at,
            used=orm_token.used,
        )

    # ----------------------------------------------------------

    def mark_password_reset_token_used(
        self,
        *,
        session,
        token_id: int
    ) -> None:

        stmt = select(PasswordResetTokenORM).where(
            PasswordResetTokenORM.id == token_id
        )

        orm_token = session.execute(stmt).scalar_one_or_none()

        if not orm_token:
            raise NotFoundError("Reset token not found")

        orm_token.used = True

        session.flush()

    # ==========================================================
    # REFRESH TOKENS
    # ==========================================================

    def create_refresh_token(
        self,
        *,
        session,
        user_id: int,
        token_hash: str,
        expires_at: datetime | None
    ) -> int:

        orm_token = RefreshTokenORM(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False,
        )

        session.add(orm_token)

        session.flush()

        return orm_token.id

    # ----------------------------------------------------------

    def get_refresh_token(
        self,
        *,
        session,
        token_hash: str
    ) -> RefreshTokenRecord:

        stmt = select(RefreshTokenORM).where(
            RefreshTokenORM.token_hash == token_hash
        )

        orm_token = session.execute(stmt).scalar_one_or_none()

        if not orm_token:
            raise NotFoundError("Refresh token not found")

        return RefreshTokenRecord(
            id=orm_token.id,
            user_id=orm_token.user_id,
            token_hash=orm_token.token_hash,
            expires_at=orm_token.expires_at,
            used=orm_token.used,
        )

    # ----------------------------------------------------------

    def mark_refresh_token_used(
        self,
        *,
        session,
        token_id: int
    ) -> None:

        stmt = select(RefreshTokenORM).where(
            RefreshTokenORM.id == token_id
        )

        orm_token = session.execute(stmt).scalar_one_or_none()

        if not orm_token:
            raise NotFoundError("Refresh token not found")

        orm_token.used = True

        session.flush()