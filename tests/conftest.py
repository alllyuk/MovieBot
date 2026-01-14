"""Pytest configuration and fixtures for BDD tests."""

import pytest
from dataclasses import dataclass, field
from pathlib import Path

from src.database import Database, run_migrations
from src.database.repositories import (
    UserRepository,
    WishlistRepository,
    HistoryRepository,
    StateRepository,
)
from src.services import (
    UserService,
    WishlistService,
    SelectionService,
    WatchService,
    HistoryService,
)


@dataclass
class FakeUser:
    """Test user data."""
    telegram_id: int
    display_name: str


@dataclass
class FakeBot:
    """Captures bot responses for assertions."""
    messages: list[str] = field(default_factory=list)
    keyboards: list[list] = field(default_factory=list)

    def send(self, text: str, keyboard: list = None):
        self.messages.append(text)
        if keyboard:
            self.keyboards.append(keyboard)

    @property
    def last_response(self) -> str | None:
        return self.messages[-1] if self.messages else None

    def clear(self):
        self.messages.clear()
        self.keyboards.clear()


# Pre-defined test users
TEST_USERS = {
    "Андрей": FakeUser(telegram_id=1001, display_name="Андрей"),
    "Маша": FakeUser(telegram_id=1002, display_name="Маша"),
}


@pytest.fixture
def db(tmp_path: Path):
    """Fresh database for each test using temp file."""
    db_path = tmp_path / "test_moviebot.db"
    database = Database(str(db_path))
    run_migrations(database)
    yield database
    database.close()


@pytest.fixture
def user_repo(db: Database) -> UserRepository:
    return UserRepository(db)


@pytest.fixture
def wishlist_repo(db: Database) -> WishlistRepository:
    return WishlistRepository(db)


@pytest.fixture
def history_repo(db: Database) -> HistoryRepository:
    return HistoryRepository(db)


@pytest.fixture
def state_repo(db: Database) -> StateRepository:
    return StateRepository(db)


@pytest.fixture
def user_service(user_repo: UserRepository) -> UserService:
    return UserService(user_repo)


@pytest.fixture
def wishlist_service(
    wishlist_repo: WishlistRepository,
    user_repo: UserRepository,
) -> WishlistService:
    return WishlistService(wishlist_repo, user_repo)


@pytest.fixture
def selection_service(
    wishlist_repo: WishlistRepository,
    history_repo: HistoryRepository,
    state_repo: StateRepository,
    user_repo: UserRepository,
) -> SelectionService:
    return SelectionService(wishlist_repo, history_repo, state_repo, user_repo)


@pytest.fixture
def watch_service(
    user_repo: UserRepository,
    wishlist_repo: WishlistRepository,
    history_repo: HistoryRepository,
) -> WatchService:
    return WatchService(user_repo, wishlist_repo, history_repo)


@pytest.fixture
def history_service(history_repo: HistoryRepository) -> HistoryService:
    return HistoryService(history_repo)


@pytest.fixture
def fake_bot() -> FakeBot:
    return FakeBot()


@pytest.fixture
def users() -> dict[str, FakeUser]:
    return TEST_USERS.copy()
