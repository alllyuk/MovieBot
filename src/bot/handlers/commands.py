# -*- coding: utf-8 -*-
"""Command handlers for /start and /help."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.messages import Messages
from src.services import UserService

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, user_service: UserService):
    """Handle /start command - register user and send welcome."""
    user_service.register(message.from_user.id, message.from_user.full_name)
    await message.answer(Messages.WELCOME)


@router.message(Command("help"))
async def cmd_help(message: Message, user_service: UserService):
    """Handle /help command - send help message."""
    user_service.register(message.from_user.id, message.from_user.full_name)
    await message.answer(Messages.HELP)
