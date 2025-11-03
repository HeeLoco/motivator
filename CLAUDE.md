# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Motivator Bot is a Telegram bot designed for mental health support and motivation. It sends personalized motivational messages, tracks user mood, manages goals, and provides mental health resources. The bot supports bilingual content (English/German).

**Purpose**: Support individuals with psychological challenges through automated motivational messaging, mood tracking, and goal management.

## Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your BOT_TOKEN from @BotFather

# Run the bot (default: INFO level, text format)
python main.py

# Run with debug logging
LOG_LEVEL=DEBUG python main.py

# Run with JSON logging (for testing container format)
LOG_FORMAT=json python main.py

# Run with custom log file
LOG_FILE=custom.log python main.py
```

### Database Management
```bash
# View database contents (SQLite)
sqlite3 motivator.db

# Backup database
cp motivator.db motivator.db.backup

# Reset database (WARNING: deletes all data)
rm motivator.db
python main.py  # Recreates database
```

### Testing
```bash
# Test logging system (both JSON and text formats)
python test_logging.py

# Test module imports
python test_imports.py

# Manual testing
# - Test manually by interacting with the bot
# - Use group chats for beta testing
# - Monitor logs: tail -f motivator_bot.log
# - Monitor container logs: docker compose logs -f
```

## Architecture

### Core Components

The bot uses a **modular handler architecture** with clear separation of concerns:

**Core Modules:**
1. **`main.py`** - Entry point, environment setup, logging initialization
2. **`bot.py`** - Orchestrator - coordinates handlers and manages application lifecycle
3. **`logging_config.py`** - Structured logging with JSON/text formatters, correlation IDs, environment-based configuration
4. **`database.py`** - SQLite operations, user data management, analytics
5. **`content.py`** - Motivational content management, categorization, multi-language support
6. **`smart_scheduler.py`** - Intelligent message scheduling with peak-time optimization
7. **`goals.py`** - Goal templates and management logic

**Handler Modules** (`src/handlers/`):
- **`base.py`** - Base handler class with shared utilities
- **`user_commands.py`** - User commands (/start, /help, /settings, /pause, /resume, /motivateMe)
- **`mood_commands.py`** - Mood tracking (/mood, /stats)
- **`goal_commands.py`** - Goal management (/goals)
- **`admin_commands.py`** - Admin operations (/admin_*)
- **`message_handler.py`** - Text message processing

**Callback Handlers** (`src/handlers/callbacks/`):
- **`router.py`** - Central callback routing
- **`settings.py`** - Settings-related callbacks (language, frequency, timing)
- **`mood.py`** - Mood selection and feedback callbacks
- **`goals.py`** - Goal workflow callbacks
- **`admin.py`** - Admin operation callbacks

### Key Design Patterns

**Database Schema**: 
- `users` - User settings, preferences, activity status
- `user_timing_preferences` - Smart scheduling settings (active hours, peak times, minimum gaps)
- `message_schedule_log` - Engagement tracking for learning optimal send times
- `sent_messages` - Message tracking for analytics
- `feedback` - User feedback on message effectiveness
- `mood_entries` - Mood tracking (1-10 scale)
- `user_goals` - Personal goal management

**Content Management**:
- Enum-based categorization (MoodCategory: ANXIETY, DEPRESSION, STRESS, MOTIVATION, SELF_CARE, GENERAL)
- Content types: TEXT, IMAGE, VIDEO, LINK
- Language-specific content arrays in `content.py`
- Mood-based content selection algorithm

**Smart Message Scheduling**:
- Peak-focused distribution (60% during optimal motivation times)
- Intelligent timing with morning (8-10 AM), afternoon (2-4 PM), evening (6-8 PM) peaks
- User-configurable active hours and minimum gaps (1-6 hours)
- Mood-based frequency boost (+50% after low mood, +100% after very low mood)
- Engagement tracking for learning optimal send times
- Daily limits to prevent over-messaging
- Daily mood reminders at 8 PM

### User Interaction Flow

1. User starts with `/start` → Language selection → Database user creation
2. Settings configuration via `/settings` → Inline keyboards (language, frequency, timing preferences)
3. Mood tracking via `/mood` → Triggers personalized content selection
4. Scheduled messages → Content based on recent mood and user preferences
5. Feedback collection → Simple emoji reactions logged to database

## Content Guidelines

### Adding New Motivational Content

```python
# Edit content.py to add new messages
new_content = MotivationalContent(
    id=0,  # Auto-assigned
    content="Your supportive message here",
    content_type=ContentType.TEXT,
    language='en',  # or 'de'
    category=MoodCategory.MOTIVATION,  # Choose appropriate category
    media_url=None,  # Optional for links/videos
    tags=None  # Optional tags for future filtering
)
```

**Content Standards**:
- Focus on mental health best practices
- Appropriate for individuals with anxiety, depression, stress
- Non-triggering, supportive language
- Include both English and German versions
- Crisis resources should link to legitimate support organizations

### Media Content Guidelines
- YouTube shorts for breathing exercises, meditation
- Links to official mental health resources
- No user-generated content that hasn't been verified
- Always include descriptive text with media links

## Configuration

### Environment Variables

**Bot Configuration:**
- `BOT_TOKEN` (required) - From @BotFather on Telegram
- `ADMIN_USER_ID` (optional) - Admin user for bot management

**Logging Configuration:**
- `LOG_LEVEL` (optional, default: INFO) - Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FORMAT` (optional, auto-detected) - Format type ('json' or 'text')
  - Auto-detects 'json' in containers, 'text' in development
