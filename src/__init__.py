"""
Motivator Bot - Mental Health Support Bot

This package contains the core modules for the Motivator Telegram bot.
"""

from .bot import MotivatorBot
from .database import Database
from .content import ContentManager
from .smart_scheduler import SmartMessageScheduler

__all__ = ['MotivatorBot', 'Database', 'ContentManager', 'SmartMessageScheduler']