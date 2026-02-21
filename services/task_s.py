from typing import List
from models.task import Task
from models.user import User
from core.enums.user_role import UserRole
from storage.base_st import BaseStorage
from utils.exceptions import (
    PermissionDeniedError,
    NotFoundError,
    ValidationError,
)


class TaskService:
    """
    Business logic layer for Tasks.

    Responsibilities:
    - Enforce permissions
    - Validate ownership
    - Decide which storage method to call
    - NEVER expose storage details to API
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    # =========================
    # Create
    # =========================

    def create_task(
        self,
        owner_id: int,
        title: str,
        description: str | None = None,
    ) -> Task:
        
        if not title or not title.strip():
            raise ValidationError("Task title is required")

        task = Task(
            id=None,
            owner_id=owner_id,
            title=title.strip(),
            description=description,
            completed=False,
        )

        return self.storage.save_task(task)

    # =========================
    # Read
    # =========================

    def get_task(self, task_id: int, user: User) -> Task:
        task = self.storage.get_task_by_id(task_id)
        if not task:
            raise NotFoundError("resource not found")#No info leak or enumeration risk by saying "not found" instead of "forbidden"

        if user.role != UserRole.ADMIN and task.owner_id != user.id:
            raise NotFoundError("resource not found")#denied to avoid info leak or enumeration

        return task

    def list_tasks(self, user: User) -> List[Task]:
        """
        - Admin: see all tasks
        - User: see only own tasks
        """
        if user.role == UserRole.ADMIN:
            return self.storage.list_all_tasks()

        return self.storage.list_tasks_by_owner(user.id)

    # =========================
    # Update
    # =========================
    def update_task(self, task_id: int, user: User, **kwargs) -> Task:
              
       task = self.get_task(task_id, user)
       title = kwargs.get("title")
       if title is not None:
           if not title.strip():
             raise ValidationError("Title cannot be empty")
           task.title = title.strip()

       if "description" in kwargs:
          task.description = kwargs["description"]

       if "completed" in kwargs and kwargs["completed"] is not None:
          task.completed = kwargs["completed"]

       return self.storage.save_task(task)
    
    # =========================
    # Delete
    # =========================
    def delete_task(self, task_id: int, user: User) -> None:
        self.get_task(task_id, user)
        
        self.storage.delete_task(task_id)