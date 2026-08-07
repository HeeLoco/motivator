"""
Message handler for Motivator Bot.

Handles non-command text messages:
- Simple feedback detection
- AI-powered conversational replies (with static fallback)
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from .base import BaseHandler
from src import ai_motivator


class MessageHandler(BaseHandler):
    """Handles non-command text message processing"""

    # Maximum conversation turns (user + assistant entries) kept per chat
    MAX_HISTORY_ENTRIES = 20

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
            # Regular message - answer conversationally via AI
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'

            recent_mood = self.db.get_recent_mood(user_id, 1)
            mood_score = recent_mood[0]['score'] if recent_mood else None

            history = context.chat_data.setdefault('ai_history', [])

            await update.message.chat.send_action(ChatAction.TYPING)
            response = await ai_motivator.generate_chat_reply(
                language, update.message.text, mood_score, history
            )

            if response:
                # Remember this exchange for follow-up messages
                history.append({'role': 'user', 'content': update.message.text})
                history.append({'role': 'assistant', 'content': response})
                del history[:-self.MAX_HISTORY_ENTRIES]
            else:
                # Static fallback when AI is unavailable
                if language == 'de':
                    response = "Ich habe deine Nachricht erhalten! Verwende /help um alle verfügbaren Befehle zu sehen."
                else:
                    response = "I received your message! Use /help to see all available commands."

            await update.message.reply_text(response)
