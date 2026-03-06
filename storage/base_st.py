from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from models.user import User
from models.task import Task
from dataclasses import dataclass


@dataclass
class PasswordResetTokenRecord:
    """
    DTO بسيط لقراءة بيانات reset token
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
    expires_at:datetime
    used: bool 


class BaseStorage(ABC):
    """
    Clean storage contract (v2).

    This contract enforces:
    - User isolation
    - Pagination at storage level
    - No full dataset exposure
    """

    # ---------- Tasks ----------

    @abstractmethod
    def create_task(
        self,
        *,
        session,
        title:str,
        description: str,
        owner_id:int
    ) -> Task:
        """
        Create anew task Must set:
        - id
        -completed = False
        -created_at internally
        Return created Task
        """
        
    @abstractmethod
    def get_task(
        self,
        *,
        session,
        task_id: int,
    ) -> Task :
        """
        retrieve task by Id Raises Not foundError if not found
        """
        
    @abstractmethod
    def update_task(
        self,
        *,
        session,
        task_id:int,
        title:str |None,
        description:str |None,
        completed:bool |None
    ) -> Task :
        """
        Update mutable fields of task return update task
        raises notfounderror if not found
        """
    

    @abstractmethod
    def delete_task(
        self,
        *,
        session,
        task_id: int,
    ) -> None:
        """
        delete task by id 
        raises notfounderror if not found

        """
        
    
    @abstractmethod
    def list_tasks(
        self,
        *,
        session,
        owner_id: int,
        limit: int,
        offset: int,
    ) -> List[Task]:
        """
        Return paginated slice only.
        MUST NOT return all tasks.
        """
        

    @abstractmethod
    def count_tasks(
        self,
        *,
        session,
        owner_id: int,
    ) -> int:
        """
        Return total task count for owner.
        """
        

    # ============
    # User methods
    # ============

    @abstractmethod
    def create_user(self,*,session, user: User) -> User:
        """
        Persist a new user.
        -  must Assigns id .
        - Returns the saved user.
        """
        

    @abstractmethod
    def update_user(self,* , session, user:User)-> User:
        """
        update existing user fieldes
        """
        
    
    @abstractmethod
    def get_user_by_email(self,*, session, email:str)-> User :
        """
        Docstring for get_user_by_email
        login by email
        :param self: Description
        :param email: Description
        :type email: str
        :return: Description
        :rtype: User | None
        """
        
    
    @abstractmethod
    def get_user_by_id(self,*, session, user_id:int)-> User :
        """fetch user by id      """
        

    @abstractmethod
    def update_user_password(
        self,
        *,
        session,
        user_id: int,
        password_hash: str,
    ) -> None:
        """
        Update stored password hash 
        """
        

    # ---------- Password Reset ----------
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
        persist password rest token
        return internal ID 
        """
        

    @abstractmethod
    def get_password_reset_token(
        self,
        *,
        session,
        token_hash: str,
    ) -> PasswordResetTokenRecord :
        """
        retrieve reset tokeb by hash
        raises notfounderror if not found
        """
        

    @abstractmethod
    def mark_password_reset_token_used(self,*,session, token_id: int) -> None:
        """
        mark reset token as used
        raises notfounderror if not found

        """
    

    # ============================
    # Refresh Token Storage
    # ============================

    @abstractmethod
    def create_refresh_token(
        self,
        *,
        session,
        user_id: int,
        token_hash: str,
        expires_at: datetime |None,
    ) -> int:
        """
        Persist a refresh token.
        Returns  internal id.
        """
        


    @abstractmethod
    def get_refresh_token(
        self,
        *,
        session,
        token_hash: str,
    )->RefreshTokenRecord:
        """
        Retrieve refresh token record by hash.
        """
        


    @abstractmethod
    def mark_refresh_token_used(
        self,
        *,
        session,
        token_id: int,
    ) -> None:
        """
        Mark refresh token as used (one-time).
        """
        
