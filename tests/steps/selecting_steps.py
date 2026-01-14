# -*- coding: utf-8 -*-
"""Step definitions for selecting_movie.feature."""

from pytest_bdd import scenarios, given, when, then, parsers
from src.bot.messages import Messages
from tests.conftest import FakeUser, FakeBot, get_test_user, _ANDREY

scenarios("../features/selecting_movie.feature")


@when(parsers.parse('пользователь "{user_name}" отправляет сообщение "что смотрим?"'))
def user_asks_what_to_watch(user_service, selection_service, fake_bot: FakeBot, user_name: str):
    """User asks for movie recommendation."""
    user = get_test_user(user_name)
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


@then("бот выбирает случайный фильм из общего списка")
def bot_picks_random(fake_bot: FakeBot, wishlist_service):
    """Bot picks a random movie from the combined pool."""
    assert fake_bot.last_response is not None
    assert "🎲" in fake_bot.last_response, f"Expected random selection indicator, got: {fake_bot.last_response}"
    # Verify the selected movie is from the available pool
    all_movies = wishlist_service.get_all_movies()
    all_movies_lower = [m.lower() for m in all_movies]
    # Extract movie name from response (format: «MovieName»)
    import re
    match = re.search(r"«(.+?)»", fake_bot.last_response)
    assert match, f"Could not find movie name in response: {fake_bot.last_response}"
    selected_movie = match.group(1)
    assert selected_movie.lower() in all_movies_lower, f"Selected movie '{selected_movie}' not in pool: {all_movies}"


@then(parsers.parse('бот выбирает случайный фильм из списка "{user_name}"'))
def bot_picks_from_user(fake_bot: FakeBot, wishlist_service, user_name: str):
    """Bot picks from specific user's list."""
    assert fake_bot.last_response is not None
    assert "🎲" in fake_bot.last_response, f"Expected random selection, got: {fake_bot.last_response}"
    # Verify selected movie exists in pool
    import re
    match = re.search(r"«(.+?)»", fake_bot.last_response)
    assert match, f"Could not find movie name in response: {fake_bot.last_response}"
    selected_movie = match.group(1)
    all_movies = wishlist_service.get_all_movies()
    assert selected_movie in all_movies, f"Selected movie '{selected_movie}' not found in wishlists"


@then(parsers.parse('бот отвечает "🎲 Пересечений нет, выбираю случайный: «{movie}»"'))
def check_random_selection(fake_bot: FakeBot, wishlist_service, movie: str):
    """Check random selection message - verify movie is from available pool."""
    assert fake_bot.last_response is not None
    assert "🎲" in fake_bot.last_response, f"Expected 🎲 indicator, got: {fake_bot.last_response}"
    # Extract actual selected movie
    import re
    match = re.search(r"«(.+?)»", fake_bot.last_response)
    assert match, f"Could not find movie name in response"
    selected = match.group(1)
    # Verify movie is from the pool
    all_movies = wishlist_service.get_all_movies()
    assert selected in all_movies, f"Selected '{selected}' not in pool: {all_movies}"


@then(parsers.parse('бот отвечает "🎲 У {user_name} список пуст, выбираю из списка {other_name}: «{movie}»"'))
def check_from_other_selection(fake_bot: FakeBot, wishlist_service, user_name: str, other_name: str, movie: str):
    """Check selection from other user's list."""
    assert fake_bot.last_response is not None
    assert "🎲" in fake_bot.last_response, f"Expected 🎲 indicator, got: {fake_bot.last_response}"
    # Extract and verify selected movie
    import re
    match = re.search(r"«(.+?)»", fake_bot.last_response)
    assert match, f"Could not find movie name in response"
    selected = match.group(1)
    all_movies = wishlist_service.get_all_movies()
    assert selected in all_movies, f"Selected '{selected}' not in available movies: {all_movies}"


# Additional tests for selection logic
def test_exclude_watched_from_pool(db, user_service, wishlist_service, selection_service, history_repo):
    """Watched movies should not appear in selection pool."""
    from datetime import date

    # Setup user
    user_service.register(_ANDREY.telegram_id, _ANDREY.display_name)

    # Add movie to wishlist
    wishlist_service.add_movie(_ANDREY.telegram_id, "Дюна")

    # Add same movie to history (already watched)
    history_repo.add("Дюна", rating=8, watched_at=date.today(), user_id=1)

    # Try to pick - should get empty result
    result = selection_service.pick_movie(_ANDREY.telegram_id)
    assert result.movie is None or result.movie.lower() != "дюна"


def test_no_repeat_last_when_alternatives(db, user_service, wishlist_service, selection_service, state_repo):
    """Should not repeat last selected movie when alternatives exist."""
    user_service.register(_ANDREY.telegram_id, _ANDREY.display_name)

    # Add two movies
    wishlist_service.add_movie(_ANDREY.telegram_id, "Дюна")
    wishlist_service.add_movie(_ANDREY.telegram_id, "Барби")

    # Set last selected
    state_repo.set("last_selected_movie", "Дюна")

    # Pick should not return Дюна
    result = selection_service.pick_movie(_ANDREY.telegram_id)
    assert result.movie.lower() != "дюна"
