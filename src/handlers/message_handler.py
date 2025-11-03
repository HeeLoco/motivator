"""
Message handler for Motivator Bot.

Handles non-command text messages:
- Simple feedback detection
- Default acknowledgment
"""

from telegram import Update
from telegram.ext import ContextTypes

from .base import BaseHandler


class MessageHandler(BaseHandler):
    """Handles non-command text message processing"""

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages and feedback"""
        user_id = update.effective_user.id
        message_text = update.message.text.lower()

        # Simple feedback detection
        if message_text in ['❤️', '👍', '👎', 'helpful', 'hilfreich', 'good', 'gut', 'bad', 'schlecht']:
            # This is feedback - log it
            feedback_type = 'positive' if message_text in ['❤️', '👍', 'helpful', 'hilfreich', 'good', 'gut'] else 'negative'

            # Get the message they're replying to (simplified - in practice you'd track this better)
            self.db.add_feedback(user_id, 0, feedback_type, message_text)

            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'

            if language == 'de':
                response = "Danke für dein Feedback! Das hilft mir zu lernen. 📝"
            else:
                response = "Thanks for your feedback! This helps me learn. 📝"

            await update.message.reply_text(response)
        else:
            # Regular message - could be goal setting or other input
            # For now, just acknowledge
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'

            if language == 'de':
                response = "Ich habe deine Nachricht erhalten! Verwende /help um alle verfügbaren Befehle zu sehen."
            else:
                response = "I received your message! Use /help to see all available commands."

            await update.message.reply_text(response)