- `LOG_FILE` (optional, default: motivator_bot.log in dev, disabled in containers) - Log file path
- `CONTAINER_ENV` (optional, auto-detected) - Set to 'true' to force container mode

### User Settings (Database)
- `language` - 'en' or 'de' 
- `message_frequency` - 1-5 messages per day
- `timezone` - User timezone (not fully implemented)
- `active` - Boolean for pause/resume functionality

### Smart Timing Preferences (Database)
- `active_start_hour/minute` - When daily messages should begin
- `active_end_hour/minute` - When daily messages should end
- `min_gap_hours` - Minimum time between messages (1-6 hours)
- `distribution_style` - peak_focused, even_spacing, or random
- `mood_boost_enabled` - Enable frequency boost after low mood
- `auto_adjust_timing` - Allow system to learn optimal send times
- `peak_morning/afternoon/evening_start/end` - Customizable peak time windows

## Deployment

### Local Development
```bash
# Virtual environment recommended
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with BOT_TOKEN

# Run the bot
python main.py
```

### Docker Deployment

**Build and run with Docker Compose:**
```bash
# Create .env file with BOT_TOKEN
cp .env.example .env
# Edit .env file

# Build and start the bot
docker compose up -d

# View logs (JSON format)
docker compose logs -f

# View logs with grep filtering
docker compose logs -f | grep ERROR

# Stop the bot
docker compose down

# Restart the bot
docker compose restart

# View bot status
docker compose ps
```

**Logging in Containers:**
- Logs output to stdout/stderr in JSON format
- Captured by Docker's json-file driver
- Max 3 files, 10MB each (rotates automatically)
- View with: `docker compose logs -f`
- File logging disabled by default in containers

**Database Persistence:**
- Database mounted as volume in docker-compose.yml
- Survives container restarts
- Backup: `cp motivator.db motivator.db.backup`

**Optional: Log Aggregation with Loki**
Uncomment the Loki, Promtail, and Grafana sections in docker-compose.yml to enable centralized logging:
```bash
docker compose up -d
# Access Grafana at http://localhost:3000 (admin/admin)
```

### Security Considerations
- No sensitive data in code - use environment variables
- Bot token in .env file (never commit to git)
- .env file excluded from Docker builds (.dockerignore)
- SQLite database with local storage only
- User data remains on local system
- Container runs as non-root (future enhancement)

## Debugging and Monitoring

### Logging System

The bot uses a **dual-format structured logging system** optimized for both development and production:

**Architecture:**
- **Development**: Human-readable text format with color coding
- **Container**: Structured JSON format for machine parsing
- **Auto-detection**: Automatically selects format based on environment
- **Correlation IDs**: Track related operations across log entries
- **Structured Context**: User IDs, extra fields, and metadata

