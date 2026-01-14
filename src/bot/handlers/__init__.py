# -*- coding: utf-8 -*-
"""Bot handlers package."""

from .commands import router as commands_router
from .wishlist import router as wishlist_router
from .selection import router as selection_router
from .watching import router as watching_router
from .history import router as history_router
from .fallback import router as fallback_router

__all__ = [
    "commands_router",
    "wishlist_router",
    "selection_router",
    "watching_router",
    "history_router",
    "fallback_router",
]
