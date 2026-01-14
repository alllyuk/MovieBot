# -*- coding: utf-8 -*-
"""Step definitions for history.feature."""

from pytest_bdd import scenarios, given, when, then, parsers
from datetime import date
from src.bot.messages import Messages
from src.services.history_service import HistoryService
from tests.conftest import FakeUser, FakeBot, get_test_user, _ANDREY

scenarios("../features/history.feature")


@given(parsers.parse('в истории просмотров есть фильмы:'))
def add_movies_to_history(history_repo, user_service, datatable):
    """Add movies to watch history from data table."""
    user = _ANDREY
    user_service.register(user.telegram_id, user.display_name)

    # Skip header row if present
    data_rows = datatable
    if data_rows and isinstance(data_rows[0], list):
        first_cell = str(data_rows[0][0]).lower()
        if "назван" in first_cell or first_cell == "название":
            data_rows = datatable[1:]  # Skip header

    for row in data_rows:
        # Handle both dict and list formats
        if isinstance(row, dict):
            movie = row.get("название") or list(row.values())[0]
            rating = int(row.get("оценка") or row.get(list(row.keys())[1]) or list(row.values())[1])
            date_str = row.get("дата") or row.get(list(row.keys())[2]) or list(row.values())[2]
        else:
            # List format: [movie, rating, date]
            movie = row[0]
            rating = int(row[1])
            date_str = row[2]
        watched_at = date.fromisoformat(str(date_str))
        history_repo.add(movie, rating, watched_at, user_id=1)


@given("история просмотров пуста")
def empty_history():
    """History is empty by default in fresh database."""
    pass


@when(parsers.parse('пользователь "{user_name}" отправляет сообщение "история"'))
def user_asks_history(user_service, history_service, fake_bot: FakeBot, user_name: str):
    """User asks for watch history."""
    user = get_test_user(user_name)
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


# Multiline response step defined in conftest.py
