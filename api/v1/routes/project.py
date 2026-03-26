# ==========================================================
# Project Endpoints (FINAL SaaS VERSION)
# ==========================================================

from fastapi import APIRouter, Depends, status
from typing import List

# Schemas
from api.schemas.project import (
    ProjectCreateRequest,
    ProjectResponse,
)

# Service
from services.project_service import ProjectService
from api.deps.services_dep import get_project_service
from api.deps.auth_dep import get_current_user

# Auth / Permissions
from api.deps.permissions_dep import require_permission
from core.enums.permission import Permission
from domain.user import User


# ==========================================================
# Router
# ==========================================================

router = APIRouter(
    prefix="/projects",
    tags=["PROJECTS"]
)


# ==========================================================
# CREATE PROJECT
# ==========================================================

@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    data: ProjectCreateRequest,
    current_user: User = Depends(
        require_permission(Permission.PROJECT_CREATE)  # 🔥 FIXED
    ),
    service: ProjectService = Depends(get_project_service),
):
    """
    Create new project

    Logic:
    - Owner = current user
    - Name is required

    Security:
    - User must have CREATE_PROJECT permission
    """

    return service.create_project(
        owner_id=current_user.id,
        name=data.name,
    )


# ==========================================================
# LIST PROJECTS
# ==========================================================

@router.get(
    "",
    response_model=List[ProjectResponse],
)
def list_projects(
    current_user: User = Depends(
        require_permission(Permission.PROJECT_VIEW)  # 🔥 FIXED
    ),
    service: ProjectService = Depends(get_project_service),
):
    """
    Get all projects owned by current user

    Note:
    - Currently returns owned projects only
    - Later: include shared projects
    """

    return service.list_projects(
        owner_id=current_user.id,
    )


# ==========================================================
# GET PROJECT
# ==========================================================

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: int,
    current_user: User = Depends(
        require_permission(Permission.PROJECT_VIEW)
    ),
    service: ProjectService = Depends(get_project_service),
):
    """
    Get single project

    Security:
    - Owner OR member can access
    - Others → NotFound (Anti-IDOR)
    """

    return service.get_project(
        project_id=project_id,
        requester_id=current_user.id,
    )


# ==========================================================
# DELETE PROJECT
# ==========================================================

@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: int,
    current_user: User = Depends(  get_current_user   ),
    service: ProjectService = Depends(get_project_service),
):
    """
    Delete project

    Rules:
    - Only owner can delete
    """

    service.delete_project(
        project_id=project_id,
        requester_id=current_user.id,
    )


# ==========================================================
# ADD MEMBER (INVITE USER)
# ==========================================================

@router.post(
    "/{project_id}/members",
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    project_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user
    ),
    service: ProjectService = Depends(get_project_service),
):
    """
    Invite user to project

    Rules:
    - Only owner can invite
    - User must exist
    """

    service.add_member(
        project_id=project_id,
        owner_id=current_user.id,
        user_id=user_id,
    )

    return {"message": "Member added successfully"}


# ==========================================================
# REMOVE MEMBER
# ==========================================================

@router.delete(
    "/{project_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_member(
    project_id: int,
    user_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    service: ProjectService = Depends(get_project_service),
):
    """
    Remove user from project

    Rules:
    - Only owner can remove
    - Owner cannot remove himself
    """

    service.remove_member(
        project_id=project_id,
        owner_id=current_user.id,
        user_id=user_id,
    )


# ==========================================================
# LIST MEMBERS
# ==========================================================

@router.get(
    "/{project_id}/members",
    status_code=status.HTTP_200_OK,
)
def list_members(
    project_id: int,
    current_user: User = Depends(
        require_permission(Permission.PROJECT_VIEW)
    ),
    service: ProjectService = Depends(get_project_service),
):
    """
    Get all project members

    Security:
    - Only members (or owner) can view
    """


    return {"members": service.list_members(
        project_id=project_id,
        requester_id=current_user.id
    )
            
            }