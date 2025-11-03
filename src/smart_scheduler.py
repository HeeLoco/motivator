import random
import asyncio
import uuid
from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .logging_config import get_logger, log_with_context, set_correlation_id, clear_correlation_id
import logging

logger = get_logger(__name__)

class SmartMessageScheduler:
    def __init__(self, database, content_manager):
        self.db = database
        self.content_manager = content_manager
        self.scheduler = AsyncIOScheduler()
        
    def start(self, bot_instance):
        """Start the smart message scheduler"""
        self.bot = bot_instance
        
        # Remove the frequent 10-minute check - use smarter scheduling
        # Main scheduling check every hour
        self.scheduler.add_job(
            func=self._smart_scheduling_check,
            trigger=CronTrigger(minute=0),  # Every hour at minute 0
            id='smart_message_check'
        )
        
        # Daily planning - plan next day's messages at midnight
        self.scheduler.add_job(
            func=self._plan_daily_messages,
            trigger=CronTrigger(hour=0, minute=5),  # 12:05 AM daily
            id='daily_message_planning'
        )
        
        # Daily mood reminder (8 PM)
        self.scheduler.add_job(
            func=self._send_mood_reminders,
            trigger=CronTrigger(hour=20, minute=0),
            id='daily_mood_reminder'
        )
        
        self.scheduler.start()
        logger.info("Smart message scheduler started")
    
    async def _smart_scheduling_check(self):
        """Smart scheduling check - only schedule if needed"""
        try:
            current_hour = datetime.now().hour
            active_users = self.db.get_active_users()
            
            for user_id in active_users:
                await self._check_user_needs_message(user_id, current_hour)
                    
        except Exception as e:
            logger.error(f"Error in smart scheduling: {e}")
    
    async def _check_user_needs_message(self, user_id: int, current_hour: int):
        """Check if user needs a message and schedule accordingly"""
        try:
            # Get user settings and preferences
            user_settings = self.db.get_user_settings(user_id)
            timing_prefs = self.db.get_user_timing_preferences(user_id)
            
            if not user_settings or not timing_prefs:
                return
            
            # Check if within user's active hours
            if not self._is_user_active_hour(current_hour, timing_prefs):
                return
            
            # Get recent mood for mood boost calculation
            recent_mood = self.db.get_recent_mood(user_id, 1)
            mood_boost_factor = self._calculate_mood_boost(recent_mood, timing_prefs)
            
            # Calculate adjusted frequency for today
            base_frequency = user_settings['message_frequency']
            adjusted_frequency = base_frequency * mood_boost_factor
            
            # Check if user already has enough messages scheduled/sent today
            if await self._user_has_enough_messages_today(user_id, adjusted_frequency):
                return
            
            # Check minimum gap since last message
            if not await self._check_minimum_gap(user_id, timing_prefs['min_gap_hours']):
                return
            
            # Calculate probability for this hour based on peak times
            probability = self._calculate_hour_probability(current_hour, timing_prefs, adjusted_frequency)
            
            # Random decision
            if random.random() < probability:
                await self._schedule_smart_message(user_id, timing_prefs)
                
        except Exception as e:
            logger.error(f"Error checking user {user_id} needs: {e}")
    
    def _is_user_active_hour(self, hour: int, timing_prefs: Dict) -> bool:
        """Check if current hour is within user's active hours"""
        start_hour = timing_prefs['active_start_hour']
        end_hour = timing_prefs['active_end_hour']
        
        if start_hour <= end_hour:
            return start_hour <= hour <= end_hour
        else:  # Crosses midnight
            return hour >= start_hour or hour <= end_hour
    
    def _calculate_mood_boost(self, recent_mood: List, timing_prefs: Dict) -> float:
        """Calculate mood boost factor for message frequency"""
        if not timing_prefs['mood_boost_enabled'] or not recent_mood:
            return 1.0
        
        latest_mood = recent_mood[0]['score']
        
        # Mood boost settings as specified
        if latest_mood <= 2:  # Very low mood
            return 2.0  # +100% for 12 hours (simplified to daily)
        elif latest_mood <= 4:  # Low mood  
            return 1.5  # +50% for 24 hours
        else:
            return 1.0  # Normal frequency
    
    async def _user_has_enough_messages_today(self, user_id: int, target_frequency: float) -> bool:
        """Check if user already received enough messages today"""
        try:
            # Get today's sent messages count
            today = datetime.now().strftime('%Y-%m-%d')
            sent_today = self.db.get_message_stats_by_date(user_id, today)
            
            # Include scheduled messages for today
            scheduled_today = await self._count_scheduled_messages_today(user_id)
            
            total_today = sent_today + scheduled_today
            
            return total_today >= int(target_frequency)
            
        except Exception as e:
            logger.error(f"Error checking daily message count: {e}")
            return False
    
    async def _count_scheduled_messages_today(self, user_id: int) -> int:
        """Count messages already scheduled for today"""
        try:
            # This would require tracking scheduled jobs - simplified implementation
            # In a full implementation, you'd maintain a schedule database
            return 0
        except Exception as e:
            logger.error(f"Error counting scheduled messages: {e}")
            return 0
    
    async def _check_minimum_gap(self, user_id: int, min_gap_hours: int) -> bool:
        """Check if enough time passed since last message"""
        try:
            # Get last sent message time
            last_messages = self.db.get_message_stats_detailed(user_id, 1)
            if not last_messages:
                return True
            
            last_message_time = datetime.fromisoformat(last_messages[0]['sent_at'])
            time_since_last = datetime.now() - last_message_time
            
            return time_since_last.total_seconds() >= (min_gap_hours * 3600)
            
        except Exception as e:
            logger.error(f"Error checking minimum gap: {e}")
            return True  # Allow if unsure
    
    def _calculate_hour_probability(self, hour: int, timing_prefs: Dict, daily_frequency: float) -> float:
        """Calculate probability of sending message this hour based on peak times"""
        # Base probability: divide daily frequency across active hours
        active_hours = self._calculate_active_hours(timing_prefs)
        base_probability = daily_frequency / active_hours if active_hours > 0 else 0
        
        # Peak time multipliers (60% of messages during peak times)
        if self._is_peak_hour(hour, timing_prefs):
            return base_probability * 2.0  # Higher during peak times
        else:
            return base_probability * 0.5  # Lower during non-peak times
    
    def _calculate_active_hours(self, timing_prefs: Dict) -> int:
        """Calculate total active hours per day"""
        start = timing_prefs['active_start_hour']
        end = timing_prefs['active_end_hour']
        
        if start <= end:
            return end - start
        else:  # Crosses midnight
            return (24 - start) + end
    
    def _is_peak_hour(self, hour: int, timing_prefs: Dict) -> bool:
        """Check if hour is within any peak time window"""
        peak_windows = [
            (timing_prefs['peak_morning_start'], timing_prefs['peak_morning_end']),
            (timing_prefs['peak_afternoon_start'], timing_prefs['peak_afternoon_end']),
            (timing_prefs['peak_evening_start'], timing_prefs['peak_evening_end'])
        ]
        
        for start, end in peak_windows:
            if start <= hour < end:
                return True
        return False
    
    async def _schedule_smart_message(self, user_id: int, timing_prefs: Dict):
        """Schedule a message with smart timing within the next hour"""
        try:
            # Random delay within next hour, but avoid very short delays
            delay_minutes = random.randint(5, 60)
            
            scheduled_time = datetime.now() + timedelta(minutes=delay_minutes)
            
            self.scheduler.add_job(
                func=self._send_tracked_message,
                trigger='date',
                run_date=scheduled_time,
                args=[user_id, scheduled_time.isoformat()],
                id=f'smart_message_{user_id}_{scheduled_time.timestamp()}'
            )
            
            logger.info(f"Smart scheduled message for user {user_id} in {delay_minutes} minutes")
            
        except Exception as e:
            logger.error(f"Error smart scheduling message for user {user_id}: {e}")
    
    async def _send_tracked_message(self, user_id: int, scheduled_time: str):
        """Send message and track engagement"""
        # Generate correlation ID for this message send operation
        correlation_id = f"msg_{user_id}_{uuid.uuid4().hex[:8]}"
        set_correlation_id(correlation_id)

        try:
            actual_send_time = datetime.now().isoformat()

            log_with_context(
                logger, logging.INFO,
                "Sending scheduled message",
                user_id=user_id,
                scheduled_time=scheduled_time,
                actual_send_time=actual_send_time
            )

            # Send the motivational message
            await self.bot.send_motivational_message(user_id)

            # Log the engagement (basic tracking)
            self.db.log_message_engagement(
                user_id=user_id,
                scheduled_time=scheduled_time,
                actual_send_time=actual_send_time,
                message_type='motivational'
            )

            log_with_context(
                logger, logging.INFO,
                "Message sent successfully",
                user_id=user_id,
                message_type='motivational'
            )

        except Exception as e:
            log_with_context(
                logger, logging.ERROR,
                f"Error sending tracked message: {e}",
                user_id=user_id,
                error=str(e)
            )
        finally:
            clear_correlation_id()
    
    async def _plan_daily_messages(self):
        """Plan next day's messages for optimal distribution (future enhancement)"""
        # This would implement advanced daily planning
        # For now, we rely on hourly smart checks
        logger.info("Daily message planning - using smart hourly checks")
    
    async def _send_mood_reminders(self):
        """Send daily mood check reminders (unchanged from original)"""
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
        logger.info("Smart message scheduler stopped")