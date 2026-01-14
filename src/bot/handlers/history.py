# -*- coding: utf-8 -*-
"""History handler - 'история'"""

from aiogram import Router, F
from aiogram.types import Message

from src.bot.messages import Messages
from src.services import UserService, HistoryService

router = Router()


@router.message(F.text.lower().in_({"история", "📚 история"}))
async def show_history(
    message: Message, user_service: UserService, history_service: HistoryService
):
    """Handle 'история' - show watch history."""
    user_service.register(message.from_user.id, message.from_user.full_name)

    result = history_service.get_history()

    if result.is_empty:
        await message.answer(Messages.EMPTY_HISTORY)
    else:
        lines = ["📚 История просмотров:"]
        for month in result.months:
            lines.append("")
            lines.append(f"{month.month_name}:")
            for movie in month.movies:
                date_str = HistoryService.format_date(movie.watched_at)
                lines.append(
                    f"• {movie.movie_title} — {movie.rating}/10 ({date_str})"
                )

        lines.append("")
        lines.append(
            f"Всего за год: {result.total_count} фильма, средняя оценка: {result.average_rating}"
        )

        await message.answer("\n".join(lines))
