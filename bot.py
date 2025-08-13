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
from scheduler import MessageScheduler

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
        self.scheduler = MessageScheduler(self.db, self.content_manager)
        
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
🌟 *Welcome to MotivatOR Bot, {user.first_name}!* 🌟

I'm here to support you with personalized motivational messages throughout the day. 

*What I can do:*
• Send you motivational messages at random times
• Help you track your mood and goals
• Provide support resources when you need them
• Adapt messages based on your feedback

*Quick Setup:*
/settings - Configure your preferences
/mood - Track how you're feeling today
/goals - Set personal goals for motivation

*Commands:*
/help - Show all available commands
/motivateMe - Get instant motivation right now!
/pause - Temporarily stop messages
/resume - Resume receiving messages

Let's start your journey to better mental wellness! 💪

Which language would you prefer?
"""
        
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de")]
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
        language = user_settings.get('language', 'en') if user_settings else 'en'
        
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
        language = user_settings.get('language', 'en') if user_settings else 'en'
        
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
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            mood_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def goals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Goals management interface"""
        user_settings = self.db.get_user_settings(update.effective_user.id)
        language = user_settings.get('language', 'en') if user_settings else 'en'
        
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
        language = user_settings.get('language', 'en') if user_settings else 'en'
        
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
        language = user_settings.get('language', 'en') if user_settings else 'en'
        
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
        language = user_settings.get('language', 'en') if user_settings else 'en'
        
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
        language = user_settings.get('language', 'en') if user_settings else 'en'
        
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
            language = user_settings.get('language', 'en') if user_settings else 'en'
            
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
            language = user_settings.get('language', 'en') if user_settings else 'en'
            
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
        
        # Add more callback handlers for settings, goals, etc.
    
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
            language = user_settings.get('language', 'en') if user_settings else 'en'
            
            if language == 'de':
                response = "Danke für dein Feedback! Das hilft mir zu lernen. 📝"
            else:
                response = "Thanks for your feedback! This helps me learn. 📝"
            
            await update.message.reply_text(response)
        else:
            # Regular message - could be goal setting or other input
            # For now, just acknowledge
            user_settings = self.db.get_user_settings(user_id)
            language = user_settings.get('language', 'en') if user_settings else 'en'
            
            if language == 'de':
                response = "Ich habe deine Nachricht erhalten! Verwende /help um alle verfügbaren Befehle zu sehen."
            else:
                response = "I received your message! Use /help to see all available commands."
            
            await update.message.reply_text(response)
    
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