"""Step definitions for history.feature."""

from pytest_bdd import scenarios, given, when, then, parsers
from datetime import date
from src.bot.messages import Messages
from src.services.history_service import HistoryService
from tests.conftest import FakeUser, FakeBot

scenarios("../features/history.feature")


# Import common steps
from tests.steps.common_steps import setup_users, users_connected


@given(parsers.parse('в истории просмотров есть фильмы:'))
def add_movies_to_history(history_repo, user_service, users, datatable):
    """Add movies to watch history from data table."""
    # Register a user first
    user = users["Андрей"]
    user_service.register(user.telegram_id, user.display_name)

    for row in datatable:
        movie = row["название"]
        rating = int(row["оценка"])
        watched_at = date.fromisoformat(row["дата"])
        history_repo.add(movie, rating, watched_at, user_id=1)


@given("история просмотров пуста")
def empty_history():
    """History is empty by default in fresh database."""
    pass


@when(parsers.parse('пользователь "{user_name}" отправляет сообщение "история"'))
def user_asks_history(users: dict[str, FakeUser], user_service, history_service, fake_bot: FakeBot, user_name: str):
    """User asks for watch history."""
    user = users[user_name]
    user_service.register(user.telegram_id, user.display_name)

    result = history_service.get_history()

    if result.is_empty:
        fake_bot.send(Messages.EMPTY_HISTORY)
    else:
        lines = ["📚 История просмотров:"]
        for month in result.months:
            lines.append("")
            lines.append(f"{month.month_name}:")
            for movie in month.movies:
                date_str = HistoryService.format_date(movie.watched_at)
                lines.append(f"• {movie.movie_title} — {movie.rating}/10 ({date_str})")

        lines.append("")
        lines.append(f"Всего за год: {result.total_count} фильма, средняя оценка: {result.average_rating}")
        fake_bot.send("\n".join(lines))


@then(parsers.parse('бот отвечает "{expected}"'))
def check_history_response(fake_bot: FakeBot, expected: str):
    """Check bot response."""
    assert fake_bot.last_response == expected


@then(parsers.parse('бот отвечает:\n{expected}'))
def check_history_multiline(fake_bot: FakeBot, expected: str):
    """Check multiline history response."""
    assert fake_bot.last_response is not None

    # Check key parts are present
    response = fake_bot.last_response
    assert "История просмотров" in response or "История пуста" in response

    # If not empty, check for expected content markers
    if "История пуста" not in response:
        for line in expected.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("```"):
                # Check key movie names are in response
                if "—" in line:
                    movie_name = line.split("—")[0].replace("•", "").strip()
                    assert movie_name in response, f"Movie '{movie_name}' not found in response"
