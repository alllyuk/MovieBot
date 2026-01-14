# -*- coding: utf-8 -*-
"""Configuration settings loaded from environment."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Bot token from environment
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Database path
DB_PATH = os.getenv("DB_PATH", str(Path(__file__).parent.parent / "moviebot.db"))
