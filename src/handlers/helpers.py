"""
Shared handler helpers for Motivator Bot.

Home of small utilities used by both command handlers and callback
handlers, so user-facing views and defaults exist exactly once.
"""

from typing import Tuple

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

DEFAULT_LANGUAGE = 'de'


def get_user_language(db, user_id: int) -> str:
    """Get the user's preferred language, falling back to the default."""
    settings = db.get_user_settings(user_id)
    return settings.get('language', DEFAULT_LANGUAGE) if settings else DEFAULT_LANGUAGE


def get_display_name(user_settings, telegram_first_name: str = None):
    """
    Name the bot should address the user with.

    preferred_name semantics: None = use the Telegram first name,
    '' = the user asked not to be addressed by name (returns None),
    anything else = the custom name the user chose.
    """
    if user_settings:
        preferred = user_settings.get('preferred_name')
        if preferred == '':
            return None
        if preferred:
            return preferred
        return user_settings.get('first_name') or telegram_first_name
    return telegram_first_name


def build_settings_view(user_settings: dict) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Build the main settings menu (text + keyboard) for a user.

    Used by the /settings command and the back-to-settings callback so
    both always render the identical menu.
    """
    language = user_settings['language']
    frequency = user_settings['message_frequency']
    active = "✅ Active" if user_settings['active'] else "⏸️ Paused"

    display_name = get_display_name(user_settings)

    if language == 'de':
        name_display = display_name if display_name else "Keine Namensansprache"
        settings_text = f"""
⚙️ *Deine Einstellungen*

Sprache: {'🇩🇪 Deutsch' if language == 'de' else '🇬🇧 English'}
Anrede: {name_display}
Nachrichten pro Tag: {frequency}
Status: {active}

Was möchtest du ändern?
"""
        keyboard = [
            [InlineKeyboardButton("🌍 Sprache", callback_data="set_language")],
            [InlineKeyboardButton("📛 Anrede", callback_data="set_name")],
            [InlineKeyboardButton("📊 Häufigkeit", callback_data="set_frequency")],
            [InlineKeyboardButton("⏸️ Pausieren" if user_settings['active'] else "▶️ Fortsetzen",
                                callback_data="toggle_active")],
            [InlineKeyboardButton("⏰ Zeiten", callback_data="set_timing")],
            [InlineKeyboardButton("🔄 Zurücksetzen", callback_data="reset_user")],
            [InlineKeyboardButton("❌ Schließen", callback_data="close_menu")]
        ]
    else:
        name_display = display_name if display_name else "No name"
        settings_text = f"""
⚙️ *Your Settings*

Language: {'🇩🇪 Deutsch' if language == 'de' else '🇬🇧 English'}
Address as: {name_display}
Messages per day: {frequency}
Status: {active}

What would you like to change?
"""
        keyboard = [
            [InlineKeyboardButton("🌍 Language", callback_data="set_language")],
            [InlineKeyboardButton("📛 Name", callback_data="set_name")],
            [InlineKeyboardButton("📊 Frequency", callback_data="set_frequency")],
            [InlineKeyboardButton("⏸️ Pause" if user_settings['active'] else "▶️ Resume",
                                callback_data="toggle_active")],
            [InlineKeyboardButton("⏰ Timing", callback_data="set_timing")],
            [InlineKeyboardButton("🔄 Reset", callback_data="reset_user")],
            [InlineKeyboardButton("❌ Close", callback_data="close_menu")]
        ]

    return settings_text, InlineKeyboardMarkup(keyboard)
