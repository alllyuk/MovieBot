"""User service for user management."""

from dataclasses import dataclass
from src.database.repositories import UserRepository, User


@dataclass
class RegisterResult:
    user: User
    is_new: bool


class UserService:
    """Business logic for user operations."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register(self, telegram_id: int, display_name: str) -> RegisterResult:
        """Register user or get existing one."""
        existing = self.user_repo.get_by_telegram_id(telegram_id)
        if existing:
            return RegisterResult(user=existing, is_new=False)

        user = self.user_repo.create(telegram_id, display_name)
        return RegisterResult(user=user, is_new=True)

    def get_user(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID."""
        return self.user_repo.get_by_telegram_id(telegram_id)

    def get_all_users(self) -> list[User]:
        """Get all registered users."""
        return self.user_repo.get_all()
