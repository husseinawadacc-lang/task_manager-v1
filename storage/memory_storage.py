from datetime import datetime,timezone
from typing import Dict, List
from storage.base_st import (
    BaseStorage,
    PasswordResetTokenRecord,
    RefreshTokenRecord,)
from domain.user import User
from domain.task import Task
from domain.project import Project
from domain.audit_log import AuditLog
from utils.exceptions import NotFoundError
import copy

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
        self._projects:Dict[int,Project]= {}
        self._project_members:Dict[int,Dict[int,str]]={}
        self._audit_logs: Dict[int,AuditLog]={}
        # auto increment counters (simulate database sequences)
        self._user_id_seq = 1
        self._task_id_seq = 1
        self._password_token_id_seq = 1
        self._refresh_token_id_seq = 1
        self._project_id_seq =1
        self._audit_id_logs =1
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

    def create_task(self, *, session, task: Task) -> Task:

        task.id = self._task_id_seq
        self._task_id_seq += 1

        task.completed = task.completed or False
        task.created_at = task.created_at or datetime.now(timezone.utc)
        task.priority = task.priority or "low"

        self._tasks[task.id] = copy.deepcopy(task)

        return task
    
    def get_task(self, *, session, task_id: int) -> Task:
        """
        Retrieve task by id.
        """

        task = self._tasks.get(task_id)

        if not task:
            raise NotFoundError("Task not found")

        return task

    def update_task(self, *, session, task: Task) -> Task:

        existing = self._tasks.get(task.id)

        if not existing:
            raise NotFoundError("Task not found")

        if not task.id :
            raise ValueError ("Task ID is require")
        if task.title is not None:
            existing.title = task.title

        if task.description is not None:
            existing.description = task.description

        if task.completed is not None:
            existing.completed = task.completed

        if task.priority is not None:
            existing.priority = task.priority

        return existing

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
        project_id :int,
        limit: int,
        offset: int,
    ) -> List[Task]:

        tasks = [t for t in self._tasks.values() if t.owner_id == owner_id and
                 t.project_id == project_id
                 ]

        tasks.sort(key=lambda t: t.created_at , reverse=True)

        return tasks[offset: offset + limit]
    
    def count_tasks(self, *, session, owner_id: int,project_id:int) -> int:
        """
        Count tasks for pagination.
        """

        return sum(1 for t in self._tasks.values() if t.owner_id == owner_id
                   and t.project_id == project_id
                   )


    def get_tasks_by_parent(self,*,session, parent_id: int) -> List[Task]:
            return [
                t for t in self.tasks.values()
                if t.parent_id == parent_id
            ]
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
        family_id:str,
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
            revoked=False,
            family_id=family_id
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

    def revoke_refresh_token(
            self,
            *,
            session,
            token_id,
    )-> None:
        
        token= self._refresh_tokens.get(token_id)
        if not token:
           raise NotFoundError("Refresh token not found")
        
        token.revoked= True


    def revoke_token_family(
            self,
            *,
            session,
            family_id:str,
    )-> None:
        
        for token in self._refresh_tokens.values():
            if token.family_id == family_id:
               token.revoked = True        


    def revoke_tokens_by_user(
            self,
            *,
            session,
            user_id:int,
    )-> None:
        
        for token in self._refresh_tokens.values():
            if token.user_id == user_id:
               token.revoked = True        


    def create_project(self, *, session, project: Project) -> Project:

        project.id = self._project_id_seq
        self._project_id_seq += 1

        project.created_at = datetime.now(timezone.utc)

        self._projects[project.id] = copy.deepcopy(project)

        # 🔥 RBAC FIX
        self._project_members[project.id] = {
            project.owner_id: "owner"
        }

        return project

    def get_project(self, *, session, project_id: int) -> Project:

        project = self._projects.get(project_id)

        if not project:
            raise NotFoundError("Project not found")

        return project  
    
    def list_projects(self, *, session, owner_id: int) -> List[Project]:

        return [
            p for p in self._projects.values()
            if p.owner_id == owner_id
        ]
    def delete_project(
            self,
            *,
            session,
            project_id: int,
        ) -> None:

            if project_id not in self._projects:
                raise NotFoundError("Project not found")
            
            self._project_members.pop(project_id,None)

            del self._projects[project_id]

    # ======================================================
    # Project Members (RBAC FIXED)
    # ======================================================

    def add_project_member(
        self,
        *,
        session,
        project_id: int,
        user_id: int,
        role: str = "member",
    ) -> None:

        members = self._project_members.setdefault(project_id, {})

        members[user_id] = role


    # ------------------------------------------------------

    def get_project_member_role(
        self,
        *,
        session,
        project_id: int,
        user_id: int,
    ) -> str | None:

        members = self._project_members.get(project_id, {})

        return members.get(user_id)


    # ------------------------------------------------------

    def remove_project_member(
        self,
        *,
        session,
        project_id: int,
        user_id: int,
    ) -> None:

        members = self._project_members.get(project_id, {})

        members.pop(user_id, None)


    # ------------------------------------------------------

    def list_project_members(
        self,
        *,
        session,
        project_id: int,
    ) -> Dict[int, str]:

        return  Dict(self._project_members.get(project_id, {}))


    # ------------------------------------------------------

    def is_project_member(
        self,
        *,
        session,
        project_id: int,
        user_id: int,
    ) -> bool:

        return user_id in self._project_members.get(project_id, {})
    
    def create_audit_log(self, *, session, log: AuditLog) -> AuditLog:

        log.id = self._audit_id_seq
        self._audit_id_seq += 1

        log.created_at = datetime.now(timezone.utc)

        self._audit_logs[log.id] = log

        return log