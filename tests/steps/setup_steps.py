# -*- coding: utf-8 -*-
"""Step definitions for setup.feature."""

from pytest_bdd import scenarios, given, when, then, parsers
from src.bot.messages import Messages
from tests.conftest import FakeUser, FakeBot, get_test_user

scenarios("../features/setup.feature")


@given(parsers.parse('пользователь "{name}" впервые запускает бота'))
def user_first_time(name: str):
    """User is running bot for the first time - no-op, just context."""
    pass


@when(parsers.parse('пользователь "{name}" отправляет команду "/start"'))
def user_sends_start(user_service, fake_bot: FakeBot, name: str):
    """User sends /start command."""
    user = get_test_user(name)
    user_service.register(user.telegram_id, user.display_name)
    fake_bot.send(Messages.WELCOME)


@when(parsers.parse('пользователь "{name}" отправляет команду "/help"'))
def user_sends_help(user_service, fake_bot: FakeBot, name: str):
    """User sends /help command."""
    user = get_test_user(name)
    user_service.register(user.telegram_id, user.display_name)
    fake_bot.send(Messages.HELP)


# Multiline response step defined in conftest.py
