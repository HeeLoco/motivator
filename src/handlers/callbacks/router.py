"""
Callback routing for Motivator Bot.

Central router that dispatches callback queries to appropriate domain handlers.
"""

from telegram import Update
from telegram.ext import ContextTypes

from .settings import SettingsCallbackHandler
from .mood import MoodCallbackHandler
from .admin import AdminCallbackHandler


class CallbackRouter:
    """Routes callback queries to appropriate domain handlers"""

    def __init__(self, bot_instance):
        """
        Initialize callback router with all domain handlers.

        Args:
            bot_instance: Reference to the main MotivatorBot instance
        """
        self.bot = bot_instance

        # Initialize domain handlers
        self.settings_handler = SettingsCallbackHandler(bot_instance)
        self.mood_handler = MoodCallbackHandler(bot_instance)
        self.admin_handler = AdminCallbackHandler(bot_instance)

        # Map callback data patterns to handlers
        # Pattern prefixes for routing
        self.prefix_handlers = {
            'lang_': self.settings_handler.handle_language_select,
            'mood_': self.mood_handler.handle_mood_select,
            'feedback_': self.mood_handler.handle_feedback,
            'freq_': self.settings_handler.handle_frequency_select,
            'start_time_': self.settings_handler.handle_start_time_select,
            'end_time_': self.settings_handler.handle_end_time_select,
            'min_gap_': self.settings_handler.handle_min_gap_select,
            'admin_reset_confirm_': self.admin_handler.handle_admin_reset_confirm,
        }

        # Exact match handlers
        self.exact_handlers = {
            # Settings
            'set_language': self.settings_handler.handle_set_language,
            'set_frequency': self.settings_handler.handle_set_frequency,
            'toggle_active': self.settings_handler.handle_toggle_active,
            'set_timing': self.settings_handler.handle_set_timing,
            'set_start_time': self.settings_handler.handle_set_start_time,
            'set_end_time': self.settings_handler.handle_set_end_time,
            'set_min_gap': self.settings_handler.handle_set_min_gap,
            'reset_user': self.settings_handler.handle_reset_user,
            'confirm_reset': self.settings_handler.handle_confirm_reset,
            'back_to_settings': self.settings_handler.handle_back_to_settings,

            # Admin
            'confirm_broadcast': self.admin_handler.handle_confirm_broadcast,
            'cancel_broadcast': self.admin_handler.handle_cancel_broadcast,
            'admin_reset_cancel': self.admin_handler.handle_admin_reset_cancel,

            # Utility
            'close_menu': self._handle_close_menu,
        }

    async def route(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Route callback query to appropriate handler.

        Args:
            update: Telegram update object
            context: Callback context
        """
        query = update.callback_query
        await query.answer()

        data = query.data

        # Try prefix matching first (more specific patterns like goal_delete_confirm_ before goal_delete_)
        # Sort by length descending to match more specific prefixes first
        for prefix in sorted(self.prefix_handlers.keys(), key=len, reverse=True):
            if data.startswith(prefix):
                handler = self.prefix_handlers[prefix]
                await handler(query, context)
                return

        # Try exact matching
        if data in self.exact_handlers:
            handler = self.exact_handlers[data]
            await handler(query, context)
            return

        # Unknown callback data
        await query.edit_message_text("❌ Unknown action. Please try again or use /help")

    async def _handle_close_menu(self, query, context):
        """Close the menu by deleting the message"""
        await query.delete_message()
