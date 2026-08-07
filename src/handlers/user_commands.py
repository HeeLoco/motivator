"""
User command handlers for Motivator Bot.

Handles basic user commands:
- /start - Welcome and language selection
- /help - Command documentation
- /settings - Settings menu
- /pause - Pause messages
- /resume - Resume messages
- /motivateMe - Instant motivation
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .base import BaseHandler
from .helpers import build_settings_view, get_user_language
from src import ai_motivator

from src.logging_config import get_logger

logger = get_logger(__name__)


class UserCommandHandler(BaseHandler):
    """Handles user command handlers"""

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command - welcome new users"""
        user = update.effective_user

        # Add user to database
        self.db.add_user(user.id, user.username, user.first_name)

        welcome_text = f"""
🌟 *Willkommen beim Motivator Bot, {user.first_name}!* 🌟

Ich bin hier, um dich mit personalisierten motivierenden Nachrichten den ganzen Tag über zu unterstützen.

*Was ich kann:*
• Dir motivierende Nachrichten zu zufälligen Zeiten senden
• Dir beim Verfolgen deiner Stimmung helfen
• Unterstützungsressourcen bereitstellen, wenn du sie brauchst
• Nachrichten basierend auf deinem Feedback anpassen

*Schnelle Einrichtung:*
/settings - Deine Einstellungen konfigurieren
/mood - Verfolge, wie du dich heute fühlst

*Befehle:*
/help - Alle verfügbaren Befehle anzeigen
/motivateMe - Sofortige Motivation erhalten!
/pause - Nachrichten vorübergehend stoppen
/resume - Nachrichten wieder aktivieren

Lass uns deine Reise zu besserem mentalen Wohlbefinden beginnen! 💪

Welche Sprache bevorzugst du?
"""

        keyboard = [
            [InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help information"""
        language = get_user_language(self.db, update.effective_user.id)

        if language == 'de':
            help_text = """
🤖 *Motivator Bot Hilfe*

*Befehle:*
/start - Bot starten und einrichten
/settings - Einstellungen anpassen
/mood - Stimmung eingeben (1-10)
/stats - Deine Statistiken anzeigen
/motivateMe - Sofortige Motivation erhalten!
/pause - Nachrichten pausieren
/resume - Nachrichten wieder aktivieren
/forgetme - Gesprächsgedächtnis der AI löschen
/help - Diese Hilfe anzeigen

*Funktionen:*
• Erhalte personalisierte motivierende Nachrichten
• Verfolge deine Stimmung und Fortschritte
• Stelle deine Nachrichtenhäufigkeit ein
• Gib Feedback zu Nachrichten

*Feedback geben:*
Antworte einfach auf meine Nachrichten mit:
• ❤️ für hilfreich
• 👍 für okay
• 👎 für nicht hilfreich

Ich bin hier, um dich zu unterstützen! 💙
"""
        else:
            help_text = """
🤖 *Motivator Bot Help*

*Commands:*
/start - Start and setup the bot
/settings - Adjust your preferences
/mood - Log your mood (1-10 scale)
/stats - View your statistics
/motivateMe - Get instant motivation right now!
/pause - Pause motivational messages
/resume - Resume receiving messages
/forgetme - Delete the AI's conversation memory
/help - Show this help message

*Features:*
• Receive personalized motivational messages
• Track your mood and progress over time
• Customize message frequency and timing
• Give feedback on messages I send

*Giving Feedback:*
Simply reply to my messages with:
• ❤️ for helpful
• 👍 for okay
• 👎 for not helpful

I'm here to support you! 💙
"""

        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

    async def settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show settings menu"""
        user_settings = self.db.get_user_settings(update.effective_user.id)
        if not user_settings:
            await update.message.reply_text("Please start the bot first with /start")
            return

        settings_text, reply_markup = build_settings_view(user_settings)
        await update.message.reply_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def pause_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Pause motivational messages"""
        user_id = update.effective_user.id
        self.db.update_user_setting(user_id, 'active', False)

        language = get_user_language(self.db, user_id)

        if language == 'de':
            text = "⏸️ Motivierende Nachrichten wurden pausiert. Verwende /resume um sie wieder zu aktivieren."
        else:
            text = "⏸️ Motivational messages have been paused. Use /resume to reactivate them."

        await update.message.reply_text(text)

    async def resume_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Resume motivational messages"""
        user_id = update.effective_user.id
        self.db.update_user_setting(user_id, 'active', True)

        language = get_user_language(self.db, user_id)

        if language == 'de':
            text = "▶️ Motivierende Nachrichten wurden wieder aktiviert! 🌟"
        else:
            text = "▶️ Motivational messages have been resumed! 🌟"

        await update.message.reply_text(text)

    async def forget_me(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Delete the user's AI chat memory (history, summary, facts)"""
        user_id = update.effective_user.id
        language = self.get_user_language(user_id)

        success = self.db.delete_chat_memory(user_id)

        if language == 'de':
            if success:
                text = ("🗑️ Erledigt! Ich habe unseren Gesprächsverlauf, die Zusammenfassung "
                        "und alles, was ich mir über dich gemerkt hatte, gelöscht.\n\n"
                        "Deine Einstellungen und Stimmungseinträge bleiben erhalten — "
                        "die kannst du über /settings → Zurücksetzen löschen.")
            else:
                text = "❌ Beim Löschen ist etwas schiefgegangen. Versuche es später nochmal."
        else:
            if success:
                text = ("🗑️ Done! I deleted our conversation history, the summary, "
                        "and everything I had remembered about you.\n\n"
                        "Your settings and mood entries are kept — you can delete "
                        "those via /settings → Reset.")
            else:
                text = "❌ Something went wrong while deleting. Please try again later."

        await update.message.reply_text(text)

    async def _send_feedback_buttons(self, update: Update, language: str, message_id: int):
        """Send instant-feedback buttons referencing a just-sent message"""
        keyboard = [
            [
                InlineKeyboardButton("❤️", callback_data=f"feedback_love_{message_id}"),
                InlineKeyboardButton("👍", callback_data=f"feedback_like_{message_id}"),
                InlineKeyboardButton("👎", callback_data=f"feedback_dislike_{message_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if language == 'de':
            feedback_text = "💭 Wie hilfreich war diese Nachricht?"
        else:
            feedback_text = "💭 How helpful was this message?"

        await update.message.reply_text(feedback_text, reply_markup=reply_markup)

    async def motivate_me(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send an instant motivational message"""
        user_id = update.effective_user.id

        # Add user to database if not exists
        self.db.add_user(user_id, update.effective_user.username, update.effective_user.first_name)

        language = get_user_language(self.db, user_id)

        # Get recent mood to personalize content
        recent_mood = self.db.get_recent_mood(user_id, 1)
        mood_score = recent_mood[0]['score'] if recent_mood else 5  # Default to neutral mood

        # Try AI-generated motivation first, fall back to static content
        ai_text = await ai_motivator.generate_motivation(
            language, mood_score, update.effective_user.first_name,
            self.db.get_user_facts(user_id), user_id=user_id
        )
        if ai_text:
            try:
                message = await update.message.reply_text(ai_text)
                self.db.log_sent_message(user_id, message.message_id, 'ai_text')
                await self._send_feedback_buttons(update, language, message.message_id)
                return
            except Exception as e:
                logger.error(f"Error sending AI motivation to user {user_id}: {e}")

        # Get appropriate content based on mood
        content = self.content_manager.get_content_by_mood(mood_score, language)

        if not content:
            # Fallback to random content if mood-based selection fails
            content = self.content_manager.get_random_content(language)

        if not content:
            # Ultimate fallback
            if language == 'de':
                fallback_text = "🌟 Du schaffst das! Jeder Tag bringt neue Möglichkeiten. 💪"
            else:
                fallback_text = "🌟 You've got this! Every day brings new opportunities. 💪"

            await update.message.reply_text(fallback_text)
            return

        try:
            # Send the motivational content
            if content.content_type.value == 'text':
                message = await update.message.reply_text(
                    content.content,
                    parse_mode=ParseMode.MARKDOWN
                )
            elif content.content_type.value in ['video', 'link'] and content.media_url:
                message = await update.message.reply_text(
                    f"{content.content}\n\n🔗 {content.media_url}",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                message = await update.message.reply_text(content.content)

            # Log the sent message
            self.db.log_sent_message(user_id, message.message_id, content.content_type.value, content.id)

            # Add feedback buttons for instant feedback
            await self._send_feedback_buttons(update, language, message.message_id)

        except Exception as e:
            logger.error(f"Error sending motivational message to user {user_id}: {e}")

            if language == 'de':
                error_text = "Entschuldigung, es gab ein Problem beim Senden deiner Motivation. Versuche es später nochmal! 🤗"
            else:
                error_text = "Sorry, there was a problem sending your motivation. Please try again later! 🤗"

            await update.message.reply_text(error_text)
