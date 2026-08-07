"""
Settings callback handlers for Motivator Bot.

Handles all settings-related callback queries:
- Language selection
- Message frequency
- Timing preferences (start time, end time, minimum gap)
- Active/pause toggle
- User data reset
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

from ..helpers import build_settings_view, get_display_name, get_user_language


class SettingsCallbackHandler:
    """Handles settings-related callback queries"""

    def __init__(self, bot_instance):
        """
        Initialize settings callback handler.

        Args:
            bot_instance: Reference to the main MotivatorBot instance
        """
        self.bot = bot_instance
        self.db = bot_instance.db

    async def handle_language_select(self, query, context):
        """Handle language selection callback (lang_de, lang_en)"""
        user_id = query.from_user.id
        language = query.data.split("_")[1]
        self.db.update_user_setting(user_id, 'language', language)

        if language == 'de':
            text = "🇩🇪 Sprache auf Deutsch eingestellt!\n\nVerwende /settings um weitere Einstellungen anzupassen."
        else:
            text = "🇬🇧 Language set to English!\n\nUse /settings to adjust more preferences."

        await query.edit_message_text(text)

    async def handle_set_language(self, query, context):
        """Show language selection menu"""
        user_id = query.from_user.id
        language = get_user_language(self.db, user_id)

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

    async def handle_set_name(self, query, context):
        """Show the address-name submenu"""
        user_id = query.from_user.id
        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'

        display_name = get_display_name(user_settings, query.from_user.first_name)

        if language == 'de':
            current = display_name if display_name else "Keine Namensansprache"
            text = (f"📛 *Anrede*\n\nAktuell spreche ich dich so an: *{current}*\n\n"
                    "Wie soll ich dich nennen?")
            keyboard = [
                [InlineKeyboardButton("✏️ Eigenen Namen eingeben", callback_data="name_enter")],
                [InlineKeyboardButton("📱 Telegram-Namen verwenden", callback_data="name_telegram")],
                [InlineKeyboardButton("🚫 Ohne Namen", callback_data="name_none")],
                [InlineKeyboardButton("⬅️ Zurück", callback_data="back_to_settings")]
            ]
        else:
            current = display_name if display_name else "No name"
            text = (f"📛 *Address*\n\nI currently address you as: *{current}*\n\n"
                    "What should I call you?")
            keyboard = [
                [InlineKeyboardButton("✏️ Enter a custom name", callback_data="name_enter")],
                [InlineKeyboardButton("📱 Use my Telegram name", callback_data="name_telegram")],
                [InlineKeyboardButton("🚫 No name", callback_data="name_none")],
                [InlineKeyboardButton("⬅️ Back", callback_data="back_to_settings")]
            ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    async def handle_name_choice(self, query, context):
        """Handle address-name choice (name_enter, name_telegram, name_none)"""
        user_id = query.from_user.id
        language = get_user_language(self.db, user_id)
        choice = query.data

        if choice == 'name_enter':
            context.user_data['awaiting_preferred_name'] = True
            if language == 'de':
                text = "✏️ Schreib mir einfach den Namen, mit dem ich dich ansprechen soll."
            else:
                text = "✏️ Just send me the name you'd like me to call you."
            await query.edit_message_text(text)
            return

        if choice == 'name_telegram':
            self.db.update_user_setting(user_id, 'preferred_name', None)
            name = query.from_user.first_name
            if language == 'de':
                text = f"📱 Alles klar, ich nenne dich wieder *{name}*."
            else:
                text = f"📱 Got it, I'll call you *{name}* again."
        else:  # name_none
            self.db.update_user_setting(user_id, 'preferred_name', '')
            if language == 'de':
                text = "🚫 Verstanden, ich spreche dich nicht mehr mit Namen an."
            else:
                text = "🚫 Understood, I won't address you by name anymore."

        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)

    async def handle_set_frequency(self, query, context):
        """Show frequency selection menu"""
        user_id = query.from_user.id
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

    async def handle_frequency_select(self, query, context):
        """Handle frequency selection (freq_1, freq_2, etc.)"""
        user_id = query.from_user.id
        frequency = int(query.data.split("_")[1])
        self.db.update_user_setting(user_id, 'message_frequency', frequency)

        language = get_user_language(self.db, user_id)

        if language == 'de':
            text = f"📊 Nachrichtenhäufigkeit auf {frequency} pro Tag eingestellt!\n\nVerwende /settings um weitere Einstellungen anzupassen."
        else:
            text = f"📊 Message frequency set to {frequency} per day!\n\nUse /settings to adjust more preferences."

        await query.edit_message_text(text)

    async def handle_toggle_active(self, query, context):
        """Toggle active/pause status"""
        user_id = query.from_user.id
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

    async def handle_set_timing(self, query, context):
        """Show timing preferences menu"""
        user_id = query.from_user.id
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

    async def handle_set_start_time(self, query, context):
        """Show start time selection menu"""
        user_id = query.from_user.id
        language = get_user_language(self.db, user_id)

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

    async def handle_set_end_time(self, query, context):
        """Show end time selection menu"""
        user_id = query.from_user.id
        language = get_user_language(self.db, user_id)

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

    async def handle_set_min_gap(self, query, context):
        """Show minimum gap selection menu"""
        user_id = query.from_user.id
        language = get_user_language(self.db, user_id)

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

    async def handle_start_time_select(self, query, context):
        """Handle start time selection (start_time_6, start_time_7, etc.)"""
        user_id = query.from_user.id
        hour = int(query.data.split("_")[-1])
        self.db.update_timing_preference(user_id, 'active_start_hour', hour)

        language = get_user_language(self.db, user_id)

        if language == 'de':
            text = f"✅ Start-Zeit auf {hour:02d}:00 eingestellt!\n\nVerwende /settings um weitere Einstellungen anzupassen."
        else:
            text = f"✅ Start time set to {hour:02d}:00!\n\nUse /settings to adjust more preferences."

        await query.edit_message_text(text)

    async def handle_end_time_select(self, query, context):
        """Handle end time selection (end_time_18, end_time_19, etc.)"""
        user_id = query.from_user.id
        hour = int(query.data.split("_")[-1])
        self.db.update_timing_preference(user_id, 'active_end_hour', hour)

        language = get_user_language(self.db, user_id)

        if language == 'de':
            text = f"✅ End-Zeit auf {hour:02d}:00 eingestellt!\n\nVerwende /settings um weitere Einstellungen anzupassen."
        else:
            text = f"✅ End time set to {hour:02d}:00!\n\nUse /settings to adjust more preferences."

        await query.edit_message_text(text)

    async def handle_min_gap_select(self, query, context):
        """Handle minimum gap selection (min_gap_1, min_gap_2, etc.)"""
        user_id = query.from_user.id
        hours = int(query.data.split("_")[-1])
        self.db.update_timing_preference(user_id, 'min_gap_hours', hours)

        language = get_user_language(self.db, user_id)

        if language == 'de':
            text = f"✅ Mindestabstand auf {hours} Stunde{'n' if hours > 1 else ''} eingestellt!\n\nVerwende /settings um weitere Einstellungen anzupassen."
        else:
            text = f"✅ Minimum gap set to {hours} hour{'s' if hours > 1 else ''}!\n\nUse /settings to adjust more preferences."

        await query.edit_message_text(text)

    async def handle_reset_user(self, query, context):
        """Show reset confirmation dialog"""
        user_id = query.from_user.id
        language = get_user_language(self.db, user_id)

        if language == 'de':
            text = """⚠️ *Warnung: Daten zurücksetzen*

