# -*- coding: utf-8 -*-
"""Fallback handler for unknown commands."""

from aiogram import Router
from aiogram.types import Message

from src.bot.messages import Messages
from src.services import UserService, WishlistService
from src.database.repositories import StateRepository

router = Router()


@router.message()
async def unknown_command(
    message: Message,
    user_service: UserService,
    wishlist_service: WishlistService,
    state_repo: StateRepository,
):
    """Handle unknown messages or awaited input."""
    user_service.register(message.from_user.id, message.from_user.full_name)

    # Check if user is awaiting movie input
    awaiting_key = f"awaiting_movie:{message.from_user.id}"
    if state_repo.get(awaiting_key):
        state_repo.delete(awaiting_key)
        movie_name = message.text.strip()
        if movie_name:
            result = wishlist_service.add_movie(message.from_user.id, movie_name)
            if result.already_exists:
                await message.answer(Messages.movie_already_exists(result.movie_title))
            else:
                await message.answer(Messages.movie_added(result.movie_title))
            return

    await message.answer(Messages.UNKNOWN_COMMAND)
