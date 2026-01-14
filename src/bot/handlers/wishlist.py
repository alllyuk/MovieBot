# -*- coding: utf-8 -*-
"""Wishlist handlers - add/remove/list movies."""

from aiogram import Router, F
from aiogram.types import Message

from src.bot.messages import Messages
from src.services import UserService, WishlistService

router = Router()


@router.message(F.text.lower().startswith("хочу посмотреть"))
async def add_movie(
    message: Message, user_service: UserService, wishlist_service: WishlistService
):
    """Handle 'хочу посмотреть [название]' - add movie to wishlist."""
    user_service.register(message.from_user.id, message.from_user.full_name)

    movie_name = message.text[len("хочу посмотреть") :].strip()
    if not movie_name:
        await message.answer(Messages.EMPTY_MOVIE_NAME)
        return

    result = wishlist_service.add_movie(message.from_user.id, movie_name)
    if result.already_exists:
        await message.answer(Messages.movie_already_exists(result.movie_title))
    else:
        await message.answer(Messages.movie_added(result.movie_title))


@router.message(F.text.lower() == "мой список")
async def my_list(
    message: Message, user_service: UserService, wishlist_service: WishlistService
):
    """Handle 'мой список' - show user's wishlist."""
    user_service.register(message.from_user.id, message.from_user.full_name)

    movies = wishlist_service.get_user_wishlist(message.from_user.id)
    await message.answer(Messages.format_my_list(movies))


@router.message(F.text.lower() == "наш список")
async def our_list(
    message: Message, user_service: UserService, wishlist_service: WishlistService
):
    """Handle 'наш список' - show intersection of wishlists."""
    user_service.register(message.from_user.id, message.from_user.full_name)

    movies = wishlist_service.get_intersection()
    await message.answer(Messages.format_our_list(movies))


@router.message(F.text.lower().startswith("удали"))
async def delete_movie(
    message: Message, user_service: UserService, wishlist_service: WishlistService
):
    """Handle 'удали [название]' - remove movie from wishlist."""
    user_service.register(message.from_user.id, message.from_user.full_name)

    movie_name = message.text[len("удали") :].strip()
    if not movie_name:
        return

    result = wishlist_service.delete_movie(message.from_user.id, movie_name)
    if result.deleted:
        await message.answer(Messages.movie_deleted(result.movie_title))
