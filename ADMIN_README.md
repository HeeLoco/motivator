# MotivatOR Bot - Admin Commands Documentation

This document provides comprehensive documentation for all administrative commands available in the MotivatOR Bot. These commands are restricted to users with valid `ADMIN_USER_ID` credentials.

## Setup

### Environment Configuration
```bash
# Set your Telegram user ID as admin in .env file
ADMIN_USER_ID=your_telegram_user_id_here

# You can find your user ID by messaging @userinfobot on Telegram
```

## Admin Commands Overview

| Command | Description | Example |
|---------|-------------|---------|
| `/admin_stats` | View bot usage statistics | `/admin_stats` |
| `/admin_broadcast` | Send message to all users | `/admin_broadcast Hello everyone!` |
| `/admin_users` | List all users or get detailed user info | `/admin_users 1153831100` |
| `/admin_content` | Manage motivational content | `/admin_content list de` |
| `/admin_reset` | Reset specific user's data | `/admin_reset 1153831100` |

---

## 1. `/admin_stats` - Bot Statistics

View comprehensive bot usage statistics and analytics.

### Usage
```
/admin_stats
```

### Information Displayed
- **User Statistics**: Total registered, active, inactive, recently active (7 days)
- **Message Statistics**: Total messages sent, breakdown by type (text/media/links)
- **Engagement**: Total mood entries, average messages per user

### Example Output
```
📊 Admin Statistics Dashboard

👥 Users:
• Total registered: 5
• Active: 4
• Inactive/Paused: 1
• Active in last 7 days: 3

📧 Messages sent:
• Total: 47
• Text: 42
• Media: 3
• Links: 2

📈 Engagement:
• Total mood entries: 12
• Avg messages per user: 9.4
```

---

## 2. `/admin_broadcast` - Message Broadcasting

Send messages to all registered users with confirmation and progress tracking.

### Usage
```
/admin_broadcast <message>
```

### Examples
```bash
/admin_broadcast Hello everyone! The bot has been updated with new features.
/admin_broadcast Scheduled maintenance will occur tomorrow at 2 PM UTC.
```

### Features
- **Confirmation dialog** with message preview
- **Progress tracking** during send process
- **Results summary** showing success/failure counts
- **Error handling** for blocked users or delivery failures
- **Cancel option** before sending

### Safety Features
- Two-step confirmation required
- Message preview before broadcasting
- Detailed delivery reports
- Admin-only access control

---

## 3. `/admin_users` - User Management

List all users or get detailed information about specific users.

### Usage
```bash
# List all users
/admin_users

# Get detailed info for specific user
/admin_users <user_id>
```

### Examples
```bash
/admin_users                    # Show all users
/admin_users 1153831100        # Detailed info for user ID 1153831100
```

### User List Display
```
👥 All Registered Users

💡 Tip: Use /admin_users <user_id> for detailed info

1. 1153831100
📛 Edgard (@HeeLoco)
🌍 de | 📊 2/day | ✅
🕒 Last: 2025-08-15

2. 7625881376
📛 Han (@No username)
🌍 de | 📊 2/day | ✅
🕒 Last: 2025-08-14
```

### Detailed User Information
```
👤 Detailed User Information

🆔 User ID: 1153831100
📛 Name: Edgard
👤 Username: @HeeLoco
🌍 Language: de
📊 Messages per day: 5
🔄 Status: ✅ Active

📅 Activity:
• Created: 2025-08-14
• Last active: 2025-08-15

📈 Statistics:
• Messages received: 23
• Mood entries (30d): 5
• Avg mood (30d): 7.2/10

📧 Message breakdown:
• Text: 20
• Media: 2
• Links: 1
```

---

## 4. `/admin_content` - Content Management

Manage the bot's motivational content including viewing, statistics, and removal.

### Usage
```bash
# Show help menu
/admin_content

# List all content
/admin_content list

# List content by language
/admin_content list en          # English content only
/admin_content list de          # German content only

# Show content statistics
/admin_content stats

# Remove content by ID
/admin_content remove <id>

# Get help for adding content
/admin_content add
```

### Examples
```bash
/admin_content list de          # Show German content
/admin_content remove 15        # Remove content ID 15
/admin_content stats           # Show content statistics
```

### Content List Display
```
📝 Motivational Content (DE)

Found 14 items:

1. ID: 15 | DE | motivation
📱 TEXT
💬 "Du bist stärker als du denkst. Jede Herausforderung..."

2. ID: 16 | DE | motivation
📱 TEXT
💬 "Fortschritt, nicht Perfektion. Kleine Schritte..."
```

### Content Statistics
```
📊 Content Statistics

Total content: 28

By language:
• English: 14
• German: 14

By category:
• Motivation: 8
• Anxiety: 6
• Depression: 4
• Stress: 4
• Self Care: 4
• General: 2

By type:
• TEXT: 24
• VIDEO: 2
• LINK: 2
```

### Content Categories
- **ANXIETY** - For anxiety support
- **DEPRESSION** - For depression support
- **STRESS** - For stress management
- **MOTIVATION** - General motivation
- **SELF_CARE** - Self-care reminders
- **GENERAL** - General mental health

---

## 5. `/admin_reset` - User Data Reset

Reset all data for a specific user with comprehensive safety measures.

### Usage
```bash
# Show help
/admin_reset

# Reset specific user
/admin_reset <user_id>
```

