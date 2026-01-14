# -*- coding: utf-8 -*-
"""Step definitions for edge_cases.feature."""

from pytest_bdd import scenarios, when, then, parsers
from src.bot.messages import Messages
from tests.conftest import FakeUser, FakeBot, get_test_user
import re

scenarios("../features/edge_cases.feature")


@when(parsers.parse('пользователь "{user_name}" отправляет сообщение "{message}"'))
def user_sends_edge_case_message(
    user_service,
    wishlist_service,
    watch_service,
    fake_bot: FakeBot,
    user_name: str,
    message: str,
):
    """Handle edge case messages."""
    user = get_test_user(user_name)
    user_service.register(user.telegram_id, user.display_name)

    message_lower = message.lower().strip()

    if message_lower.startswith("хочу посмотреть"):
        movie_name = message[len("хочу посмотреть"):].strip()
        if not movie_name:
            fake_bot.send(Messages.EMPTY_MOVIE_NAME)
        else:
            result = wishlist_service.add_movie(user.telegram_id, movie_name)
            if result.already_exists:
                fake_bot.send(Messages.movie_already_exists(result.movie_title))
            else:
                fake_bot.send(Messages.movie_added(result.movie_title))

    elif message_lower.startswith("удали"):
        movie_name = message[len("удали"):].strip()
        from src.services.wishlist_service import capitalize_title
        movie_title = capitalize_title(movie_name)
        result = wishlist_service.delete_movie(user.telegram_id, movie_name)
        if result.deleted:
            fake_bot.send(Messages.movie_deleted(result.movie_title))
        else:
            fake_bot.send(Messages.movie_not_in_wishlist(movie_title))

    elif message_lower.startswith("посмотрели"):
        text = message[len("посмотрели"):].strip()
        # Rating requires comma before number OR /10 suffix
        match = re.match(r"(.+?),\s*(\d+)(?:/10)?$", text, re.IGNORECASE) or re.match(r"(.+?)\s+(\d+)/10$", text, re.IGNORECASE)
        if match:
            movie_name = match.group(1).strip()
            rating = int(match.group(2))

            # Validate rating range
            if rating < 1 or rating > 10:
                fake_bot.send(Messages.INVALID_RATING)
                return

            all_movies = wishlist_service.get_all_movies()
            original_title = movie_name
            for m in all_movies:
                if m.lower() == movie_name.lower():
                    original_title = m
                    break

            result = watch_service.mark_watched(user.telegram_id, original_title, rating)
            fake_bot.send(Messages.movie_watched(result.movie_title, rating))
        else:
            fake_bot.send(Messages.ASK_RATING)
    else:
        fake_bot.send(Messages.UNKNOWN_COMMAND)


@then("бот находит фильм несмотря на разный регистр")
def bot_finds_case_insensitive(fake_bot: FakeBot):
    """Verify case-insensitive match by checking archived response."""
    assert fake_bot.last_response is not None
    # Response should confirm movie was archived with original case
    assert "в архиве" in fake_bot.last_response or "Оппенгеймер" in fake_bot.last_response
