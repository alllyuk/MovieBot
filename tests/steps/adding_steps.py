# -*- coding: utf-8 -*-
"""Step definitions for adding_movies.feature."""

from pytest_bdd import scenarios, when, then, parsers
from src.bot.messages import Messages
from tests.conftest import FakeUser, FakeBot, get_test_user

scenarios("../features/adding_movies.feature")


@when(parsers.parse('пользователь "{user_name}" отправляет сообщение "{message}"'))
def user_sends_message(user_service, wishlist_service, fake_bot: FakeBot, user_name: str, message: str):
    """User sends a message to the bot."""
    user = get_test_user(user_name)
    user_service.register(user.telegram_id, user.display_name)

    if message.startswith("хочу посмотреть"):
        movie_name = message[len("хочу посмотреть"):].strip()
        if not movie_name:
            fake_bot.send(Messages.EMPTY_MOVIE_NAME)
        else:
            result = wishlist_service.add_movie(user.telegram_id, movie_name)
            if result.already_exists:
                fake_bot.send(Messages.movie_already_exists(result.movie_title))
            else:
                fake_bot.send(Messages.movie_added(result.movie_title))

    elif message == "мой список":
        movies = wishlist_service.get_user_wishlist(user.telegram_id)
        fake_bot.send(Messages.format_my_list(movies))

    elif message == "наш список":
        movies = wishlist_service.get_intersection()
        fake_bot.send(Messages.format_our_list(movies))

    elif message.startswith("удали"):
        movie_name = message[len("удали"):].strip()
        result = wishlist_service.delete_movie(user.telegram_id, movie_name)
        if result.deleted:
            fake_bot.send(Messages.movie_deleted(result.movie_title))


@then(parsers.parse('бот отвечает "{expected}"'))
def check_bot_response(fake_bot: FakeBot, expected: str):
    """Check bot response matches expected text."""
    assert fake_bot.last_response == expected, f"Expected: {expected}, Got: {fake_bot.last_response}"


@then(parsers.parse('фильм "{movie}" появляется в списке желаний "{user_name}"'))
def movie_in_wishlist(wishlist_service, movie: str, user_name: str):
    """Check movie is in user's wishlist."""
    user = get_test_user(user_name)
    movies = wishlist_service.get_user_wishlist(user.telegram_id)
    movie_titles_lower = [m.lower() for m in movies]
    assert movie.lower() in movie_titles_lower, f"Movie '{movie}' not found in wishlist: {movies}"


@then(parsers.parse('фильм "{movie}" отсутствует в списке желаний "{user_name}"'))
def movie_not_in_wishlist(wishlist_service, movie: str, user_name: str):
    """Check movie is NOT in user's wishlist."""
    user = get_test_user(user_name)
    movies = wishlist_service.get_user_wishlist(user.telegram_id)
    movie_titles_lower = [m.lower() for m in movies]
    assert movie.lower() not in movie_titles_lower, f"Movie '{movie}' should not be in wishlist: {movies}"
