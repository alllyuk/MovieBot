"""Wishlist service for movie list management."""

from dataclasses import dataclass
from src.database.repositories import UserRepository, WishlistRepository


@dataclass
class AddMovieResult:
    movie_title: str
    already_exists: bool


@dataclass
class DeleteMovieResult:
    movie_title: str
    deleted: bool


class WishlistService:
    """Business logic for wishlist operations."""

    def __init__(self, wishlist_repo: WishlistRepository, user_repo: UserRepository):
        self.wishlist_repo = wishlist_repo
        self.user_repo = user_repo

    def add_movie(self, telegram_id: int, movie_title: str) -> AddMovieResult:
        """Add movie to user's wishlist."""
        user = self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError(f"User with telegram_id {telegram_id} not found")

        existing = self.wishlist_repo.find_by_title(user.id, movie_title)
        if existing:
            return AddMovieResult(movie_title=existing.movie_title, already_exists=True)

        item = self.wishlist_repo.add(user.id, movie_title)
        return AddMovieResult(movie_title=item.movie_title, already_exists=False)

    def get_user_wishlist(self, telegram_id: int) -> list[str]:
        """Get user's wishlist as list of movie titles."""
        user = self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return []

        items = self.wishlist_repo.get_user_wishlist(user.id)
        return [item.movie_title for item in items]

    def delete_movie(self, telegram_id: int, movie_title: str) -> DeleteMovieResult:
        """Remove movie from user's wishlist."""
        user = self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return DeleteMovieResult(movie_title=movie_title, deleted=False)

        # Find the original title (preserving case)
        existing = self.wishlist_repo.find_by_title(user.id, movie_title)
        original_title = existing.movie_title if existing else movie_title

        deleted = self.wishlist_repo.delete(user.id, movie_title)
        return DeleteMovieResult(movie_title=original_title, deleted=deleted)

    def get_intersection(self) -> list[str]:
        """Get movies that all users want (intersection of all wishlists)."""
        movies_by_user = self.wishlist_repo.get_movies_by_user()

        if not movies_by_user:
            return []

        # Get sets of lowercase titles for each user
        user_sets = [
            {title.lower() for title in titles}
            for titles in movies_by_user.values()
        ]

        # Find intersection
        if len(user_sets) == 1:
            # Only one user - return their list
            return list(movies_by_user.values())[0]

        intersection_lower = user_sets[0]
        for s in user_sets[1:]:
            intersection_lower &= s

        if not intersection_lower:
            return []

        # Return original titles (with original case)
        all_movies = self.wishlist_repo.get_all_movies()
        return [m for m in all_movies if m.lower() in intersection_lower]

    def get_all_movies(self) -> list[str]:
        """Get all movies from all wishlists."""
        return self.wishlist_repo.get_all_movies()
