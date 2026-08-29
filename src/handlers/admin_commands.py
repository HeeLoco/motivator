"""
Admin command handlers for Motivator Bot.

Handles admin-only commands:
- /admin_stats - System statistics
- /admin_broadcast - Broadcast messages to all users
- /admin_users - User management and detailed info
- /admin_content - Content management (list, add, remove, stats)
- /admin_reset - Reset user data

Plus helper method for sending scheduled messages.
"""

import functools
from collections import Counter
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .base import BaseHandler
from .helpers import get_display_name, get_mood_with_age
from ..content import ContentType
from src import ai_motivator

from src.logging_config import get_logger

logger = get_logger(__name__)


def admin_only(func):
    """Restrict a command handler to the configured admin user"""
    @functools.wraps(func)
    async def wrapper(self, update, context, *args, **kwargs):
        if self.admin_user_id is None or update.effective_user.id != self.admin_user_id:
            await self._reply(update, "❌ This command is only available to administrators.")
            return
        return await func(self, update, context, *args, **kwargs)
    return wrapper


class AdminCommandHandler(BaseHandler):
    """Handles admin-only command handlers"""

    def __init__(self, db, content_manager, scheduler, admin_user_id, application):
        """
        Initialize admin command handler.

        Args:
            db: Database instance
            content_manager: ContentManager instance
            scheduler: SmartMessageScheduler instance
            admin_user_id: Telegram user ID of admin
            application: Telegram application instance
        """
        super().__init__(db, content_manager, scheduler)
        self.admin_user_id = admin_user_id
        self.application = application

    async def _reply(self, update: Update, text: str, **kwargs):
        """Reply via the message if present, else via the chat (callback context)"""
        if update.message:
            await update.message.reply_text(text, **kwargs)
        elif update.effective_chat:
            await update.effective_chat.send_message(text, **kwargs)

    @admin_only
    async def admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show admin statistics - only for admin users"""
        try:
            # Get all users
            all_users = self.db.get_active_users()  # This gets active users
            # Let's get total users (active + inactive)
            total_users = len(self.db.get_all_users())
            active_users = len(all_users)
            inactive_users = total_users - active_users

            # Get global message statistics
            global_message_stats = self.db.get_message_stats()
            total_messages = sum(global_message_stats.values())

            # Get total mood entries
            total_mood_entries = self.db.get_total_mood_entries()

            # Get recent activity (users active in last 7 days)
            recent_active = self.db.get_recently_active_users(7)

            # AI token usage of the last 30 days, grouped by use case
            ai_usage = self.db.get_ai_usage_stats(30)
            if ai_usage:
                total_in = sum(u['input_tokens'] for u in ai_usage)
                total_out = sum(u['output_tokens'] for u in ai_usage)
                total_requests = sum(u['requests'] for u in ai_usage)
                usage_lines = "\n".join(
                    f"• {u['use_case']}: {u['requests']} req, "
                    f"{u['input_tokens']:,} in / {u['output_tokens']:,} out"
                    for u in ai_usage
                )
                ai_usage_text = (
                    f"\n🤖 *AI usage (30 days):*\n"
                    f"• Total: {total_requests} requests, "
                    f"{total_in:,} in / {total_out:,} out tokens\n"
                    f"{usage_lines}\n"
                )
            else:
                ai_usage_text = "\n🤖 *AI usage (30 days):* no requests recorded\n"

            stats_text = f"""
📊 *Admin Statistics Dashboard*

👥 *Users:*
• Total registered: {total_users}
• Active: {active_users}
• Inactive/Paused: {inactive_users}
• Active in last 7 days: {len(recent_active)}

📧 *Messages sent:*
• Total: {total_messages}
• Text: {global_message_stats.get('text', 0)}
• Media: {global_message_stats.get('image', 0) + global_message_stats.get('video', 0)}
• Links: {global_message_stats.get('link', 0)}

