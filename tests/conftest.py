"""
Pytest fixtures for Motivator Bot tests.

Provides common test fixtures including mocks for database, bot, and Telegram objects.
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime

# Mock Telegram types
class MockUser:
    """Mock Telegram User"""
    def __init__(self, user_id=12345, username="testuser", first_name="Test"):
        self.id = user_id
        self.username = username
        self.first_name = first_name


class MockMessage:
    """Mock Telegram Message"""
    def __init__(self, user_id=12345, text="test"):
        self.message_id = 1
        self.text = text
        self.from_user = MockUser(user_id)
        self.reply_text = AsyncMock()


class MockCallbackQuery:
    """Mock Telegram CallbackQuery"""
    def __init__(self, user_id=12345, data="test_callback"):
        self.id = "callback_123"
        self.data = data
        self.from_user = MockUser(user_id)
        self.message = MockMessage(user_id)
        self.answer = AsyncMock()
        self.edit_message_text = AsyncMock()
        self.delete_message = AsyncMock()


class MockUpdate:
    """Mock Telegram Update"""
    def __init__(self, user_id=12345, message_text="test", callback_data=None):
        self.effective_user = MockUser(user_id)
        self.effective_chat = Mock()
        self.effective_chat.send_message = AsyncMock()

        if callback_data:
            self.callback_query = MockCallbackQuery(user_id, callback_data)
            self.message = None
        else:
            self.message = MockMessage(user_id, message_text)
            self.callback_query = None


class MockContext:
    """Mock Telegram Context"""
    def __init__(self):
        self.args = []
        self.user_data = {}
        self.bot = Mock()
        self.bot.send_message = AsyncMock()


# Fixtures

@pytest.fixture
def mock_database():
    """Mock database with common methods"""
    db = Mock()

    # User management
    db.add_user = Mock()
    db.get_user_settings = Mock(return_value={
        'user_id': 12345,
        'username': 'testuser',
        'first_name': 'Test',
        'language': 'en',
        'message_frequency': 2,
        'active': True,
        'created_at': datetime.now().isoformat(),
        'last_active': datetime.now().isoformat()
    })
    db.get_all_users = Mock(return_value=[12345, 67890])
    db.get_active_users = Mock(return_value=[12345])
    db.get_all_users_detailed = Mock(return_value=[])
    db.get_user_detailed_info = Mock(return_value=None)
    db.update_user_setting = Mock()
    db.reset_user_data = Mock(return_value=True)

    # Timing preferences
    db.get_user_timing_preferences = Mock(return_value={
        'active_start_hour': 8,
        'active_start_minute': 0,
        'active_end_hour': 22,
        'active_end_minute': 0,
        'min_gap_hours': 2
    })
    db.update_timing_preference = Mock()

    # Mood tracking
    db.add_mood_entry = Mock()
    db.get_recent_mood = Mock(return_value=[])
    db.get_message_stats = Mock(return_value={'text': 10, 'image': 2, 'video': 1, 'link': 3})
    db.get_total_mood_entries = Mock(return_value=25)
    db.get_recently_active_users = Mock(return_value=[12345])

    # Messages and feedback
    db.log_sent_message = Mock()
    db.add_feedback = Mock()
    db.get_recent_sent_content_ids = Mock(return_value=[])

    return db


@pytest.fixture
def mock_content_manager():
    """Mock content manager"""
    cm = Mock()

    mock_content = Mock()
    mock_content.id = 1
    mock_content.content = "Test motivational message"
    mock_content.content_type = Mock(value='text')
    mock_content.language = 'en'
    mock_content.category = Mock(value='motivation')
    mock_content.media_url = None

    cm.get_content_by_mood = Mock(return_value=mock_content)
    cm.get_random_content = Mock(return_value=mock_content)
    cm.get_all_content = Mock(return_value=[mock_content])
    cm.remove_content = Mock(return_value=True)

    return cm


@pytest.fixture
def mock_scheduler():
    """Mock smart scheduler"""
    scheduler = Mock()
    scheduler.start = Mock()
    return scheduler


@pytest.fixture
def mock_update():
    """Create a mock Telegram Update"""
    return MockUpdate()


@pytest.fixture
def mock_context():
    """Create a mock Telegram Context"""
    return MockContext()


@pytest.fixture
def mock_application():
    """Mock Telegram Application"""
    app = Mock()
    app.bot = Mock()
    app.bot.send_message = AsyncMock()
    return app


@pytest.fixture
def test_user_id():
    """Standard test user ID"""
    return 12345


@pytest.fixture
def admin_user_id():
    """Admin user ID for testing"""
    return 99999
