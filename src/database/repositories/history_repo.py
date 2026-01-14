"""Watch history repository for database operations."""

from dataclasses import dataclass
from datetime import date
from typing import Optional
from ..connection import Database


@dataclass
class HistoryItem:
    id: int
    movie_title: str
    rating: int
    watched_at: date


class HistoryRepository:
    """Repository for watch_history table operations."""

    def __init__(self, db: Database):
        self.db = db

    def add(self, movie_title: str, rating: int, watched_at: date, user_id: int) -> HistoryItem:
        """Add movie to watch history."""
        cursor = self.db.execute(
            """INSERT INTO watch_history
               (movie_title, movie_title_lower, rating, watched_at, marked_by_user_id)
               VALUES (?, ?, ?, ?, ?)""",
            (movie_title, movie_title.lower(), rating, watched_at.isoformat(), user_id),
        )
        self.db.commit()
        return HistoryItem(
            id=cursor.lastrowid,
            movie_title=movie_title,
            rating=rating,
            watched_at=watched_at,
        )

    def get_all(self) -> list[HistoryItem]:
        """Get all watch history ordered by date descending."""
        cursor = self.db.execute(
            "SELECT id, movie_title, rating, watched_at FROM watch_history ORDER BY watched_at DESC"
        )
        return [
            HistoryItem(
                id=row["id"],
                movie_title=row["movie_title"],
                rating=row["rating"],
                watched_at=date.fromisoformat(row["watched_at"]),
            )
            for row in cursor.fetchall()
        ]

    def get_watched_titles_lower(self) -> set[str]:
        """Get set of all watched movie titles (lowercase) for filtering."""
        cursor = self.db.execute("SELECT DISTINCT movie_title_lower FROM watch_history")
        return {row["movie_title_lower"] for row in cursor.fetchall()}

    def find_by_title(self, movie_title: str) -> Optional[HistoryItem]:
        """Find movie in history by title (case-insensitive)."""
        cursor = self.db.execute(
            "SELECT id, movie_title, rating, watched_at FROM watch_history WHERE movie_title_lower = ?",
            (movie_title.lower(),),
        )
        row = cursor.fetchone()
        if row:
            return HistoryItem(
                id=row["id"],
                movie_title=row["movie_title"],
                rating=row["rating"],
                watched_at=date.fromisoformat(row["watched_at"]),
            )
        return None

    def is_empty(self) -> bool:
        """Check if history is empty."""
        cursor = self.db.execute("SELECT COUNT(*) as cnt FROM watch_history")
        return cursor.fetchone()["cnt"] == 0
