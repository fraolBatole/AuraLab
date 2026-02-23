from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from core.database import bot_db


class AspectRatio(str, Enum):
    RATIO_1_1 = "1:1"
    RATIO_9_16 = "9:16"
    RATIO_16_9 = "16:9"
    RATIO_4_3 = "4:3"
    RATIO_3_4 = "3:4"


class VideoAspectRatio(str, Enum):
    RATIO_16_9 = "16:9"
    RATIO_9_16 = "9:16"
    RATIO_1_1 = "1:1"


class Language(str, Enum):
    ENGLISH = "English"
    AMHARIC = "Amharic"


def detect_language_from_telegram(language_code: str) -> Language:
    """Map Telegram language codes to our supported languages."""
    # Map common language codes to our enum values
    language_map = {
        'en': Language.ENGLISH,
        'am': Language.AMHARIC,
        # Add more mappings as needed
        'en-us': Language.ENGLISH,
        'en-gb': Language.ENGLISH,
    }

    # Extract base language code (e.g., 'en' from 'en-US')
    base_code = language_code.lower().split('-')[0]

    return language_map.get(language_code.lower(), language_map.get(base_code, Language.ENGLISH))


@dataclass
class UserPreference:
    aspect_ratio: AspectRatio = AspectRatio.RATIO_9_16
    video_aspect_ratio: VideoAspectRatio = VideoAspectRatio.RATIO_9_16
    language: Language = Language.ENGLISH
    uploaded_image_path: Optional[str] = None
    video_mode_text_only: bool = False
    image_mode_text_only: bool = True  # Default to text-only for image generation


