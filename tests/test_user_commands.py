"""
Unit tests for UserCommandHandler.

Tests all user-facing commands: /start, /help, /settings, /pause, /resume, /motivateMe
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.handlers.user_commands import UserCommandHandler


@pytest.mark.unit
@pytest.mark.asyncio
class TestUserCommandHandler:
    """Test suite for user command handlers"""

    @pytest.fixture
    def handler(self, mock_database, mock_content_manager, mock_scheduler, mock_goal_manager):
        """Create handler instance with mocked dependencies"""
        return UserCommandHandler(
            mock_database,
            mock_content_manager,
            mock_scheduler,
            mock_goal_manager
        )

    async def test_start_command_new_user(self, handler, mock_update, mock_context):
        """Test /start command for new user"""
        # Execute
        await handler.start(mock_update, mock_context)

        # Verify user was added to database
        handler.db.add_user.assert_called_once_with(
            mock_update.effective_user.id,
            mock_update.effective_user.username,
            mock_update.effective_user.first_name
        )

        # Verify welcome message was sent
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Willkommen" in call_args[0][0] or "Welcome" in call_args[0][0]

    async def test_help_command_german(self, handler, mock_update, mock_context):
        """Test /help command returns German help text"""
        handler.db.get_user_settings.return_value = {'language': 'de'}

        await handler.help_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Motivator Bot Hilfe" in call_args[0][0]

    async def test_help_command_english(self, handler, mock_update, mock_context):
        """Test /help command returns English help text"""
        handler.db.get_user_settings.return_value = {'language': 'en'}

        await handler.help_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Motivator Bot Help" in call_args[0][0]

    async def test_settings_command_no_user(self, handler, mock_update, mock_context):
        """Test /settings command when user not found"""
        handler.db.get_user_settings.return_value = None

        await handler.settings(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once_with(
            "Please start the bot first with /start"
        )

    async def test_settings_command_success(self, handler, mock_update, mock_context):
        """Test /settings command displays settings menu"""
        handler.db.get_user_settings.return_value = {
            'language': 'en',
            'message_frequency': 3,
            'active': True
        }

        await handler.settings(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Your Settings" in call_args[0][0]
        assert "Messages per day: 3" in call_args[0][0]

    async def test_pause_messages(self, handler, mock_update, mock_context):
        """Test /pause command pauses messages"""
        handler.db.get_user_settings.return_value = {'language': 'en'}

        await handler.pause_messages(mock_update, mock_context)

        # Verify active status was set to False
        handler.db.update_user_setting.assert_called_once_with(
            mock_update.effective_user.id,
            'active',
            False
        )

        # Verify confirmation message
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "paused" in call_args[0][0].lower()

    async def test_resume_messages(self, handler, mock_update, mock_context):
        """Test /resume command resumes messages"""
        handler.db.get_user_settings.return_value = {'language': 'en'}

        await handler.resume_messages(mock_update, mock_context)

        # Verify active status was set to True
        handler.db.update_user_setting.assert_called_once_with(
            mock_update.effective_user.id,
            'active',
            True
        )

        # Verify confirmation message
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "resumed" in call_args[0][0].lower()

    async def test_motivate_me_success(self, handler, mock_update, mock_context):
        """Test /motivateMe sends motivational message"""
        handler.db.get_user_settings.return_value = {'language': 'en'}
        handler.db.get_recent_mood.return_value = [{'score': 7}]

        await handler.motivate_me(mock_update, mock_context)

        # Verify user was added (in case they're new)
        handler.db.add_user.assert_called_once()

        # Verify content was fetched based on mood
        handler.content_manager.get_content_by_mood.assert_called_once_with(7, 'en')

        # Verify message was sent
        assert mock_update.message.reply_text.call_count >= 1

        # Verify message was logged
        handler.db.log_sent_message.assert_called_once()

    async def test_motivate_me_no_mood_uses_default(self, handler, mock_update, mock_context):
        """Test /motivateMe uses default mood when no mood history"""
        handler.db.get_user_settings.return_value = {'language': 'en'}
        handler.db.get_recent_mood.return_value = []

        await handler.motivate_me(mock_update, mock_context)

        # Should use default mood of 5
        handler.content_manager.get_content_by_mood.assert_called_once_with(5, 'en')

    async def test_motivate_me_fallback_to_random(self, handler, mock_update, mock_context):
        """Test /motivateMe falls back to random content when mood-based fails"""
        handler.db.get_user_settings.return_value = {'language': 'en'}
        handler.db.get_recent_mood.return_value = []
        handler.content_manager.get_content_by_mood.return_value = None

        await handler.motivate_me(mock_update, mock_context)

        # Should try random content as fallback
        handler.content_manager.get_random_content.assert_called_once_with('en')

    async def test_motivate_me_ultimate_fallback(self, handler, mock_update, mock_context):
        """Test /motivateMe uses hardcoded fallback when all else fails"""
        handler.db.get_user_settings.return_value = {'language': 'en'}
        handler.db.get_recent_mood.return_value = []
        handler.content_manager.get_content_by_mood.return_value = None
        handler.content_manager.get_random_content.return_value = None

        await handler.motivate_me(mock_update, mock_context)

        # Should send fallback message
        mock_update.message.reply_text.assert_called()
        call_args = mock_update.message.reply_text.call_args
        assert "You've got this" in call_args[0][0] or "Du schaffst das" in call_args[0][0]
