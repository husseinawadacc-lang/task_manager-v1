from abc import ABC, abstractmethod
from typing import List, Optional,Dict
from datetime import datetime
from dataclasses import dataclass

from domain.user import User
from domain.task import Task
from domain.project import Project
from domain.audit_log import AuditLog
# ================================
# 🔐 DTOs
# ================================

@dataclass
class PasswordResetTokenRecord:
    """
    DTO لقراءة بيانات reset token
    """
    id: int
    user_id: int
    token_hash: str
    expires_at: datetime
    used: bool


@dataclass
class RefreshTokenRecord:
    id: int
    user_id: int
    token_hash: str
    expires_at: datetime
    used: bool
    revoked: bool
    family_id: str


# ================================
# 🧱 Base Storage Contract
# ================================

class BaseStorage(ABC):
    """
    Clean Storage Contract (Final Version)

    Principles:
    - Storage does NOT control transactions
    - Storage returns Domain models (NOT ORM)
    - Service handles business logic
    - Supports pagination & isolation
    """

    # ==========================================================
    # TASKS
    # ==========================================================

    @abstractmethod
    def create_task(
        self,
        *,
        session,
        task: Task
    ) -> Task:
        """
        Persist a new task.

        Must:
        - assign id
        - set created_at if missing
        - set completed default if needed

        Returns created Task
        """

    @abstractmethod
    def get_task(
        self,
        *,
        session,
        task_id: int,
    ) -> Task:
        """
        Retrieve task by ID.

        Raises NotFoundError if not found.
        """

    @abstractmethod
    def update_task(
        self,
        *,
        session,
        task:Task,
    ) -> Task:
        """
        Partial update.

        Only non-None fields should be updated.

        Returns updated Task.
        Raises NotFoundError if not found.
        """

    @abstractmethod
    def delete_task(
        self,
        *,
        session,
        task_id: int,
    ) -> None:
        """
        Delete task by ID.

        Raises NotFoundError if not found.
        """

    @abstractmethod
    def list_tasks(
        self,
        *,
        session,
        owner_id: int,
        project_id:int,
        limit: int,
        offset: int,
    ) -> List[Task]:
        """
        Return paginated tasks.

        MUST NOT return full dataset.
        """

    @abstractmethod
    def count_tasks(
        self,
        *,
        session,
        owner_id: int,
        project_id: int,
    ) -> int:
        """
        Return total number of tasks.
        """
    @abstractmethod
    def get_tasks_by_parent(self, session, parent_id: int)-> list [Task]:
        pass
    

    # ==========================================================
    # USERS
    # ==========================================================

    @abstractmethod
    def create_user(
        self,
        *,
        session,
        user: User
    ) -> User:
        """
        Persist a new user.
        Must assign ID.
        """

    @abstractmethod
    def update_user(
        self,
        *,
        session,
        user: User
    ) -> User:
        """
        Update user fields.
        """

    @abstractmethod
    def get_user_by_email(
        self,
        *,
        session,
        email: str
    ) -> User:
        """
        Retrieve user by email.
        """

    @abstractmethod
    def get_user_by_id(
        self,
        *,
        session,
        user_id: int
    ) -> User:
        """
        Retrieve user by ID.
        """

    @abstractmethod
    def update_user_password(
        self,
        *,
        session,
        user_id: int,
        password_hash: str,
    ) -> None:
        """
        Update password hash.
        """

    # ==========================================================
    # PASSWORD RESET TOKENS
    # ==========================================================

    @abstractmethod
    def create_password_reset_token(
        self,
        *,
        session,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
    ) -> int:
        """
        Persist password reset token.
        """

    @abstractmethod
    def get_password_reset_token(
        self,
        *,
        session,
        token_hash: str,
    ) -> PasswordResetTokenRecord:
        """
        Retrieve reset token by hash.
        """

    @abstractmethod
    def mark_password_reset_token_used(
        self,
        *,
        session,
        token_id: int
    ) -> None:
        """
        Mark reset token as used.
        """

    # ==========================================================
    # REFRESH TOKENS
    # ==========================================================

    @abstractmethod
    def create_refresh_token(
        self,
        *,
        session,
        user_id: int,
        token_hash: str,
        family_id: str,
        expires_at: datetime,
    ) -> int:
        """
        Persist refresh token.
        """

    @abstractmethod
    def get_refresh_token(
        self,
        *,
        session,
        token_hash: str,
    ) -> RefreshTokenRecord:
        """
        Retrieve refresh token.
        """

    @abstractmethod
    def mark_refresh_token_used(
        self,
        *,
        session,
        token_id: int
    ) -> None:
        """
        Mark token as used.
        """

    @abstractmethod
    def revoke_refresh_token(
        self,
        *,
        session,
        token_id: int
    ) -> None:
        """
        Revoke single token.
        """

    @abstractmethod
    def revoke_token_family(
        self,
        *,
        session,
        family_id: str
    ) -> None:
        """
        Revoke all tokens in family.
        """

    @abstractmethod
    def revoke_tokens_by_user(
        self,
        *,
        session,
        user_id: int
    ) -> None:
        """
        Revoke all user tokens.
        """




    # ==========================================================
    # PROJECT OPERATIONS 🔥 (NEW)
    # ==========================================================

    @abstractmethod
    def create_project(
        self,
        *,
        session,
        project: Project
    ) -> Project:
        """Create new project"""

    @abstractmethod
    def get_project(
        self,
        *,
        session,
        project_id: int,
    ) -> Project:
        """Get project by id"""

    @abstractmethod
    def list_projects(
        self,
        *,
        session,
        owner_id: int,
    ) -> List[Project]:
        """List user projects"""

    @abstractmethod
    def delete_project(
        self,
        session,
        project_id:int,
    )  ->None:
        """
        delete project by id
        """  

    # ==========================================================
    # PROJECT MEMBERS (RBAC)
    # ==========================================================

    @abstractmethod
    def add_project_member(
        self,
        *,
        session,
        project_id: int,
        user_id: int,
        role: str = "member",
    ) -> None:
        """
        Add user to project with role.
        """


    @abstractmethod
    def remove_project_member(
        self,
        *,
        session,
        project_id: int,
        user_id: int,
    ) -> None:
        """
        Remove user from project.
        """


    @abstractmethod
    def list_project_members(
        self,
        *,
        session,
        project_id: int,
    ) -> Dict[int, str]:
        """
        Return all members of project.

        Format:
            { user_id: role }
        """


    @abstractmethod
    def get_project_member_role(
        self,
        *,
        session,
        project_id: int,
        user_id: int,
    ) -> Optional[str]:
        """
        Return role of user in project.

        Returns:
            role OR None
        """


    @abstractmethod
    def is_project_member(
        self,
        *,
        session,
        project_id: int,
        user_id: int,
    ) -> bool:
        """
        Check if user belongs to project.
        """  

    @abstractmethod
    def create_audit_log(
        self,
        session,
        log:AuditLog,

    )-> AuditLog:
        pass    