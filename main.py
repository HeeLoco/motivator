#!/usr/bin/env python3
"""
Motivator Bot - A Telegram bot for mental health motivation and support

This bot sends personalized motivational messages to users throughout the day,
tracks mood and goals, and provides mental health resources.
"""

import os
import sys
from dotenv import load_dotenv

from src.bot import MotivatorBot
from src.logging_config import setup_logging, get_logger

def main():
    """Main function to start the bot"""
    # Load environment variables
    load_dotenv()

    # Setup logging (reads LOG_LEVEL, LOG_FORMAT, LOG_FILE from env)
    setup_logging()
    logger = get_logger(__name__)
    
    # Get bot token from environment
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables!")
        logger.error("Please create a .env file with your bot token:")
        logger.error("BOT_TOKEN=your_telegram_bot_token_here")
        sys.exit(1)
    
    # Get admin user ID (optional)
    admin_user_id = os.getenv('ADMIN_USER_ID')
    if admin_user_id:
        try:
            admin_user_id = int(admin_user_id)
        except ValueError:
            logger.warning("Invalid ADMIN_USER_ID format, ignoring")
            admin_user_id = None
    
    # Create and start the bot
    try:
        logger.info("Initializing Motivator Bot...")
        bot = MotivatorBot(bot_token, admin_user_id)
        
        logger.info("Starting bot...")
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()