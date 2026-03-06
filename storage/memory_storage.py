from datetime import datetime
from typing import Dict, List

from storage.base_st import (
    BaseStorage,
    PasswordResetTokenRecord,
    RefreshTokenRecord,
)

from models.user import User
from models.task import Task
from utils.exceptions import NotFoundError


class MemoryStorage(BaseStorage):
    """
    In-memory storage implementation.

    This storage simulates database behavior using Python dictionaries.

    Important notes:
    - Used mainly for testing
    - Session argument is ignored (for contract compatibility)
    - IDs are generated using internal counters
    """

    # ======================================================
    # Constructor
    # ======================================================

    def __init__(self):

        # storage containers
        self._users: Dict[int, User] = {}
        self._tasks: Dict[int, Task] = {}

        self._password_reset_tokens: Dict[int, PasswordResetTokenRecord] = {}
        self._refresh_tokens: Dict[int, RefreshTokenRecord] = {}

        # auto increment counters (simulate database sequences)
        self._user_id_seq = 1
        self._task_id_seq = 1
        self._password_token_id_seq = 1
        self._refresh_token_id_seq = 1

    # ======================================================
    # User operations
    # ======================================================

    def create_user(self, *, session, user: User) -> User:
        """
        Create a new user.

        session parameter is ignored in MemoryStorage.
        """

        user.id = self._user_id_seq
        self._user_id_seq += 1

        self._users[user.id] = user

        return user

    def update_user(self, *, session, user: User) -> User:
        """
        Update existing user.
        """

        if user.id not in self._users:
            raise NotFoundError("User not found")

        self._users[user.id] = user

        return user

    def get_user_by_id(self, *, session, user_id: int) -> User:
        """
        Retrieve user by id.
        """

        user = self._users.get(user_id)

        if not user:
            raise NotFoundError("User not found")

        return user

    def get_user_by_email(self, *, session, email: str) -> User:
        """
        Retrieve user by email.
        """

        for user in self._users.values():
            if user.email == email:
                return user

        raise NotFoundError("User not found")

    def update_user_password(self, *, session, user_id: int, password_hash: str) -> None:
        """
        Update password hash.
        """

        user = self._users.get(user_id)

        if not user:
            raise NotFoundError("User not found")

        user.password_hash = password_hash

    # ======================================================
    # Task operations
    # ======================================================

    def create_task(self, *, session, title: str, description: str, owner_id: int) -> Task:
        """
        Create new task.
        """

        task = Task(
            id=self._task_id_seq,
            title=title,
            description=description,
            owner_id=owner_id,
            completed=False,
            created_at=datetime.utcnow(),
        )

        self._task_id_seq += 1

        self._tasks[task.id] = task

        return task

    def get_task(self, *, session, task_id: int) -> Task:
        """
        Retrieve task by id.
        """

        task = self._tasks.get(task_id)

        if not task:
            raise NotFoundError("Task not found")

        return task

    def update_task(
        self,
        *,
        session,
        task_id: int,
        title: str | None,
        description: str | None,
        completed: bool | None,
    ) -> Task:
        """
        Update task fields.
        """

        task = self._tasks.get(task_id)

        if not task:
            raise NotFoundError("Task not found")

        if title is not None:
            task.title = title

        if description is not None:
            task.description = description

        if completed is not None:
            task.completed = completed

        return task

    def delete_task(self, *, session, task_id: int) -> None:
        """
        Delete task.
        """

        if task_id not in self._tasks:
            raise NotFoundError("Task not found")

        del self._tasks[task_id]

    # ======================================================
    # Pagination
    # ======================================================

    def list_tasks(
        self,
        *,
        session,
        owner_id: int,
        limit: int,
        offset: int,
    ) -> List[Task]:
        """
        Return paginated tasks for a user.
        """

        tasks = [t for t in self._tasks.values() if t.owner_id == owner_id]

        tasks.sort(key=lambda t: t.id)

        return tasks[offset : offset + limit]

    def count_tasks(self, *, session, owner_id: int) -> int:
        """
        Count tasks for pagination.
        """

        return sum(1 for t in self._tasks.values() if t.owner_id == owner_id)

    # ======================================================
    # Password reset tokens
    # ======================================================

    def create_password_reset_token(
        self,
        *,
        session,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
    ) -> int:
        """
        Create password reset token.
        """
        token_id = self._password_token_id_seq
        self._password_token_id_seq += 1

        record = PasswordResetTokenRecord(
            id=token_id,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False,
        )

        self._password_reset_tokens[token_id] = record

        return token_id

    def get_password_reset_token(
        self,
        *,
        session,
        token_hash: str,
    ) -> PasswordResetTokenRecord:
        """
        Retrieve reset token by hash.
        """

        for token in self._password_reset_tokens.values():
            if token.token_hash == token_hash:
                return token

        raise NotFoundError("Reset token not found")

    def mark_password_reset_token_used(
        self,
        *,
        session,
        token_id: int,
    ) -> None:
        """
        Mark reset token as used.
        """

        token = self._password_reset_tokens.get(token_id)

        if not token:
            raise NotFoundError("Reset token not found")

        token.used = True

    # ======================================================
    # Refresh tokens
    # ======================================================

    def create_refresh_token(
        self,
        *,
        session,
        user_id: int,
        token_hash: str,
        expires_at: datetime | None,
    ) -> int:
        """
        Create refresh token.
        """

        token_id = self._refresh_token_id_seq
        self._refresh_token_id_seq += 1

        record = RefreshTokenRecord(
            id=token_id,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False,
        )

        self._refresh_tokens[token_id] = record

        return token_id

    def get_refresh_token(
        self,
        *,
        session,
        token_hash: str,
    ) -> RefreshTokenRecord:
        """
        Retrieve refresh token.
        """

        for token in self._refresh_tokens.values():
            if token.token_hash == token_hash:
                return token

        raise NotFoundError("Refresh token not found")

    def mark_refresh_token_used(
        self,
        *,
        session,
        token_id: int,
    ) -> None:
        """
        Mark refresh token as used.
        """

        token = self._refresh_tokens.get(token_id)

        if not token:
            raise NotFoundError("Refresh token not found")

        token.used = True