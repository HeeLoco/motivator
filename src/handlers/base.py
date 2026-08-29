"""
Base handler class for Motivator Bot.

Provides shared utilities and common functionality for all command handlers.
"""

from .helpers import get_user_language


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
        return get_user_language(self.db, user_id)