@dataclass
class UserSettings:
    _store: Dict[int, UserPreference] = field(default_factory=dict)
    _awaiting_prompt_users: set[int] = field(default_factory=set)
    _awaiting_video_prompt_users: set[int] = field(default_factory=set)
    _awaiting_image_upload_users: set[int] = field(default_factory=set)
    _awaiting_video_choice_users: set[int] = field(default_factory=set)
    _awaiting_image_choice_users: set[int] = field(default_factory=set)
    _awaiting_image_upload_for_image_gen_users: set[int] = field(default_factory=set)

    def sync_from_db(self, user_id: int) -> None:
        """Ensure in-memory preferences reflect the database record."""
        try:
            user_data = bot_db.get_user_preferences(user_id)
            if not user_data:
                return
            language_value, ratio_value, video_ratio_value = user_data
            pref = self._store.get(user_id)
            if pref is None:
                pref = UserPreference()
                self._store[user_id] = pref
            if ratio_value:
                pref.aspect_ratio = AspectRatio(ratio_value)
            if video_ratio_value:
                pref.video_aspect_ratio = VideoAspectRatio(video_ratio_value)
            if language_value:
                pref.language = Language(language_value)
        except Exception:
            # Fail silently to avoid crashing the bot; defaults will be used instead.
            pass

    def persist_ratio(self, user_id: int) -> None:
        pref = self._store.get(user_id)
        if not pref:
            return
        try:
            bot_db.update_user_aspect_ratios(
                user_id=user_id,
                image_ratio=pref.aspect_ratio.value,
                video_ratio=pref.video_aspect_ratio.value,
            )
        except Exception:
            pass

    def persist_language(self, user_id: int) -> None:
        pref = self._store.get(user_id)
        if not pref:
            return
        try:
            bot_db.update_user_language(
                user_id=user_id,
                language=pref.language.value,
            )
        except Exception:
            pass

    def get_ratio(self, user_id: int) -> AspectRatio:
        pref = self._store.get(user_id)
        if pref is None:
            self.sync_from_db(user_id)
            pref = self._store.get(user_id)
            if pref is None:
                pref = UserPreference()
                self._store[user_id] = pref
        return pref.aspect_ratio

    def get_video_ratio(self, user_id: int) -> VideoAspectRatio:
        pref = self._store.get(user_id)
        if pref is None:
            self.sync_from_db(user_id)
            pref = self._store.get(user_id)
            if pref is None:
                pref = UserPreference()
                self._store[user_id] = pref
        return pref.video_aspect_ratio

    def set_ratio(self, user_id: int, ratio: AspectRatio) -> None:
        pref = self._store.get(user_id)
        if pref is None:
            self._store[user_id] = UserPreference(aspect_ratio=ratio)
        else:
            pref.aspect_ratio = ratio

        self.persist_ratio(user_id)

    def set_video_ratio(self, user_id: int, ratio: VideoAspectRatio) -> None:
        pref = self._store.get(user_id)
        if pref is None:
            self._store[user_id] = UserPreference(video_aspect_ratio=ratio)
        else:
            pref.video_aspect_ratio = ratio

        self.persist_ratio(user_id)

    def has_ratio(self, user_id: int) -> bool:
        return user_id in self._store

    def is_new_user(self, user_id: int) -> bool:
        """Check if this is a new user who hasn't interacted with the bot before."""
        pref = self._store.get(user_id)
        if pref is None:
            self.sync_from_db(user_id)
            pref = self._store.get(user_id)
        return pref is None

    def get_language(self, user_id: int) -> Language:
        pref = self._store.get(user_id)
        if pref is None:
            self.sync_from_db(user_id)
            pref = self._store.get(user_id)
            if pref is None:
                pref = UserPreference()
                self._store[user_id] = pref
        return pref.language

    def set_language(self, user_id: int, language: Language) -> None:
        pref = self._store.get(user_id)
        if pref is None:
            self._store[user_id] = UserPreference(language=language)
        else:
            pref.language = language

        self.persist_language(user_id)

    def auto_detect_and_set_language(self, user_id: int, telegram_language_code: str) -> None:
        """Auto-detect user's language from Telegram and set it if not already set."""
        pref = self._store.get(user_id)
        if pref is None:
            # New user - detect language from Telegram
            detected_language = detect_language_from_telegram(telegram_language_code)
            self._store[user_id] = UserPreference(language=detected_language)
        # If user already exists, don't override their manual language choice

    # Prompt awaiting state for images
    def is_awaiting_prompt(self, user_id: int) -> bool:
        return user_id in self._awaiting_prompt_users

    def set_awaiting_prompt(self, user_id: int) -> None:
        self._awaiting_prompt_users.add(user_id)

    def clear_awaiting_prompt(self, user_id: int) -> None:
        self._awaiting_prompt_users.discard(user_id)

    # Video generation state
    def is_awaiting_video_prompt(self, user_id: int) -> bool:
        return user_id in self._awaiting_video_prompt_users

    def set_awaiting_video_prompt(self, user_id: int) -> None:
        self._awaiting_video_prompt_users.add(user_id)

    def clear_awaiting_video_prompt(self, user_id: int) -> None:
        self._awaiting_video_prompt_users.discard(user_id)

    # Image upload state for video generation
    def is_awaiting_image_upload(self, user_id: int) -> bool:
        return user_id in self._awaiting_image_upload_users

    def set_awaiting_image_upload(self, user_id: int) -> None:
        self._awaiting_image_upload_users.add(user_id)

    def clear_awaiting_image_upload(self, user_id: int) -> None:
        self._awaiting_image_upload_users.discard(user_id)

    # Uploaded image management
    def set_uploaded_image_path(self, user_id: int, image_path: str) -> None:
        pref = self._store.get(user_id)
        if pref is None:
            self._store[user_id] = UserPreference(uploaded_image_path=image_path)
        else:
            pref.uploaded_image_path = image_path

    def get_uploaded_image_path(self, user_id: int) -> Optional[str]:
        pref = self._store.get(user_id)
        return pref.uploaded_image_path if pref else None

    def clear_uploaded_image_path(self, user_id: int) -> None:
        pref = self._store.get(user_id)
        if pref:
            pref.uploaded_image_path = None

    # Video choice state
    def is_awaiting_video_choice(self, user_id: int) -> bool:
        return user_id in self._awaiting_video_choice_users

    def set_awaiting_video_choice(self, user_id: int) -> None:
        self._awaiting_video_choice_users.add(user_id)

    def clear_awaiting_video_choice(self, user_id: int) -> None:
        self._awaiting_video_choice_users.discard(user_id)

    # Video mode management
    def set_video_mode_text_only(self, user_id: int) -> None:
        pref = self._store.get(user_id)
        if pref is None:
            self._store[user_id] = UserPreference(video_mode_text_only=True)
        else:
            pref.video_mode_text_only = True

    def set_video_mode_with_image(self, user_id: int) -> None:
        pref = self._store.get(user_id)
        if pref is None:
            self._store[user_id] = UserPreference(video_mode_text_only=False)
        else:
            pref.video_mode_text_only = False

    def is_video_mode_text_only(self, user_id: int) -> bool:
        pref = self._store.get(user_id)
        return pref.video_mode_text_only if pref else False

    def clear_video_mode(self, user_id: int) -> None:
        pref = self._store.get(user_id)
        if pref:
            pref.video_mode_text_only = False

    # Image choice state (similar to video choice)
    def is_awaiting_image_choice(self, user_id: int) -> bool:
        return user_id in self._awaiting_image_choice_users

    def set_awaiting_image_choice(self, user_id: int) -> None:
        self._awaiting_image_choice_users.add(user_id)

    def clear_awaiting_image_choice(self, user_id: int) -> None:
        self._awaiting_image_choice_users.discard(user_id)

    # Image upload state for image-to-image generation (separate from video)
    def is_awaiting_image_upload_for_image_gen(self, user_id: int) -> bool:
        return user_id in self._awaiting_image_upload_for_image_gen_users

    def set_awaiting_image_upload_for_image_gen(self, user_id: int) -> None:
        self._awaiting_image_upload_for_image_gen_users.add(user_id)

    def clear_awaiting_image_upload_for_image_gen(self, user_id: int) -> None:
        self._awaiting_image_upload_for_image_gen_users.discard(user_id)

    # Image mode management
    def set_image_mode_text_only(self, user_id: int) -> None:
        pref = self._store.get(user_id)
        if pref is None:
            self._store[user_id] = UserPreference(image_mode_text_only=True)
        else:
            pref.image_mode_text_only = True

    def set_image_mode_with_image(self, user_id: int) -> None:
        pref = self._store.get(user_id)
        if pref is None:
            self._store[user_id] = UserPreference(image_mode_text_only=False)
        else:
            pref.image_mode_text_only = False

    def is_image_mode_text_only(self, user_id: int) -> bool:
        pref = self._store.get(user_id)
        return pref.image_mode_text_only if pref else True  # Default to text-only

    def clear_image_mode(self, user_id: int) -> None:
        pref = self._store.get(user_id)
        if pref:
            pref.image_mode_text_only = True  # Reset to default


