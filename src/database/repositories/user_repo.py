"""User repository for database operations."""

from dataclasses import dataclass
from typing import Optional
from ..connection import Database


@dataclass
class User:
    id: int
    telegram_id: int
    display_name: str


class UserRepository:
    """Repository for user table operations."""

    def __init__(self, db: Database):
        self.db = db

    def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Find user by Telegram ID."""
        cursor = self.db.execute(
            "SELECT id, telegram_id, display_name FROM users WHERE telegram_id = ?",
            (telegram_id,),
        )
        row = cursor.fetchone()
        if row:
            return User(id=row["id"], telegram_id=row["telegram_id"], display_name=row["display_name"])
        return None

    def create(self, telegram_id: int, display_name: str) -> User:
        """Create new user."""
        cursor = self.db.execute(
            "INSERT INTO users (telegram_id, display_name) VALUES (?, ?)",
            (telegram_id, display_name),
        )
        self.db.commit()
        return User(id=cursor.lastrowid, telegram_id=telegram_id, display_name=display_name)

    def get_or_create(self, telegram_id: int, display_name: str) -> User:
        """Get existing user or create new one."""
        user = self.get_by_telegram_id(telegram_id)
        if user:
            return user
        return self.create(telegram_id, display_name)

    def get_all(self) -> list[User]:
        """Get all users."""
        cursor = self.db.execute("SELECT id, telegram_id, display_name FROM users")
        return [
            User(id=row["id"], telegram_id=row["telegram_id"], display_name=row["display_name"])
            for row in cursor.fetchall()
        ]
