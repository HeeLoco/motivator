"""
Integration tests for MotivatorBot.

Tests bot initialization, handler registration, and full system integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.bot import MotivatorBot


@pytest.mark.integration
class TestBotIntegration:
    """Integration tests for full bot setup"""

    @patch('src.bot.Database')
    @patch('src.bot.ContentManager')
    @patch('src.bot.SmartMessageScheduler')
    @patch('src.bot.Application')
    def test_bot_initialization(self, mock_app, mock_scheduler,
                               mock_content_mgr, mock_db):
        """Test bot initializes all dependencies correctly"""
        # Setup mocks
        mock_app_instance = Mock()
        mock_app.builder.return_value.token.return_value.build.return_value = mock_app_instance

        # Create bot
        bot = MotivatorBot("test_token", admin_user_id=99999)

        # Verify core dependencies were initialized
        mock_db.assert_called_once()
        mock_content_mgr.assert_called_once()
        mock_scheduler.assert_called_once()

        # Verify bot attributes
        assert bot.bot_token == "test_token"
        assert bot.admin_user_id == 99999
        assert bot.db is not None
        assert bot.content_manager is not None
        assert bot.scheduler is not None

    @patch('src.bot.Database')
    @patch('src.bot.ContentManager')
    @patch('src.bot.SmartMessageScheduler')
    
    @patch('src.bot.Application')
    def test_all_handlers_initialized(self, mock_app, mock_scheduler,
                                      mock_content_mgr, mock_db):
        """Test all command handlers are initialized"""
        mock_app_instance = Mock()
        mock_app.builder.return_value.token.return_value.build.return_value = mock_app_instance

        bot = MotivatorBot("test_token")

        # Verify all handlers exist
        assert bot.user_handler is not None
        assert bot.mood_handler is not None
        
        assert bot.admin_handler is not None
        assert bot.text_handler is not None
        assert bot.callback_router is not None

    @patch('src.bot.Database')
    @patch('src.bot.ContentManager')
    @patch('src.bot.SmartMessageScheduler')
    
    @patch('src.bot.Application')
    def test_handlers_registered(self, mock_app, mock_scheduler,
                                 mock_content_mgr, mock_db):
        """Test all handlers are registered with the application"""
        mock_app_instance = Mock()
        mock_app.builder.return_value.token.return_value.build.return_value = mock_app_instance

        bot = MotivatorBot("test_token")

        # Verify handlers were added (add_handler should have been called multiple times)
        assert mock_app_instance.add_handler.call_count >= 14  # At least 14 handlers

    @patch('src.bot.Database')
    @patch('src.bot.ContentManager')
    @patch('src.bot.SmartMessageScheduler')
    
    @patch('src.bot.Application')
    def test_user_commands_registered(self, mock_app, mock_scheduler,
                                     mock_content_mgr, mock_db):
        """Test user commands are registered"""
        mock_app_instance = Mock()
        mock_app.builder.return_value.token.return_value.build.return_value = mock_app_instance

        bot = MotivatorBot("test_token")

        # Get all CommandHandler registrations
        command_calls = [
            call for call in mock_app_instance.add_handler.call_args_list
            if 'CommandHandler' in str(call)
        ]

        # Verify key commands were registered
        registered_commands = [str(call) for call in command_calls]
        commands_to_check = ['start', 'help', 'settings', 'mood', 'stats']

        for cmd in commands_to_check:
            assert any(cmd in str(call) for call in registered_commands), \
                f"Command /{cmd} should be registered"

    @patch('src.bot.Database')
    @patch('src.bot.ContentManager')
    @patch('src.bot.SmartMessageScheduler')
    
    @patch('src.bot.Application')
    def test_admin_commands_registered(self, mock_app, mock_scheduler,
                                      mock_content_mgr, mock_db):
        """Test admin commands are registered"""
        mock_app_instance = Mock()
        mock_app.builder.return_value.token.return_value.build.return_value = mock_app_instance

        bot = MotivatorBot("test_token", admin_user_id=99999)

        # Verify admin commands
        command_calls = [str(call) for call in mock_app_instance.add_handler.call_args_list]
        admin_commands = ['admin_stats', 'admin_broadcast', 'admin_users',
                         'admin_content', 'admin_reset']

        for cmd in admin_commands:
            assert any(cmd in str(call) for call in command_calls), \
                f"Admin command /{cmd} should be registered"

    @patch('src.bot.Database')
    @patch('src.bot.ContentManager')
    @patch('src.bot.SmartMessageScheduler')
    
    @patch('src.bot.Application')
    def test_callback_handler_registered(self, mock_app, mock_scheduler,
                                         mock_content_mgr, mock_db):
        """Test callback query handler is registered"""
        mock_app_instance = Mock()
        mock_app.builder.return_value.token.return_value.build.return_value = mock_app_instance

        bot = MotivatorBot("test_token")

        # Verify CallbackQueryHandler was registered
        handler_calls = [str(call) for call in mock_app_instance.add_handler.call_args_list]
        assert any('CallbackQueryHandler' in str(call) for call in handler_calls), \
            "CallbackQueryHandler should be registered"

    @patch('src.bot.Database')
    @patch('src.bot.ContentManager')
    @patch('src.bot.SmartMessageScheduler')
    
    @patch('src.bot.Application')
    @pytest.mark.asyncio
    async def test_send_motivational_message_delegates(self, mock_app,
                                                       mock_scheduler, mock_content_mgr, mock_db):
        """Test send_motivational_message delegates to admin handler"""
        mock_app_instance = Mock()
        mock_app.builder.return_value.token.return_value.build.return_value = mock_app_instance

        bot = MotivatorBot("test_token")

        # Mock the admin handler's method
        from unittest.mock import AsyncMock
        bot.admin_handler.send_motivational_message = AsyncMock()

        # Call the wrapper
        await bot.send_motivational_message(12345)

        # Verify delegation
        bot.admin_handler.send_motivational_message.assert_called_once_with(12345)

    @patch('src.bot.Database')
    @patch('src.bot.ContentManager')
    @patch('src.bot.SmartMessageScheduler')
    
    @patch('src.bot.Application')
    def test_run_starts_scheduler_and_bot(self, mock_app, mock_scheduler,
                                         mock_content_mgr, mock_db):
        """Test run() starts both scheduler and bot polling"""
        mock_app_instance = Mock()
        mock_app.builder.return_value.token.return_value.build.return_value = mock_app_instance
        mock_scheduler_instance = Mock()
        mock_scheduler.return_value = mock_scheduler_instance

        bot = MotivatorBot("test_token")
        bot.run()

        # Verify scheduler was started
        mock_scheduler_instance.start.assert_called_once_with(bot)

        # Verify bot started polling
        mock_app_instance.run_polling.assert_called_once()
