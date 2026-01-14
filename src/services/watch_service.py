"""Watch service for marking movies as watched."""

from dataclasses import dataclass
from datetime import date
from typing import Optional
from src.database.repositories import (
    UserRepository,
    WishlistRepository,
    HistoryRepository,
)


@dataclass
class WatchResult:
    movie_title: str
    rating: Optional[int]
    needs_rating: bool  # True if rating was not provided


class WatchService:
    """Business logic for watch operations."""

    def __init__(
        self,
        user_repo: UserRepository,
        wishlist_repo: WishlistRepository,
        history_repo: HistoryRepository,
    ):
        self.user_repo = user_repo
        self.wishlist_repo = wishlist_repo
        self.history_repo = history_repo

    def mark_watched(
        self,
        telegram_id: int,
        movie_title: str,
        rating: Optional[int] = None,
    ) -> WatchResult:
        """Mark movie as watched with optional rating."""
        user = self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError(f"User with telegram_id {telegram_id} not found")

        # Find original title from wishlist (case-insensitive)
        original_title = self._find_original_title(movie_title)

        if rating is None:
            return WatchResult(movie_title=original_title, rating=None, needs_rating=True)

        # Validate rating
        if not (1 <= rating <= 10):
            raise ValueError("Rating must be between 1 and 10")

        # Add to history
        self.history_repo.add(
            movie_title=original_title,
            rating=rating,
            watched_at=date.today(),
            user_id=user.id,
        )

        # Remove from all wishlists
        self.wishlist_repo.delete_from_all(original_title)

        return WatchResult(movie_title=original_title, rating=rating, needs_rating=False)

    def _find_original_title(self, movie_title: str) -> str:
        """Find original title with correct case from wishlists."""
        all_movies = self.wishlist_repo.get_all_movies()
        for m in all_movies:
            if m.lower() == movie_title.lower():
                return m
        return movie_title  # Return as-is if not found
