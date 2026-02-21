from storage.base_st import BaseStorage
from models.user import User
from models.task import Task
from typing import List, Optional,Dict
class MemoryStorage(BaseStorage):
    
    def __init__(self):
        self._tasks: dict[int,Task] = {}
        self._users: dict[int,User] = {}
        self._users_by_email:dict[int,User]={}     
        self._user_id_seq =1
        self ._task_id_seq =1

    def clear(self):
        self._tasks.clear()
        self._users.clear()
        self._users_by_email.clear()
        self._user_id_seq =1
        self ._task_id_seq =1    

    def save_user(self, user: User) -> User:
       if user.id is None:
          user.id = self._user_id_seq
          self._user_id_seq += 1

       self._users[user.id] = user
       self._users_by_email[user.email]=user
       return user
       
    def get_user_by_email(self, email:str)-> User |None:
        return self._users_by_email.get(email)

    def get_user_by_id(self, user_id: int) ->User |None:
        return self._users.get(user_id)
    

    def save_task(self, task:Task) ->Task:
        if task.id is None:
            task.id =self._task_id_seq
            self._task_id_seq += 1
            self._tasks[task.id] =task
        return task

    def get_task_by_id(self, task_id: int)->Optional[Task] :
        return self._tasks.get(task_id)
    
    def list_tasks_by_owner(self, owner_id:int)-> list[Task]:
        return [task for task in self._tasks.values() if task.owner_id == owner_id]
    
    def list_all_tasks(self) -> list [Task]:
        return list(self._tasks.values())

    def delete_task(self, task_id: int) -> None:
        if task_id not in self._tasks:
            raise ValueError("Task not found")
        del self._tasks[task_id]