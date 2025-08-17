# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MotivatOR Bot is a Telegram bot designed for mental health support and motivation. It sends personalized motivational messages, tracks user mood, manages goals, and provides mental health resources. The bot is designed to run on a Raspberry Pi and supports bilingual content (English/German).

**Purpose**: Support individuals with psychological challenges through automated motivational messaging, mood tracking, and goal management.

## Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your BOT_TOKEN from @BotFather

# Run the bot
python main.py

# Run with debug logging
python main.py --debug
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
- No formal test suite exists yet
- Test manually by interacting with the bot
- Use group chats for beta testing
- Monitor logs with `tail -f motivator_bot.log`

## Architecture

### Core Components

1. **`main.py`** - Entry point, environment setup, logging configuration
2. **`bot.py`** - Main bot logic, Telegram handlers, user interactions
3. **`database.py`** - SQLite operations, user data management, analytics
4. **`content.py`** - Motivational content management, categorization, multi-language support
5. **`smart_scheduler.py`** - Intelligent message scheduling with peak-time optimization, mood-based frequency adjustment

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
- `BOT_TOKEN` (required) - From @BotFather on Telegram
- `ADMIN_USER_ID` (optional) - Admin user for bot management

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

## Deployment Notes

### Raspberry Pi Deployment
- Use systemd service for auto-start
- Virtual environment recommended
- SQLite database requires write permissions
- Log monitoring via `journalctl -u motivator-bot -f`

### Security Considerations
- No sensitive data in code - use environment variables
- Local SQLite database (no cloud storage)
- User data remains on local system
- Bot token should be protected

## Debugging and Monitoring

### Common Issues
- **Bot not responding**: Check BOT_TOKEN in .env
- **Database errors**: Verify file permissions
- **Scheduling issues**: Check system time/timezone, verify user timing preferences
- **Message delivery failures**: Monitor Telegram API rate limits
- **Timing not working**: Check user active hours and minimum gap settings
- **Too many/few messages**: Verify smart scheduling algorithm and mood boost settings

### Logging
- Application logs to `motivator_bot.log`
- Database operations logged at INFO level
- Scheduler events logged for debugging
- Error handling with user-friendly messages

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