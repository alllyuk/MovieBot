# -*- coding: utf-8 -*-
"""Inline keyboards for the bot."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def rating_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard with rating buttons 1-10."""
    buttons = []
    # First row: 1-5
    row1 = [
        InlineKeyboardButton(text=str(i), callback_data=f"rate:{i}")
        for i in range(1, 6)
    ]
    # Second row: 6-10
    row2 = [
        InlineKeyboardButton(text=str(i), callback_data=f"rate:{i}")
        for i in range(6, 11)
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2])
