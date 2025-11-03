# Motivator Bot 🤖💙

A Telegram bot designed to support mental health and motivation through personalized messages and mood tracking. Perfect for individuals dealing with psychological challenges and their support networks.

## Features

### 🌟 Core Features
- **Personalized Motivational Messages**: Random supportive messages throughout the day
- **Bilingual Support**: English and German content
- **Mood Tracking**: Daily mood logging with personalized responses
- **Feedback System**: Learn from user reactions to improve content
- **Media Content**: YouTube videos, support links, and motivational images

### 🎯 Mental Health Focus
- Content specifically designed for anxiety, depression, and stress support
- Self-care reminders and coping strategies
- Crisis resources and support links
- Adaptive messaging based on mood patterns

### ⚙️ Customization
- Configurable message frequency (1-5 messages per day)
- Language preferences (English/German)
- Pause/resume functionality
- Personal timezone support

## Virtual Environment Setup (Recommended)

Using a virtual environment isolates your project dependencies and prevents conflicts with other Python projects.

### Why Use Virtual Environment?
- **Isolation**: Keeps project dependencies separate
- **Version Control**: Manages specific package versions
- **Clean System**: Prevents conflicts with system Python
- **Reproducibility**: Ensures consistent environment across devices

### Virtual Environment Commands
```bash
# Create virtual environment (one time setup)
python3 -m venv venv

# Activate virtual environment (every time you work on the project)
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install/update dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run your bot
python main.py

# Deactivate when done working
deactivate
```

### Daily Usage Workflow
```bash
cd motivator
source venv/bin/activate  # Start working
python main.py           # Run bot
# Work with bot...
deactivate              # Stop working
```

## Quick Start

### 1. Prerequisites
- Python 3.8+
- Telegram Bot Token (from @BotFather)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd motivator

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your bot token
nano .env
```

### 3. Get Your Bot Token
1. Message @BotFather on Telegram
2. Create a new bot with `/newbot`
3. Copy your bot token to `.env`

### 4. Run the Bot
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the bot
python main.py

# Stop the bot with Ctrl+C when done
# Deactivate virtual environment when finished
deactivate
```

## Configuration

### Environment Variables (.env)
```
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_USER_ID=your_telegram_user_id_here  # Optional
```

### User Commands
- `/start` - Initialize bot and setup
- `/help` - Show all available commands
- `/settings` - Configure preferences
- `/mood` - Log mood (1-10 scale)
- `/stats` - View usage statistics
- `/motivateMe` - Get instant motivation right now!
- `/pause` - Temporarily stop messages
- `/resume` - Resume receiving messages

## Content Management

All motivational content is now stored in the SQLite database (`motivator.db`), making it easy to add, edit, and manage content without modifying code.

### Adding Custom Content

#### Method 1: Direct Database Access (Recommended)
```python
from src.database import Database

db = Database()
db.add_content(
    content="Your custom motivational message here",
    content_type="text",      # text, image, video, link
    language="en",             # en or de
    category="motivation",     # anxiety, depression, stress, motivation, self_care, general
    media_url=None             # Optional: URL for videos/images
)
```

#### Method 2: Using ContentManager
```python
from src.database import Database
from src.content import ContentManager

db = Database()
content_manager = ContentManager(db)

content_manager.add_content_to_db(
    content="Your motivational message",
    content_type="text",
    language="en",
    category="motivation",
    media_url=None  # Optional
)
```

#### Method 3: Admin Bot Commands
Administrators can manage content directly through bot commands:
- `/admin_content list` - View all content
- `/admin_content list en` - View English content only
- `/admin_content add` - Get help on adding content
- `/admin_content remove <id>` - Remove content by ID
- `/admin_content stats` - View content statistics

#### Method 4: Import from JSON
Use the migration script to bulk import content:
```bash
python scripts/migrate_content_to_db.py
```

### Content Categories

- **anxiety** - Support for anxiety management
- **depression** - Support for depression
- **stress** - Stress relief and management
- **motivation** - General motivational messages
- **self_care** - Self-care reminders and tips
- **general** - General mental health support

### Content Types

