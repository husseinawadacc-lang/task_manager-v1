from fastapi import Depends

from storage.base_st import BaseStorage
from storage.st_factory import get_storage

from services.task_s import TaskService
from services.auth_s import AuthService
from services.password_policy_s import PasswordPolicyService
from services.password_reset_services import PasswordResetService
from services.token_services import TokenService
from services.unit_of_work import UnitOfWork


# --------------------------------
# UnitOfWork
# --------------------------------

def get_unit_of_work() -> UnitOfWork:
    """
    Provide UnitOfWork instance.
    """
    return UnitOfWork()


# --------------------------------
# Password Policy
# --------------------------------

def get_password_policy_service() -> PasswordPolicyService:
    """
    Stateless service.
    Safe to instantiate per request.
    """
    return PasswordPolicyService()


# --------------------------------
# TaskService
# --------------------------------

def get_task_service(
    storage: BaseStorage = Depends(get_storage),
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> TaskService:

    return TaskService(
        storage=storage,
        uow=uow
    )


# --------------------------------
# TokenService
# --------------------------------

def get_token_service(
    storage: BaseStorage = Depends(get_storage),
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> TokenService:

    return TokenService(
        storage=storage,
        uow=uow
    )


# --------------------------------
# AuthService
# --------------------------------

def get_auth_service(
    storage: BaseStorage = Depends(get_storage),
    policy: PasswordPolicyService = Depends(get_password_policy_service),
    uow: UnitOfWork = Depends(get_unit_of_work),
    token_service:TokenService=Depends(get_token_service)
) -> AuthService:

    return AuthService(
        storage=storage,
        password_policy=policy,
        uow=uow,
        token_service=token_service
    )


# --------------------------------
# PasswordResetService
# --------------------------------

def get_password_reset_service(
    storage: BaseStorage = Depends(get_storage),
    policy: PasswordPolicyService = Depends(get_password_policy_service),
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> PasswordResetService:

    return PasswordResetService(
        storage=storage,
        password_policy=policy,
        uow=uow
    )