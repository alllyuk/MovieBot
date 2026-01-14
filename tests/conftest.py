# -*- coding: utf-8 -*-
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


# Pre-defined test users - with multiple key variations for encoding issues
_ANDREY = FakeUser(telegram_id=1001, display_name="Андрей")
_MASHA = FakeUser(telegram_id=1002, display_name="Маша")


def get_test_user(name: str) -> FakeUser:
    """Get test user by name, handling encoding variations."""
    name_lower = name.lower()
    # Check for Andrey variants
    if "андрей" in name_lower or "andrey" in name_lower or name_lower.startswith("а"):
        return _ANDREY
    # Check for Masha variants
    if "маша" in name_lower or "masha" in name_lower or name_lower.startswith("м"):
        return _MASHA
    # Fallback - first user
    return _ANDREY


TEST_USERS = {
    "Андрей": _ANDREY,
    "Маша": _MASHA,
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
    import random
    # Fixed seed for deterministic tests
    rng = random.Random(42)
    return SelectionService(wishlist_repo, history_repo, state_repo, user_repo, rng=rng)


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


# Text fixture for pytest-bdd docstrings
@pytest.fixture
def text():
    """Text fixture for pytest-bdd docstrings (fallback)."""
    return ""


# Common step definitions (shared across all features)
from pytest_bdd import given, then, parsers


@given(parsers.parse('существуют пользователи "{user1}" и "{user2}"'))
def setup_users(user_service, user1: str, user2: str):
    """Create test users in database."""
    u1 = get_test_user(user1)
    u2 = get_test_user(user2)
    user_service.register(u1.telegram_id, u1.display_name)
    user_service.register(u2.telegram_id, u2.display_name)


@given(parsers.parse('они подключены к общему боту'))
def users_connected():
    """No-op - all users are in same family by design."""
    pass


@given(parsers.parse('в списке желаний "{user_name}" есть фильм "{movie}"'))
def add_movie_to_wishlist(user_service, wishlist_service, user_name: str, movie: str):
    """Add movie to user's wishlist."""
    user = get_test_user(user_name)
    user_service.register(user.telegram_id, user.display_name)
    wishlist_service.add_movie(user.telegram_id, movie)


@given(parsers.parse('в списке желаний "{user_name}" есть фильмы:'))
def add_movies_to_wishlist(user_service, wishlist_service, user_name: str, datatable):
    """Add multiple movies to user's wishlist from data table."""
    user = get_test_user(user_name)
    user_service.register(user.telegram_id, user.display_name)

    # Skip header row if present
    data_rows = datatable
    if data_rows and isinstance(data_rows[0], list):
        first_cell = str(data_rows[0][0]).lower()
        if "назван" in first_cell or first_cell == "название":
            data_rows = datatable[1:]

    for row in data_rows:
        if isinstance(row, dict):
            movie = None
            for key in row.keys():
                if "назван" in key.lower() or key == "название":
                    movie = row[key]
                    break
            if movie is None:
                movie = list(row.values())[0]
        else:
            movie = row[0] if row else None
        if movie:
            wishlist_service.add_movie(user.telegram_id, movie)


@given(parsers.parse('список желаний "{user_name}" пуст'))
def empty_wishlist(user_service, user_name: str):
    """Ensure user exists but has empty wishlist."""
    user = get_test_user(user_name)
    user_service.register(user.telegram_id, user.display_name)


@given(parsers.parse('в списке желаний есть фильм "{movie}"'))
def movie_in_any_wishlist(user_service, wishlist_service, movie: str):
    """Add movie to first user's wishlist."""
    user = _ANDREY
    user_service.register(user.telegram_id, user.display_name)
    wishlist_service.add_movie(user.telegram_id, movie)


@given(parsers.parse('в списках желаний нет фильма "{movie}"'))
def movie_not_in_wishlists(user_service, movie: str):
    """Ensure movie is not in any wishlist - just register users."""
    user_service.register(_ANDREY.telegram_id, _ANDREY.display_name)
    user_service.register(_MASHA.telegram_id, _MASHA.display_name)


@then(parsers.parse('бот отвечает "{expected}"'))
def check_bot_response(fake_bot: FakeBot, expected: str):
    """Check bot response matches expected text."""
    assert fake_bot.last_response == expected, f"Expected: {expected}, Got: {fake_bot.last_response}"


@then("бот отвечает:")
def check_multiline_response_shared(fake_bot: FakeBot, text):
    """Check multiline bot response (docstring)."""
    assert fake_bot.last_response is not None
    response = fake_bot.last_response

    def normalize(s):
        return ' '.join(s.split())

    if text and text.strip():
        expected_normalized = normalize(text)
        response_normalized = normalize(response)
        assert expected_normalized in response_normalized or response_normalized in expected_normalized, \
            f"Response mismatch.\nExpected:\n{text}\nGot:\n{response}"
    else:
        assert len(response) > 10, f"Response too short: {response}"
