"""
Goals callback handlers for Motivator Bot.

Handles all goal-related callback queries:
- Add goal workflow (categories, templates, custom)
- View goals list
- Goal details
- Check-in
- Complete goal
- Delete goal
- Daily check-in
"""

from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode


class GoalsCallbackHandler:
    """Handles goal-related callback queries"""

    def __init__(self, bot_instance):
        """
        Initialize goals callback handler.

        Args:
            bot_instance: Reference to the main MotivatorBot instance
        """
        self.bot = bot_instance
        self.db = bot_instance.db
        self.goal_manager = bot_instance.goal_manager

    async def handle_add_goal(self, query, context):
        """Show goal categories for selection"""
        user_id = query.from_user.id
        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'

        categories = self.goal_manager.get_categories(language)

        if language == 'de':
            text = "🎯 *Ziel-Kategorie wählen*\n\nWähle eine Kategorie für dein neues Ziel:"
        else:
            text = "🎯 *Choose Goal Category*\n\nSelect a category for your new goal:"

        keyboard = []
        for category_key, category_name in categories.items():
            keyboard.append([InlineKeyboardButton(category_name, callback_data=f"goal_category_{category_key}")])

        keyboard.append([InlineKeyboardButton("✏️ Eigenes Ziel" if language == 'de' else "✏️ Custom Goal", callback_data="goal_custom")])
        keyboard.append([InlineKeyboardButton("⬅️ Zurück" if language == 'de' else "⬅️ Back", callback_data="view_goals")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    async def handle_goal_category(self, query, context):
        """Show goal templates for a category"""
        user_id = query.from_user.id
        category = query.data.split("_", 2)[2]

        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'

        templates = self.goal_manager.get_templates_by_category(category, language)
        categories = self.goal_manager.get_categories(language)
        category_name = categories.get(category, category)

        if language == 'de':
            text = f"📋 *{category_name}*\n\nWähle eine Vorlage oder erstelle ein eigenes Ziel:"
        else:
            text = f"📋 *{category_name}*\n\nChoose a template or create your own goal:"

        keyboard = []
        for template in templates:
            difficulty_emoji = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}
            emoji = difficulty_emoji.get(template.difficulty.value, "🟢")
            keyboard.append([InlineKeyboardButton(f"{emoji} {template.title}", callback_data=f"goal_template_{template.id}")])

        keyboard.append([InlineKeyboardButton("✏️ Eigenes Ziel" if language == 'de' else "✏️ Custom Goal", callback_data="goal_custom")])
        keyboard.append([InlineKeyboardButton("⬅️ Zurück" if language == 'de' else "⬅️ Back", callback_data="add_goal")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    async def handle_goal_template(self, query, context):
        """Create a goal from template"""
        user_id = query.from_user.id
        template_id = query.data.split("_", 2)[2]

        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'

        template = self.goal_manager.get_template_by_id(template_id, language)
        if not template:
            await query.edit_message_text("❌ Template not found")
            return

        # Create goal in database
        goal_id = self.db.add_goal(
            user_id=user_id,
            goal_text=template.title,
            category=template.category.value,
            difficulty_level=template.difficulty.value,
            goal_type='template',
            is_daily=template.is_daily
        )

        if goal_id > 0:
            tips_text = '\n• '.join(template.tips)

            if language == 'de':
                text = f"""✅ *Ziel erfolgreich erstellt!*

🎯 **{template.title}**
📝 {template.description}

💡 **Tipps für den Erfolg:**
• {tips_text}

Viel Erfolg bei deinem neuen Ziel! 🌟"""
            else:
                text = f"""✅ *Goal successfully created!*

🎯 **{template.title}**
📝 {template.description}

💡 **Tips for success:**
• {tips_text}

Good luck with your new goal! 🌟"""

            keyboard = [
                [InlineKeyboardButton("📋 Meine Ziele" if language == 'de' else "📋 My Goals", callback_data="view_goals")],
                [InlineKeyboardButton("❌ Schließen" if language == 'de' else "❌ Close", callback_data="close_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        else:
            await query.edit_message_text("❌ Error creating goal")

    async def handle_goal_custom(self, query, context):
        """Show custom goal creation form"""
        user_id = query.from_user.id
        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'

        if language == 'de':
            text = """✏️ *Eigenes Ziel erstellen*

Schicke mir eine Nachricht mit deinem Ziel im folgenden Format:

`Ziel: [Dein Ziel hier]`

Beispiel:
`Ziel: Jeden Tag 5 Minuten Klavier üben`

Danach kannst du weitere Details hinzufügen."""
        else:
            text = """✏️ *Create Custom Goal*

Send me a message with your goal in the following format:

`Goal: [Your goal here]`

Example:
`Goal: Practice piano for 5 minutes every day`

You can then add more details."""

        keyboard = [
            [InlineKeyboardButton("⬅️ Zurück" if language == 'de' else "⬅️ Back", callback_data="add_goal")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    async def handle_view_goals(self, query, context):
        """Show user's active goals"""
        user_id = query.from_user.id
        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'

        goals = self.db.get_user_goals(user_id, active_only=True)

        if not goals:
            if language == 'de':
                text = """🎯 *Meine Ziele*

Du hast noch keine aktiven Ziele.

Ziele helfen dir dabei, fokussiert zu bleiben und deine mentale Gesundheit zu verbessern. Erstelle dein erstes Ziel!"""
            else:
                text = """🎯 *My Goals*

You don't have any active goals yet.

Goals help you stay focused and improve your mental health. Create your first goal!"""

            keyboard = [
                [InlineKeyboardButton("➕ Erstes Ziel erstellen" if language == 'de' else "➕ Create First Goal", callback_data="add_goal")],
                [InlineKeyboardButton("❌ Schließen" if language == 'de' else "❌ Close", callback_data="close_menu")]
            ]
        else:
            if language == 'de':
                text = f"🎯 *Meine Ziele* ({len(goals)} aktiv)\n\n"
            else:
                text = f"🎯 *My Goals* ({len(goals)} active)\n\n"

            keyboard = []
            for goal in goals[:5]:  # Limit to 5 goals for display
                goal_display = self.goal_manager.format_goal_display(goal, language)
                keyboard.append([InlineKeyboardButton(f"📋 {goal['text'][:30]}...", callback_data=f"goal_detail_{goal['id']}")])

            keyboard.append([InlineKeyboardButton("➕ Neues Ziel" if language == 'de' else "➕ New Goal", callback_data="add_goal")])
            keyboard.append([InlineKeyboardButton("✅ Täglicher Check-in" if language == 'de' else "✅ Daily Check-in", callback_data="daily_checkin")])
            keyboard.append([InlineKeyboardButton("❌ Schließen" if language == 'de' else "❌ Close", callback_data="close_menu")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    async def handle_goal_detail(self, query, context):
        """Show detailed view of a specific goal"""
        user_id = query.from_user.id
        goal_id = int(query.data.split("_")[2])

        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'

        goals = self.db.get_user_goals(user_id, active_only=False)
        goal = next((g for g in goals if g['id'] == goal_id), None)

        if not goal:
            await query.edit_message_text("❌ Goal not found")
            return

        # Format goal details
        goal_display = self.goal_manager.format_goal_display(goal, language)

        if language == 'de':
            text = f"""📋 *Ziel Details*

{goal_display}

📅 Erstellt: {goal['created_at'][:10]}
🔥 Aktueller Streak: {goal['streak_days']} Tage
🎯 Schwierigkeit: {goal['difficulty_level'].title()}

Was möchtest du tun?"""
        else:
            text = f"""📋 *Goal Details*

{goal_display}

📅 Created: {goal['created_at'][:10]}
🔥 Current Streak: {goal['streak_days']} days
🎯 Difficulty: {goal['difficulty_level'].title()}

What would you like to do?"""

        keyboard = []

        if not goal['completed']:
            keyboard.append([InlineKeyboardButton("✅ Check-in für heute" if language == 'de' else "✅ Check-in for today", callback_data=f"goal_checkin_{goal_id}")])
            keyboard.append([InlineKeyboardButton("🏆 Ziel abschließen" if language == 'de' else "🏆 Complete goal", callback_data=f"goal_complete_{goal_id}")])

        keyboard.append([InlineKeyboardButton("🗑️ Ziel löschen" if language == 'de' else "🗑️ Delete goal", callback_data=f"goal_delete_{goal_id}")])
        keyboard.append([InlineKeyboardButton("⬅️ Zurück zu Zielen" if language == 'de' else "⬅️ Back to goals", callback_data="view_goals")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    async def handle_goal_checkin(self, query, context):
        """Handle daily goal check-in"""
        user_id = query.from_user.id
        goal_id = int(query.data.split("_")[2])

        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'

        success = self.db.update_goal_progress(goal_id, user_id)

        if success:
            # Get updated goal to show new streak
            goals = self.db.get_user_goals(user_id, active_only=False)
            goal = next((g for g in goals if g['id'] == goal_id), None)

            if goal:
                streak = goal['streak_days']

                # Celebration messages based on streak
                if streak == 1:
                    celebration = "🎉 Großartiger Start!"
                elif streak == 7:
                    celebration = "🔥 Eine Woche geschafft!"
                elif streak == 21:
                    celebration = "💪 Drei Wochen! Du bildest eine Gewohnheit!"
                elif streak == 30:
                    celebration = "🏆 Ein Monat! Unglaublich!"
                elif streak % 10 == 0:
                    celebration = f"🌟 {streak} Tage Streak!"
                else:
                    celebration = "✅ Gut gemacht!"

                if language == 'de':
                    text = f"""{celebration}

🎯 **{goal['text']}**
🔥 Streak: {streak} Tage

Du machst großartige Fortschritte! Weiter so! 💪"""
                else:
                    text = f"""{celebration}

🎯 **{goal['text']}**
🔥 Streak: {streak} days

You're making great progress! Keep going! 💪"""
        else:
            if language == 'de':
                text = "❌ Check-in fehlgeschlagen. Versuche es später erneut."
            else:
                text = "❌ Check-in failed. Please try again later."

        keyboard = [
            [InlineKeyboardButton("📋 Ziel Details" if language == 'de' else "📋 Goal Details", callback_data=f"goal_detail_{goal_id}")],
            [InlineKeyboardButton("🎯 Alle Ziele" if language == 'de' else "🎯 All Goals", callback_data="view_goals")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    async def handle_goal_complete(self, query, context):
        """Complete a goal"""
        user_id = query.from_user.id
        goal_id = int(query.data.split("_")[2])

        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'

        success = self.db.complete_goal(goal_id, user_id)

        if success:
            if language == 'de':
                text = """🏆 *Herzlichen Glückwunsch!*

Du hast dein Ziel erfolgreich abgeschlossen!

Das ist ein großartiger Erfolg für deine persönliche Entwicklung und mentale Gesundheit. Du solltest stolz auf dich sein! 🌟

Möchtest du ein neues Ziel setzen?"""
            else:
                text = """🏆 *Congratulations!*

You have successfully completed your goal!

This is a great achievement for your personal development and mental health. You should be proud of yourself! 🌟

Would you like to set a new goal?"""

            keyboard = [
                [InlineKeyboardButton("➕ Neues Ziel setzen" if language == 'de' else "➕ Set New Goal", callback_data="add_goal")],
                [InlineKeyboardButton("📋 Alle Ziele" if language == 'de' else "📋 All Goals", callback_data="view_goals")]
            ]
        else:
            if language == 'de':
                text = "❌ Fehler beim Abschließen des Ziels."
            else:
                text = "❌ Error completing goal."

            keyboard = [
                [InlineKeyboardButton("⬅️ Zurück" if language == 'de' else "⬅️ Back", callback_data=f"goal_detail_{goal_id}")]
            ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    async def handle_goal_delete(self, query, context):
        """Confirm goal deletion"""
        user_id = query.from_user.id
        goal_id = int(query.data.split("_")[2])

        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'

        if language == 'de':
            text = """⚠️ *Ziel löschen*

Bist du sicher, dass du dieses Ziel löschen möchtest?

**Diese Aktion kann nicht rückgängig gemacht werden!**"""
        else:
            text = """⚠️ *Delete Goal*

Are you sure you want to delete this goal?

**This action cannot be undone!**"""

        keyboard = [
            [InlineKeyboardButton("🗑️ Ja, löschen" if language == 'de' else "🗑️ Yes, delete", callback_data=f"goal_delete_confirm_{goal_id}")],
            [InlineKeyboardButton("❌ Abbrechen" if language == 'de' else "❌ Cancel", callback_data=f"goal_detail_{goal_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    async def handle_goal_delete_confirm(self, query, context):
        """Delete a goal"""
        user_id = query.from_user.id
        goal_id = int(query.data.split("_")[3])

        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'

        success = self.db.delete_goal(goal_id, user_id)

        if success:
            if language == 'de':
                text = "✅ Ziel wurde erfolgreich gelöscht."
            else:
                text = "✅ Goal was successfully deleted."
        else:
            if language == 'de':
                text = "❌ Fehler beim Löschen des Ziels."
            else:
                text = "❌ Error deleting goal."

        keyboard = [
            [InlineKeyboardButton("📋 Meine Ziele" if language == 'de' else "📋 My Goals", callback_data="view_goals")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    async def handle_daily_checkin(self, query, context):
        """Show daily check-in for all goals"""
        user_id = query.from_user.id
        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'

        goals = self.db.get_user_goals(user_id, active_only=True)

        if not goals:
            if language == 'de':
                text = "📋 Du hast keine aktiven Ziele für den Check-in."
            else:
                text = "📋 You have no active goals to check in."

            keyboard = [
                [InlineKeyboardButton("➕ Ziel erstellen" if language == 'de' else "➕ Create Goal", callback_data="add_goal")]
            ]
        else:
            if language == 'de':
                text = f"✅ *Täglicher Check-in*\n\nWähle ein Ziel für das heutige Check-in:\n\n"
            else:
                text = f"✅ *Daily Check-in*\n\nChoose a goal for today's check-in:\n\n"

            keyboard = []
            for goal in goals:
                last_checkin = goal['last_check_in']
                today = datetime.now().date().isoformat()

                if last_checkin == today:
                    status_emoji = "✅"
                else:
                    status_emoji = "⏰"

                keyboard.append([InlineKeyboardButton(f"{status_emoji} {goal['text'][:25]}...", callback_data=f"goal_checkin_{goal['id']}")])

            keyboard.append([InlineKeyboardButton("⬅️ Zurück" if language == 'de' else "⬅️ Back", callback_data="view_goals")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
