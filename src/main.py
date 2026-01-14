# -*- coding: utf-8 -*-
"""Main entry point for MovieBot."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from src.config import BOT_TOKEN, DB_PATH
from src.database import Database, run_migrations
from src.database.repositories import (
    UserRepository,
    WishlistRepository,
    HistoryRepository,
    StateRepository,
)
from src.services import (
    UserService,
    WishlistService,
    SelectionService,
    WatchService,
    HistoryService,
)
from src.bot.handlers import (
    commands_router,
    wishlist_router,
    selection_router,
    watching_router,
    history_router,
    fallback_router,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to run the bot."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable is not set!")
        logger.info("Create a .env file with BOT_TOKEN=your_token_here")
        return

    # Initialize database
    logger.info(f"Initializing database at {DB_PATH}")
    db = Database(DB_PATH)
    run_migrations(db)

    # Create repositories
    user_repo = UserRepository(db)
    wishlist_repo = WishlistRepository(db)
    history_repo = HistoryRepository(db)
    state_repo = StateRepository(db)

    # Create services
    user_service = UserService(user_repo)
    wishlist_service = WishlistService(wishlist_repo, user_repo)
    selection_service = SelectionService(wishlist_repo, history_repo, state_repo, user_repo)
    watch_service = WatchService(user_repo, wishlist_repo, history_repo)
    history_service = HistoryService(history_repo)

    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # Register routers (order matters - fallback should be last)
    dp.include_router(commands_router)
    dp.include_router(wishlist_router)
    dp.include_router(selection_router)
    dp.include_router(watching_router)
    dp.include_router(history_router)
    dp.include_router(fallback_router)

    # Inject dependencies
    dp["user_service"] = user_service
    dp["wishlist_service"] = wishlist_service
    dp["selection_service"] = selection_service
    dp["watch_service"] = watch_service
    dp["history_service"] = history_service
    dp["state_repo"] = state_repo

    # Start polling
    logger.info("Starting MovieBot...")
    try:
        await dp.start_polling(bot)
    finally:
        db.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
