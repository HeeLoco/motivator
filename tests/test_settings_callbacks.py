"""
Unit tests for SettingsCallbackHandler.

Tests settings-related callback handling: language, frequency, timing, etc.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from src.handlers.callbacks.settings import SettingsCallbackHandler
from tests.conftest import MockCallbackQuery, MockContext


@pytest.mark.unit
@pytest.mark.asyncio
class TestSettingsCallbackHandler:
    """Test suite for settings callback handlers"""

    @pytest.fixture
    def mock_bot(self, mock_database):
        """Create mock bot instance"""
        bot = Mock()
        bot.db = mock_database
        return bot

    @pytest.fixture
    def handler(self, mock_bot):
        """Create handler instance"""
        return SettingsCallbackHandler(mock_bot)

    async def test_handle_language_select_german(self, handler):
        """Test selecting German language"""
        query = MockCallbackQuery(user_id=12345, data="lang_de")
        context = MockContext()

        await handler.handle_language_select(query, context)

        # Verify language was updated
        handler.db.update_user_setting.assert_called_once_with(12345, 'language', 'de')

        # Verify confirmation message
        query.edit_message_text.assert_called_once()
        call_args = query.edit_message_text.call_args
        assert "Deutsch" in call_args[0][0]

    async def test_handle_language_select_english(self, handler):
        """Test selecting English language"""
        query = MockCallbackQuery(user_id=12345, data="lang_en")
        context = MockContext()

        await handler.handle_language_select(query, context)

        handler.db.update_user_setting.assert_called_once_with(12345, 'language', 'en')

        query.edit_message_text.assert_called_once()
        call_args = query.edit_message_text.call_args
        assert "English" in call_args[0][0]

    async def test_handle_set_language_menu(self, handler):
        """Test displaying language selection menu"""
        query = MockCallbackQuery(user_id=12345, data="set_language")
        context = MockContext()

        await handler.handle_set_language(query, context)

        # Verify menu was displayed
        query.edit_message_text.assert_called_once()
        call_kwargs = query.edit_message_text.call_args[1]
        assert 'reply_markup' in call_kwargs

    async def test_handle_frequency_select(self, handler):
        """Test selecting message frequency"""
        query = MockCallbackQuery(user_id=12345, data="freq_3")
        context = MockContext()

        await handler.handle_frequency_select(query, context)

        # Verify frequency was updated to 3
        handler.db.update_user_setting.assert_called_once_with(12345, 'message_frequency', 3)

        # Verify confirmation
        query.edit_message_text.assert_called_once()

    async def test_handle_toggle_active_pause(self, handler):
        """Test toggling active status from active to paused"""
        query = MockCallbackQuery(user_id=12345, data="toggle_active")
        context = MockContext()
        handler.db.get_user_settings.return_value = {'active': True, 'language': 'en'}

        await handler.handle_toggle_active(query, context)

        # Verify active was set to False (paused)
        handler.db.update_user_setting.assert_called_once_with(12345, 'active', False)

        # Verify pause message
        call_args = query.edit_message_text.call_args
        assert "paused" in call_args[0][0].lower()

    async def test_handle_toggle_active_resume(self, handler):
        """Test toggling active status from paused to active"""
        query = MockCallbackQuery(user_id=12345, data="toggle_active")
        context = MockContext()
        handler.db.get_user_settings.return_value = {'active': False, 'language': 'en'}

        await handler.handle_toggle_active(query, context)

        # Verify active was set to True (resumed)
        handler.db.update_user_setting.assert_called_once_with(12345, 'active', True)

        # Verify resume message
        call_args = query.edit_message_text.call_args
        assert "resumed" in call_args[0][0].lower()

    async def test_handle_set_timing_menu(self, handler):
        """Test displaying timing preferences menu"""
        query = MockCallbackQuery(user_id=12345, data="set_timing")
        context = MockContext()

        await handler.handle_set_timing(query, context)

        # Verify timing menu was displayed
        query.edit_message_text.assert_called_once()
        call_args = query.edit_message_text.call_args
        assert "08:00 - 22:00" in call_args[0][0]  # From mock timing prefs

    async def test_handle_start_time_select(self, handler):
        """Test selecting start time"""
        query = MockCallbackQuery(user_id=12345, data="start_time_9")
        context = MockContext()

        await handler.handle_start_time_select(query, context)

        # Verify start time was updated to 9
        handler.db.update_timing_preference.assert_called_once_with(12345, 'active_start_hour', 9)

    async def test_handle_end_time_select(self, handler):
        """Test selecting end time"""
        query = MockCallbackQuery(user_id=12345, data="end_time_20")
        context = MockContext()

        await handler.handle_end_time_select(query, context)

        # Verify end time was updated to 20
        handler.db.update_timing_preference.assert_called_once_with(12345, 'active_end_hour', 20)

    async def test_handle_min_gap_select(self, handler):
        """Test selecting minimum gap between messages"""
        query = MockCallbackQuery(user_id=12345, data="min_gap_3")
        context = MockContext()

        await handler.handle_min_gap_select(query, context)

        # Verify min gap was updated to 3 hours
        handler.db.update_timing_preference.assert_called_once_with(12345, 'min_gap_hours', 3)

    async def test_handle_reset_user_confirmation(self, handler):
        """Test displaying reset confirmation dialog"""
        query = MockCallbackQuery(user_id=12345, data="reset_user")
        context = MockContext()

        await handler.handle_reset_user(query, context)

        # Verify warning message was displayed
        query.edit_message_text.assert_called_once()
        call_args = query.edit_message_text.call_args
        assert "Warning" in call_args[0][0] or "Warnung" in call_args[0][0]
        assert "cannot be undone" in call_args[0][0] or "rückgängig" in call_args[0][0]

    async def test_handle_confirm_reset(self, handler):
        """Test confirming user data reset"""
        query = MockCallbackQuery(user_id=12345, data="confirm_reset")
        context = MockContext()
        handler.db.reset_user_data.return_value = True

        await handler.handle_confirm_reset(query, context)

        # Verify reset was executed
        handler.db.reset_user_data.assert_called_once_with(12345)

        # Verify success message
        query.edit_message_text.assert_called_once()
        call_args = query.edit_message_text.call_args
        assert "successful" in call_args[0][0].lower() or "erfolgreich" in call_args[0][0].lower()

    async def test_handle_back_to_settings(self, handler):
        """Test navigating back to settings menu"""
        query = MockCallbackQuery(user_id=12345, data="back_to_settings")
        context = MockContext()

        await handler.handle_back_to_settings(query, context)

        # Verify settings menu was redisplayed
        query.edit_message_text.assert_called_once()
        call_args = query.edit_message_text.call_args
        assert "Settings" in call_args[0][0] or "Einstellungen" in call_args[0][0]
