# -*- coding: utf-8 -*-
"""Fallback handler for unknown commands."""

from aiogram import Router
from aiogram.types import Message

from src.bot.messages import Messages

router = Router()


@router.message()
async def unknown_command(message: Message):
    """Handle unknown messages."""
    await message.answer(Messages.UNKNOWN_COMMAND)
