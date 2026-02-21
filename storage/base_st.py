from abc import ABC, abstractmethod
from models.user import User
from models.task import Task
from typing import List, Optional

class BaseStorage(ABC):
    # ============
    # User methods
    # ============

    @abstractmethod
    def save_user(self, user: User) -> User:
        """
        Persist a user.
        - Assigns id if needed.
        - Returns the saved user.
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_user_by_email(self,email:str)-> User |None:
        """
        Docstring for get_user_by_email
        login by email
        :param self: Description
        :param email: Description
        :type email: str
        :return: Description
        :rtype: User | None
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_user_by_id(self,user_id:int)-> User |None:
        pass


    # =========================
    # Task Storage
    # =========================

    @abstractmethod
    def save_task(self, task: Task) -> Task:
        """
        Create or update task.
        """
        raise NotImplementedError

    @abstractmethod
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Fetch task by its ID.
        """
        raise NotImplementedError

    @abstractmethod
    def list_tasks_by_owner(self, owner_id: int) -> List[Task]:
        """
        List all tasks for a specific user.
        """
        raise NotImplementedError

    @abstractmethod
    def list_all_tasks(self) -> List[Task]:
        """
        Admin-only: list all tasks.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_task(self, task_id: int) -> None:
        """
        Hard delete task.
        """
        raise NotImplementedError