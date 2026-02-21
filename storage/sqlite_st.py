import sqlite3
from typing import Optional,List
from datetime import datetime
from storage.base_st import BaseStorage
from models.user import User
from models.task import Task
from core.enums.user_role import UserRole


class SQLiteStorage(BaseStorage):
    def __init__(self, db_path: str = "data/app.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                owner_id INTEGER NOT NULL,
                completed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        
        self.conn.commit()

    # =========================
    # User Storage
    # =========================

    def save_user(self, user: User) -> User:
        cur = self.conn.cursor()

        if user.id is None:
            cur.execute(
                """
                INSERT INTO users (username, email, password_hash,role, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user.username,
                    user.email,
                    user.password_hash,
                    user.role.value,
                    int(user.is_active),
                    user.created_at.isoformat(),
                ),
            )
            user.id = cur.lastrowid
        else:
            cur.execute(
                """
                UPDATE users
                SET username=?, email=?, password_hash=?,  role=?, is_active=?
                WHERE id=?
                """,
                (
                    user.username,
                    user.email,
                    user.password_hash,
                    user.role.value,
                    int(user.is_active),
                    user.id,
                ),
            )

        self.conn.commit()
        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        return self._row_to_user(row)

    def get_user_by_email(self, email: str) -> Optional[User]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        row = cur.fetchone()
        return self._row_to_user(row)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Used for display/search purposes only.
        MUST NOT be used for authentication.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        return self._row_to_user(row)

    # ================= TASK =================

    def save_task(self, task: Task) -> Task:
        cur = self.conn.cursor()
        if task.id is None:
            cur.execute("""
            INSERT INTO tasks (title, description, owner_id, completed, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (
                task.title,
                task.description or "",
                task.owner_id,
                int(bool(task.completed)),
                task.created_at.isoformat(),
            ))
            task.id = cur.lastrowid
        else:
            cur.execute("""
            UPDATE tasks
            SET title=?, description=?, completed=?
            WHERE id=?
            """, (
                task.title,
                task.description or "",
                int(bool(task.completed)),
                task.id,
            ))

        self.conn.commit()
        return task

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        return self._row_to_task(cur.fetchone())

    def list_tasks_by_owner(self, owner_id: int) -> List[Task]:
        cur = self.conn.cursor()
        cur.execute("""
                    SELECT id, title, description, owner_id, completed,
                     created_at FROM tasks WHERE owner_id=?
                     ORDER BY id DESC""", (owner_id,))
        rows = cur.fetchall()
        return [self._row_to_task(row) for row in rows]
    
    def list_all_tasks(self):
        cur= self.conn.cursor()
        cur.execute("""
                    SELECT id, title, description, owner_id, completed,
                     created_at FROM tasks ORDER BY id DESC""")
        rows = cur.fetchall()
        return [self._row_to_task(row) for row in rows]
    
    def delete_task(self, task_id: int) -> bool:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        self.conn.commit()
        return cur.rowcount > 0
    
    # ================= HELPERS =================

    def _row_to_user(self, row) -> Optional[User]:
        if not row:
            return None
        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            role=UserRole(row["role"]),
            is_active=bool(row["is_active"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _row_to_task(self, row) -> Optional[Task]:
        if not row:
            return None
        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            owner_id=row["owner_id"],
            completed=bool(row["completed"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )