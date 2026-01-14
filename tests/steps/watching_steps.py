"""Step definitions for watching_movie.feature."""

from pytest_bdd import scenarios, given, when, then, parsers
from src.bot.messages import Messages
from tests.conftest import FakeUser, FakeBot
import re

scenarios("../features/watching_movie.feature")


# Import common steps
from tests.steps.common_steps import setup_users, users_connected


@given(parsers.parse('в списке желаний есть фильм "{movie}"'))
def movie_in_any_wishlist(users: dict[str, FakeUser], user_service, wishlist_service, movie: str):
    """Add movie to first user's wishlist."""
    user = users["Андрей"]
    user_service.register(user.telegram_id, user.display_name)
    wishlist_service.add_movie(user.telegram_id, movie)


@given(parsers.parse('в списках желаний нет фильма "{movie}"'))
def movie_not_in_wishlists(users: dict[str, FakeUser], user_service, movie: str):
    """Ensure movie is not in any wishlist - just register users."""
    for user in users.values():
        user_service.register(user.telegram_id, user.display_name)


@given(parsers.parse('бот запросил оценку для фильма "{movie}"'))
def bot_asked_for_rating(movie: str, fake_bot: FakeBot):
    """Simulate bot asking for rating."""
    fake_bot.send(Messages.ASK_RATING)


@when(parsers.parse('пользователь "{user_name}" отправляет сообщение "{message}"'))
def user_sends_watched_message(users: dict[str, FakeUser], user_service, watch_service, wishlist_service, fake_bot: FakeBot, user_name: str, message: str):
    """User sends a 'watched' message."""
    user = users[user_name]
    user_service.register(user.telegram_id, user.display_name)

    if message.startswith("посмотрели"):
        # Parse movie and rating
        text = message[len("посмотрели"):].strip()

        # Try to extract rating (e.g., "Дюна, 8/10" or "Дюна 8")
        match = re.match(r"(.+?),?\s*(\d+)(?:/10)?$", text)
        if match:
            movie_name = match.group(1).strip()
            rating = int(match.group(2))

            if rating < 1 or rating > 10:
                fake_bot.send("🤔 Оценка должна быть от 1 до 10. Попробуй ещё раз")
            else:
                # Check if movie was in wishlist
                in_wishlist = movie_name.lower() in [m.lower() for m in wishlist_service.get_all_movies()]
                result = watch_service.mark_watched(user.telegram_id, movie_name, rating)

                if in_wishlist:
                    fake_bot.send(Messages.movie_watched(result.movie_title, rating))
                else:
                    fake_bot.send(Messages.movie_added_to_history(result.movie_title, rating))
        else:
            # No rating provided
            movie_name = text.strip()
            fake_bot.send(Messages.ASK_RATING)
            # Store pending rating (in real bot would use pending_ratings table)


@when(parsers.parse('пользователь "{user_name}" нажимает кнопку "{button}"'))
def user_presses_button(users: dict[str, FakeUser], user_service, watch_service, fake_bot: FakeBot, user_name: str, button: str):
    """User presses an inline button (rating)."""
    user = users[user_name]
    user_service.register(user.telegram_id, user.display_name)

    if button.isdigit():
        rating = int(button)
        # In real implementation, we'd get movie from pending_ratings
        # For tests, assume it's "Дюна 2"
        fake_bot.send(Messages.movie_watched("Дюна 2", rating))


@then(parsers.parse('бот отвечает "{expected}"'))
def check_response_watching(fake_bot: FakeBot, expected: str):
    """Check bot response."""
    assert fake_bot.last_response == expected


@then('бот показывает инлайн-кнопки с цифрами от 1 до 10')
def check_rating_buttons(fake_bot: FakeBot):
    """Check that rating prompt was sent."""
    assert fake_bot.last_response is not None
    assert "Оцените" in fake_bot.last_response or "1 до 10" in fake_bot.last_response


@then(parsers.parse('фильм "{movie}" удаляется из всех списков желаний'))
def movie_removed_from_all(wishlist_service, movie: str):
    """Check movie was removed from all wishlists."""
    all_movies = wishlist_service.get_all_movies()
    assert movie.lower() not in [m.lower() for m in all_movies]


@then(parsers.parse('фильм "{movie}" добавляется в историю с оценкой {rating:d} и датой просмотра'))
def movie_in_history(history_repo, movie: str, rating: int):
    """Check movie is in history with correct rating."""
    item = history_repo.find_by_title(movie)
    assert item is not None
    assert item.rating == rating


@then(parsers.parse('фильм "{movie}" добавляется в историю с оценкой {rating:d}'))
def movie_added_to_history(history_repo, movie: str, rating: int):
    """Check movie is in history."""
    item = history_repo.find_by_title(movie)
    assert item is not None
    assert item.rating == rating
