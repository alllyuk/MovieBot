"""Database schema and migrations."""

from .connection import Database

SCHEMA = """
-- Users (auto-register on /start)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Personal wishlists
CREATE TABLE IF NOT EXISTS wishlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    movie_title TEXT NOT NULL,
    movie_title_lower TEXT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, movie_title_lower)
);

-- Shared watch history
CREATE TABLE IF NOT EXISTS watch_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_title TEXT NOT NULL,
    movie_title_lower TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 10),
    watched_at DATE NOT NULL,
    marked_by_user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (marked_by_user_id) REFERENCES users(id)
);

-- Pending ratings (for inline button flow)
CREATE TABLE IF NOT EXISTS pending_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    movie_title TEXT NOT NULL,
    message_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Bot state (key-value storage for last_selected_movie etc.)
CREATE TABLE IF NOT EXISTS bot_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_wishlist_user ON wishlist(user_id);
CREATE INDEX IF NOT EXISTS idx_wishlist_title ON wishlist(movie_title_lower);
CREATE INDEX IF NOT EXISTS idx_history_date ON watch_history(watched_at);
CREATE INDEX IF NOT EXISTS idx_history_title ON watch_history(movie_title_lower);
"""


def run_migrations(db: Database) -> None:
    """Initialize database schema."""
    db.connect().executescript(SCHEMA)
    db.commit()
