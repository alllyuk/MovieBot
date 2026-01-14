# -*- coding: utf-8 -*-
"""Keyboards for the bot."""

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


def rating_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard with rating buttons 1-10."""
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


def main_keyboard() -> ReplyKeyboardMarkup:
    """Create persistent keyboard with main commands."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 Мой список"),
                KeyboardButton(text="💑 Наш список"),
            ],
            [
                KeyboardButton(text="🎲 Что смотрим?"),
                KeyboardButton(text="📚 История"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Или напиши: хочу посмотреть [фильм]",
    )