📈 *Engagement:*
• Total mood entries: {total_mood_entries}
• Avg messages per user: {total_messages / total_users if total_users > 0 else 0:.1f}
{ai_usage_text}"""

            await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            logger.error(f"Error in admin_stats: {e}")
            await self._reply(update, "❌ Error retrieving statistics. Check logs for details.")

    @admin_only
    async def admin_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send broadcast message to all users - only for admin users"""
        # Check if message text was provided
        if not context.args:
            await update.message.reply_text(
                "📢 *Admin Broadcast*\n\n"
                "Usage: `/admin_broadcast <message>`\n\n"
                "Example: `/admin_broadcast Hello everyone! The bot has been updated with new features.`\n\n"
                "This will send the message to ALL registered users.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Get the broadcast message
        broadcast_message = " ".join(context.args)

        # Show confirmation
        confirmation_text = f"""
📢 *Broadcast Confirmation*

Message to send:
"{broadcast_message}"

This will be sent to ALL users. Continue?
"""

        keyboard = [
            [InlineKeyboardButton("✅ Send to All Users", callback_data="confirm_broadcast")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Store the broadcast message temporarily (we'll need to handle this in callback)
        context.user_data['broadcast_message'] = broadcast_message

        await self._reply(
                confirmation_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
        )

    def build_user_detail(self, target_user_id: int):
        """
        Build the detail view text for one user, or None if unknown.

        Shared by the /admin_users command and the interactive user list.
        """
        user_details = self.db.get_user_detailed_info(target_user_id)
        if not user_details:
            return None

        # Get additional statistics for this user
        mood_entries = self.db.get_recent_mood(target_user_id, 30)  # Last 30 days
        message_stats = self.db.get_message_stats(target_user_id)
        total_messages = sum(message_stats.values())

        # Calculate average mood
        avg_mood = (sum(m['score'] for m in mood_entries) / len(mood_entries)) if mood_entries else None

        # AI token usage of the last 30 days
        ai_usage = self.db.get_user_ai_usage(target_user_id, 30)
        if ai_usage:
            total_in = sum(u['input_tokens'] for u in ai_usage)
            total_out = sum(u['output_tokens'] for u in ai_usage)
            usage_lines = "\n".join(
                f"• {u['use_case']}: {u['requests']} req, "
                f"{u['input_tokens']:,} in / {u['output_tokens']:,} out"
                for u in ai_usage
            )
            ai_text = (f"\n🤖 **AI usage (30d):** {total_in:,} in / {total_out:,} out tokens\n"
                       f"{usage_lines}\n")
        else:
            ai_text = "\n🤖 **AI usage (30d):** none\n"

        return f"""
👤 *Detailed User Information*

🆔 **User ID:** `{user_details['user_id']}`
📛 **Name:** {user_details['first_name'] or 'No name'}
👤 **Username:** @{user_details['username'] or 'No username'}
🌍 **Language:** {user_details['language']}
📊 **Messages per day:** {user_details['message_frequency']}
🔄 **Status:** {'✅ Active' if user_details['active'] else '⏸️ Paused'}

📅 **Activity:**
• Created: {user_details['created_at'][:10] if user_details['created_at'] else 'Unknown'}
• Last active: {user_details['last_active'][:10] if user_details['last_active'] else 'Never'}

📈 **Statistics:**
• Messages received: {total_messages}
• Mood entries (30d): {len(mood_entries)}
• Avg mood (30d): {f'{avg_mood:.1f}/10' if avg_mood else 'No data'}

📧 **Message breakdown:**
• Text: {message_stats.get('text', 0)}
• Media: {message_stats.get('image', 0) + message_stats.get('video', 0)}
• Links: {message_stats.get('link', 0)}
{ai_text}"""

    def build_users_list(self):
        """
        Build the interactive user list: header text plus one button per
        user that opens the detail view. Returns (text, reply_markup).
        """
        users_info = self.db.get_all_users_detailed()
        if not users_info:
            return "📝 No users found in database.", None

        text = (f"👥 *All Registered Users* ({len(users_info)})\n\n"
                "Tap a user for details (incl. AI token usage):")

        keyboard = []
        for user in users_info[:50]:  # Telegram keyboard size limit
            active = "✅" if user['active'] else "⏸️"
            name = user['first_name'] or user['username'] or str(user['user_id'])
            username = f" (@{user['username']})" if user['username'] else ""
            keyboard.append([InlineKeyboardButton(
                f"{active} {name}{username}",
                callback_data=f"admin_user_{user['user_id']}"
            )])
        if len(users_info) > 50:
            text += f"\n\n(showing first 50 of {len(users_info)})"

        keyboard.append([InlineKeyboardButton("📄 Text overview", callback_data="admin_users_overview")])

        return text, InlineKeyboardMarkup(keyboard)

    def build_users_overview(self):
        """
        Build the classic text overview of all users (compact, at a glance).
        Returns (text, reply_markup) with a switch back to the interactive list.
        """
        users_info = self.db.get_all_users_detailed()
        if not users_info:
            return "📝 No users found in database.", None

        users_text = f"👥 *All Registered Users* ({len(users_info)})\n"

        ai_usage_by_user = self.db.get_ai_usage_by_user(30)

        for i, user in enumerate(users_info, 1):
            user_id_str = user['user_id']
            username = user['username'] or "No username"
            first_name = user['first_name'] or "No name"
            language = user['language']
            frequency = user['message_frequency']
            active = "✅" if user['active'] else "⏸️"
            last_active = user['last_active'][:10] if user['last_active'] else "Never"

            usage = ai_usage_by_user.get(user['user_id'])
            if usage:
                ai_line = (f"🤖 {usage['requests']} req | "
                           f"{usage['input_tokens']:,} in / {usage['output_tokens']:,} out (30d)")
            else:
                ai_line = "🤖 no AI usage (30d)"

            users_text += f"""
*{i}.* `{user_id_str}`
📛 {first_name} (@{username})
🌍 {language} | 📊 {frequency}/day | {active}
🕒 Last: {last_active}
{ai_line}
"""

            # Telegram has message length limits, break into chunks if needed
            if len(users_text) > 3500:  # Leave room for more text
                users_text += f"\n... and {len(users_info) - i} more users"
                break

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔘 Interactive list", callback_data="admin_users_list")
        ]])

        return users_text, keyboard

    @admin_only
    async def admin_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show interactive user list or detailed info for specific user"""
        try:
            if context.args and context.args[0].lower() == 'list':
                # Classic text overview via /admin_users list
                text, reply_markup = self.build_users_overview()
                await self._reply(update, text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            elif context.args:
                # Direct detail view via /admin_users <user_id>
                try:
                    target_user_id = int(context.args[0])
                except ValueError:
                    await self._reply(update, "❌ Invalid user ID. Please provide a numeric user ID.")
                    return

                user_text = self.build_user_detail(target_user_id)
                if user_text is None:
                    await self._reply(update, f"❌ User `{target_user_id}` not found in database.", parse_mode=ParseMode.MARKDOWN)
                    return

                await self._reply(update, user_text, parse_mode=ParseMode.MARKDOWN)
            else:
                # Interactive list with one button per user
                text, reply_markup = self.build_users_list()
                await self._reply(update, text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

        except Exception as e:
            logger.error(f"Error in admin_users: {e}")
            await self._reply(update, "❌ Error retrieving user information. Check logs for details.")

    @admin_only
    async def admin_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manage motivational content - only for admin users"""
        try:
            # Check if specific action was provided
            if context.args and len(context.args) >= 1:
                action = context.args[0].lower()

                if action == "list":
                    # List all content
                    await self._admin_content_list(update, context)

                elif action == "add":
                    # Add new content
                    await self._admin_content_add_help(update, context)

                elif action == "remove":
                    # Remove content by ID
                    if len(context.args) >= 2:
                        try:
                            content_id = int(context.args[1])
                            await self._admin_content_remove(update, content_id)
                        except ValueError:
                            await update.message.reply_text("❌ Invalid content ID. Please provide a numeric ID.")
                    else:
                        await update.message.reply_text("❌ Please provide content ID to remove.\nUsage: `/admin_content remove <id>`", parse_mode=ParseMode.MARKDOWN)

                elif action == "stats":
                    # Show content statistics
                    await self._admin_content_stats(update)

                else:
                    await self._admin_content_help(update)
            else:
                # Show help/menu
                await self._admin_content_help(update)

        except Exception as e:
            logger.error(f"Error in admin_content: {e}")
            await self._reply(update, "❌ Error managing content. Check logs for details.")

    async def _admin_content_help(self, update: Update):
        """Show admin content management help"""
        help_text = """
📝 *Admin Content Management*

**Available commands:**
• `/admin_content list` - Show all content
• `/admin_content add` - Get help for adding content
• `/admin_content remove <id>` - Remove content by ID
• `/admin_content stats` - Show content statistics

**Examples:**
• `/admin_content list de` - List German content
• `/admin_content remove 15` - Remove content ID 15
"""

        await self._reply(update, help_text, parse_mode=ParseMode.MARKDOWN)

    async def _admin_content_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all motivational content"""
        try:
            # Check if language filter was provided
            language_filter = context.args[1] if len(context.args) >= 2 else None

            # Debug logging
            logger.info(f"Admin content list - args: {context.args}, language_filter: {language_filter}")

            if language_filter and language_filter not in ['en', 'de']:
                await update.message.reply_text("❌ Invalid language. Use 'en' or 'de'.")
                return

            # Get all content
            all_content = self.content_manager.get_all_content(language_filter)

            logger.info(f"Found {len(all_content)} content items for language: {language_filter}")

            if not all_content:
                msg = f"📝 No content found" + (f" for language '{language_filter}'" if language_filter else "") + "."
                await update.message.reply_text(msg)
                return

            # Format content list (using plain text to avoid Markdown issues)
            content_text = f"📝 Motivational Content"
            if language_filter:
                content_text += f" ({language_filter.upper()})"
            content_text += f"\n\nFound {len(all_content)} items:\n\n"

            for i, content in enumerate(all_content, 1):
                # Truncate content for display
                content_preview = content.content[:80] + "..." if len(content.content) > 80 else content.content

                content_text += f"{i}. ID: {content.id} | {content.language.upper()} | {content.category.value}\n"
                content_text += f"📱 {content.content_type.value.upper()}\n"
                content_text += f"💬 \"{content_preview}\"\n"

                if content.media_url:
                    content_text += f"🔗 {content.media_url}\n"
                content_text += "\n"

                # Telegram message length limit
                if len(content_text) > 3500:
                    content_text += f"... and {len(all_content) - i} more items\n"
                    break

            content_text += f"\n💡 Use /admin_content remove <id> to delete content"

            await self._reply(update, content_text)

        except Exception as e:
            logger.error(f"Error in _admin_content_list: {e}")
            await self._reply(update, f"❌ Error listing content: {str(e)}")

    async def _admin_content_add_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help for adding content"""
        help_text = """
➕ *Adding New Content*

Content is now stored in the database. You have three ways to add content:

**Method 1: Direct Database Access**
```python
from src.database import Database
from src.content import ContentManager

db = Database()
db.add_content(
    content="Your motivational message here",
    content_type="text",
    language="en",
    category="motivation"
)
```

**Method 2: Using ContentManager**
```python
content_manager.add_content_to_db(
    content="Your message",
    content_type="text",
    language="en",
    category="motivation",
    media_url=None  # Optional
)
```

**Method 3: Import from JSON**
Use the import script:
```bash
python scripts/migrate_content_to_db.py
```

**Content Types:**
• `text` - Text messages
• `image` - Image with caption
• `video` - Video content (YouTube shorts)
• `link` - External links

**Languages:**
• `en` - English
• `de` - German (Deutsch)

**Categories:**
• `anxiety` - Anxiety support
• `depression` - Depression support
• `stress` - Stress management
• `motivation` - General motivation
• `self_care` - Self-care reminders
• `general` - General mental health

All content is immediately available after adding!
"""

        await self._reply(update, help_text, parse_mode=ParseMode.MARKDOWN)

    async def _admin_content_remove(self, update: Update, content_id: int):
        """Remove content by ID"""
        # Remove the content
        success = self.content_manager.remove_content(content_id)

        if success:
            await update.message.reply_text(f"✅ Content ID `{content_id}` has been removed successfully.", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(f"❌ Content ID `{content_id}` not found or could not be removed.", parse_mode=ParseMode.MARKDOWN)

    async def _admin_content_stats(self, update: Update):
        """Show content statistics"""
        all_content = self.content_manager.get_all_content()

        # Count by language
        en_count = len([c for c in all_content if c.language == 'en'])
        de_count = len([c for c in all_content if c.language == 'de'])

        # Count by category
        category_counts = Counter(c.category.value for c in all_content)

        # Count by type
        type_counts = Counter(c.content_type.value for c in all_content)

        # Build category list safely
        category_lines = []
        for category, count in category_counts.items():
            category_lines.append(f"• {category.replace('_', ' ').title()}: {count}")

        # Build type list safely
        type_lines = []
        for content_type, count in type_counts.items():
            type_lines.append(f"• {content_type.upper()}: {count}")

        # Build complete stats text
        stats_text = f"""📊 *Content Statistics*

**Total content:** {len(all_content)}

**By language:**
• English: {en_count}
• German: {de_count}

**By category:**
{chr(10).join(category_lines)}

**By type:**
{chr(10).join(type_lines)}"""

        await self._reply(update, stats_text, parse_mode=ParseMode.MARKDOWN)

    @admin_only
    async def admin_reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reset a specific user's data - only for admin users"""
        # Check if user ID was provided
        if not context.args:
            await update.message.reply_text(
                "🔄 *Admin Reset User Data*\n\n"
                "Usage: `/admin_reset <user_id>`\n\n"
                "Example: `/admin_reset 1153831100`\n\n"
                "This will reset ALL data for the specified user:\n"
                "• Settings reset to defaults\n"
                "• All mood entries deleted\n"
                "• All feedback deleted\n"
                "• Message history deleted\n"
                "• AI conversation memory deleted\n\n"
                "⚠️ *Warning: This action cannot be undone!*",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Validate user ID
        try:
            target_user_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
            return

        # Check if user exists
        user_details = self.db.get_user_detailed_info(target_user_id)
        if not user_details:
            await update.message.reply_text(f"❌ User `{target_user_id}` not found in database.", parse_mode=ParseMode.MARKDOWN)
            return

        # Show confirmation dialog
        user_name = user_details['first_name'] or 'Unknown'
        username = user_details['username'] or 'No username'

        confirmation_text = f"""⚠️ *Reset User Data Confirmation*

**Target User:**
🆔 ID: `{target_user_id}`
📛 Name: {user_name} (@{username})

**This will DELETE ALL data for this user:**
• Reset settings to defaults (German, 2 msg/day, active)
• Delete all mood entries
• Delete all feedback
• Delete all message history
• Delete AI conversation memory

**⚠️ This action cannot be undone!**

Are you sure you want to proceed?"""

        keyboard = [
            [InlineKeyboardButton("⚠️ Yes, Reset All Data", callback_data=f"admin_reset_confirm_{target_user_id}")],
            [InlineKeyboardButton("❌ Cancel", callback_data="admin_reset_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self._reply(
            update,
            confirmation_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def send_motivational_message(self, user_id: int):
        """
        Send a motivational message to a user.

        This method is called by the scheduler and sends mood-based content.

        Args:
            user_id: Telegram user ID
        """
        user_settings = self.db.get_user_settings(user_id)
        if not user_settings or not user_settings['active']:
            return

        language = user_settings['language']

        # Get recent mood (with age) to personalize content
        mood_score, mood_age_hours = get_mood_with_age(self.db, user_id)

        # Try AI-generated motivation first, fall back to static content
        ai_text = await ai_motivator.generate_motivation(
            language, mood_score, get_display_name(user_settings),
            self.db.get_user_facts(user_id), user_id=user_id,
            recent_messages=self.db.get_recent_ai_texts(user_id),
            mood_age_hours=mood_age_hours
        )
        if ai_text:
            try:
                message = await self.application.bot.send_message(
                    chat_id=user_id,
                    text=ai_text
                )
                self.db.log_sent_message(user_id, message.message_id, 'ai_text',
                                         content_text=ai_text)
                return
            except Exception as e:
                logger.error(f"Error sending AI motivation to user {user_id}: {e}")

        # Get recently sent content IDs to avoid duplicates
        duplicate_avoidance_count = user_settings.get('duplicate_avoidance_count', 5)
        recent_content_ids = self.db.get_recent_sent_content_ids(user_id, duplicate_avoidance_count)

        # Get appropriate content while avoiding recent duplicates
        content = self.content_manager.get_content_by_mood(
            mood_score if mood_score is not None else 5, language, recent_content_ids)

        if not content:
            return

        try:
            if content.content_type == ContentType.TEXT:
                message = await self.application.bot.send_message(
                    chat_id=user_id,
                    text=content.content,
                    parse_mode=ParseMode.MARKDOWN
                )
            elif content.content_type == ContentType.VIDEO and content.media_url:
                message = await self.application.bot.send_message(
                    chat_id=user_id,
                    text=f"{content.content}\n\n🎥 {content.media_url}",
                    parse_mode=ParseMode.MARKDOWN
                )
            elif content.content_type == ContentType.LINK and content.media_url:
                message = await self.application.bot.send_message(
                    chat_id=user_id,
                    text=f"{content.content}\n\n🔗 {content.media_url}",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                message = await self.application.bot.send_message(
                    chat_id=user_id,
                    text=content.content
                )

            # Log the sent message
            self.db.log_sent_message(user_id, message.message_id, content.content_type.value, content.id)

        except Exception as e:
            logger.error(f"Error sending motivational message to user {user_id}: {e}")
