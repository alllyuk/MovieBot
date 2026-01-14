"""Wishlist repository for database operations."""

from dataclasses import dataclass
from typing import Optional
from ..connection import Database


@dataclass
class WishlistItem:
    id: int
    user_id: int
    movie_title: str


class WishlistRepository:
    """Repository for wishlist table operations."""

    def __init__(self, db: Database):
        self.db = db

    def add(self, user_id: int, movie_title: str) -> WishlistItem:
        """Add movie to user's wishlist."""
        cursor = self.db.execute(
            "INSERT INTO wishlist (user_id, movie_title, movie_title_lower) VALUES (?, ?, ?)",
            (user_id, movie_title, movie_title.lower()),
        )
        self.db.commit()
        return WishlistItem(id=cursor.lastrowid, user_id=user_id, movie_title=movie_title)

    def find_by_title(self, user_id: int, movie_title: str) -> Optional[WishlistItem]:
        """Find movie in user's wishlist (case-insensitive)."""
        cursor = self.db.execute(
            "SELECT id, user_id, movie_title FROM wishlist WHERE user_id = ? AND movie_title_lower = ?",
            (user_id, movie_title.lower()),
        )
        row = cursor.fetchone()
        if row:
            return WishlistItem(id=row["id"], user_id=row["user_id"], movie_title=row["movie_title"])
        return None

    def get_user_wishlist(self, user_id: int) -> list[WishlistItem]:
        """Get all movies in user's wishlist."""
        cursor = self.db.execute(
            "SELECT id, user_id, movie_title FROM wishlist WHERE user_id = ? ORDER BY added_at",
            (user_id,),
        )
        return [
            WishlistItem(id=row["id"], user_id=row["user_id"], movie_title=row["movie_title"])
            for row in cursor.fetchall()
        ]

    def delete(self, user_id: int, movie_title: str) -> bool:
        """Remove movie from user's wishlist. Returns True if deleted."""
        cursor = self.db.execute(
            "DELETE FROM wishlist WHERE user_id = ? AND movie_title_lower = ?",
            (user_id, movie_title.lower()),
        )
        self.db.commit()
        return cursor.rowcount > 0

    def delete_from_all(self, movie_title: str) -> int:
        """Remove movie from all wishlists. Returns count of deleted items."""
        cursor = self.db.execute(
            "DELETE FROM wishlist WHERE movie_title_lower = ?",
            (movie_title.lower(),),
        )
        self.db.commit()
        return cursor.rowcount

    def get_all_movies(self) -> list[str]:
        """Get all unique movie titles from all wishlists."""
        cursor = self.db.execute(
            "SELECT DISTINCT movie_title FROM wishlist ORDER BY movie_title"
        )
        return [row["movie_title"] for row in cursor.fetchall()]

    def get_movies_by_user(self) -> dict[int, list[str]]:
        """Get movies grouped by user_id."""
        cursor = self.db.execute(
            "SELECT user_id, movie_title FROM wishlist ORDER BY user_id, added_at"
        )
        result: dict[int, list[str]] = {}
        for row in cursor.fetchall():
            user_id = row["user_id"]
            if user_id not in result:
                result[user_id] = []
            result[user_id].append(row["movie_title"])
        return result
