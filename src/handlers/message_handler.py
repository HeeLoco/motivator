"""
Message handler for Motivator Bot.

Handles non-command text messages:
- Simple feedback detection
- AI-powered conversational replies (with static fallback)

Conversation memory is database-backed: every turn is stored in
chat_messages, older turns get folded into a rolling summary
(chat_summaries), and long-lived knowledge about the user is kept
as facts (user_facts). The AI context per reply is:
summary + user facts + the recent verbatim turns.
"""

import asyncio

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from .base import BaseHandler
from .helpers import get_display_name, get_user_language
from src import ai_motivator

from src.logging_config import get_logger

logger = get_logger(__name__)


class MessageHandler(BaseHandler):
    """Handles non-command text message processing"""

    # When more unsummarized turns than this accumulate, consolidate
    SUMMARIZE_THRESHOLD = 20
    # How many recent turns stay verbatim after consolidation
    KEEP_VERBATIM = 8

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages and feedback"""
        user_id = update.effective_user.id
        message_text = update.message.text.lower()

        # Pending name input from the settings menu?
        if context.user_data.pop('awaiting_preferred_name', False):
            await self._save_preferred_name(update, user_id)
            return

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
            chat_id = update.effective_chat.id
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'

            recent_mood = self.db.get_recent_mood(user_id, 1)
            mood_score = recent_mood[0]['score'] if recent_mood else None

            summary = self.db.get_chat_summary(user_id, chat_id)
            facts = self.db.get_user_facts(user_id)
            history = [
                {'role': m['role'], 'content': m['content']}
                for m in self.db.get_unsummarized_messages(user_id, chat_id)
            ]

            await update.message.chat.send_action(ChatAction.TYPING)
            response = await ai_motivator.generate_chat_reply(
                language, update.message.text, mood_score, history,
                get_display_name(user_settings, update.effective_user.first_name),
                facts, summary, user_id=user_id
            )

            if response:
                # Persist this exchange for follow-up messages
                self.db.add_chat_message(user_id, chat_id, 'user', update.message.text)
                self.db.add_chat_message(user_id, chat_id, 'assistant', response)

                # Consolidate memory in the background (summary + facts)
                asyncio.create_task(self._maintain_memory(user_id, chat_id, language))
            else:
                # Static fallback when AI is unavailable
                if language == 'de':
                    response = "Ich habe deine Nachricht erhalten! Verwende /help um alle verfügbaren Befehle zu sehen."
                else:
                    response = "I received your message! Use /help to see all available commands."

            await update.message.reply_text(response)

    async def _save_preferred_name(self, update: Update, user_id: int):
        """Save the custom address name the user just typed"""
        name = update.message.text.strip()[:32]
        language = get_user_language(self.db, user_id)

        if not name:
            if language == 'de':
                text = "❌ Das sah leer aus — bitte versuche es nochmal über /settings."
            else:
                text = "❌ That looked empty - please try again via /settings."
            await update.message.reply_text(text)
            return

        self.db.update_user_setting(user_id, 'preferred_name', name)

        if language == 'de':
            text = f"📛 Schön, ich nenne dich ab jetzt {name}! 😊"
        else:
            text = f"📛 Great, I'll call you {name} from now on! 😊"

        await update.message.reply_text(text)

    async def _maintain_memory(self, user_id: int, chat_id: int, language: str):
        """
        Fold older turns into the rolling summary and refresh user facts
        once enough unsummarized messages accumulated.

        Runs as a background task after replying so the user never waits
        for memory maintenance.
        """
        try:
            messages = self.db.get_unsummarized_messages(user_id, chat_id)
            if len(messages) <= self.SUMMARIZE_THRESHOLD:
                return

            to_fold = messages[:-self.KEEP_VERBATIM]

            old_summary = self.db.get_chat_summary(user_id, chat_id)
            new_summary = await ai_motivator.summarize_conversation(
                language, old_summary, to_fold, user_id=user_id
            )
            if new_summary:
                self.db.save_chat_summary(user_id, chat_id, new_summary)
                self.db.mark_messages_summarized([m['id'] for m in to_fold])
                logger.info(f"Folded {len(to_fold)} messages into summary for user {user_id}")

            existing_facts = self.db.get_user_facts(user_id)
            new_facts = await ai_motivator.extract_user_facts(
                language, existing_facts, to_fold, user_id=user_id
            )
            if new_facts is not None:
                self.db.replace_user_facts(user_id, new_facts)
                logger.info(f"Updated facts for user {user_id}: {len(new_facts)} facts")

        except Exception as e:
            logger.error(f"Error maintaining chat memory for user {user_id}: {e}")
