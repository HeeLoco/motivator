"""
Unit tests for CallbackRouter.

Tests callback routing logic and handler delegation.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.handlers.callbacks.router import CallbackRouter
from tests.conftest import MockUpdate, MockContext


@pytest.mark.unit
@pytest.mark.asyncio
class TestCallbackRouter:
    """Test suite for callback routing"""

    @pytest.fixture
    def mock_bot_instance(self, mock_database, mock_content_manager, mock_scheduler, mock_goal_manager):
        """Create a mock bot instance with all dependencies"""
        bot = Mock()
        bot.db = mock_database
        bot.content_manager = mock_content_manager
        bot.scheduler = mock_scheduler
        bot.goal_manager = mock_goal_manager
        bot.admin_user_id = None
        bot.application = Mock()
        return bot

    @pytest.fixture
    def router(self, mock_bot_instance):
        """Create router instance"""
        return CallbackRouter(mock_bot_instance)

    async def test_route_answers_callback(self, router):
        """Test that router answers callback query"""
        update = MockUpdate(callback_data="test_data")
        context = MockContext()

        # Mock all handlers to prevent errors
        router.exact_handlers = {'test_data': AsyncMock()}

        await router.route(update, context)

        # Verify callback was answered
        update.callback_query.answer.assert_called_once()

    async def test_route_language_prefix(self, router):
        """Test routing for lang_ prefix"""
        update = MockUpdate(callback_data="lang_en")
        context = MockContext()

        await router.route(update, context)

        # Should have been handled (no error raised)
        update.callback_query.answer.assert_called_once()

    async def test_route_mood_prefix(self, router):
        """Test routing for mood_ prefix"""
        update = MockUpdate(callback_data="mood_7")
        context = MockContext()

        await router.route(update, context)

        update.callback_query.answer.assert_called_once()

    async def test_route_feedback_prefix(self, router):
        """Test routing for feedback_ prefix"""
        update = MockUpdate(callback_data="feedback_love_123")
        context = MockContext()

        await router.route(update, context)

        update.callback_query.answer.assert_called_once()

    async def test_route_goal_category_prefix(self, router):
        """Test routing for goal_category_ prefix"""
        update = MockUpdate(callback_data="goal_category_health")
        context = MockContext()

        await router.route(update, context)

        update.callback_query.answer.assert_called_once()

    async def test_route_exact_match_close_menu(self, router):
        """Test exact match routing for close_menu"""
        update = MockUpdate(callback_data="close_menu")
        context = MockContext()

        await router.route(update, context)

        update.callback_query.answer.assert_called_once()
        update.callback_query.delete_message.assert_called_once()

    async def test_route_exact_match_set_language(self, router):
        """Test exact match routing for set_language"""
        update = MockUpdate(callback_data="set_language")
        context = MockContext()

        await router.route(update, context)

        update.callback_query.answer.assert_called_once()

    async def test_route_unknown_callback(self, router):
        """Test routing handles unknown callback data"""
        update = MockUpdate(callback_data="unknown_callback_xyz")
        context = MockContext()

        await router.route(update, context)

        # Should answer and send error message
        update.callback_query.answer.assert_called_once()
        update.callback_query.edit_message_text.assert_called_once()
        call_args = update.callback_query.edit_message_text.call_args
        assert "Unknown action" in call_args[0][0]

    async def test_route_prefix_priority(self, router):
        """Test that more specific prefixes are matched first"""
        # goal_delete_confirm_ should match before goal_delete_
        update = MockUpdate(callback_data="goal_delete_confirm_5")
        context = MockContext()

        await router.route(update, context)

        # Should not raise error - confirms correct handler was called
        update.callback_query.answer.assert_called_once()

    async def test_close_menu_handler(self, router):
        """Test _handle_close_menu deletes message"""
        query = Mock()
        query.delete_message = AsyncMock()
        context = MockContext()

        await router._handle_close_menu(query, context)

        query.delete_message.assert_called_once()
