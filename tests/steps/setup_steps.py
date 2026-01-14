"""Step definitions for setup.feature."""

from pytest_bdd import scenarios, given, when, then, parsers
from src.bot.messages import Messages
from tests.conftest import FakeUser, FakeBot

scenarios("../features/setup.feature")


@given(parsers.parse('пользователь "{name}" отправляет команду "/start"'))
def user_sends_start(users: dict[str, FakeUser], user_service, fake_bot: FakeBot, name: str):
    """User sends /start command."""
    user = users[name]
    result = user_service.register(user.telegram_id, user.display_name)
    fake_bot.send(Messages.WELCOME)


@when(parsers.parse('пользователь "{name}" отправляет команду "/start"'))
def when_user_sends_start(users: dict[str, FakeUser], user_service, fake_bot: FakeBot, name: str):
    """User sends /start command."""
    user = users[name]
    result = user_service.register(user.telegram_id, user.display_name)
    fake_bot.send(Messages.WELCOME)


@when(parsers.parse('пользователь "{name}" отправляет команду "/help"'))
def user_sends_help(fake_bot: FakeBot, name: str):
    """User sends /help command."""
    fake_bot.send(Messages.HELP)


@given(parsers.parse('пользователь "{name}" впервые запускает бота'))
def user_first_time(name: str):
    """User is running bot for the first time - no-op, just context."""
    pass


@then("бот отвечает приветственным сообщением с инструкцией")
def check_welcome_message(fake_bot: FakeBot):
    """Check that bot responded with welcome message."""
    assert fake_bot.last_response is not None
    assert "Привет" in fake_bot.last_response
    assert "хочу посмотреть" in fake_bot.last_response


@then("бот отвечает списком доступных команд")
def check_help_message(fake_bot: FakeBot):
    """Check that bot responded with help message."""
    assert fake_bot.last_response is not None
    assert "Команды" in fake_bot.last_response
    assert "хочу посмотреть" in fake_bot.last_response


@then(parsers.parse('бот отвечает:\n{expected}'))
def check_multiline_response(fake_bot: FakeBot, expected: str):
    """Check multiline bot response."""
    assert fake_bot.last_response is not None
    # Normalize whitespace for comparison
    actual_lines = [line.strip() for line in fake_bot.last_response.strip().split("\n") if line.strip()]
    expected_lines = [line.strip() for line in expected.strip().split("\n") if line.strip()]

    for expected_line in expected_lines:
        found = any(expected_line in actual for actual in actual_lines)
        assert found, f"Expected line '{expected_line}' not found in response"
