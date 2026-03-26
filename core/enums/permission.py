from enum import Enum

class Permission(str, Enum):

    # Task
    TASK_CREATE = "task:create"
    TASK_UPDATE = "task:update"
    TASK_DELETE = "task:delete"
    TASK_VIEW   = "task:view"

    # Project
    PROJECT_CREATE = "project:create"
    PROJECT_DELETE = "project:delete"
    PROJECT_INVITE = "project:invite"
    PROJECT_VIEW   = "project:view"

    # User
    USER_VIEW   = "user:view"
    USER_MANAGE = "user:manage"