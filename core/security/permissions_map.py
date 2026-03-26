from core.enums.permission import Permission
from core.enums.role import UserRole

ROLE_PERMISSIONS = {

    UserRole.ADMIN: {
        Permission.TASK_CREATE,
        Permission.TASK_UPDATE,
        Permission.TASK_DELETE,
        Permission.TASK_VIEW,

        Permission.PROJECT_CREATE,
        Permission.PROJECT_INVITE,
        Permission.PROJECT_VIEW,
        Permission.PROJECT_DELETE,
        Permission.USER_VIEW,
        Permission.USER_MANAGE,
    },

    UserRole.USER: {
        Permission.TASK_CREATE,
        Permission.TASK_UPDATE,
        Permission.TASK_VIEW,

        Permission.PROJECT_CREATE,
        Permission.PROJECT_VIEW,
    },
}