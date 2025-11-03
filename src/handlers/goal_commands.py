"""
Goal command handlers for Motivator Bot.

Handles goal-related commands:
- /goals - Goals management interface
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .base import BaseHandler


class GoalCommandHandler(BaseHandler):
    """Handles goal-related command handlers"""

    async def goals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Goals management interface"""
        user_settings = self.db.get_user_settings(update.effective_user.id)
        language = user_settings.get('language', 'de') if user_settings else 'de'

        if language == 'de':
            goals_text = """
🎯 *Persönliche Ziele*

Ziele helfen dabei, fokussiert und motiviert zu bleiben.

Was möchtest du tun?
"""
            keyboard = [
                [InlineKeyboardButton("➕ Neues Ziel hinzufügen", callback_data="add_goal")],
                [InlineKeyboardButton("📋 Meine Ziele anzeigen", callback_data="view_goals")],
                [InlineKeyboardButton("❌ Schließen", callback_data="close_menu")]
            ]
        else:
            goals_text = """
🎯 *Personal Goals*

Goals help you stay focused and motivated.

What would you like to do?
"""
            keyboard = [
                [InlineKeyboardButton("➕ Add New Goal", callback_data="add_goal")],
                [InlineKeyboardButton("📋 View My Goals", callback_data="view_goals")],
                [InlineKeyboardButton("❌ Close", callback_data="close_menu")]
            ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            goals_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
