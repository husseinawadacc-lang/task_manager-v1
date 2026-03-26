# ==========================================
# TaskService (FINAL RBAC VERSION)
# ==========================================

from typing import Tuple, List
from domain.task import Task
from storage.base_st import BaseStorage
from services.unit_of_work import UnitOfWork
from services.ai_service import AIService
from services.project_service import ProjectService
from services.audit_service import AuditService
from utils.logger import get_logger
from utils.exceptions import (
    TaskNotFoundError,
    InvalidPaginationError,
    NotFoundError,)


logger = get_logger(__name__)


class TaskService:
    """
    TaskService (RBAC Final)

    Responsibilities:
    - Manage task lifecycle
    - Enforce RBAC via ProjectService
    - Prevent IDOR
    - Handle pagination
    - Integrate AI (priority)
    """

    DEFAULT_LIMIT = 20
    MAX_LIMIT = 100

    def __init__(
        self,
        storage: BaseStorage,
        uow: UnitOfWork,
        project_service: ProjectService,
        audit_service:AuditService
    ):
        self.storage = storage
        self.uow = uow
        self.project_service = project_service
        self.ai = AIService()
        self.audit =audit_service
    # =====================================================
    # CREATE TASK
    # =====================================================
    def create_task(
        self,
        *,
        title: str,
        description: str,
        owner_id: int,
        project_id: int,
    ) -> Task:

        with self.uow as session:

            # 🔥 RBAC: only admin / member
            project= self.project_service.storage.get_project(
                session=session,
                project_id=project_id,
                            )
            self.project_service.require_role(
                session=session,
                project=project,
                user_id=owner_id,
                allowed_roles=["admin","member"]
            )

            priority = self.ai.suggest_priority(title)

            task = Task(
                id=None,
                title=title,
                description=description,
                owner_id=owner_id,
                project_id=project_id,
                completed=False,
                priority=priority,
            )
            created = self.storage.create_task(
                session=session,
                task=task,
            )

            # 🔥 AUDIT
            self.audit.log(
                session=session,
                user_id=owner_id,
                action="task_created",
                resource_type="task",
                resource_id=created.id,
                details={
                    "title": created.title,
                    "project_id": project_id,
                },
            )

            return created

    # =====================================================
    # GET TASK
    # =====================================================
    def get_task(
        self,
        *,
        task_id: int,
        requester_id: int,
    ) -> Task:

        with self.uow as session:

            try:
                task = self.storage.get_task(
                    session=session,
                    task_id=task_id,
                )
            except NotFoundError:
                raise TaskNotFoundError()

            # 🔥 RBAC: viewer+
            project= self.project_service.storage.get_project(
                session=session,
                project_id=task.project_id,
                            )
          
            self.project_service.require_role(
                session=session,
                project=project,
                user_id=requester_id,
                allowed_roles=["admin", "member", "viewer"],
            )

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
        priority: str | None = None,
    ) -> Task:

        with self.uow as session:

            try:
                existing = self.storage.get_task(
                    session=session,
                    task_id=task_id,
                )
            except NotFoundError:
                raise TaskNotFoundError()

            # 🔥 RBAC: only admin / member
            project= self.project_service.storage.get_project(
                session=session,
                project_id=existing.project_id,
                            )
          
            self.project_service.require_role(
                session=session,
                project=project,
                user_id=requester_id,
                allowed_roles=["admin", "member"],
            )

            task = Task(
                id=task_id,
                title=title,
                description=description,
                completed=completed,
                priority=priority,
                owner_id=existing.owner_id,
                project_id=existing.project_id,
            )

            updated = self.storage.update_task(
                session=session,
                task=task,
            )

            # 🔥 AUDIT
            self.audit.log(
                session=session,
                user_id=requester_id,
                action="task_updated",
                resource_type="task",
                resource_id=task_id,
                details={
                    "title": title,
                    "completed": completed,
                    "priority": priority,
                },
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

        with self.uow as session:

            try:
                task = self.storage.get_task(
                    session=session,
                    task_id=task_id,
                )
            except NotFoundError:
                raise TaskNotFoundError()

            # 🔥 RBAC: only admin
            project= self.project_service.storage.get_project(
                session=session,
                project_id=task.project_id,
                            )
          
            self.project_service.require_role(
                session=session,
                project=project,
                user_id=requester_id,
                allowed_roles=["admin"],
            )
            self.storage.delete_task(
                session=session,
                task_id=task_id,
            )

            # 🔥 AUDIT
            self.audit.log(
                session=session,
                user_id=requester_id,
                action="task_deleted",
                resource_type="task",
                resource_id=task_id,
            )

    # =====================================================
    # LIST TASKS
    # =====================================================
    def list_tasks(
        self,
        *,
        owner_id: int,
        project_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Tuple[List[Task], int]:

        limit = limit or self.DEFAULT_LIMIT
        offset = offset or 0

        if limit < 1:
            raise InvalidPaginationError("limit must be >= 1")

        if limit > self.MAX_LIMIT:
            raise InvalidPaginationError("limit too large")

        if offset < 0:
            raise InvalidPaginationError("offset must be >= 0")

        with self.uow as session:

            # 🔥 RBAC: viewer+
            project= self.project_service.storage.get_project(
                session=session,
                project_id=project_id,
                            )
          

            self.project_service.require_role(
                session=session,
                project=project,
                user_id=owner_id,
                allowed_roles=["admin", "member", "viewer"],
            )

            items = self.storage.list_tasks(
                session=session,
                owner_id=owner_id,
                project_id=project_id,
                limit=limit,
                offset=offset,
            )

            total = self.storage.count_tasks(
                session=session,
                owner_id=owner_id,
                project_id=project_id,
            )

            return items, total