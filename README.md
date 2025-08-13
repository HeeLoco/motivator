# MotivatOR Bot 🤖💙

A Telegram bot designed to support mental health and motivation through personalized messages, mood tracking, and goal setting. Perfect for individuals dealing with psychological challenges and their support networks.

## Features

### 🌟 Core Features
- **Personalized Motivational Messages**: Random supportive messages throughout the day
- **Bilingual Support**: English and German content
- **Mood Tracking**: Daily mood logging with personalized responses
- **Goal Setting**: Personal goal management and motivation
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
- Raspberry Pi (recommended) or any Linux/macOS/Windows system

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
- `/goals` - Manage personal goals
- `/stats` - View usage statistics
- `/motivateMe` - Get instant motivation right now!
- `/pause` - Temporarily stop messages
- `/resume` - Resume receiving messages

## Content Management

### Adding Custom Content
Content can be managed by editing `content.py` or directly through the database:

```python
# Example: Adding new motivational content
from content import ContentManager, MotivationalContent, ContentType, MoodCategory

content_manager = ContentManager()
new_content = MotivationalContent(
    id=0,  # Will be auto-assigned
    content="Your custom motivational message",
    content_type=ContentType.TEXT,
    language='en',
    category=MoodCategory.MOTIVATION
)
content_manager.add_custom_content(new_content)
```

### Database Access
SQLite database (`motivator.db`) contains:
- User settings and preferences
- Sent message history
- Mood tracking data
- Feedback and analytics
- Personal goals

Query examples:
```sql
-- View user statistics
SELECT * FROM users;

-- Check mood trends
SELECT * FROM mood_entries WHERE user_id = 123 ORDER BY created_at DESC;

-- Analyze message effectiveness
SELECT feedback_type, COUNT(*) FROM feedback GROUP BY feedback_type;
```

## Deployment on Raspberry Pi

### 1. System Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
sudo apt install python3-pip python3-venv -y

# Navigate to project directory
cd /home/pi/motivator

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
cp .env.example .env
nano .env  # Add your bot token
```

### 2. Auto-start Service
Create `/etc/systemd/system/motivator-bot.service`:

```ini
[Unit]
Description=MotivatOR Telegram Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/motivator
Environment=PATH=/home/pi/motivator/venv/bin
ExecStart=/home/pi/motivator/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable motivator-bot
sudo systemctl start motivator-bot
sudo systemctl status motivator-bot
```

### 3. Monitoring
```bash
# View logs
sudo journalctl -u motivator-bot -f

# Check bot status
sudo systemctl status motivator-bot
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
- Mood and message data stored locally on your Raspberry Pi
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