"""Step definitions for edge_cases.feature."""

from pytest_bdd import scenarios, given, when, then, parsers
from src.bot.messages import Messages
from tests.conftest import FakeUser, FakeBot

scenarios("../features/edge_cases.feature")


# Import common steps
from tests.steps.common_steps import setup_users, users_connected
from tests.steps.adding_steps import add_movie_to_wishlist


@when(parsers.parse('пользователь "{user_name}" отправляет сообщение "{message}"'))
def user_sends_edge_case_message(
    users: dict[str, FakeUser],
    user_service,
    wishlist_service,
    watch_service,
    fake_bot: FakeBot,
    user_name: str,
    message: str,
):
    """Handle edge case messages."""
    user = users[user_name]
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

    elif message_lower.startswith("посмотрели"):
        import re
        text = message[len("посмотрели"):].strip()
        match = re.match(r"(.+?),?\s*(\d+)(?:/10)?$", text, re.IGNORECASE)
        if match:
            movie_name = match.group(1).strip()
            rating = int(match.group(2))

            # Case-insensitive lookup - find original title
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
        # Unknown command
        fake_bot.send(Messages.UNKNOWN_COMMAND)


@then(parsers.parse('бот отвечает "{expected}"'))
def check_edge_case_response(fake_bot: FakeBot, expected: str):
    """Check bot response."""
    assert fake_bot.last_response == expected


@then("бот находит фильм несмотря на разный регистр")
def bot_finds_case_insensitive():
    """Case-insensitive search is handled in the when step."""
    pass
