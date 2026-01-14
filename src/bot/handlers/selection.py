# -*- coding: utf-8 -*-
"""Selection handler - 'что смотрим?'"""

from aiogram import Router, F
from aiogram.types import Message

from src.bot.messages import Messages
from src.services import UserService, SelectionService

router = Router()


@router.message(F.text.lower().regexp(r"^(🎲\s*)?что смотрим"))
async def what_to_watch(
    message: Message, user_service: UserService, selection_service: SelectionService
):
    """Handle 'что смотрим?' - pick a movie."""
    user_service.register(message.from_user.id, message.from_user.full_name)

    result = selection_service.pick_movie(message.from_user.id)

    if result.movie is None:
        await message.answer(Messages.ALL_LISTS_EMPTY)
    elif result.from_intersection:
        await message.answer(Messages.movie_selected_intersection(result.movie))
    elif result.other_user_name:
        await message.answer(
            Messages.movie_selected_from_other(result.movie, result.other_user_name)
        )
    else:
        await message.answer(Messages.movie_selected_random(result.movie))
