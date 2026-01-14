"""Selection service for movie picking logic."""

import random
from dataclasses import dataclass
from typing import Optional
from src.database.repositories import (
    WishlistRepository,
    HistoryRepository,
    StateRepository,
    UserRepository,
)


@dataclass
class SelectionResult:
    movie: Optional[str]
    from_intersection: bool
    empty_reason: Optional[str] = None  # "all_empty", "user_empty", etc.
    other_user_name: Optional[str] = None  # For "picking from X's list" message


class SelectionService:
    """Business logic for movie selection."""

    LAST_SELECTED_KEY = "last_selected_movie"

    def __init__(
        self,
        wishlist_repo: WishlistRepository,
        history_repo: HistoryRepository,
        state_repo: StateRepository,
        user_repo: UserRepository,
    ):
        self.wishlist_repo = wishlist_repo
        self.history_repo = history_repo
        self.state_repo = state_repo
        self.user_repo = user_repo

    def pick_movie(self, telegram_id: int) -> SelectionResult:
        """Pick a movie for the evening."""
        # 1. Get all movies from all wishlists
        all_movies = self.wishlist_repo.get_all_movies()

        if not all_movies:
            return SelectionResult(movie=None, from_intersection=False, empty_reason="all_empty")

        # 2. Filter out watched movies
        watched = self.history_repo.get_watched_titles_lower()
        pool = [m for m in all_movies if m.lower() not in watched]

        if not pool:
            return SelectionResult(movie=None, from_intersection=False, empty_reason="all_watched")

        # 3. Try intersection first
        intersection = self._get_intersection(pool)
        from_intersection = bool(intersection)

        if intersection:
            pool = intersection
        # else: use full filtered list (fallback)

        # 4. Check for empty user list scenario
        empty_user_info = self._check_empty_user(telegram_id)

        # 5. Exclude last selected (if alternatives exist)
        last = self.state_repo.get(self.LAST_SELECTED_KEY)
        if last and len(pool) > 1:
            pool = [m for m in pool if m.lower() != last.lower()]

        # 6. Random pick
        selected = random.choice(pool)

        # 7. Save as last selected
        self.state_repo.set(self.LAST_SELECTED_KEY, selected)

        return SelectionResult(
            movie=selected,
            from_intersection=from_intersection,
            other_user_name=empty_user_info,
        )

    def _get_intersection(self, available_movies: list[str]) -> list[str]:
        """Get movies that all users want from available pool."""
        movies_by_user = self.wishlist_repo.get_movies_by_user()

        if len(movies_by_user) < 2:
            return []  # Need at least 2 users for intersection

        # Filter to only available movies
        available_lower = {m.lower() for m in available_movies}

        user_sets = [
            {title.lower() for title in titles if title.lower() in available_lower}
            for titles in movies_by_user.values()
        ]

        # Remove empty sets (users with no available movies)
        user_sets = [s for s in user_sets if s]

        if len(user_sets) < 2:
            return []

        intersection_lower = user_sets[0]
        for s in user_sets[1:]:
            intersection_lower &= s

        if not intersection_lower:
            return []

        return [m for m in available_movies if m.lower() in intersection_lower]

    def _check_empty_user(self, current_telegram_id: int) -> Optional[str]:
        """Check if current user has empty list, return other user's name."""
        current_user = self.user_repo.get_by_telegram_id(current_telegram_id)
        if not current_user:
            return None

        movies_by_user = self.wishlist_repo.get_movies_by_user()

        # Check if current user has movies
        current_has_movies = current_user.id in movies_by_user

        if current_has_movies:
            return None

        # Find other user with movies
        all_users = self.user_repo.get_all()
        for user in all_users:
            if user.id != current_user.id and user.id in movies_by_user:
                return user.display_name

        return None
