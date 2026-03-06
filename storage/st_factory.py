from core.config import get_settings
from storage.base_st import BaseStorage
from storage.memory_storage import MemoryStorage
from storage.sqlalchemy_storage import SQLAlchemyStorage

settings = get_settings()
def get_storage() -> BaseStorage:
    """
    Storage Factory
    Single decision point for storage backend.
    """

    if settings.STORAGE_BACKEND == "memory":
        return MemoryStorage()
    if settings.STORAGE_BACKEND == "sqlalchemy":
        return SQLAlchemyStorage ()


    raise RuntimeError(
        f"Unsupported STORAGE_BACKEND: {settings.STORAGE_BACKEND}"
    )