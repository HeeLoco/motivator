import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

class Database:
    def __init__(self, db_path: str = "motivator.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    language TEXT DEFAULT 'de',
                    timezone TEXT DEFAULT 'UTC',
                    message_frequency INTEGER DEFAULT 2,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Messages table for tracking sent messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sent_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message_id INTEGER,
                    message_type TEXT,
                    content_id INTEGER,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message_id INTEGER,
                    feedback_type TEXT,
                    feedback_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Mood tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mood_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    mood_score INTEGER,
                    mood_note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # User timing preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_timing_preferences (
                    user_id INTEGER PRIMARY KEY,
                    active_start_hour INTEGER DEFAULT 8,
                    active_start_minute INTEGER DEFAULT 0,
                    active_end_hour INTEGER DEFAULT 22,
                    active_end_minute INTEGER DEFAULT 0,
                    min_gap_hours INTEGER DEFAULT 1,
                    distribution_style TEXT DEFAULT 'peak_focused',
                    mood_boost_enabled BOOLEAN DEFAULT 1,
                    auto_adjust_timing BOOLEAN DEFAULT 1,
                    timezone TEXT DEFAULT 'UTC',
                    peak_morning_start INTEGER DEFAULT 8,
                    peak_morning_end INTEGER DEFAULT 10,
                    peak_afternoon_start INTEGER DEFAULT 14,
                    peak_afternoon_end INTEGER DEFAULT 16,
                    peak_evening_start INTEGER DEFAULT 18,
                    peak_evening_end INTEGER DEFAULT 20,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Message scheduling log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_schedule_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    scheduled_time TIMESTAMP,
                    actual_send_time TIMESTAMP,
                    message_type TEXT,
                    engagement_score REAL,
                    response_time_minutes INTEGER,
                    user_mood_before INTEGER,
                    user_mood_after INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            # Motivational content table for database-driven content management
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS motivational_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    language TEXT NOT NULL,
                    category TEXT NOT NULL,
                    media_url TEXT,
                    tags TEXT,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for efficient content queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_content_language_category
                ON motivational_content(language, category, active)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_content_active
                ON motivational_content(active)
            """)

            conn.commit()
            logging.info("Database initialized successfully")

    def add_user(self, user_id: int, username: str = None, first_name: str = None) -> bool:
        """Add or update user in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if user already exists
                cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
                user_exists = cursor.fetchone() is not None
                
                if user_exists:
                    # User exists - only update username, first_name, and last_active
                    cursor.execute("""
                        UPDATE users 
                        SET username = ?, first_name = ?, last_active = ?
                        WHERE user_id = ?
                    """, (username, first_name, datetime.now(), user_id))
                else:
                    # New user - insert with all default values
                    cursor.execute("""
                        INSERT INTO users 
                        (user_id, username, first_name, language, timezone, message_frequency, active, created_at, last_active) 
                        VALUES (?, ?, ?, 'de', 'UTC', 2, 1, ?, ?)
                    """, (user_id, username, first_name, datetime.now(), datetime.now()))
                
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error adding user: {e}")
            return False

    def get_user_settings(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user settings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT language, timezone, message_frequency, active, duplicate_avoidance_count 
                    FROM users WHERE user_id = ?
                """, (user_id,))
                result = cursor.fetchone()
                if result:
                    return {
                        'language': result[0],
                        'timezone': result[1], 
                        'message_frequency': result[2],
                        'active': result[3],
                        'duplicate_avoidance_count': result[4] or 5
                    }
                return None
        except Exception as e:
            logging.error(f"Error getting user settings: {e}")
            return None

    def update_user_setting(self, user_id: int, setting: str, value: Any) -> bool:
        """Update a specific user setting"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    UPDATE users SET {setting} = ?, last_active = ? 
                    WHERE user_id = ?
                """, (value, datetime.now(), user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error updating user setting: {e}")
            return False

    def log_sent_message(self, user_id: int, message_id: int, message_type: str, content_id: int = None) -> bool:
        """Log sent message for tracking"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sent_messages (user_id, message_id, message_type, content_id)
                    VALUES (?, ?, ?, ?)
                """, (user_id, message_id, message_type, content_id))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error logging sent message: {e}")
            return False

    def add_feedback(self, user_id: int, message_id: int, feedback_type: str, feedback_value: str) -> bool:
        """Add user feedback"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO feedback (user_id, message_id, feedback_type, feedback_value)
                    VALUES (?, ?, ?, ?)
                """, (user_id, message_id, feedback_type, feedback_value))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error adding feedback: {e}")
            return False

    def add_mood_entry(self, user_id: int, mood_score: int, mood_note: str = None) -> bool:
        """Add mood entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO mood_entries (user_id, mood_score, mood_note)
                    VALUES (?, ?, ?)
                """, (user_id, mood_score, mood_note))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error adding mood entry: {e}")
            return False

    def get_recent_mood(self, user_id: int, days: int = 7) -> List[Dict]:
        """Get recent mood entries for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT mood_score, mood_note, created_at 
                    FROM mood_entries 
                    WHERE user_id = ? AND created_at >= datetime('now', '-{} days')
                    ORDER BY created_at DESC
                """.format(days), (user_id,))
                results = cursor.fetchall()
                return [{'score': r[0], 'note': r[1], 'date': r[2]} for r in results]
        except Exception as e:
            logging.error(f"Error getting recent mood: {e}")
            return []

    def get_recent_sent_content_ids(self, user_id: int, limit: int = 5) -> List[int]:
        """Get recently sent content IDs to avoid duplicates"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT content_id 
                    FROM sent_messages 
                    WHERE user_id = ? AND content_id IS NOT NULL
                    ORDER BY sent_at DESC 
                    LIMIT ?
                """, (user_id, limit))
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting recent sent content IDs: {e}")
            return []

    def get_active_users(self) -> List[int]:
        """Get list of active user IDs"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users WHERE active = 1")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting active users: {e}")
            return []

    def get_message_stats(self, user_id: int = None) -> Dict[str, int]:
        """Get message statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if user_id:
                    cursor.execute("""
                        SELECT message_type, COUNT(*) 
                        FROM sent_messages 
                        WHERE user_id = ?
                        GROUP BY message_type
                    """, (user_id,))
                else:
                    cursor.execute("""
                        SELECT message_type, COUNT(*) 
                        FROM sent_messages 
                        GROUP BY message_type
                    """)
                return dict(cursor.fetchall())
        except Exception as e:
            logging.error(f"Error getting message stats: {e}")
            return {}

    def reset_user_data(self, user_id: int) -> bool:
        """Reset all user data to defaults and clear history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Reset user settings to defaults
                cursor.execute("""
                    UPDATE users 
                    SET language = 'de', 
                        message_frequency = 2, 
                        active = 1,
                        last_active = ?
                    WHERE user_id = ?
                """, (datetime.now(), user_id))
                
                # Delete all user's mood entries
                cursor.execute("DELETE FROM mood_entries WHERE user_id = ?", (user_id,))

                # Delete all user's feedback
                cursor.execute("DELETE FROM feedback WHERE user_id = ?", (user_id,))
                
                # Delete all user's sent message history
                cursor.execute("DELETE FROM sent_messages WHERE user_id = ?", (user_id,))
                
                conn.commit()
                logging.info(f"Reset all data for user {user_id}")
                return True
                
        except Exception as e:
            logging.error(f"Error resetting user data: {e}")
            return False

    def get_all_users(self) -> List[int]:
        """Get list of all user IDs (active and inactive)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting all users: {e}")
            return []

    def get_total_mood_entries(self) -> int:
        """Get total number of mood entries across all users"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM mood_entries")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logging.error(f"Error getting total mood entries: {e}")
            return 0

    def get_recently_active_users(self, days: int = 7) -> List[int]:
        """Get list of users who were active in the last N days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id FROM users 
                    WHERE last_active >= datetime('now', '-{} days')
                """.format(days))
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting recently active users: {e}")
            return []

    def get_all_users_detailed(self) -> List[Dict[str, Any]]:
        """Get detailed information for all users"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, username, first_name, language, 
                           message_frequency, active, last_active, created_at
                    FROM users 
                    ORDER BY last_active DESC
                """)
                results = cursor.fetchall()
                
                users = []
                for row in results:
                    users.append({
                        'user_id': row[0],
                        'username': row[1],
                        'first_name': row[2],
                        'language': row[3],
                        'message_frequency': row[4],
                        'active': row[5],
                        'last_active': row[6],
                        'created_at': row[7]
                    })
                
                return users
                
        except Exception as e:
            logging.error(f"Error getting detailed user list: {e}")
            return []

    def get_user_detailed_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, username, first_name, language, 
                           message_frequency, active, last_active, created_at
                    FROM users 
                    WHERE user_id = ?
                """, (user_id,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        'user_id': result[0],
                        'username': result[1],
                        'first_name': result[2],
                        'language': result[3],
                        'message_frequency': result[4],
                        'active': result[5],
                        'last_active': result[6],
                        'created_at': result[7]
                    }
                
                return None
                
        except Exception as e:
            logging.error(f"Error getting detailed user info: {e}")
            return None

    def get_user_timing_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's timing preferences"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT active_start_hour, active_start_minute, active_end_hour, active_end_minute,
                           min_gap_hours, distribution_style, mood_boost_enabled, auto_adjust_timing,
                           timezone, peak_morning_start, peak_morning_end, peak_afternoon_start,
                           peak_afternoon_end, peak_evening_start, peak_evening_end
                    FROM user_timing_preferences 
                    WHERE user_id = ?
                """, (user_id,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        'active_start_hour': result[0],
                        'active_start_minute': result[1],
                        'active_end_hour': result[2],
                        'active_end_minute': result[3],
                        'min_gap_hours': result[4],
                        'distribution_style': result[5],
                        'mood_boost_enabled': result[6],
                        'auto_adjust_timing': result[7],
                        'timezone': result[8],
                        'peak_morning_start': result[9],
                        'peak_morning_end': result[10],
                        'peak_afternoon_start': result[11],
                        'peak_afternoon_end': result[12],
                        'peak_evening_start': result[13],
                        'peak_evening_end': result[14]
                    }
                else:
                    # Create default preferences for user
                    return self._create_default_timing_preferences(user_id)
                
        except Exception as e:
            logging.error(f"Error getting timing preferences: {e}")
            return None

    def _create_default_timing_preferences(self, user_id: int) -> Dict[str, Any]:
        """Create default timing preferences for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO user_timing_preferences (user_id)
                    VALUES (?)
                """, (user_id,))
                conn.commit()
                
            # Return default values
            return {
                'active_start_hour': 8,
                'active_start_minute': 0,
                'active_end_hour': 22,
                'active_end_minute': 0,
                'min_gap_hours': 1,
                'distribution_style': 'peak_focused',
                'mood_boost_enabled': True,
                'auto_adjust_timing': True,
                'timezone': 'UTC',
                'peak_morning_start': 8,
                'peak_morning_end': 10,
                'peak_afternoon_start': 14,
                'peak_afternoon_end': 16,
                'peak_evening_start': 18,
                'peak_evening_end': 20
            }
            
        except Exception as e:
            logging.error(f"Error creating default timing preferences: {e}")
            return None

    def update_timing_preference(self, user_id: int, setting: str, value: Any) -> bool:
        """Update a specific timing preference"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Ensure user has timing preferences record
                cursor.execute("""
                    INSERT OR IGNORE INTO user_timing_preferences (user_id)
                    VALUES (?)
                """, (user_id,))
                
                # Update the specific setting
                cursor.execute(f"""
                    UPDATE user_timing_preferences 
                    SET {setting} = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (value, user_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logging.error(f"Error updating timing preference: {e}")
            return False

    def log_message_engagement(self, user_id: int, scheduled_time: str, actual_send_time: str, 
                              message_type: str, engagement_score: float = None, 
                              response_time_minutes: int = None) -> bool:
        """Log message engagement for learning user patterns"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO message_schedule_log 
                    (user_id, scheduled_time, actual_send_time, message_type, 
                     engagement_score, response_time_minutes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, scheduled_time, actual_send_time, message_type, 
                      engagement_score, response_time_minutes))
                conn.commit()
                return True
                
        except Exception as e:
            logging.error(f"Error logging message engagement: {e}")
            return False

    def get_user_engagement_patterns(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get user's engagement patterns for the last N days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT scheduled_time, actual_send_time, engagement_score, 
                           response_time_minutes, created_at
                    FROM message_schedule_log 
                    WHERE user_id = ? AND created_at >= datetime('now', '-{} days')
                    ORDER BY created_at DESC
                """.format(days), (user_id,))
                
                results = cursor.fetchall()
                return [{
                    'scheduled_time': r[0],
                    'actual_send_time': r[1], 
                    'engagement_score': r[2],
                    'response_time_minutes': r[3],
                    'created_at': r[4]
                } for r in results]
                
        except Exception as e:
            logging.error(f"Error getting engagement patterns: {e}")
            return []

    def get_message_stats_by_date(self, user_id: int, date: str) -> int:
        """Get count of messages sent to user on specific date"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM sent_messages 
                    WHERE user_id = ? AND DATE(sent_at) = ?
                """, (user_id, date))
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except Exception as e:
            logging.error(f"Error getting message stats by date: {e}")
            return 0

    def get_message_stats_detailed(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get detailed message statistics for user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT message_type, content_preview, sent_at, feedback
                    FROM sent_messages 
                    WHERE user_id = ? 
                    ORDER BY sent_at DESC 
                    LIMIT ?
                """, (user_id, limit))
                
                results = cursor.fetchall()
                return [{
                    'message_type': r[0],
                    'content_preview': r[1],
                    'sent_at': r[2],
                    'feedback': r[3]
                } for r in results]
                
        except Exception as e:
            logging.error(f"Error getting detailed message stats: {e}")
            return []

    # ==================== Content Management Methods ====================

    def add_content(self, content: str, content_type: str, language: str,
                   category: str, media_url: str = None, tags: str = None) -> Optional[int]:
        """Add new motivational content to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO motivational_content
                    (content, content_type, language, category, media_url, tags, active)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                """, (content, content_type, language, category, media_url, tags))
                conn.commit()
                logging.info(f"Added content: {content[:50]}... (ID: {cursor.lastrowid})")
                return cursor.lastrowid
        except Exception as e:
            logging.error(f"Error adding content: {e}")
            return None

    def get_all_content(self, language: str = None, category: str = None,
                       active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all motivational content, optionally filtered"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM motivational_content WHERE 1=1"
                params = []

                if active_only:
                    query += " AND active = 1"
                if language:
                    query += " AND language = ?"
                    params.append(language)
                if category:
                    query += " AND category = ?"
                    params.append(category)

                query += " ORDER BY created_at DESC"

                cursor.execute(query, params)
                results = cursor.fetchall()

                return [{
                    'id': r[0],
                    'content': r[1],
                    'content_type': r[2],
                    'language': r[3],
                    'category': r[4],
                    'media_url': r[5],
                    'tags': r[6],
                    'active': r[7],
                    'created_at': r[8],
                    'updated_at': r[9]
                } for r in results]

        except Exception as e:
            logging.error(f"Error getting content: {e}")
            return []

    def get_content_by_criteria(self, language: str, category: str = None) -> List[Dict[str, Any]]:
        """Get content matching specific criteria (used by ContentManager)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if category:
                    cursor.execute("""
                        SELECT id, content, content_type, language, category, media_url, tags
                        FROM motivational_content
                        WHERE language = ? AND category = ? AND active = 1
                        ORDER BY RANDOM()
                    """, (language, category))
                else:
                    cursor.execute("""
                        SELECT id, content, content_type, language, category, media_url, tags
                        FROM motivational_content
                        WHERE language = ? AND active = 1
                        ORDER BY RANDOM()
                    """, (language,))

                results = cursor.fetchall()

                return [{
                    'id': r[0],
                    'content': r[1],
                    'content_type': r[2],
                    'language': r[3],
                    'category': r[4],
                    'media_url': r[5],
                    'tags': r[6]
                } for r in results]

        except Exception as e:
            logging.error(f"Error getting content by criteria: {e}")
            return []

    def update_content(self, content_id: int, **kwargs) -> bool:
        """Update existing content"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                allowed_fields = ['content', 'content_type', 'language', 'category',
                                'media_url', 'tags', 'active']
                updates = []
                values = []

                for key, value in kwargs.items():
                    if key in allowed_fields:
                        updates.append(f"{key} = ?")
                        values.append(value)

                if not updates:
                    return False

                # Add updated_at timestamp
                updates.append("updated_at = CURRENT_TIMESTAMP")
                values.append(content_id)

                query = f"UPDATE motivational_content SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()

                logging.info(f"Updated content ID {content_id}")
                return cursor.rowcount > 0

        except Exception as e:
            logging.error(f"Error updating content: {e}")
            return False

    def delete_content(self, content_id: int) -> bool:
        """Delete content (soft delete by setting active=0)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE motivational_content
                    SET active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (content_id,))
                conn.commit()

                logging.info(f"Deactivated content ID {content_id}")
                return cursor.rowcount > 0

        except Exception as e:
            logging.error(f"Error deleting content: {e}")
            return False

    def get_content_stats(self) -> Dict[str, Any]:
        """Get statistics about content in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total count
                cursor.execute("SELECT COUNT(*) FROM motivational_content WHERE active = 1")
                total = cursor.fetchone()[0]

                # By language
                cursor.execute("""
                    SELECT language, COUNT(*)
                    FROM motivational_content
                    WHERE active = 1
                    GROUP BY language
                """)
                by_language = {row[0]: row[1] for row in cursor.fetchall()}

                # By category
                cursor.execute("""
                    SELECT category, COUNT(*)
                    FROM motivational_content
                    WHERE active = 1
                    GROUP BY category
                """)
                by_category = {row[0]: row[1] for row in cursor.fetchall()}

                # By type
                cursor.execute("""
                    SELECT content_type, COUNT(*)
                    FROM motivational_content
                    WHERE active = 1
                    GROUP BY content_type
                """)
                by_type = {row[0]: row[1] for row in cursor.fetchall()}

                return {
                    'total': total,
                    'by_language': by_language,
                    'by_category': by_category,
                    'by_type': by_type
                }

        except Exception as e:
            logging.error(f"Error getting content stats: {e}")
            return {}