"""
Unit tests for MoodCommandHandler.

Tests mood tracking and statistics commands: /mood, /stats
"""

import pytest
from src.handlers.mood_commands import MoodCommandHandler


@pytest.mark.unit
@pytest.mark.asyncio
class TestMoodCommandHandler:
    """Test suite for mood command handlers"""

    @pytest.fixture
    def handler(self, mock_database, mock_content_manager, mock_scheduler, mock_goal_manager):
        """Create handler instance with mocked dependencies"""
        return MoodCommandHandler(
            mock_database,
            mock_content_manager,
            mock_scheduler,
            mock_goal_manager
        )

    async def test_mood_check_german(self, handler, mock_update, mock_context):
        """Test /mood command displays German mood selection"""
        handler.db.get_user_settings.return_value = {'language': 'de'}

        await handler.mood_check(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Wie fühlst du dich heute" in call_args[0][0]

    async def test_mood_check_english(self, handler, mock_update, mock_context):
        """Test /mood command displays English mood selection"""
        handler.db.get_user_settings.return_value = {'language': 'en'}

        await handler.mood_check(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "How are you feeling today" in call_args[0][0]

    async def test_mood_check_includes_all_options(self, handler, mock_update, mock_context):
        """Test /mood command includes all mood options 1-10"""
        handler.db.get_user_settings.return_value = {'language': 'en'}

        await handler.mood_check(mock_update, mock_context)

        # Verify keyboard with 10 mood options was created
        call_kwargs = mock_update.message.reply_text.call_args[1]
        assert 'reply_markup' in call_kwargs

    async def test_stats_no_data(self, handler, mock_update, mock_context):
        """Test /stats command with no mood data"""
        handler.db.get_user_settings.return_value = {'language': 'en'}
        handler.db.get_message_stats.return_value = {}
        handler.db.get_recent_mood.return_value = []

        await handler.stats(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Your Statistics" in call_args[0][0]
        assert "Total: 0" in call_args[0][0]

    async def test_stats_with_data(self, handler, mock_update, mock_context):
        """Test /stats command displays statistics correctly"""
        handler.db.get_user_settings.return_value = {'language': 'en'}
        handler.db.get_message_stats.return_value = {
            'text': 15,
            'image': 3,
            'video': 2,
            'link': 5
        }
        handler.db.get_recent_mood.return_value = [
            {'score': 7},
            {'score': 8},
            {'score': 6}
        ]

        await handler.stats(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        stats_text = call_args[0][0]

        # Check message counts
        assert "Total: 25" in stats_text  # 15+3+2+5
        assert "Text: 15" in stats_text

        # Check mood statistics
        assert "Entries: 3" in stats_text
        assert "Average: 7.0/10" in stats_text

    async def test_stats_german_language(self, handler, mock_update, mock_context):
        """Test /stats command displays German text"""
        handler.db.get_user_settings.return_value = {'language': 'de'}
        handler.db.get_message_stats.return_value = {'text': 10}
        handler.db.get_recent_mood.return_value = []

        await handler.stats(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Deine Statistiken" in call_args[0][0]

    async def test_stats_calculates_average_correctly(self, handler, mock_update, mock_context):
        """Test /stats correctly calculates mood average"""
        handler.db.get_user_settings.return_value = {'language': 'en'}
        handler.db.get_message_stats.return_value = {}
        handler.db.get_recent_mood.return_value = [
            {'score': 10},
            {'score': 5},
            {'score': 3}
        ]

        await handler.stats(mock_update, mock_context)

        call_args = mock_update.message.reply_text.call_args
        stats_text = call_args[0][0]

        # Average should be (10+5+3)/3 = 6.0
        assert "6.0/10" in stats_text
