"""Common step definitions shared across features."""

from pytest_bdd import given, parsers
from tests.conftest import FakeUser


@given(parsers.parse('существуют пользователи "{user1}" и "{user2}"'))
def setup_users(users: dict[str, FakeUser], user_service, user1: str, user2: str):
    """Create test users in database."""
    user_service.register(users[user1].telegram_id, users[user1].display_name)
    user_service.register(users[user2].telegram_id, users[user2].display_name)


@given(parsers.parse('они подключены к общему боту'))
def users_connected():
    """No-op - all users are in same family by design."""
    pass