- **text** - Plain text messages
- **image** - Image with caption
- **video** - Video content (e.g., YouTube shorts)
- **link** - External resource links

### Database Access
SQLite database (`motivator.db`) contains:
- **motivational_content** - All motivational messages (NEW!)
- **users** - User settings and preferences
- **mood_entries** - Mood tracking data
- **sent_messages** - Message history
- **feedback** - User feedback and analytics
- **user_timing_preferences** - Smart scheduling settings

Query examples:
```sql
-- View all active content
SELECT * FROM motivational_content WHERE active = 1;

-- View content by language
SELECT * FROM motivational_content WHERE language = 'en' AND active = 1;

-- View content by category
SELECT * FROM motivational_content WHERE category = 'motivation' AND active = 1;

-- Get content statistics
SELECT language, category, COUNT(*)
FROM motivational_content
WHERE active = 1
GROUP BY language, category;

-- View user statistics
SELECT * FROM users;

-- Check mood trends
SELECT * FROM mood_entries WHERE user_id = 123 ORDER BY created_at DESC;

-- Analyze message effectiveness
SELECT feedback_type, COUNT(*) FROM feedback GROUP BY feedback_type;
```

## Architecture

### File Structure
```
motivator/
├── main.py           # Entry point
├── bot.py            # Main bot logic and handlers
├── database.py       # Database operations
├── content.py        # Content management and categories
├── scheduler.py      # Message scheduling system
├── requirements.txt  # Python dependencies
├── .env.example     # Environment template
└── README.md        # This file
```

### Key Components
- **Bot (`bot.py`)**: Telegram interface, command handlers, user interactions
- **Database (`database.py`)**: SQLite operations, user data, analytics
- **Content (`content.py`)**: Motivational content, categorization, personalization
- **Scheduler (`scheduler.py`)**: Random message timing, mood reminders

### Message Flow
1. Scheduler determines when to send messages based on user frequency settings
2. Content Manager selects appropriate content based on recent mood and category
3. Bot sends personalized message via Telegram API
4. User feedback is logged for content improvement
5. Analytics track effectiveness and user engagement

## Beta Testing & Groups

The bot supports group chats for beta testing:
- Add bot to group chats for collaborative testing
- Group members can test features together
- Feedback from groups helps identify bugs and improvements
- Use `/stats` in groups to see collective usage data

## Privacy & Security

- No personal data shared with third parties
- Local SQLite database (not cloud-based)
- Mood and message data stored locally on your system
- Optional data export for personal analysis
- User can delete their data anytime

## Troubleshooting

### Common Issues
1. **Bot not responding**: Check bot token in `.env`
2. **Database errors**: Ensure write permissions in bot directory
3. **Messages not sending**: Verify internet connection and Telegram API access
4. **Scheduler issues**: Check system time and timezone settings
5. **Module not found errors**: Ensure virtual environment is activated (`source venv/bin/activate`)
6. **Permission denied**: Make sure you have write permissions in the project directory
7. **Python version issues**: Ensure Python 3.8+ is being used in your virtual environment

### Debug Mode
```bash
# Run with verbose logging
python main.py --debug
```

### Database Reset
```bash
# Backup first
cp motivator.db motivator.db.backup

# Reset database (WARNING: Deletes all data)
rm motivator.db
python main.py  # Will recreate database
```

## Contributing

This project is designed for personal use and mental health support. When contributing:

1. Focus on mental health best practices
2. Ensure content is appropriate and supportive
3. Test thoroughly before deploying
4. Consider privacy and security implications
5. Maintain bilingual support (English/German)

## License

This project is for personal and educational use. Please use responsibly and in accordance with Telegram's Terms of Service.

## Support Resources

- **Crisis Text Line**: Text HOME to 741741
- **National Suicide Prevention Lifeline**: 988
- **European Mental Health**: https://www.eufami.org/
- **German Mental Health**: https://www.bundesgesundheitsministerium.de/

---

**Remember**: This bot is a supportive tool and should not replace professional mental health care. If you're experiencing a mental health crisis, please contact emergency services or a mental health professional immediately.