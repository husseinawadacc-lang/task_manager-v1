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

from datetime import datetime,timezone
from typing import List,Dict

from sqlalchemy import select, func
from sqlalchemy.orm import Session
from storage.base_st import (
    BaseStorage,
    PasswordResetTokenRecord,
    RefreshTokenRecord
)
from domain.project import Project
from db.models.project import ProjectORM

from domain.user import User
from domain.task import Task
from domain.audit_log import AuditLog
from db.models.user import UserORM
from db.models.task import TaskORM
from db.models.password_reset import PasswordResetTokenORM
from db.models.refresh_token import RefreshTokenORM
from db .models.project_member import ProjectMemberORM
from db.models.audit_log import AuditLogORM
from sqlalchemy.exc import IntegrityError
from utils.exceptions import NotFoundError,ConflictError


class SQLAlchemyStorage(BaseStorage):

    # ==========================================================
    # USER OPERATIONS
    # ==========================================================

    def create_user(self, *, session:Session, user: User) -> User:
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
        try: 
            session.flush()
        except IntegrityError as e:
            raise ConflictError ("resource already exists") from e
        
        return User(
                    id=orm_user.id,
                    email=orm_user.email,
                    password_hash=orm_user.password_hash,
                    role=orm_user.role,
                    is_active=orm_user.is_active,
                    created_at=orm_user.created_at,
                )

    # ----------------------------------------------------------

    def update_user(self, *, session:Session, user: User) -> User:
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

    def get_user_by_id(self, *, session:Session, user_id: int) -> User:

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

    def get_user_by_email(self, *, session:Session, email: str) -> User:

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
        session:Session,
        user_id: int,
        password_hash: str
    ) -> None:

        stmt = select(UserORM).where(UserORM.id == user_id)

        orm_user = session.execute(stmt).scalar_one_or_none()

        if not orm_user:
            raise NotFoundError("User not found")

        orm_user.password_hash = password_hash

        session.flush()


    # =========================================================
    # MAPPER HELPER
    # ========================================================
    def map_task(self,orm: TaskORM) -> Task:
        return Task(
            id=orm.id,
            title=orm.title,
            description=orm.description,
            owner_id=orm.owner_id,
            project_id=orm.project_id,
            parent_id=orm.parent_id,
            completed=orm.completed,
            created_at=orm.created_at,
            priority=orm.priority,
        )    

    # ==========================================================
    # TASK OPERATIONS
    # ==========================================================
    def create_task(
        self,
        *,
        session: Session,
        task: Task
    ) -> Task:
        orm_task = TaskORM(
            title=task.title,
            description=task.description,
            owner_id=task.owner_id,
            project_id = task.project_id,
            parent_id =task.parent_id,
            completed=task.completed or False,
            created_at=task.created_at or None,
            priority=task.priority or "low",
        )

        session.add(orm_task)
        session.flush()

        return self.map_task(orm_task)

    # ----------------------------------------------------------

    def get_task(self, *, session: Session, task_id: int) -> Task:

        stmt = select(TaskORM).where(TaskORM.id == task_id)

        orm_task = session.execute(stmt).scalar_one_or_none()

        if not orm_task:
            raise NotFoundError("Task not found")

        return self.map_task(orm_task)
    # ----------------------------------------------------------

    def update_task(
        self,
        *,
        session: Session,
        task: Task
    ) -> Task:

        stmt = select(TaskORM).where(TaskORM.id == task.id)

        orm_task = session.execute(stmt).scalar_one_or_none()

        if not orm_task:
            raise NotFoundError("Task not found")
          
        if  not task.id :
            raise ConflictError ("invalid task state")  
        if task.title is not None:
            orm_task.title = task.title

        if task.description is not None:
            orm_task.description = task.description

        if task.completed is not None:
            orm_task.completed = task.completed

        if task.priority is not None:
            orm_task.priority = task.priority

        session.flush()

        return self.map_task(orm_task)
    # ----------------------------------------------------------

    def delete_task(self, *, session:Session, task_id: int) -> None:

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
        session: Session,
        owner_id: int,
        project_id:int,
        limit: int,
        offset: int
    ) -> List[Task]:

        stmt = (
            select(TaskORM)
            .where(TaskORM.owner_id == owner_id,
                   TaskORM.project_id == project_id,
                   )
            .limit(limit)
            .offset(offset)
        )

        tasks = session.execute(stmt).scalars().all()

        return [self.map_task(t) for t in tasks
        ]

    # ----------------------------------------------------------

    def count_tasks(self, *, session:Session, owner_id: int,project_id:int) -> int:

        stmt = select(func.count()).where(TaskORM.owner_id == owner_id,
                                            TaskORM.project_id == project_id
                                          )

        return session.execute(stmt).scalar_one()
    
    # --------------------------------------------------------
    def get_tasks_by_parent(self, *, session, parent_id: int) -> List[Task]:
        stmt = select(TaskORM).where(TaskORM.parent_id == parent_id)

        tasks = session.execute(stmt).scalars().all()

        return [self.map_task(t) for t in tasks]    
    # ------------------------------------------------------
    def map_task_with_subtasks(self,orm: TaskORM) -> Task:
        task = self.map_task(orm)

        task.subtasks = [
            self.map_task(sub) for sub in orm.subtasks
        ]

        return task

    # ==========================================================
    # PASSWORD RESET TOKENS
    # ==========================================================

    def create_password_reset_token(
        self,
        *,
        session:Session,
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
        session:Session,
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
        session:Session,
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
        session:Session,
        user_id: int,
        token_hash: str,
        family_id:str,
        expires_at: datetime 
    ) -> int:

        orm_token = RefreshTokenORM(
            user_id=user_id,
            token_hash=token_hash,
            family_id=family_id,
            expires_at=expires_at,
            used=False,
            revoked=False
        )

        session.add(orm_token)

        session.flush()

        return orm_token.id

    # ----------------------------------------------------------

    def get_refresh_token(
        self,
        *,
        session:Session,
        token_hash: str
    ) -> RefreshTokenRecord:

        stmt = (
            select(RefreshTokenORM)
            .where(RefreshTokenORM.token_hash == token_hash)
            .with_for_update()
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
            revoked=orm_token.revoked,
            family_id=orm_token.family_id,
        )

    # ----------------------------------------------------------

    def mark_refresh_token_used(
        self,
        *,
        session:Session,
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

    def revoke_refresh_token(
    self,
    *,
    session: Session,
    token_id: int
) -> None:

        stmt = select(RefreshTokenORM).where(
            RefreshTokenORM.id == token_id
        )

        orm_token = session.execute(stmt).scalar_one_or_none()

        if not orm_token:
            raise NotFoundError("Refresh token not found")

        orm_token.revoked = True

        session.flush()        
    
    def revoke_token_family(
    self,
    *,
    session: Session,
    family_id: str
) -> None:

        stmt = select(RefreshTokenORM).where(
            RefreshTokenORM.family_id == family_id
        )

        tokens = session.execute(stmt).scalars().all()

        for token in tokens:
            token.revoked = True

        session.flush()
    
    def revoke_tokens_by_user(
    self,
    *,
    session: Session,
    user_id: int
) -> None:

        stmt = select(RefreshTokenORM).where(
            RefreshTokenORM.user_id == user_id
        )

        tokens = session.execute(stmt).scalars().all()

        for token in tokens:
            token.revoked = True

        session.flush()


    # ==========================================================
    # PROJECT OPERATIONS
    # ==========================================================

   

    def map_project(self, orm: ProjectORM) -> Project:
        return Project(
            id=orm.id,
            name=orm.name,
            owner_id=orm.owner_id,
            created_at=orm.created_at,
        )


    # ----------------------------------------------------------

    def create_project(
        self,
        *,
        session: Session,
        project: Project
    ) -> Project:

        orm_project = ProjectORM(
            name=project.name,
            owner_id=project.owner_id,
            created_at=datetime.now(timezone.utc))
        try:
            session.add(orm_project)
            session.flush()
        except IntegrityError as e:
                
            if "unique" in str(e).lower():
                raise ConflictError("project already exists") from e
    
    # 🔥 add owner 
        owner_member = ProjectMemberORM(
        project_id=orm_project.id,
        user_id=orm_project.owner_id,
        role="owner",)


        session.add(owner_member)
        session.flush()

       
        return self.map_project(orm_project)


    # ----------------------------------------------------------

    def get_project(
        self,
        *,
        session: Session,
        project_id: int
    ) -> Project:

        stmt = select(ProjectORM).where(ProjectORM.id == project_id)

        orm_project = session.execute(stmt).scalar_one_or_none()

        if not orm_project:
            raise NotFoundError("Project not found")

        return self.map_project(orm_project)


    # ----------------------------------------------------------

    def list_projects(
        self,
        *,
        session: Session,
        owner_id: int
    ) -> List[Project]:

        stmt = select(ProjectORM).join(ProjectMemberORM).where(ProjectMemberORM.user_id == owner_id)

        projects = session.execute(stmt).scalars().all()

        return [self.map_project(p) for p in projects]     

    # -------------------------------------------------------------

    def delete_project(
            self,
            *,
            session:Session,
            project_id:int,
    )  ->  None :
        stmt=select(ProjectORM).where(ProjectORM.id== project_id)
        orm_project = session.execute(stmt).scalar_one_or_none()
        if not orm_project:
            raise NotFoundError("project not found")
        
        tasks = session.execute(
        select(TaskORM).where(TaskORM.project_id == project_id)
        ).scalars().first()

        if tasks:
            raise ConflictError("Project has tasks")
        session.delete(orm_project)
        session.flush()

    
    # ==========================================================
    # PROJECT  MEMBER OPERATIONS
    # ==========================================================

    def add_project_member(
        self,
        *,
        session,
        project_id: int,
        user_id: int,
        role: str = "member",
    ) -> None:

        orm = ProjectMemberORM(
            project_id=project_id,
            user_id=user_id,
            role=role,
        )
        try:
            session.add(orm)
            session.flush()  
        except IntegrityError:
            raise ConflictError("member already exists")    


    def remove_project_member(
        self,
        *,
        session,
        project_id: int,
        user_id: int,
    ) -> None:

        stmt = select(ProjectMemberORM).where(
            ProjectMemberORM.project_id == project_id,
            ProjectMemberORM.user_id == user_id,
        )

        orm = session.execute(stmt).scalar_one_or_none()

        if orm:
            session.delete(orm)   
            session.flush()
             

    def list_project_members(
        self,
        *,
        session,
        project_id: int,
    ) -> dict[int, str]:

        stmt = select(
            ProjectMemberORM.user_id,
            ProjectMemberORM.role
        ).where(
            ProjectMemberORM.project_id == project_id
        )

        rows = session.execute(stmt).all()

        return {user_id: role for user_id, role in rows}
    
    def get_project_member_role(
        self,
        *,
        session,
        project_id: int,
        user_id: int,
    ) -> str | None:

        stmt = select(ProjectMemberORM.role).where(
            ProjectMemberORM.project_id == project_id,
            ProjectMemberORM.user_id == user_id,
        )

        return session.execute(stmt).scalar_one_or_none()
    
    def is_project_member(
        self,
        *,
        session,
        project_id: int,
        user_id: int,
    ) -> bool:

        stmt = select(ProjectMemberORM.user_id).where(
            ProjectMemberORM.project_id == project_id,
            ProjectMemberORM.user_id == user_id,
        )

        return session.execute(stmt).scalar_one_or_none() is not None  
    
    def create_audit_log(self, *, session, log: AuditLog) -> AuditLog:

        orm = AuditLogORM(
            user_id=log.user_id,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            details=log.details,
        )

        session.add(orm)
        session.flush()

        return AuditLog(
            id=orm.id,
            user_id=orm.user_id,
            action=orm.action,
            resource_type=orm.resource_type,
            resource_id=orm.resource_id,
            details=orm.details,
            created_at=orm.created_at,
        ) 