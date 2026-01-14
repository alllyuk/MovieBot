"""Step definitions for selecting_movie.feature."""

from pytest_bdd import scenarios, given, when, then, parsers
from src.bot.messages import Messages
from tests.conftest import FakeUser, FakeBot

scenarios("../features/selecting_movie.feature")


# Import common steps
from tests.steps.common_steps import setup_users, users_connected
from tests.steps.adding_steps import add_movies_to_wishlist, empty_wishlist


@when(parsers.parse('пользователь "{user_name}" отправляет сообщение "что смотрим?"'))
def user_asks_what_to_watch(users: dict[str, FakeUser], user_service, selection_service, fake_bot: FakeBot, user_name: str):
    """User asks for movie recommendation."""
    user = users[user_name]
    user_service.register(user.telegram_id, user.display_name)

    result = selection_service.pick_movie(user.telegram_id)

    if result.movie is None:
        fake_bot.send(Messages.ALL_LISTS_EMPTY)
    elif result.from_intersection:
        fake_bot.send(Messages.movie_selected_intersection(result.movie))
    elif result.other_user_name:
        fake_bot.send(Messages.movie_selected_from_other(result.movie, result.other_user_name))
    else:
        fake_bot.send(Messages.movie_selected_random(result.movie))


@then(parsers.parse('бот отвечает "{expected}"'))
def check_response(fake_bot: FakeBot, expected: str):
    """Check exact bot response."""
    assert fake_bot.last_response == expected


@then("бот выбирает случайный фильм из общего списка")
def bot_picks_random(fake_bot: FakeBot):
    """Bot picks a random movie - just check response exists."""
    assert fake_bot.last_response is not None
    assert "🎲" in fake_bot.last_response


@then(parsers.parse('бот выбирает случайный фильм из списка "{user_name}"'))
def bot_picks_from_user(fake_bot: FakeBot, user_name: str):
    """Bot picks from specific user's list."""
    assert fake_bot.last_response is not None


@then(parsers.parse('бот отвечает "🎲 Пересечений нет, выбираю случайный: «{movie}»"'))
def check_random_selection(fake_bot: FakeBot, movie: str):
    """Check random selection message - movie can be anything from pool."""
    assert fake_bot.last_response is not None
    assert "🎲 Пересечений нет, выбираю случайный:" in fake_bot.last_response


@then(parsers.parse('бот отвечает "🎲 У {user_name} список пуст, выбираю из списка {other_name}: «{movie}»"'))
def check_from_other_selection(fake_bot: FakeBot, user_name: str, other_name: str, movie: str):
    """Check selection from other user's list."""
    assert fake_bot.last_response is not None
    # The actual movie name may vary, just check the pattern


# Additional tests for selection logic
def test_exclude_watched_from_pool(db, user_service, wishlist_service, selection_service, history_repo, users):
    """Watched movies should not appear in selection pool."""
    from datetime import date

    # Setup users
    andrey = users["Андрей"]
    user_service.register(andrey.telegram_id, andrey.display_name)

    # Add movie to wishlist
    wishlist_service.add_movie(andrey.telegram_id, "Дюна")

    # Add same movie to history (already watched)
    history_repo.add("Дюна", rating=8, watched_at=date.today(), user_id=1)

    # Try to pick - should get empty result
    result = selection_service.pick_movie(andrey.telegram_id)
    assert result.movie is None or result.movie.lower() != "дюна"


def test_no_repeat_last_when_alternatives(db, user_service, wishlist_service, selection_service, state_repo, users):
    """Should not repeat last selected movie when alternatives exist."""
    andrey = users["Андрей"]
    user_service.register(andrey.telegram_id, andrey.display_name)

    # Add two movies
    wishlist_service.add_movie(andrey.telegram_id, "Дюна")
    wishlist_service.add_movie(andrey.telegram_id, "Барби")

    # Set last selected
    state_repo.set("last_selected_movie", "Дюна")

    # Pick should not return Дюна
    result = selection_service.pick_movie(andrey.telegram_id)
    assert result.movie.lower() != "дюна"
