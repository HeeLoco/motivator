"""
Motivator Bot - Main orchestrator module.

This module coordinates all bot handlers and manages the application lifecycle.
Refactored architecture with separated concerns:
- Callbacks routed through handlers/callbacks/router.py
- Commands handled by domain-specific handlers
- Business logic isolated from presentation layer
"""

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from .database import Database
from .content import ContentManager
from .smart_scheduler import SmartMessageScheduler
from .logging_config import get_logger

# Import all command handlers
from .handlers.user_commands import UserCommandHandler
from .handlers.mood_commands import MoodCommandHandler
from .handlers.admin_commands import AdminCommandHandler
from .handlers.message_handler import MessageHandler as TextMessageHandler
from .handlers.callbacks import CallbackRouter

logger = get_logger(__name__)


class MotivatorBot:
    """Main bot orchestrator - coordinates handlers and manages application lifecycle"""

    def __init__(self, bot_token: str, admin_user_id: int = None):
        """
        Initialize Motivator Bot with all dependencies.

        Args:
            bot_token: Telegram bot token from BotFather
            admin_user_id: Optional admin user ID for admin commands
        """
        self.bot_token = bot_token
        self.admin_user_id = admin_user_id

        # Initialize core dependencies
        self.db = Database()
        self.content_manager = ContentManager(self.db)
        self.scheduler = SmartMessageScheduler(self.db, self.content_manager)

        # Create Telegram application
        self.application = Application.builder().token(bot_token).build()

        # Initialize all command handlers
        self.user_handler = UserCommandHandler(
            self.db,
            self.content_manager,
            self.scheduler
        )

        self.mood_handler = MoodCommandHandler(
            self.db,
            self.content_manager,
            self.scheduler
        )

        self.admin_handler = AdminCommandHandler(
            self.db,
            self.content_manager,
            self.scheduler,
            self.admin_user_id,
            self.application
        )

        self.text_handler = TextMessageHandler(
            self.db,
            self.content_manager,
            self.scheduler
        )

        # Initialize callback router
        self.callback_router = CallbackRouter(self)

        # Setup all handlers
        self._setup_handlers()

    def _setup_handlers(self):
        """Register all command, callback, and message handlers with the application"""

        # User commands
        self.application.add_handler(CommandHandler("start", self.user_handler.start))
        self.application.add_handler(CommandHandler("help", self.user_handler.help_command))
        self.application.add_handler(CommandHandler("settings", self.user_handler.settings))
        self.application.add_handler(CommandHandler("pause", self.user_handler.pause_messages))
        self.application.add_handler(CommandHandler("resume", self.user_handler.resume_messages))
        self.application.add_handler(CommandHandler("motivateMe", self.user_handler.motivate_me))

        # Mood commands
        self.application.add_handler(CommandHandler("mood", self.mood_handler.mood_check))
        self.application.add_handler(CommandHandler("stats", self.mood_handler.stats))

        # Admin commands
        self.application.add_handler(CommandHandler("admin_stats", self.admin_handler.admin_stats))
        self.application.add_handler(CommandHandler("admin_broadcast", self.admin_handler.admin_broadcast))
        self.application.add_handler(CommandHandler("admin_users", self.admin_handler.admin_users))
        self.application.add_handler(CommandHandler("admin_content", self.admin_handler.admin_content))
        self.application.add_handler(CommandHandler("admin_reset", self.admin_handler.admin_reset))

        # Callback query handler (routes to callback_router)
        self.application.add_handler(CallbackQueryHandler(self.callback_router.route))

        # Text message handler
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_handler.handle_message))

    async def send_motivational_message(self, user_id: int):
        """
        Send a motivational message to a user.

        Wrapper method that delegates to admin_handler for scheduler compatibility.

        Args:
            user_id: Telegram user ID
        """
        await self.admin_handler.send_motivational_message(user_id)

    def run(self):
        """Start the bot and scheduler"""
        # Start the smart scheduler
        self.scheduler.start(self)

        # Start the bot
        logger.info("Starting Motivator Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
