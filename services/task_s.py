from typing import Tuple, List

from models.task import Task
from storage.base_st import BaseStorage
from services.unit_of_work import UnitOfWork

from utils.exceptions import (
    TaskNotFoundError,
    ForbiddenTaskAccessError,
    InvalidPaginationError,
    NotFoundError,
)


class TaskService:
    """
    TaskService

    Responsibilities
    ----------------
    - Enforce business rules
    - Enforce user isolation
    - Validate pagination
    - Coordinate storage operations
    - Manage transaction via UnitOfWork
    """

    DEFAULT_LIMIT = 20
    MAX_LIMIT = 100

    def __init__(self, storage: BaseStorage, uow: UnitOfWork):
        self.storage = storage
        self.uow = uow

    # =====================================================
    # CREATE TASK
    # =====================================================

    def create_task(
        self,
        *,
        title: str,
        description: str,
        owner_id: int,
    ) -> Task:
        """
        Create a new task.

        Steps:
        1. Start transaction
        2. Call storage to persist task
        3. UnitOfWork handles commit automatically
        """

        with self.uow as session:

            task = self.storage.create_task(
                session=session,
                title=title,
                description=description,
                owner_id=owner_id,
            )

            return task

    # =====================================================
    # GET TASK
    # =====================================================

    def get_task(
        self,
        *,
        task_id: int,
        requester_id: int,
    ) -> Task:
        """
        Retrieve a task and enforce ownership.

        Security rule:
        If user is not owner → return NOT FOUND
        to prevent resource enumeration (IDOR).
        """

        with self.uow as session:

            try:
                task = self.storage.get_task(
                    session=session,
                    task_id=task_id,
                )

            except NotFoundError:
                raise TaskNotFoundError()

            # Ownership enforcement
            if task.owner_id != requester_id:
                raise TaskNotFoundError()

            return task

    # =====================================================
    # UPDATE TASK
    # =====================================================

    def update_task(
        self,
        *,
        task_id: int,
        requester_id: int,
        title: str | None = None,
        description: str | None = None,
        completed: bool | None = None,
    ) -> Task:
        """
        Update task fields.

        Rules:
        - Task must exist
        - Requester must be owner
        """

        with self.uow as session:

            try:
                task = self.storage.get_task(
                    session=session,
                    task_id=task_id,
                )

            except NotFoundError:
                raise TaskNotFoundError()

            if task.owner_id != requester_id:
                raise TaskNotFoundError()

            updated = self.storage.update_task(
                session=session,
                task_id=task_id,
                title=title,
                description=description,
                completed=completed,
            )

            return updated

    # =====================================================
    # DELETE TASK
    # =====================================================

    def delete_task(
        self,
        *,
        task_id: int,
        requester_id: int,
    ) -> None:
        """
        Delete a task.

        Only the owner may delete it.
        """

        with self.uow as session:

            try:
                task = self.storage.get_task(
                    session=session,
                    task_id=task_id,
                )

            except NotFoundError:
                raise TaskNotFoundError()

            if task.owner_id != requester_id:
                raise TaskNotFoundError()

            self.storage.delete_task(
                session=session,
                task_id=task_id,
            )

    # =====================================================
    # LIST TASKS (PAGINATION)
    # =====================================================

    def list_tasks(
        self,
        *,
        owner_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Tuple[List[Task], int]:
        """
        Return paginated tasks.

        Returns:
        (items, total_count)
        """

        limit = limit if limit is not None else self.DEFAULT_LIMIT
        offset = offset if offset is not None else 0

        # Pagination validation
        if limit < 1:
            raise InvalidPaginationError("limit must be >= 1")

        if limit > self.MAX_LIMIT:
            raise InvalidPaginationError("limit exceeds maximum")

        if offset < 0:
            raise InvalidPaginationError("offset must be >= 0")

        with self.uow as session:

            items = self.storage.list_tasks(
                session=session,
                owner_id=owner_id,
                limit=limit,
                offset=offset,
            )

            total = self.storage.count_tasks(
                session=session,
                owner_id=owner_id,
            )

            return items, total