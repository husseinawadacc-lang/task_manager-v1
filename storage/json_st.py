import json
from pathlib import Path
from datetime import datetime
from storage.base_st import BaseStorage
from models.user import User
from core.enums.user_role import UserRole
from models.task import Task
from typing import List, Optional

class JSONStorage(BaseStorage):
    """
    Educational JSON storage for User entity only.
    NOT intended for production use.
    Login is email-based only.
    """

    def __init__(self, file_path: str = "data/app.json"):
        self.file = Path(file_path)
        self.file.parent.mkdir(parents=True, exist_ok=True)
        if not self.file.exists():
            self._write_data ({
                "users": {},
                "user_id_seq": 1,
                "tasks": {},
                "task_id_seq": 1,
            })
        
    # ======================
    # Helpers
    # ======================

    def _read_data(self) -> dict:
        
        with self.file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write_data(self, data: dict) -> None:
        
        with self.file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # ======================
    # User operations
    # ======================

    def save_user(self, user: User) -> User:
        data = self._read_data()

        # Enforce email uniqueness
        for raw in data["users"].values():
            if raw["email"] == user.email:
                raise ValueError("Email already exists")

        # Assign ID if new user
        if user.id is None:
            user.id = data["user_id_seq"]
            data["user_id_seq"] += 1

        data["users"][str(user.id)] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "password_hash": user.password_hash,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "last_login_at": (
                user.last_login_at.isoformat()
                if user.last_login_at
                else None
            ),
            "deleted_at": (
                user.deleted_at.isoformat()
                if user.deleted_at
                else None
            ),
            "created_at": user.created_at.isoformat(),
        }

        self._write_data(data)
        return user

    def get_user_by_id(self, user_id: int) -> User | None:
        data = self._read_data()
        raw = data["users"].get(str(user_id))
        if not raw:
            return None

        return self._map_raw_to_user(raw)

    def get_user_by_email(self, email: str) -> User | None:
        data = self._read_data()

        for raw in data["users"].values():
            if raw["email"] == email:
                return self._map_raw_to_user(raw)

        return None

    # ======================
    # Internal mapping
    # ======================

    def _map_raw_to_user(self, raw: dict) -> User:
        return User(
            id=raw["id"],
            username=raw["username"],
            email=raw["email"],
            password_hash=raw["password_hash"],
            role=UserRole(raw["role"]),
            is_active=raw["is_active"],
            is_verified=raw["is_verified"],
            last_login_at=(
                datetime.fromisoformat(raw["last_login_at"])
                if raw["last_login_at"]
                else None
            ),
            deleted_at=(
                datetime.fromisoformat(raw["deleted_at"])
                if raw["deleted_at"]
                else None
            ),
            created_at=datetime.fromisoformat(raw["created_at"]),
        )

    # ---------- tasks ----------
    def save_task(self, task: Task) -> Task:
        data = self._read_data()
        tasks = data["tasks"]
        # Assign ID if new task
        if task.id is None:
            task.id = data["task_id_seq"]
            data["task_id_seq"] += 1

        tasks[str(task.id)] = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "owner_id": task.owner_id,
            "completed": task.completed,
            
            "created_at": task.created_at.isoformat(),
        }

        self._write_data(data)
        return task
    def get_task_by_id(self, task_id: int) -> Task | None:
        data = self._read_data()
        raw = data["tasks"].get(str(task_id))
        
        return self._row_to_task(raw)
    def list_tasks_by_owner(self, owner_id:int)->list[Task]:
        data = self._read_data()
        result: list[Task] = []
        for raw in data["tasks"].values():
            if raw["owner_id"] == owner_id:
                result.append(self._row_to_task(raw))
        return result

    def list_all_tasks(self)->list[Task]:
        data = self._read_data()
        return [self._row_to_task(raw) for raw in data["tasks"].values()]
    
    def delete_task(self, task_id: int):
        data= self._read_data()
        tasks= data["tasks"]
        if str(task_id) not in tasks:
            raise ValueError("Task not found")       
        del tasks[str(task_id)]
        self._write_data(data)
    
    def _row_to_task(self, raw: dict) ->  Task:
        if raw is None:
            return None
        return Task(
            id=raw["id"],
            title=raw["title"],
            description=raw["description"],
            owner_id=raw["owner_id"],
            completed=raw["completed"],
            created_at=datetime.fromisoformat(raw["created_at"]),
        )   