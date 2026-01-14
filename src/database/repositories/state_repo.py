"""Bot state repository for key-value storage."""

from typing import Optional
from ..connection import Database


class StateRepository:
    """Repository for bot_state table operations."""

    def __init__(self, db: Database):
        self.db = db

    def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        cursor = self.db.execute(
            "SELECT value FROM bot_state WHERE key = ?",
            (key,),
        )
        row = cursor.fetchone()
        return row["value"] if row else None

    def set(self, key: str, value: str) -> None:
        """Set value for key (insert or update)."""
        self.db.execute(
            "INSERT OR REPLACE INTO bot_state (key, value) VALUES (?, ?)",
            (key, value),
        )
        self.db.commit()

    def delete(self, key: str) -> bool:
        """Delete key. Returns True if key existed."""
        cursor = self.db.execute(
            "DELETE FROM bot_state WHERE key = ?",
            (key,),
        )
        self.db.commit()
        return cursor.rowcount > 0
