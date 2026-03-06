from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
from services.task_s import TaskService
from utils.exceptions import (
    TaskNotFoundError,
    ForbiddenTaskAccessError,
    InvalidPaginationError)
from api.schemas.task import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskResponse,
    TaskListResponse,)
from api.deps.services import get_task_service
from api.deps.auth import get_current_user
from models.user import User


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
@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    return task_service.get_task(
            task_id=task_id,
            requester_id=current_user.id,
        )
    

    
@router.put(
    "/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    task_id: int,
    data: TaskUpdateRequest,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    return  task_service.update_task(
            task_id=task_id,
            requester_id=current_user.id,
            title=data.title,
            description=data.description,
            completed=data.completed,
        )
       


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    return task_service.delete_task(
            task_id=task_id,
            requester_id=current_user.id,
        )


@router.get(
    "",
    response_model=TaskListResponse,
)
def list_tasks(
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
):
    items, total = task_service.list_tasks(
            owner_id=current_user.id,
            limit=limit,
            offset=offset,
        )

    return TaskListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )
