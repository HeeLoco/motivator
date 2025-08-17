import os
import logging
import asyncio
from datetime import datetime, timedelta
import random
from typing import Optional

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode

from database import Database
from content import ContentManager, MoodCategory, ContentType
from smart_scheduler import SmartMessageScheduler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MotivatorBot:
    def __init__(self, bot_token: str, admin_user_id: int = None):
        self.bot_token = bot_token
        self.admin_user_id = admin_user_id
        self.db = Database()
        self.content_manager = ContentManager()
        self.scheduler = SmartMessageScheduler(self.db, self.content_manager)
        
        # Create application
        self.application = Application.builder().token(bot_token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup command and message handlers"""
        # Commands
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("settings", self.settings))
        self.application.add_handler(CommandHandler("mood", self.mood_check))
        self.application.add_handler(CommandHandler("goals", self.goals))
        self.application.add_handler(CommandHandler("stats", self.stats))
        self.application.add_handler(CommandHandler("pause", self.pause_messages))
        self.application.add_handler(CommandHandler("resume", self.resume_messages))
        self.application.add_handler(CommandHandler("motivateMe", self.motivate_me))
        
        # Admin commands
        self.application.add_handler(CommandHandler("admin_stats", self.admin_stats))
        self.application.add_handler(CommandHandler("admin_broadcast", self.admin_broadcast))
        self.application.add_handler(CommandHandler("admin_users", self.admin_users))
        self.application.add_handler(CommandHandler("admin_content", self.admin_content))
        self.application.add_handler(CommandHandler("admin_reset", self.admin_reset))
        
        # Callback query handler for inline keyboards
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command - welcome new users"""
        user = update.effective_user
        
        # Add user to database
        self.db.add_user(user.id, user.username, user.first_name)
        
        welcome_text = f"""
🌟 *Willkommen beim MotivatOR Bot, {user.first_name}!* 🌟

Ich bin hier, um dich mit personalisierten motivierenden Nachrichten den ganzen Tag über zu unterstützen.

*Was ich kann:*
• Dir motivierende Nachrichten zu zufälligen Zeiten senden
• Dir beim Verfolgen deiner Stimmung und Ziele helfen
• Unterstützungsressourcen bereitstellen, wenn du sie brauchst
• Nachrichten basierend auf deinem Feedback anpassen

*Schnelle Einrichtung:*
/settings - Deine Einstellungen konfigurieren
/mood - Verfolge, wie du dich heute fühlst
/goals - Setze persönliche Ziele für Motivation

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
        user_settings = self.db.get_user_settings(update.effective_user.id)
        language = user_settings.get('language', 'de') if user_settings else 'de'
        
        if language == 'de':
            help_text = """
🤖 *MotivatOR Bot Hilfe*

*Befehle:*
/start - Bot starten und einrichten
/settings - Einstellungen anpassen
/mood - Stimmung eingeben (1-10)
/goals - Ziele verwalten
/stats - Deine Statistiken anzeigen
/motivateMe - Sofortige Motivation erhalten!
/pause - Nachrichten pausieren
/resume - Nachrichten wieder aktivieren
/help - Diese Hilfe anzeigen

*Funktionen:*
• Erhalte personalisierte motivierende Nachrichten
• Verfolge deine Stimmung und Fortschritte
• Stelle deine Nachrichtenhäufigkeit ein
• Gib Feedback zu Nachrichten
• Setze und verfolge persönliche Ziele

*Feedback geben:*
Antworte einfach auf meine Nachrichten mit:
• ❤️ für hilfreich
• 👍 für okay  
• 👎 für nicht hilfreich

Ich bin hier, um dich zu unterstützen! 💙
"""
        else:
            help_text = """
🤖 *MotivatOR Bot Help*

*Commands:*
/start - Start and setup the bot
/settings - Adjust your preferences  
/mood - Log your mood (1-10 scale)
/goals - Manage your personal goals
/stats - View your statistics
/motivateMe - Get instant motivation right now!
/pause - Pause motivational messages
/resume - Resume receiving messages
/help - Show this help message

*Features:*
• Receive personalized motivational messages
• Track your mood and progress over time
• Customize message frequency and timing
• Give feedback on messages I send
• Set and track personal goals

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
        
        language = user_settings['language']
        frequency = user_settings['message_frequency']
        active = "✅ Active" if user_settings['active'] else "⏸️ Paused"
        
        if language == 'de':
            settings_text = f"""
⚙️ *Deine Einstellungen*

Sprache: {'🇩🇪 Deutsch' if language == 'de' else '🇬🇧 English'}
Nachrichten pro Tag: {frequency}
Status: {active}

Was möchtest du ändern?
"""
            keyboard = [
                [InlineKeyboardButton("🌍 Sprache", callback_data="set_language")],
                [InlineKeyboardButton("📊 Häufigkeit", callback_data="set_frequency")],
                [InlineKeyboardButton("⏸️ Pausieren" if user_settings['active'] else "▶️ Fortsetzen", 
                                    callback_data="toggle_active")],
                [InlineKeyboardButton("⏰ Zeiten", callback_data="set_timing")],
                [InlineKeyboardButton("🔄 Zurücksetzen", callback_data="reset_user")],
                [InlineKeyboardButton("❌ Schließen", callback_data="close_menu")]
            ]
        else:
            settings_text = f"""
⚙️ *Your Settings*

Language: {'🇩🇪 Deutsch' if language == 'de' else '🇬🇧 English'}
Messages per day: {frequency}
Status: {active}

What would you like to change?
"""
            keyboard = [
                [InlineKeyboardButton("🌍 Language", callback_data="set_language")],
                [InlineKeyboardButton("📊 Frequency", callback_data="set_frequency")],
                [InlineKeyboardButton("⏸️ Pause" if user_settings['active'] else "▶️ Resume", 
                                    callback_data="toggle_active")],
                [InlineKeyboardButton("⏰ Timing", callback_data="set_timing")],
                [InlineKeyboardButton("🔄 Reset", callback_data="reset_user")],
                [InlineKeyboardButton("❌ Close", callback_data="close_menu")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            settings_text, 
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def mood_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mood tracking interface"""
        user_settings = self.db.get_user_settings(update.effective_user.id)
        language = user_settings.get('language', 'de') if user_settings else 'de'
        
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
    
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user statistics"""
        user_id = update.effective_user.id
        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'
        
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
    
    async def pause_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Pause motivational messages"""
        user_id = update.effective_user.id
        self.db.update_user_setting(user_id, 'active', False)
        
        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'
        
        if language == 'de':
            text = "⏸️ Motivierende Nachrichten wurden pausiert. Verwende /resume um sie wieder zu aktivieren."
        else:
            text = "⏸️ Motivational messages have been paused. Use /resume to reactivate them."
        
        await update.message.reply_text(text)
    
    async def resume_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Resume motivational messages"""
        user_id = update.effective_user.id
        self.db.update_user_setting(user_id, 'active', True)
        
        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'
        
        if language == 'de':
            text = "▶️ Motivierende Nachrichten wurden wieder aktiviert! 🌟"
        else:
            text = "▶️ Motivational messages have been resumed! 🌟"
        
        await update.message.reply_text(text)
    
    async def motivate_me(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send an instant motivational message"""
        user_id = update.effective_user.id
        
        # Add user to database if not exists
        self.db.add_user(user_id, update.effective_user.username, update.effective_user.first_name)
        
        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'
        
        # Get recent mood to personalize content
        recent_mood = self.db.get_recent_mood(user_id, 1)
        mood_score = recent_mood[0]['score'] if recent_mood else 5  # Default to neutral mood
        
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
            keyboard = [
                [
                    InlineKeyboardButton("❤️", callback_data=f"feedback_love_{message.message_id}"),
                    InlineKeyboardButton("👍", callback_data=f"feedback_like_{message.message_id}"),
                    InlineKeyboardButton("👎", callback_data=f"feedback_dislike_{message.message_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if language == 'de':
                feedback_text = "💭 Wie hilfreich war diese Nachricht?"
            else:
                feedback_text = "💭 How helpful was this message?"
            
            await update.message.reply_text(
                feedback_text,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error sending motivational message to user {user_id}: {e}")
            
            if language == 'de':
                error_text = "Entschuldigung, es gab ein Problem beim Senden deiner Motivation. Versuche es später nochmal! 🤗"
            else:
                error_text = "Sorry, there was an issue sending your motivation. Please try again later! 🤗"
            
            await update.message.reply_text(error_text)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if data.startswith("lang_"):
            language = data.split("_")[1]
            self.db.update_user_setting(user_id, 'language', language)
            
            if language == 'de':
                text = "🇩🇪 Sprache auf Deutsch eingestellt!\n\nVerwende /settings um weitere Einstellungen anzupassen."
            else:
                text = "🇬🇧 Language set to English!\n\nUse /settings to adjust more preferences."
            
            await query.edit_message_text(text)
            
        elif data.startswith("mood_"):
            mood_score = int(data.split("_")[1])
            self.db.add_mood_entry(user_id, mood_score)
            
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'
            
            # Send appropriate response based on mood
            content = self.content_manager.get_content_by_mood(mood_score, language)
            
            if language == 'de':
                response = f"Danke für dein Feedback! Stimmung: {mood_score}/10 📝\n\n"
            else:
                response = f"Thanks for sharing! Mood logged: {mood_score}/10 📝\n\n"
            
            if content:
                response += content.content
                if content.media_url:
                    response += f"\n\n🔗 {content.media_url}"
            
            await query.edit_message_text(response)
            
        elif data == "close_menu":
            await query.delete_message()
            
        elif data.startswith("feedback_"):
            # Handle feedback from /motivateMe command
            feedback_parts = data.split("_")
            feedback_type = feedback_parts[1]  # love, like, dislike
            message_id = int(feedback_parts[2])
            
            # Map feedback type to database values
            feedback_map = {
                'love': 'very_positive',
                'like': 'positive', 
                'dislike': 'negative'
            }
            
            feedback_value = feedback_map.get(feedback_type, 'neutral')
            
            # Log feedback
            self.db.add_feedback(user_id, message_id, 'instant_feedback', feedback_value)
            
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'
            
            # Send thank you message
            if language == 'de':
                if feedback_type == 'love':
                    thanks_text = "❤️ Vielen Dank! Freut mich, dass dir die Nachricht geholfen hat!"
                elif feedback_type == 'like':
                    thanks_text = "👍 Danke für dein Feedback! Das hilft mir zu lernen."
                else:
                    thanks_text = "👎 Danke für dein ehrliches Feedback. Ich werde versuchen, bessere Nachrichten zu senden."
            else:
                if feedback_type == 'love':
                    thanks_text = "❤️ Thank you! So glad that message helped you!"
                elif feedback_type == 'like':
                    thanks_text = "👍 Thanks for the feedback! This helps me learn."
                else:
                    thanks_text = "👎 Thanks for your honest feedback. I'll try to send better messages."
            
            await query.edit_message_text(thanks_text)
        
        elif data == "set_language":
            # Show language selection menu
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'
            
            if language == 'de':
                text = "🌍 Sprache wählen:"
            else:
                text = "🌍 Choose language:"
            
            keyboard = [
                [InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de")],
                [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
                [InlineKeyboardButton("⬅️ Zurück" if language == 'de' else "⬅️ Back", callback_data="back_to_settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        elif data == "set_frequency":
            # Show frequency selection menu
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'
            current_freq = user_settings.get('message_frequency', 2) if user_settings else 2
            
            if language == 'de':
                text = f"📊 Nachrichtenhäufigkeit pro Tag:\nAktuell: {current_freq} Nachrichten\n\nWähle eine neue Häufigkeit:"
            else:
                text = f"📊 Message frequency per day:\nCurrent: {current_freq} messages\n\nSelect new frequency:"
            
            keyboard = []
            for i in range(1, 6):  # 1-5 messages per day
                emoji = "📧" * i
                keyboard.append([InlineKeyboardButton(f"{emoji} {i}", callback_data=f"freq_{i}")])
            
            keyboard.append([InlineKeyboardButton("⬅️ Zurück" if language == 'de' else "⬅️ Back", callback_data="back_to_settings")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
        
        elif data == "toggle_active":
            # Toggle active status
            user_settings = self.db.get_user_settings(user_id)
            current_active = user_settings.get('active', True) if user_settings else True
            new_active = not current_active
            
            self.db.update_user_setting(user_id, 'active', new_active)
            
            language = user_settings.get('language', 'de') if user_settings else 'de'
            
            if language == 'de':
                if new_active:
                    text = "✅ Nachrichten wurden wieder aktiviert!\n\nVerwende /settings um weitere Einstellungen anzupassen."
                else:
                    text = "⏸️ Nachrichten wurden pausiert.\n\nVerwende /settings um sie wieder zu aktivieren."
            else:
                if new_active:
                    text = "✅ Messages have been resumed!\n\nUse /settings to adjust more preferences."
                else:
                    text = "⏸️ Messages have been paused.\n\nUse /settings to reactivate them."
            
            await query.edit_message_text(text)
        
        elif data.startswith("freq_"):
            # Handle frequency selection
            frequency = int(data.split("_")[1])
            self.db.update_user_setting(user_id, 'message_frequency', frequency)
            
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'
            
            if language == 'de':
                text = f"📊 Nachrichtenhäufigkeit auf {frequency} pro Tag eingestellt!\n\nVerwende /settings um weitere Einstellungen anzupassen."
            else:
                text = f"📊 Message frequency set to {frequency} per day!\n\nUse /settings to adjust more preferences."
            
            await query.edit_message_text(text)
        
        elif data == "set_timing":
            # Show timing preferences menu
            user_settings = self.db.get_user_settings(user_id)
            timing_prefs = self.db.get_user_timing_preferences(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'
            
            if timing_prefs:
                start_time = f"{timing_prefs['active_start_hour']:02d}:{timing_prefs['active_start_minute']:02d}"
                end_time = f"{timing_prefs['active_end_hour']:02d}:{timing_prefs['active_end_minute']:02d}"
                min_gap = timing_prefs['min_gap_hours']
                
                if language == 'de':
                    text = f"""⏰ *Nachrichten-Zeiten*

Aktuelle Einstellungen:
• Aktive Zeiten: {start_time} - {end_time}
• Mindestabstand: {min_gap} Stunde(n)

Was möchtest du ändern?"""
                else:
                    text = f"""⏰ *Message Timing*

Current settings:
• Active hours: {start_time} - {end_time}
• Minimum gap: {min_gap} hour(s)

What would you like to change?"""
                
                keyboard = [
                    [InlineKeyboardButton("🌅 Start-Zeit" if language == 'de' else "🌅 Start Time", callback_data="set_start_time")],
                    [InlineKeyboardButton("🌙 End-Zeit" if language == 'de' else "🌙 End Time", callback_data="set_end_time")],
                    [InlineKeyboardButton("⏱️ Mindestabstand" if language == 'de' else "⏱️ Min Gap", callback_data="set_min_gap")],
                    [InlineKeyboardButton("⬅️ Zurück" if language == 'de' else "⬅️ Back", callback_data="back_to_settings")]
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            else:
                await query.edit_message_text("❌ Fehler beim Laden der Timing-Einstellungen." if language == 'de' else "❌ Error loading timing settings.")
        
        elif data == "set_start_time":
            # Show start time selection
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'
            
            if language == 'de':
                text = "🌅 *Start-Zeit wählen*\n\nWann sollen die Nachrichten beginnen?"
            else:
                text = "🌅 *Choose Start Time*\n\nWhen should messages begin?"
            
            keyboard = []
            for hour in range(6, 12):  # 6 AM to 11 AM
                time_str = f"{hour:02d}:00"
                keyboard.append([InlineKeyboardButton(time_str, callback_data=f"start_time_{hour}")])
            
            keyboard.append([InlineKeyboardButton("⬅️ Zurück" if language == 'de' else "⬅️ Back", callback_data="set_timing")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        
        elif data == "set_end_time":
            # Show end time selection
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'
            
            if language == 'de':
                text = "🌙 *End-Zeit wählen*\n\nWann sollen die Nachrichten enden?"
            else:
                text = "🌙 *Choose End Time*\n\nWhen should messages end?"
            
            keyboard = []
            for hour in range(18, 24):  # 6 PM to 11 PM
                time_str = f"{hour:02d}:00"
                keyboard.append([InlineKeyboardButton(time_str, callback_data=f"end_time_{hour}")])
            
            keyboard.append([InlineKeyboardButton("⬅️ Zurück" if language == 'de' else "⬅️ Back", callback_data="set_timing")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        
        elif data == "set_min_gap":
            # Show minimum gap selection
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'
            
            if language == 'de':
                text = "⏱️ *Mindestabstand wählen*\n\nWie viele Stunden sollen mindestens zwischen Nachrichten liegen?"
            else:
                text = "⏱️ *Choose Minimum Gap*\n\nHow many hours minimum between messages?"
            
            keyboard = []
            for hours in [1, 2, 3, 4, 6]:
                if language == 'de':
                    label = f"{hours} Stunde{'n' if hours > 1 else ''}"
                else:
                    label = f"{hours} hour{'s' if hours > 1 else ''}"
                keyboard.append([InlineKeyboardButton(label, callback_data=f"min_gap_{hours}")])
            
            keyboard.append([InlineKeyboardButton("⬅️ Zurück" if language == 'de' else "⬅️ Back", callback_data="set_timing")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        
        elif data.startswith("start_time_"):
            # Handle start time selection
            hour = int(data.split("_")[-1])
            self.db.update_timing_preference(user_id, 'active_start_hour', hour)
            
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'
            
            if language == 'de':
                text = f"✅ Start-Zeit auf {hour:02d}:00 eingestellt!\n\nVerwende /settings um weitere Einstellungen anzupassen."
            else:
                text = f"✅ Start time set to {hour:02d}:00!\n\nUse /settings to adjust more preferences."
            
            await query.edit_message_text(text)
        
        elif data.startswith("end_time_"):
            # Handle end time selection
            hour = int(data.split("_")[-1])
            self.db.update_timing_preference(user_id, 'active_end_hour', hour)
            
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'
            
            if language == 'de':
                text = f"✅ End-Zeit auf {hour:02d}:00 eingestellt!\n\nVerwende /settings um weitere Einstellungen anzupassen."
            else:
                text = f"✅ End time set to {hour:02d}:00!\n\nUse /settings to adjust more preferences."
            
            await query.edit_message_text(text)
        
        elif data.startswith("min_gap_"):
            # Handle minimum gap selection
            hours = int(data.split("_")[-1])
            self.db.update_timing_preference(user_id, 'min_gap_hours', hours)
            
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'
            
            if language == 'de':
                text = f"✅ Mindestabstand auf {hours} Stunde{'n' if hours > 1 else ''} eingestellt!\n\nVerwende /settings um weitere Einstellungen anzupassen."
            else:
                text = f"✅ Minimum gap set to {hours} hour{'s' if hours > 1 else ''}!\n\nUse /settings to adjust more preferences."
            
            await query.edit_message_text(text)
        
        elif data == "reset_user":
            # Show reset confirmation
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'
            
            if language == 'de':
                text = """⚠️ *Warnung: Daten zurücksetzen*

Das wird ALLE deine Daten löschen:
• Alle Einstellungen zurücksetzen
• Stimmungseinträge löschen  
• Ziele löschen
• Feedback-Historie löschen
• Nachrichtenverlauf löschen

Bist du sicher, dass du fortfahren möchtest?

*Diese Aktion kann nicht rückgängig gemacht werden!*"""
            else:
                text = """⚠️ *Warning: Reset Data*

This will DELETE ALL your data:
• Reset all settings
• Delete mood entries
• Delete goals
• Delete feedback history
• Delete message history

Are you sure you want to continue?

*This action cannot be undone!*"""
            
            keyboard = [
                [InlineKeyboardButton("⚠️ Ja, alles löschen" if language == 'de' else "⚠️ Yes, delete all", callback_data="confirm_reset")],
                [InlineKeyboardButton("❌ Abbrechen" if language == 'de' else "❌ Cancel", callback_data="back_to_settings")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        
        elif data == "confirm_reset":
            # Actually perform the reset
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'de') if user_settings else 'de'
            
            # Reset user data
            success = self.db.reset_user_data(user_id)
            
            if success:
                if language == 'de':
                    text = """✅ *Zurücksetzung erfolgreich!*

Alle deine Daten wurden gelöscht und Einstellungen zurückgesetzt:

• Sprache: Deutsch
• Nachrichten pro Tag: 2
• Status: Aktiv
• Alle Historie gelöscht

Du kannst jetzt mit /settings neue Einstellungen vornehmen."""
                else:
                    text = """✅ *Reset Successful!*

All your data has been deleted and settings reset:

• Language: German  
• Messages per day: 2
• Status: Active
• All history cleared

You can now use /settings to configure new preferences."""
            else:
                if language == 'de':
                    text = "❌ Fehler beim Zurücksetzen der Daten. Bitte versuche es später erneut."
                else:
                    text = "❌ Error resetting data. Please try again later."
            
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)
        
        elif data == "back_to_settings":
            # Go back to settings menu - recreate the settings message
            user_settings = self.db.get_user_settings(user_id)
            if not user_settings:
                await query.edit_message_text("Please start the bot first with /start")
                return
            
            language = user_settings['language']
            frequency = user_settings['message_frequency']
            active = "✅ Active" if user_settings['active'] else "⏸️ Paused"
            
            if language == 'de':
                settings_text = f"""
⚙️ *Deine Einstellungen*

Sprache: {'🇩🇪 Deutsch' if language == 'de' else '🇬🇧 English'}
Nachrichten pro Tag: {frequency}
Status: {active}

Was möchtest du ändern?
"""
                keyboard = [
                    [InlineKeyboardButton("🌍 Sprache", callback_data="set_language")],
                    [InlineKeyboardButton("📊 Häufigkeit", callback_data="set_frequency")],
                    [InlineKeyboardButton("⏸️ Pausieren" if user_settings['active'] else "▶️ Fortsetzen", 
                                        callback_data="toggle_active")],
                    [InlineKeyboardButton("⏰ Zeiten", callback_data="set_timing")],
                    [InlineKeyboardButton("🔄 Zurücksetzen", callback_data="reset_user")],
                    [InlineKeyboardButton("❌ Schließen", callback_data="close_menu")]
                ]
            else:
                settings_text = f"""
⚙️ *Your Settings*

Language: {'🇩🇪 Deutsch' if language == 'de' else '🇬🇧 English'}
Messages per day: {frequency}
Status: {active}

What would you like to change?
"""
                keyboard = [
                    [InlineKeyboardButton("🌍 Language", callback_data="set_language")],
                    [InlineKeyboardButton("📊 Frequency", callback_data="set_frequency")],
                    [InlineKeyboardButton("⏸️ Pause" if user_settings['active'] else "▶️ Resume", 
                                        callback_data="toggle_active")],
                    [InlineKeyboardButton("⏰ Timing", callback_data="set_timing")],
                    [InlineKeyboardButton("🔄 Reset", callback_data="reset_user")],
                    [InlineKeyboardButton("❌ Close", callback_data="close_menu")]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                settings_text, 
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        
        elif data == "confirm_broadcast":
            # Execute the broadcast
            user_id = query.from_user.id
            
            # Double-check admin permissions
            if self.admin_user_id is None or user_id != self.admin_user_id:
                await query.edit_message_text("❌ Admin access required.")
                return
            
            # Get the stored broadcast message
            broadcast_message = context.user_data.get('broadcast_message')
            if not broadcast_message:
                await query.edit_message_text("❌ Broadcast message not found. Please try again.")
                return
            
            # Start broadcasting
            await query.edit_message_text("📢 Broadcasting message... Please wait.")
            
            # Get all users
            all_users = self.db.get_all_users()
            sent_count = 0
            failed_count = 0
            
            for target_user_id in all_users:
                try:
                    await self.application.bot.send_message(
                        chat_id=target_user_id,
                        text=f"📢 *Admin Message*\n\n{broadcast_message}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    sent_count += 1
                except Exception as e:
                    logger.warning(f"Failed to send broadcast to user {target_user_id}: {e}")
                    failed_count += 1
            
            # Report results
            result_text = f"""
✅ *Broadcast Complete*

📊 Results:
• Sent successfully: {sent_count}
• Failed to send: {failed_count}
• Total users: {len(all_users)}

Message: "{broadcast_message}"
"""
            
            await query.edit_message_text(result_text, parse_mode=ParseMode.MARKDOWN)
            
            # Clear the stored message
            context.user_data.pop('broadcast_message', None)
        
        elif data == "cancel_broadcast":
            # Cancel the broadcast
            context.user_data.pop('broadcast_message', None)
            await query.edit_message_text("❌ Broadcast cancelled.")
        
        elif data.startswith("admin_reset_confirm_"):
            # Execute admin reset for specific user
            user_id = query.from_user.id
            
            # Double-check admin permissions
            if self.admin_user_id is None or user_id != self.admin_user_id:
                await query.edit_message_text("❌ Admin access required.")
                return
            
            # Extract target user ID
            target_user_id = int(data.split("_")[-1])
            
            # Get user details for confirmation message
            user_details = self.db.get_user_detailed_info(target_user_id)
            if not user_details:
                await query.edit_message_text(f"❌ User {target_user_id} not found.")
                return
            
            # Start reset process
            await query.edit_message_text("🔄 Resetting user data... Please wait.")
            
            # Perform the reset
            success = self.db.reset_user_data(target_user_id)
            
            user_name = user_details['first_name'] or 'Unknown'
            
            if success:
                result_text = f"""✅ *User Data Reset Complete*

**User:** {user_name} (ID: `{target_user_id}`)

**Actions performed:**
• Settings reset to defaults (German, 2 msg/day, active)
• All mood entries deleted
• All goals deleted  
• All feedback deleted
• Message history cleared

The user can now start fresh with default settings."""
            else:
                result_text = f"❌ *Reset Failed*\n\nFailed to reset data for user {user_name} (ID: `{target_user_id}`).\n\nCheck logs for details."
            
            await query.edit_message_text(result_text, parse_mode=ParseMode.MARKDOWN)
        
        elif data == "admin_reset_cancel":
            # Cancel the admin reset
            await query.edit_message_text("❌ User data reset cancelled.")
        
        # Add more callback handlers for goals, etc.
    
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
    
    async def admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show admin statistics - only for admin users"""
        user_id = update.effective_user.id
        
        # Check if user is admin
        if self.admin_user_id is None or user_id != self.admin_user_id:
            await update.message.reply_text("❌ This command is only available to administrators.")
            return
        
        try:
            # Get all users
            all_users = self.db.get_active_users()  # This gets active users
            # Let's get total users (active + inactive)
            total_users = len(self.db.get_all_users())  # We'll need to create this method
            active_users = len(all_users)
            inactive_users = total_users - active_users
            
            # Get global message statistics
            global_message_stats = self.db.get_message_stats()
            total_messages = sum(global_message_stats.values())
            
            # Get total mood entries
            total_mood_entries = self.db.get_total_mood_entries()  # We'll need to create this
            
            # Get recent activity (users active in last 7 days)
            recent_active = self.db.get_recently_active_users(7)  # We'll need to create this
            
            stats_text = f"""
📊 *Admin Statistics Dashboard*

👥 *Users:*
• Total registered: {total_users}
• Active: {active_users}
• Inactive/Paused: {inactive_users}
• Active in last 7 days: {len(recent_active)}

📧 *Messages sent:*
• Total: {total_messages}
• Text: {global_message_stats.get('text', 0)}
• Media: {global_message_stats.get('image', 0) + global_message_stats.get('video', 0)}
• Links: {global_message_stats.get('link', 0)}

📈 *Engagement:*
• Total mood entries: {total_mood_entries}
• Avg messages per user: {total_messages / total_users if total_users > 0 else 0:.1f}
"""
            
            await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in admin_stats: {e}")
            await update.message.reply_text("❌ Error retrieving statistics. Check logs for details.")
    
    async def admin_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send broadcast message to all users - only for admin users"""
        user_id = update.effective_user.id
        
        # Check if user is admin
        if self.admin_user_id is None or user_id != self.admin_user_id:
            await update.message.reply_text("❌ This command is only available to administrators.")
            return
        
        # Check if message text was provided
        if not context.args:
            await update.message.reply_text(
                "📢 *Admin Broadcast*\n\n"
                "Usage: `/admin_broadcast <message>`\n\n"
                "Example: `/admin_broadcast Hello everyone! The bot has been updated with new features.`\n\n"
                "This will send the message to ALL registered users.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get the broadcast message
        broadcast_message = " ".join(context.args)
        
        # Show confirmation
        confirmation_text = f"""
📢 *Broadcast Confirmation*

Message to send:
"{broadcast_message}"

This will be sent to ALL users. Continue?
"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Send to All Users", callback_data=f"confirm_broadcast")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Store the broadcast message temporarily (we'll need to handle this in callback)
        context.user_data['broadcast_message'] = broadcast_message
        
        # Safety check for message object
        if update.message:
            await update.message.reply_text(
                confirmation_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            # Fallback if called from callback query
            await update.effective_chat.send_message(
                confirmation_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    
    async def admin_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show list of all users or detailed info for specific user - only for admin users"""
        user_id = update.effective_user.id
        
        # Check if user is admin
        if self.admin_user_id is None or user_id != self.admin_user_id:
            await update.message.reply_text("❌ This command is only available to administrators.")
            return
        
        try:
            # Check if specific user ID was provided
            if context.args:
                # Show detailed info for specific user
                try:
                    target_user_id = int(context.args[0])
                except ValueError:
                    await update.message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
                    return
                
                # Get detailed user info
                user_details = self.db.get_user_detailed_info(target_user_id)
                
                if not user_details:
                    await update.message.reply_text(f"❌ User `{target_user_id}` not found in database.", parse_mode=ParseMode.MARKDOWN)
                    return
                
                # Get additional statistics for this user
                mood_entries = self.db.get_recent_mood(target_user_id, 30)  # Last 30 days
                message_stats = self.db.get_message_stats(target_user_id)
                total_messages = sum(message_stats.values())
                
                # Calculate average mood
                avg_mood = (sum(m['score'] for m in mood_entries) / len(mood_entries)) if mood_entries else None
                
                # Format detailed user info
                user_text = f"""
👤 *Detailed User Information*

🆔 **User ID:** `{user_details['user_id']}`
📛 **Name:** {user_details['first_name'] or 'No name'}
👤 **Username:** @{user_details['username'] or 'No username'}
🌍 **Language:** {user_details['language']}
📊 **Messages per day:** {user_details['message_frequency']}
🔄 **Status:** {'✅ Active' if user_details['active'] else '⏸️ Paused'}

📅 **Activity:**
• Created: {user_details['created_at'][:10] if user_details['created_at'] else 'Unknown'}
• Last active: {user_details['last_active'][:10] if user_details['last_active'] else 'Never'}

📈 **Statistics:**
• Messages received: {total_messages}
• Mood entries (30d): {len(mood_entries)}
• Avg mood (30d): {f'{avg_mood:.1f}/10' if avg_mood else 'No data'}

📧 **Message breakdown:**
• Text: {message_stats.get('text', 0)}
• Media: {message_stats.get('image', 0) + message_stats.get('video', 0)}
• Links: {message_stats.get('link', 0)}
"""
                
                # Safety check for message object
                if update.message:
                    await update.message.reply_text(user_text, parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.effective_chat.send_message(user_text, parse_mode=ParseMode.MARKDOWN)
                
            else:
                # Show list of all users (original functionality)
                users_info = self.db.get_all_users_detailed()
                
                if not users_info:
                    await update.message.reply_text("📝 No users found in database.")
                    return
                
                # Format user list with usage help
                users_text = f"""👥 *All Registered Users*

💡 *Tip:* Use `/admin_users <user_id>` for detailed info

"""
                
                for i, user in enumerate(users_info, 1):
                    user_id_str = user['user_id']
                    username = user['username'] or "No username"
                    first_name = user['first_name'] or "No name"
                    language = user['language']
                    frequency = user['message_frequency']
                    active = "✅" if user['active'] else "⏸️"
                    last_active = user['last_active'][:10] if user['last_active'] else "Never"
                    
                    users_text += f"""
*{i}.* `{user_id_str}`
📛 {first_name} (@{username})
🌍 {language} | 📊 {frequency}/day | {active}
🕒 Last: {last_active}
"""
                    
                    # Telegram has message length limits, break into chunks if needed
                    if len(users_text) > 3500:  # Leave room for more text
                        users_text += f"\n... and {len(users_info) - i} more users"
                        break
                
                # Safety check for message object
                if update.message:
                    await update.message.reply_text(users_text, parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.effective_chat.send_message(users_text, parse_mode=ParseMode.MARKDOWN)
                
        except Exception as e:
            logger.error(f"Error in admin_users: {e}")
            await update.message.reply_text("❌ Error retrieving user information. Check logs for details.")
    
    async def admin_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manage motivational content - only for admin users"""
        user_id = update.effective_user.id
        
        # Check if user is admin
        if self.admin_user_id is None or user_id != self.admin_user_id:
            await update.message.reply_text("❌ This command is only available to administrators.")
            return
        
        try:
            # Check if specific action was provided
            if context.args and len(context.args) >= 1:
                action = context.args[0].lower()
                
                if action == "list":
                    # List all content
                    await self._admin_content_list(update, context)
                    
                elif action == "add":
                    # Add new content
                    await self._admin_content_add_help(update, context)
                    
                elif action == "remove":
                    # Remove content by ID
                    if len(context.args) >= 2:
                        try:
                            content_id = int(context.args[1])
                            await self._admin_content_remove(update, content_id)
                        except ValueError:
                            await update.message.reply_text("❌ Invalid content ID. Please provide a numeric ID.")
                    else:
                        await update.message.reply_text("❌ Please provide content ID to remove.\nUsage: `/admin_content remove <id>`", parse_mode=ParseMode.MARKDOWN)
                
                elif action == "stats":
                    # Show content statistics
                    await self._admin_content_stats(update)
                    
                else:
                    await self._admin_content_help(update)
            else:
                # Show help/menu
                await self._admin_content_help(update)
                
        except Exception as e:
            logger.error(f"Error in admin_content: {e}")
            await update.message.reply_text("❌ Error managing content. Check logs for details.")
    
    async def _admin_content_help(self, update: Update):
        """Show admin content management help"""
        help_text = """
📝 *Admin Content Management*

**Available commands:**
• `/admin_content list` - Show all content
• `/admin_content add` - Get help for adding content
• `/admin_content remove <id>` - Remove content by ID
• `/admin_content stats` - Show content statistics

**Examples:**
• `/admin_content list de` - List German content
• `/admin_content remove 15` - Remove content ID 15
"""
        
        # Safety check for message object
        if update.message:
            await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.effective_chat.send_message(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def _admin_content_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all motivational content"""
        try:
            # Check if language filter was provided
            language_filter = context.args[1] if len(context.args) >= 2 else None
            
            # Debug logging
            logger.info(f"Admin content list - args: {context.args}, language_filter: {language_filter}")
            
            if language_filter and language_filter not in ['en', 'de']:
                await update.message.reply_text("❌ Invalid language. Use 'en' or 'de'.")
                return
            
            # Get all content
            all_content = self.content_manager.get_all_content(language_filter)
            
            logger.info(f"Found {len(all_content)} content items for language: {language_filter}")
            
            if not all_content:
                msg = f"📝 No content found" + (f" for language '{language_filter}'" if language_filter else "") + "."
                await update.message.reply_text(msg)
                return
            
            # Format content list (using plain text to avoid Markdown issues)
            content_text = f"📝 Motivational Content"
            if language_filter:
                content_text += f" ({language_filter.upper()})"
            content_text += f"\n\nFound {len(all_content)} items:\n\n"
            
            for i, content in enumerate(all_content, 1):
                # Truncate content for display
                content_preview = content.content[:80] + "..." if len(content.content) > 80 else content.content
                
                content_text += f"{i}. ID: {content.id} | {content.language.upper()} | {content.category.value}\n"
                content_text += f"📱 {content.content_type.value.upper()}\n"
                content_text += f"💬 \"{content_preview}\"\n"
                
                if content.media_url:
                    content_text += f"🔗 {content.media_url}\n"
                content_text += "\n"
                
                # Telegram message length limit
                if len(content_text) > 3500:
                    content_text += f"... and {len(all_content) - i} more items\n"
                    break
            
            content_text += f"\n💡 Use /admin_content remove <id> to delete content"
            
            # Safety check for message object (send as plain text)
            if update.message:
                await update.message.reply_text(content_text)
            else:
                await update.effective_chat.send_message(content_text)
                
        except Exception as e:
            logger.error(f"Error in _admin_content_list: {e}")
            await update.message.reply_text(f"❌ Error listing content: {str(e)}")
    
    async def _admin_content_add_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help for adding content"""
        help_text = """
➕ *Adding New Content*

To add content, use the content manager directly or modify `content.py`.

**Content structure:**
• ID: Auto-assigned
• Content: The motivational text
• Type: TEXT, IMAGE, VIDEO, LINK  
• Language: 'en' or 'de'
• Category: ANXIETY, DEPRESSION, STRESS, MOTIVATION, SELF_CARE, GENERAL
• Media URL: Optional link for videos/images

**Categories:**
• `ANXIETY` - For anxiety support
• `DEPRESSION` - For depression support  
• `STRESS` - For stress management
• `MOTIVATION` - General motivation
• `SELF_CARE` - Self-care reminders
• `GENERAL` - General mental health

**Note:** Dynamic content addition via bot commands will be implemented in future updates. Currently, modify `content.py` directly.
"""
        
        # Safety check for message object
        if update.message:
            await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.effective_chat.send_message(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def _admin_content_remove(self, update: Update, content_id: int):
        """Remove content by ID"""
        # Remove the content
        success = self.content_manager.remove_content(content_id)
        
        if success:
            await update.message.reply_text(f"✅ Content ID `{content_id}` has been removed successfully.", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(f"❌ Content ID `{content_id}` not found or could not be removed.", parse_mode=ParseMode.MARKDOWN)
    
    async def _admin_content_stats(self, update: Update):
        """Show content statistics"""
        all_content = self.content_manager.get_all_content()
        
        # Count by language
        en_count = len([c for c in all_content if c.language == 'en'])
        de_count = len([c for c in all_content if c.language == 'de'])
        
        # Count by category
        from collections import Counter
        category_counts = Counter(c.category.value for c in all_content)
        
        # Count by type
        type_counts = Counter(c.content_type.value for c in all_content)
        
        # Build category list safely
        category_lines = []
        for category, count in category_counts.items():
            category_lines.append(f"• {category.replace('_', ' ').title()}: {count}")
        
        # Build type list safely  
        type_lines = []
        for content_type, count in type_counts.items():
            type_lines.append(f"• {content_type.upper()}: {count}")
        
        # Build complete stats text
        stats_text = f"""📊 *Content Statistics*

**Total content:** {len(all_content)}

**By language:**
• English: {en_count}
• German: {de_count}

**By category:**
{chr(10).join(category_lines)}

**By type:**
{chr(10).join(type_lines)}"""
        
        # Safety check for message object
        if update.message:
            await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.effective_chat.send_message(stats_text, parse_mode=ParseMode.MARKDOWN)
    
    async def admin_reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reset a specific user's data - only for admin users"""
        user_id = update.effective_user.id
        
        # Check if user is admin
        if self.admin_user_id is None or user_id != self.admin_user_id:
            await update.message.reply_text("❌ This command is only available to administrators.")
            return
        
        # Check if user ID was provided
        if not context.args:
            await update.message.reply_text(
                "🔄 *Admin Reset User Data*\n\n"
                "Usage: `/admin_reset <user_id>`\n\n"
                "Example: `/admin_reset 1153831100`\n\n"
                "This will reset ALL data for the specified user:\n"
                "• Settings reset to defaults\n"
                "• All mood entries deleted\n"
                "• All goals deleted\n"
                "• All feedback deleted\n"
                "• Message history deleted\n\n"
                "⚠️ *Warning: This action cannot be undone!*",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Validate user ID
        try:
            target_user_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
            return
        
        # Check if user exists
        user_details = self.db.get_user_detailed_info(target_user_id)
        if not user_details:
            await update.message.reply_text(f"❌ User `{target_user_id}` not found in database.", parse_mode=ParseMode.MARKDOWN)
            return
        
        # Show confirmation dialog
        user_name = user_details['first_name'] or 'Unknown'
        username = user_details['username'] or 'No username'
        
        confirmation_text = f"""⚠️ *Reset User Data Confirmation*

**Target User:**
🆔 ID: `{target_user_id}`
📛 Name: {user_name} (@{username})

**This will DELETE ALL data for this user:**
• Reset settings to defaults (German, 2 msg/day, active)
• Delete all mood entries
• Delete all goals
• Delete all feedback
• Delete all message history

**⚠️ This action cannot be undone!**

Are you sure you want to proceed?"""
        
        keyboard = [
            [InlineKeyboardButton("⚠️ Yes, Reset All Data", callback_data=f"admin_reset_confirm_{target_user_id}")],
            [InlineKeyboardButton("❌ Cancel", callback_data="admin_reset_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Safety check for message object
        if update.message:
            await update.message.reply_text(
                confirmation_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            await update.effective_chat.send_message(
                confirmation_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    
    async def send_motivational_message(self, user_id: int):
        """Send a motivational message to a user"""
        user_settings = self.db.get_user_settings(user_id)
        if not user_settings or not user_settings['active']:
            return
        
        language = user_settings['language']
        
        # Get recent mood to personalize content
        recent_mood = self.db.get_recent_mood(user_id, 1)
        mood_score = recent_mood[0]['score'] if recent_mood else 5
        
        # Get appropriate content
        content = self.content_manager.get_content_by_mood(mood_score, language)
        
        if not content:
            return
        
        try:
            if content.content_type == ContentType.TEXT:
                message = await self.application.bot.send_message(
                    chat_id=user_id,
                    text=content.content,
                    parse_mode=ParseMode.MARKDOWN
                )
            elif content.content_type == ContentType.VIDEO and content.media_url:
                message = await self.application.bot.send_message(
                    chat_id=user_id,
                    text=f"{content.content}\n\n🎥 {content.media_url}",
                    parse_mode=ParseMode.MARKDOWN
                )
            elif content.content_type == ContentType.LINK and content.media_url:
                message = await self.application.bot.send_message(
                    chat_id=user_id,
                    text=f"{content.content}\n\n🔗 {content.media_url}",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                message = await self.application.bot.send_message(
                    chat_id=user_id,
                    text=content.content
                )
            
            # Log the sent message
            self.db.log_sent_message(user_id, message.message_id, content.content_type.value, content.id)
            
        except Exception as e:
            logger.error(f"Error sending message to user {user_id}: {e}")
    
    def run(self):
        """Start the bot"""
        # Start the scheduler
        self.scheduler.start(self)
        
        # Start the bot
        logger.info("Starting MotivatOR Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)