**Log Levels:**
- `DEBUG`: Detailed diagnostic info (includes module, function, line number)
- `INFO`: General operational events (default)
- `WARNING`: Unexpected but handled situations
- `ERROR`: Errors requiring attention
- `CRITICAL`: Critical failures

**Configuration:**
```bash
# Set log level
export LOG_LEVEL=DEBUG

# Force format (overrides auto-detection)
export LOG_FORMAT=json  # or 'text'

# Custom log file (default: motivator_bot.log in dev, disabled in containers)
export LOG_FILE=/path/to/custom.log

# Force container mode
export CONTAINER_ENV=true
```

**Example Text Output (Development):**
```
2025-11-03 14:30:15 - smart_scheduler - INFO - [user:12345 | corr:msg_abc123] - Message sent successfully (mood_category=MOTIVATION, message_frequency=3)
```

**Example JSON Output (Container):**
```json
{"timestamp": "2025-11-03T14:30:15Z", "level": "INFO", "logger": "smart_scheduler", "user_id": 12345, "correlation_id": "msg_abc123", "message": "Message sent successfully", "mood_category": "MOTIVATION", "message_frequency": 3}
```

**Using Logging in Code:**
```python
from src.logging_config import get_logger, log_with_context
import logging

logger = get_logger(__name__)

# Basic logging
logger.info("Operation completed")

# Logging with context
log_with_context(
    logger, logging.INFO,
    "Message sent",
    user_id=12345,
    mood_category="MOTIVATION",
    success=True
)

# Correlation IDs (for tracking related operations)
from src.logging_config import set_correlation_id, clear_correlation_id

correlation_id = f"msg_{user_id}_{uuid.uuid4().hex[:8]}"
set_correlation_id(correlation_id)
logger.info("Starting operation")
# ... do work ...
logger.info("Completed operation")
clear_correlation_id()
```

**Monitoring Logs:**
```bash
# Development (text format)
tail -f motivator_bot.log
tail -f motivator_bot.log | grep ERROR

# Container (JSON format)
docker compose logs -f
docker compose logs -f | grep '"level":"ERROR"'
docker compose logs -f | jq 'select(.user_id == 12345)'

# Filter by correlation ID
docker compose logs -f | jq 'select(.correlation_id == "msg_abc123")'
```

**Database Logging:**
The bot also maintains separate database logging for analytics:
- `sent_messages` - Message delivery tracking
- `message_schedule_log` - Engagement tracking for learning
- `feedback` - User feedback on messages
- `mood_entries` - Mood tracking history

### Common Issues
- **Bot not responding**: Check BOT_TOKEN in .env, check logs for startup errors
- **Database errors**: Verify file permissions, check logs for SQL errors
- **Scheduling issues**: Check system time/timezone, verify user timing preferences, review scheduler logs
- **Message delivery failures**: Monitor Telegram API rate limits, check ERROR level logs
- **Timing not working**: Check user active hours and minimum gap settings
- **Too many/few messages**: Verify smart scheduling algorithm and mood boost settings, review DEBUG logs
- **Logging not working**: Verify LOG_LEVEL environment variable, check file permissions for log file

## Future Development Areas

1. **Advanced Timing Features**: Calendar integration, timezone detection, sleep schedule awareness
2. **Enhanced Personalization**: Machine learning for content selection based on engagement patterns
3. **Advanced Scheduling**: Weekly patterns, holiday awareness, context-aware timing
4. **Crisis Detection**: Keyword monitoring for emergency situations  
5. **Group Features**: Collaborative goal setting, group challenges
6. **Analytics Dashboard**: Web interface for usage statistics and timing analytics
7. **Content Management**: Admin interface for non-technical content updates
8. **Integration**: Calendar apps, fitness trackers, other mental health tools

## Mental Health Considerations

- This is a supportive tool, not a replacement for professional care
- Crisis resources should always be readily available
- Content should be reviewed by mental health professionals
- User privacy and data protection are paramount
- Consider implementing crisis detection and escalation procedures