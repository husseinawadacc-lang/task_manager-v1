from fastapi import Depends
from storage.st_factory import get_storage
from services.task_s import TaskService
from services.auth_s import AuthService


def get_task_service():
    storage = get_storage()
    
    return TaskService(storage)

def get_auth_service():
    storage = Depends(get_storage)
    return AuthService(storage=storage)