# Credit management functions
def get_user_credits(user_id: int) -> tuple[int, int]:
    """Get user's image and video credits from database."""
    return bot_db.get_user_credits(user_id)


def has_image_credits(user_id: int) -> bool:
    """Check if user has image credits available."""
    image_credits, _ = get_user_credits(user_id)
    return image_credits > 0


def has_video_credits(user_id: int) -> bool:
    """Check if user has video credits available."""
    _, video_credits = get_user_credits(user_id)
    return video_credits > 0


def deduct_image_credit(user_id: int) -> bool:
    """Deduct 1 image credit from user. Returns True if successful."""
    try:
        with sqlite3.connect("bot_database.db") as conn:
            cursor = conn.cursor()
            # First check current credits
            cursor.execute(
                "SELECT image_credits FROM users WHERE user_id = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            if not result or result[0] <= 0:
                return False

            # Deduct credit
            cursor.execute(
                "UPDATE users SET image_credits = image_credits - 1 WHERE user_id = ?",
                (user_id,)
            )
            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"Database error deducting image credit for user {user_id}: {e}")
        return False


def deduct_video_credit(user_id: int) -> bool:
    """Deduct 1 video credit from user. Returns True if successful."""
    try:
        with sqlite3.connect("bot_database.db") as conn:
            cursor = conn.cursor()
            # First check current credits
            cursor.execute(
                "SELECT video_credits FROM users WHERE user_id = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            if not result or result[0] <= 0:
                return False

            # Deduct credit
            cursor.execute(
                "UPDATE users SET video_credits = video_credits - 1 WHERE user_id = ?",
                (user_id,)
            )
            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"Database error deducting video credit for user {user_id}: {e}")
        return False



# Single in-memory instance
user_settings = UserSettings()

