from __future__ import annotations

import logging
import sqlite3
from typing import Final

log = logging.getLogger(__name__)

DB_PATH: Final[str] = "bot_database.db"


class BotDatabase:
    """Database layer for bot operations, separating SQL statements from business logic."""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        return sqlite3.connect(self.db_path)

    def initialize_database(self) -> None:
        """Initialize the SQLite database and create the users table if it doesn't exist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        first_name TEXT,
                        username TEXT,
                        chat_id INTEGER,
                        image_credits INTEGER DEFAULT 0,
                        video_credits INTEGER DEFAULT 0,
                        language TEXT DEFAULT 'English',
                        image_aspect_ratio TEXT DEFAULT '9:16',
                        video_aspect_ratio TEXT DEFAULT '9:16',
                        current_plan TEXT DEFAULT 'None',
                        plan_expiry_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Check for existing columns and add missing ones
                cursor.execute("PRAGMA table_info(users)")
                existing_columns = {row[1] for row in cursor.fetchall()}

                if "language" not in existing_columns:
                    cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'English'")
                if "image_aspect_ratio" not in existing_columns:
                    cursor.execute("ALTER TABLE users ADD COLUMN image_aspect_ratio TEXT DEFAULT '9:16'")
                if "video_aspect_ratio" not in existing_columns:
                    cursor.execute("ALTER TABLE users ADD COLUMN video_aspect_ratio TEXT DEFAULT '9:16'")

                # Handle migration from old 'aspect_ratio' column to separate image/video columns
                if "aspect_ratio" in existing_columns:
                    cursor.execute(
                        "UPDATE users SET image_aspect_ratio = COALESCE(aspect_ratio, '9:16') WHERE image_aspect_ratio IS NULL OR image_aspect_ratio = ''"
                    )
                    cursor.execute(
                        "UPDATE users SET video_aspect_ratio = CASE WHEN video_aspect_ratio IS NULL OR video_aspect_ratio = '' THEN '9:16' ELSE video_aspect_ratio END"
                    )
                    cursor.execute("ALTER TABLE users DROP COLUMN aspect_ratio")

                conn.commit()
                log.info("Database initialized successfully")

        except sqlite3.Error as e:
            log.error(f"Failed to initialize database: {e}")
            raise

    def get_user_preferences(self, user_id: int) -> tuple[str, str, str] | None:
        """Get user's language, image aspect ratio, and video aspect ratio."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT language, image_aspect_ratio, video_aspect_ratio
                    FROM users
                    WHERE user_id = ?
                    """,
                    (user_id,),
                )
                return cursor.fetchone()
        except sqlite3.Error as e:
            log.error(f"Database error getting user preferences for {user_id}: {e}")
            return None

    def create_user(
        self,
        user_id: int,
        first_name: str | None,
        username: str | None,
        chat_id: int,
        language: str,
        image_ratio: str,
        video_ratio: str,
        initial_image_credits: int = 10,
        initial_video_credits: int = 5,
    ) -> None:
        """Create a new user record."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO users (
                        user_id,
                        first_name,
                        username,
                        chat_id,
                        image_credits,
                        video_credits,
                        language,
                        image_aspect_ratio,
                        video_aspect_ratio
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        first_name,
                        username,
                        chat_id,
                        initial_image_credits,
                        initial_video_credits,
                        language,
                        image_ratio,
                        video_ratio,
                    ),
                )
                conn.commit()
                log.info("Added new user %s to database with initial credits", user_id)
        except sqlite3.Error as e:
            log.error(f"Database error creating user {user_id}: {e}")
            raise

    def update_user_basic_info(self, user_id: int, first_name: str | None, username: str | None, chat_id: int) -> None:
        """Update user's basic information."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE users
                    SET first_name = ?, username = ?, chat_id = ?
                    WHERE user_id = ?
                    """,
                    (first_name, username, chat_id, user_id),
                )
                conn.commit()
                log.info("Updated user %s in database", user_id)
        except sqlite3.Error as e:
            log.error(f"Database error updating user {user_id}: {e}")
            raise

    def update_user_aspect_ratios(self, user_id: int, image_ratio: str, video_ratio: str) -> None:
        """Update user's aspect ratio preferences."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET image_aspect_ratio = ?, video_aspect_ratio = ? WHERE user_id = ?",
                    (image_ratio, video_ratio, user_id),
                )
                conn.commit()
        except sqlite3.Error as e:
            log.error(f"Database error updating aspect ratios for user {user_id}: {e}")
            raise

    def update_user_language(self, user_id: int, language: str) -> None:
        """Update user's language preference."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET language = ? WHERE user_id = ?",
                    (language, user_id),
                )
                conn.commit()
        except sqlite3.Error as e:
            log.error(f"Database error updating language for user {user_id}: {e}")
            raise

    def get_user_credits(self, user_id: int) -> tuple[int, int]:
        """Get user's image and video credits. Returns (image_credits, video_credits)."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT image_credits, video_credits FROM users WHERE user_id = ?",
                    (user_id,),
                )
                row = cursor.fetchone()
                if row:
                    return row[0] or 0, row[1] or 0
                return 0, 0
        except sqlite3.Error as e:
            log.error(f"Database error getting credits for user {user_id}: {e}")
            return 0, 0


# Global database instance
bot_db = BotDatabase()
