import random
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)

class MessageScheduler:
    def __init__(self, database, content_manager):
        self.db = database
        self.content_manager = content_manager
        self.scheduler = AsyncIOScheduler()
        
    def start(self, bot_instance):
        """Start the message scheduler"""
        self.bot = bot_instance
        
        # Schedule random message sending throughout the day
        # This will run every hour and decide whether to send messages
        self.scheduler.add_job(
            func=self._check_and_send_messages,
            trigger=CronTrigger(minute=0),  # Every hour at minute 0
            id='hourly_message_check'
        )
        
        # For testing: also check every 10 minutes (remove in production)
        self.scheduler.add_job(
            func=self._check_and_send_messages,
            trigger=CronTrigger(minute='*/10'),  # Every 10 minutes
            id='frequent_message_check'
        )
        
        # Daily mood reminder (optional)
        self.scheduler.add_job(
            func=self._send_mood_reminders,
            trigger=CronTrigger(hour=20, minute=0),  # 8 PM daily
            id='daily_mood_reminder'
        )
        
        self.scheduler.start()
        logger.info("Message scheduler started")
    
    async def _check_and_send_messages(self):
        """Check if it's time to send messages to users"""
        try:
            active_users = self.db.get_active_users()
            
            for user_id in active_users:
                user_settings = self.db.get_user_settings(user_id)
                if not user_settings:
                    continue
                
                frequency = user_settings['message_frequency']
                
                # Calculate probability of sending a message this hour
                # If frequency is 2 messages per day, probability per hour = 2/24 = ~8.3%
                hourly_probability = frequency / 24.0
                
                # Add some randomness - make it more likely during "active" hours
                current_hour = datetime.now().hour
                if 8 <= current_hour <= 22:  # Daytime hours
                    hourly_probability *= 3.0  # Increased from 1.5 to 3.0
                else:  # Night hours
                    hourly_probability *= 0.5  # Increased from 0.3 to 0.5
                
                # Random decision
                if random.random() < hourly_probability:
                    await self._schedule_random_message(user_id)
                    
        except Exception as e:
            logger.error(f"Error in message scheduling: {e}")
    
    async def _schedule_random_message(self, user_id: int):
        """Schedule a message to be sent at a random time within the next hour"""
        try:
            # Random delay between 0 and 60 minutes
            delay_minutes = random.randint(0, 60)
            
            self.scheduler.add_job(
                func=self.bot.send_motivational_message,
                trigger='date',
                run_date=datetime.now() + timedelta(minutes=delay_minutes),
                args=[user_id],
                id=f'message_{user_id}_{datetime.now().timestamp()}'
            )
            
            logger.info(f"Scheduled message for user {user_id} in {delay_minutes} minutes")
            
        except Exception as e:
            logger.error(f"Error scheduling message for user {user_id}: {e}")
    
    async def _send_mood_reminders(self):
        """Send daily mood check reminders"""
        try:
            active_users = self.db.get_active_users()
            
            for user_id in active_users:
                user_settings = self.db.get_user_settings(user_id)
                if not user_settings:
                    continue
                
                language = user_settings['language']
                
                # Check if user has logged mood today
                recent_mood = self.db.get_recent_mood(user_id, 1)
                if recent_mood and recent_mood[0]['date'].startswith(datetime.now().strftime('%Y-%m-%d')):
                    continue  # Already logged mood today
                
                # Send reminder
                if language == 'de':
                    reminder_text = "🌙 *Tägliche Erinnerung*\n\nWie war dein Tag heute? Verwende /mood um deine Stimmung zu erfassen."
                else:
                    reminder_text = "🌙 *Daily Check-in*\n\nHow was your day today? Use /mood to log how you're feeling."
                
                try:
                    await self.bot.application.bot.send_message(
                        chat_id=user_id,
                        text=reminder_text,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Error sending mood reminder to user {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in mood reminders: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Message scheduler stopped")