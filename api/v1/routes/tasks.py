from fastapi import APIRouter, Depends, Query, status
from typing import List

from services.task_service import TaskService
from api.schemas.task import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskResponse,
    TaskListResponse,
)

from api.deps.services_dep import get_task_service
from api.deps.permissions_dep import require_permission

from core.enums.permission import Permission

from domain.user import User


router = APIRouter(prefix="/tasks", tags=["TASKS"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    input: TaskCreateRequest,
    current_user: User = Depends(require_permission(Permission.TASK_CREATE)),
    task_service: TaskService = Depends(get_task_service),
):
    task = task_service.create_task(
        owner_id=current_user.id,
        title=input.title,
        description=input.description,
        project_id=input.project_id,
        parent_id=input.parent_id,)
    
    if input.auto_generate:
        task_service.generate_subtasks_for_task(

            task_id=task.id,
            title=task.title,
            owner_id=current_user.id,
            project_id=input.project_id or None,
        )
    task_with_subtasks= task_service.get_task_with_subtasks(task_id=task.id,
                                                            requester_id=current_user.id)

    return task_with_subtasks
    


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(require_permission(Permission.TASK_VIEW)),
):
    return task_service.get_task_with_subtasks(
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
    current_user: User = Depends(require_permission(Permission.TASK_UPDATE)),
):
    updated= task_service.update_task(
        task_id=task_id,
        requester_id=current_user.id,
        title=data.title,
        description=data.description,
        completed=data.completed,
    )
    return task_service.get_task_with_subtasks(
        task_id=updated.id,
        requester_id= current_user.id
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(require_permission(Permission.TASK_DELETE)),
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
    current_user: User = Depends(require_permission(Permission.TASK_VIEW)),
    project_id:int = Query(),
    limit: int = Query(20, ge=1,le=100),
    offset: int = Query(0, ge=0),
):
    items, total = task_service.list_tasks(
        owner_id=current_user.id,
        project_id=project_id,
        limit=limit,
        offset=offset,
    )

    return TaskListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )