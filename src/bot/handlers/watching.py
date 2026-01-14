# -*- coding: utf-8 -*-
"""Watching handler - 'посмотрели' + rating callbacks."""

import re

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from src.bot.messages import Messages
from src.bot.keyboards import rating_keyboard
from src.services import UserService, WishlistService, WatchService
from src.database.repositories import StateRepository

router = Router()


@router.message(F.text.lower().startswith("посмотрели"))
async def mark_watched(
    message: Message,
    user_service: UserService,
    wishlist_service: WishlistService,
    watch_service: WatchService,
    state_repo: StateRepository,
):
    """Handle 'посмотрели [название], [оценка]' - mark movie as watched."""
    user_service.register(message.from_user.id, message.from_user.full_name)

    text = message.text[len("посмотрели") :].strip()

    # Rating requires comma before number OR /10 suffix
    # This prevents "Дюна 2" from being parsed as rating=2
    match = re.match(r"(.+?),\s*(\d+)(?:/10)?$", text) or re.match(
        r"(.+?)\s+(\d+)/10$", text
    )

    if match:
        movie_name = match.group(1).strip()
        rating = int(match.group(2))

        if rating < 1 or rating > 10:
            await message.answer(Messages.INVALID_RATING)
            return

        # Check if movie is in wishlist
        all_movies = wishlist_service.get_all_movies()
        in_wishlist = movie_name.lower() in [m.lower() for m in all_movies]

        result = watch_service.mark_watched(message.from_user.id, movie_name, rating)

        if in_wishlist:
            await message.answer(Messages.movie_watched(result.movie_title, rating))
        else:
            await message.answer(
                Messages.movie_added_to_history(result.movie_title, rating)
            )
    else:
        # No rating provided - ask for it
        movie_name = text.strip()
        if movie_name:
            # Store pending movie for rating
            state_repo.set(f"pending_movie:{message.from_user.id}", movie_name)
            await message.answer(Messages.ASK_RATING, reply_markup=rating_keyboard())
        else:
            await message.answer(Messages.ASK_RATING)


@router.callback_query(F.data.startswith("rate:"))
async def handle_rating(
    callback: CallbackQuery,
    user_service: UserService,
    wishlist_service: WishlistService,
    watch_service: WatchService,
    state_repo: StateRepository,
):
    """Handle rating button press."""
    user_service.register(callback.from_user.id, callback.from_user.full_name)

    rating = int(callback.data.split(":")[1])

    # Get pending movie
    movie_name = state_repo.get(f"pending_movie:{callback.from_user.id}")
    if not movie_name:
        await callback.answer("No pending movie to rate")
        return

    # Clear pending state
    state_repo.delete(f"pending_movie:{callback.from_user.id}")

    # Check if movie is in wishlist
    all_movies = wishlist_service.get_all_movies()
    in_wishlist = movie_name.lower() in [m.lower() for m in all_movies]

    result = watch_service.mark_watched(callback.from_user.id, movie_name, rating)

    if in_wishlist:
        await callback.message.edit_text(
            Messages.movie_watched(result.movie_title, rating)
        )
    else:
        await callback.message.edit_text(
            Messages.movie_added_to_history(result.movie_title, rating)
        )

    await callback.answer()
