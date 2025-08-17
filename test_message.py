#!/usr/bin/env python3
"""
Test script to manually send a motivational message
"""

import os
import asyncio
from dotenv import load_dotenv
from bot import MotivatorBot

async def test_send_message():
    """Test sending a message to a user"""
    # Load environment variables
    load_dotenv()
    
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        print("BOT_TOKEN not found!")
        return
    
    # Create bot instance
    bot = MotivatorBot(bot_token)
    
    # Get active users
    active_users = bot.db.get_active_users()
    print(f"Active users: {active_users}")
    
    if active_users:
        user_id = active_users[0]  # Test with first user
        print(f"Sending test message to user {user_id}")
        
        # Initialize the application
        await bot.application.initialize()
        await bot.application.start()
        
        try:
            # Send motivational message
            await bot.send_motivational_message(user_id)
            print("Message sent successfully!")
        except Exception as e:
            print(f"Error sending message: {e}")
        finally:
            await bot.application.stop()
    else:
        print("No active users found")

if __name__ == '__main__':
    asyncio.run(test_send_message())