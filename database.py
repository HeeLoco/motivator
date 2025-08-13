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
                    language TEXT DEFAULT 'en',
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
            
            # Goals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    goal_text TEXT,
                    category TEXT,
                    target_date DATE,
                    completed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            conn.commit()
            logging.info("Database initialized successfully")

    def add_user(self, user_id: int, username: str = None, first_name: str = None) -> bool:
        """Add or update user in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_active) 
                    VALUES (?, ?, ?, ?)
                """, (user_id, username, first_name, datetime.now()))
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
                    SELECT language, timezone, message_frequency, active 
                    FROM users WHERE user_id = ?
                """, (user_id,))
                result = cursor.fetchone()
                if result:
                    return {
                        'language': result[0],
                        'timezone': result[1], 
                        'message_frequency': result[2],
                        'active': result[3]
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

    def add_goal(self, user_id: int, goal_text: str, category: str = None, target_date: str = None) -> bool:
        """Add user goal"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_goals (user_id, goal_text, category, target_date)
                    VALUES (?, ?, ?, ?)
                """, (user_id, goal_text, category, target_date))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error adding goal: {e}")
            return False

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