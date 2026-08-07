"""
Mood callback handlers for Motivator Bot.

Handles mood-related callback queries:
- Mood score selection
- Feedback on motivational messages
"""

from src import ai_motivator


class MoodCallbackHandler:
    """Handles mood-related callback queries"""

    def __init__(self, bot_instance):
        """
        Initialize mood callback handler.

        Args:
            bot_instance: Reference to the main MotivatorBot instance
        """
        self.bot = bot_instance
        self.db = bot_instance.db
        self.content_manager = bot_instance.content_manager

    async def handle_mood_select(self, query, context):
        """Handle mood score selection (mood_1, mood_2, ..., mood_10)"""
        user_id = query.from_user.id
        mood_score = int(query.data.split("_")[1])
        self.db.add_mood_entry(user_id, mood_score)

        user_settings = self.db.get_user_settings(user_id)
        language = user_settings.get('language', 'de') if user_settings else 'de'

        if language == 'de':
            response = f"Danke für dein Feedback! Stimmung: {mood_score}/10 📝\n\n"
        else:
            response = f"Thanks for sharing! Mood logged: {mood_score}/10 📝\n\n"

        # Try an individual AI reaction first, fall back to static content
        ai_reaction = await ai_motivator.generate_mood_reaction(
            language, mood_score, query.from_user.first_name,
            self.db.get_user_facts(user_id)
        )

        if ai_reaction:
            response += ai_reaction
        else:
            content = self.content_manager.get_content_by_mood(mood_score, language)
            if content:
                response += content.content
                if content.media_url:
                    response += f"\n\n🔗 {content.media_url}"

        await query.edit_message_text(response)

    async def handle_feedback(self, query, context):
        """Handle feedback from /motivateMe command (feedback_love, feedback_like, feedback_dislike)"""
        user_id = query.from_user.id
        feedback_parts = query.data.split("_")
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
