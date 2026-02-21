from storage.base_st import BaseStorage
from storage.memory_storage import MemoryStorage
from storage.sqlite_st import SQLiteStorage
from core.config import Settings


def get_storage(settings: Settings) -> BaseStorage:
    """
    Storage Factory
    Single decision point for storage backend
    """

    if settings.STORAGE_BACKEND == "memory":
        return MemoryStorage()

    if settings.STORAGE_BACKEND == "sqlite":
        return SQLiteStorage()

    raise RuntimeError(
        f"Unsupported STORAGE_BACKEND: {settings.STORAGE_BACKEND}"
    )