Das wird ALLE deine Daten löschen:
• Alle Einstellungen zurücksetzen
• Stimmungseinträge löschen
• Feedback-Historie löschen
• Nachrichtenverlauf löschen
• KI-Gesprächsgedächtnis löschen

Bist du sicher, dass du fortfahren möchtest?

*Diese Aktion kann nicht rückgängig gemacht werden!*"""
        else:
            text = """⚠️ *Warning: Reset Data*

This will DELETE ALL your data:
• Reset all settings
• Delete mood entries
• Delete feedback history
• Delete message history
• Delete AI conversation memory

Are you sure you want to continue?

*This action cannot be undone!*"""

        keyboard = [
            [InlineKeyboardButton("⚠️ Ja, alles löschen" if language == 'de' else "⚠️ Yes, delete all", callback_data="confirm_reset")],
            [InlineKeyboardButton("❌ Abbrechen" if language == 'de' else "❌ Cancel", callback_data="back_to_settings")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    async def handle_confirm_reset(self, query, context):
        """Execute user data reset"""
        user_id = query.from_user.id
        language = get_user_language(self.db, user_id)

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

    async def handle_back_to_settings(self, query, context):
        """Navigate back to main settings menu"""
        user_id = query.from_user.id
        user_settings = self.db.get_user_settings(user_id)
        if not user_settings:
            await query.edit_message_text("Please start the bot first with /start")
            return

        settings_text, reply_markup = build_settings_view(user_settings)
        await query.edit_message_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