### Examples
```bash
/admin_reset                    # Show usage help
/admin_reset 1153831100        # Reset data for user ID 1153831100
```

### What Gets Reset
- **Settings**: Reset to defaults (German, 2 msg/day, active)
- **Mood entries**: All deleted
- **Goals**: All deleted
- **Feedback**: All deleted
- **Message history**: All deleted

### Safety Features
- **User validation** - Checks if user exists
- **Detailed confirmation** - Shows user name and ID
- **Two-step confirmation** - Requires explicit confirmation
- **Clear warnings** - Shows exactly what will be deleted
- **Cancel option** - Can cancel before execution
- **Detailed results** - Shows success/failure status

### Confirmation Dialog
```
⚠️ Reset User Data Confirmation

Target User:
🆔 ID: 1153831100
📛 Name: Edgard (@HeeLoco)

This will DELETE ALL data for this user:
• Reset settings to defaults (German, 2 msg/day, active)
• Delete all mood entries
• Delete all goals
• Delete all feedback
• Delete all message history

⚠️ This action cannot be undone!

Are you sure you want to proceed?
```

---

## Security and Access Control

### Admin Authentication
- All admin commands require valid `ADMIN_USER_ID` in environment variables
- Commands return error message for non-admin users: `❌ This command is only available to administrators.`
- Double security checks in sensitive operations (broadcast, reset)

### Error Handling
- Input validation for all parameters
- User existence checks
- Graceful error messages
- Comprehensive logging for debugging

### Best Practices
1. **Test commands** in development environment first
2. **Backup database** before major operations
3. **Monitor logs** for any issues
4. **Use confirmation dialogs** for destructive operations
5. **Keep admin credentials secure**

---

## Troubleshooting

### Common Issues

**Command not recognized:**
- Verify `ADMIN_USER_ID` is correctly set
- Restart bot after environment changes
- Check spelling of command

**User not found errors:**
- Verify user ID is numeric
- Use `/admin_users` to see all registered users
- Check if user has ever interacted with the bot

**Broadcast delivery failures:**
- Some users may have blocked the bot
- Check individual user delivery in results summary
- Monitor logs for specific error details

**Content management issues:**
- Use plain text commands (avoid `/admin_content list de` formatting)
- Check content.py for valid content structure
- Verify content IDs exist before removal

### Logging
Admin operations are logged with INFO level:
```bash
# View logs
tail -f motivator_bot.log

# Or with systemd
journalctl -u motivator-bot -f
```

---

## Future Enhancements

Planned improvements for admin functionality:
- **Dynamic content addition** via bot commands
- **User activity analytics** with charts
- **Automated backup** and restore functions
- **Content approval** workflow
- **Multi-admin support** with role-based permissions
- **Web dashboard** for admin operations

---

## Support

For issues with admin commands:
1. Check the logs for detailed error messages
2. Verify environment configuration
3. Ensure database permissions are correct
4. Check smart scheduling settings if timing issues occur
5. Restart the bot service if needed

**Log Locations:**
- Application logs: `motivator_bot.log`
- System logs: `journalctl -u motivator-bot`

**Smart Scheduling Logs:**
Look for entries containing:
- "Smart scheduled message"
- "Smart scheduling check"
- "Mood boost factor"
- "Peak time probability"

---

## Database Schema Updates

### New Tables for Smart Scheduling

**`user_timing_preferences`** - Smart scheduling settings:
- `active_start_hour/minute` - User's active message window
- `active_end_hour/minute` - When messages should stop
- `min_gap_hours` - Minimum time between messages (1-6 hours)
- `distribution_style` - peak_focused, even_spacing, random
- `mood_boost_enabled` - Frequency boost after low mood
- `auto_adjust_timing` - Learning system enabled
- `peak_morning/afternoon/evening_start/end` - Peak time windows

**`message_schedule_log`** - Engagement tracking:
- `scheduled_time` vs `actual_send_time`
- `engagement_score` - User response metrics
- `response_time_minutes` - How quickly user responded
- `user_mood_before/after` - Mood correlation data

### Admin Database Queries

View user timing preferences:
```sql
SELECT * FROM user_timing_preferences WHERE user_id = 1153831100;
```

Check engagement patterns:
```sql
SELECT * FROM message_schedule_log WHERE user_id = 1153831100 ORDER BY created_at DESC LIMIT 10;
```

Reset user timing preferences:
```sql
DELETE FROM user_timing_preferences WHERE user_id = 1153831100;
DELETE FROM message_schedule_log WHERE user_id = 1153831100;
```

---

## Smart Scheduling Features

The bot now includes advanced timing features accessible via admin commands and user settings:

### Peak Time Optimization
- **Morning boost:** 8:00-10:00 AM (default)
- **Afternoon pickup:** 2:00-4:00 PM (default)  
- **Evening support:** 6:00-8:00 PM (default)
- 60% of messages sent during these optimal times

### User Configurable Settings
Available via `/settings` → `⏰ Timing`:
- **Active hours:** When user wants to receive messages
- **Minimum gap:** Time between messages (1-6 hours)
- **Start/end times:** Personal message window

### Mood-Based Adjustments
- **Low mood (1-4):** +50% frequency for 24 hours
- **Very low mood (1-2):** +100% frequency for 12 hours
- Automatic adjustment based on `/mood` entries

### Engagement Learning
- Tracks when users respond to messages
- Learns optimal send times per user
- Adjusts future scheduling based on engagement