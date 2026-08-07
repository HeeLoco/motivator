"""
Callback handlers package for Motivator Bot.

Contains callback query handlers split by domain (settings, mood, admin).
"""

from .router import CallbackRouter

__all__ = ['CallbackRouter']
