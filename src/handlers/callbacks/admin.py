"""
Admin callback handlers for Motivator Bot.

Handles admin-related callback queries:
- Broadcast confirmation/cancellation
- User reset confirmation/cancellation
"""

import logging
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)


class AdminCallbackHandler:
    """Handles admin-related callback queries"""

    def __init__(self, bot_instance):
        """
        Initialize admin callback handler.

        Args:
            bot_instance: Reference to the main MotivatorBot instance
        """
        self.bot = bot_instance
        self.db = bot_instance.db
        self.admin_user_id = bot_instance.admin_user_id

    async def handle_confirm_broadcast(self, query, context):
        """Execute broadcast to all users"""
        user_id = query.from_user.id

        # Double-check admin permissions
        if self.admin_user_id is None or user_id != self.admin_user_id:
            await query.edit_message_text("❌ Admin access required.")
            return

        # Get the stored broadcast message
        broadcast_message = context.user_data.get('broadcast_message')
        if not broadcast_message:
            await query.edit_message_text("❌ Broadcast message not found. Please try again.")
            return

        # Start broadcasting
        await query.edit_message_text("📢 Broadcasting message... Please wait.")

        # Get all users
        all_users = self.db.get_all_users()
        sent_count = 0
        failed_count = 0

        for target_user_id in all_users:
            try:
                await self.bot.application.bot.send_message(
                    chat_id=target_user_id,
                    text=f"📢 *Admin Message*\n\n{broadcast_message}",
                    parse_mode=ParseMode.MARKDOWN
                )
                sent_count += 1
            except Exception as e:
                logger.warning(f"Failed to send broadcast to user {target_user_id}: {e}")
                failed_count += 1

        # Report results
        result_text = f"""
✅ *Broadcast Complete*

📊 Results:
• Sent successfully: {sent_count}
• Failed to send: {failed_count}
• Total users: {len(all_users)}

Message: "{broadcast_message}"
"""

        await query.edit_message_text(result_text, parse_mode=ParseMode.MARKDOWN)

        # Clear the stored message
        context.user_data.pop('broadcast_message', None)

    async def handle_cancel_broadcast(self, query, context):
        """Cancel broadcast operation"""
        context.user_data.pop('broadcast_message', None)
        await query.edit_message_text("❌ Broadcast cancelled.")

    async def handle_admin_reset_confirm(self, query, context):
        """Execute admin reset for specific user"""
        user_id = query.from_user.id

        # Double-check admin permissions
        if self.admin_user_id is None or user_id != self.admin_user_id:
            await query.edit_message_text("❌ Admin access required.")
            return

        # Extract target user ID
        target_user_id = int(query.data.split("_")[-1])

        # Get user details for confirmation message
        user_details = self.db.get_user_detailed_info(target_user_id)
        if not user_details:
            await query.edit_message_text(f"❌ User {target_user_id} not found.")
            return

        # Start reset process
        await query.edit_message_text("🔄 Resetting user data... Please wait.")

        # Perform the reset
        success = self.db.reset_user_data(target_user_id)

        user_name = user_details['first_name'] or 'Unknown'

        if success:
            result_text = f"""✅ *User Data Reset Complete*

**User:** {user_name} (ID: `{target_user_id}`)

**Actions performed:**
• Settings reset to defaults (German, 2 msg/day, active)
• All mood entries deleted
• All goals deleted
• All feedback deleted
• Message history cleared

The user can now start fresh with default settings."""
        else:
            result_text = f"❌ *Reset Failed*\n\nFailed to reset data for user {user_name} (ID: `{target_user_id}`).\n\nCheck logs for details."

        await query.edit_message_text(result_text, parse_mode=ParseMode.MARKDOWN)

    async def handle_admin_reset_cancel(self, query, context):
        """Cancel admin user reset operation"""
        await query.edit_message_text("❌ User data reset cancelled.")
