from fastapi import APIRouter, Depends
from typing import List
from api.schemas.task import TaskCreateRequest,TaskResponse,TaskUpdateRequest
from services.task_s import TaskService
from api.deps.services import get_task_service
from api.deps.auth import get_current_user
from models.user import User
from fastapi import status
router = APIRouter(prefix="/tasks", tags=["TASKS"])

@router.post("", response_model=TaskResponse,
              status_code=status.HTTP_201_CREATED)
def create_task(
    input: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    task = task_service.create_task(
        owner_id=current_user.id,
        title=input.title,
        description=input.description,
    )
    return task

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    return task_service.get_task(task_id, current_user)

@router.get("", response_model=list[TaskResponse])
def list_tasks(
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    return task_service.list_tasks(current_user)

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    input: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    return task_service.update_task(
        task_id=task_id,
        user=current_user,
        completed=input.completed,
        title=input.title,
        description=input.description,
    )

@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    task_service.delete_task(task_id, current_user)