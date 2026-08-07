"""
Mood command handlers for Motivator Bot.

Handles mood-related commands:
- /mood - Mood tracking interface
- /stats - User statistics display
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .base import BaseHandler
from .helpers import get_user_language


class MoodCommandHandler(BaseHandler):
    """Handles mood-related command handlers"""

    async def mood_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mood tracking interface"""
        language = get_user_language(self.db, update.effective_user.id)

        if language == 'de':
            mood_text = "🌈 *Wie fühlst du dich heute?*\n\nWähle eine Zahl von 1 (sehr schlecht) bis 10 (ausgezeichnet):"
        else:
            mood_text = "🌈 *How are you feeling today?*\n\nChoose a number from 1 (very bad) to 10 (excellent):"

        keyboard = []
        for i in range(1, 11):
            if i <= 5:
                row = [InlineKeyboardButton(f"{i} {'😢' if i <= 3 else '😐'}", callback_data=f"mood_{i}")]
            else:
                row = [InlineKeyboardButton(f"{i} {'😊' if i <= 8 else '🤩'}", callback_data=f"mood_{i}")]
            keyboard.append(row)

        # Add close button
        keyboard.append([InlineKeyboardButton("❌ Schließen" if language == 'de' else "❌ Close", callback_data="close_menu")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            mood_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user statistics"""
        user_id = update.effective_user.id
        language = get_user_language(self.db, user_id)

        # Get statistics
        message_stats = self.db.get_message_stats(user_id)
        recent_mood = self.db.get_recent_mood(user_id, 7)

        if language == 'de':
            stats_text = f"""
📊 *Deine Statistiken*

*Nachrichten erhalten:*
• Gesamt: {sum(message_stats.values())}
• Text: {message_stats.get('text', 0)}
• Medien: {message_stats.get('image', 0) + message_stats.get('video', 0)}
• Links: {message_stats.get('link', 0)}

*Stimmung (letzte 7 Tage):*
• Einträge: {len(recent_mood)}
"""
            if recent_mood:
                avg_mood = sum(m['score'] for m in recent_mood) / len(recent_mood)
                stats_text += f"• Durchschnitt: {avg_mood:.1f}/10"
        else:
            stats_text = f"""
📊 *Your Statistics*

*Messages received:*
• Total: {sum(message_stats.values())}
• Text: {message_stats.get('text', 0)}
• Media: {message_stats.get('image', 0) + message_stats.get('video', 0)}
• Links: {message_stats.get('link', 0)}

*Mood (last 7 days):*
• Entries: {len(recent_mood)}
"""
            if recent_mood:
                avg_mood = sum(m['score'] for m in recent_mood) / len(recent_mood)
                stats_text += f"• Average: {avg_mood:.1f}/10"

        await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)
