"""
Base handler class for Motivator Bot.

Provides shared utilities and common functionality for all command handlers.
"""

from typing import Optional


class BaseHandler:
    """Base class for command handlers with shared utilities"""

    def __init__(self, db, content_manager, scheduler):
        """
        Initialize base handler with shared dependencies.

        Args:
            db: Database instance
            content_manager: ContentManager instance
            scheduler: SmartMessageScheduler instance
        """
        self.db = db
        self.content_manager = content_manager
        self.scheduler = scheduler

    def get_user_language(self, user_id: int) -> str:
        """
        Get user's preferred language.

        Args:
            user_id: Telegram user ID

        Returns:
            Language code ('de' or 'en'), defaults to 'de'
        """
        settings = self.db.get_user_settings(user_id)
        return settings.get('language', 'de') if settings else 'de'

    def get_user_settings(self, user_id: int) -> Optional[dict]:
        """
        Get user settings from database.

        Args:
            user_id: Telegram user ID

        Returns:
            User settings dict or None if user not found
        """
        return self.db.get_user_settings(user_id)
