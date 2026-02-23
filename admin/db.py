from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


@dataclass
class UserRecord:
    user_id: int
    first_name: str | None
    username: str | None
    chat_id: int | None
    image_credits: int
    video_credits: int
    current_plan: str | None
    plan_expiry_date: str | None
    created_at: str


class AdminDatabase:
    """Simple wrapper around the bot SQLite database for admin operations."""

    def __init__(self, db_path: Path | str) -> None:
        self._path = Path(db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        return conn

    def iter_users(self) -> Iterator[UserRecord]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT user_id, first_name, username, chat_id,
                       image_credits, video_credits,
                       current_plan, plan_expiry_date, created_at
                FROM users
                ORDER BY created_at DESC
                """
            )
            for row in cursor.fetchall():
                yield UserRecord(
                    user_id=row["user_id"],
                    first_name=row["first_name"],
                    username=row["username"],
                    chat_id=row["chat_id"],
                    image_credits=row["image_credits"] or 0,
                    video_credits=row["video_credits"] or 0,
                    current_plan=row["current_plan"],
                    plan_expiry_date=row["plan_expiry_date"],
                    created_at=row["created_at"],
                )

    def reset_credits(self, user_ids: Iterable[int], *, image: int | None = None, video: int | None = None) -> int:
        """Reset credits for given users. Returns number of affected rows."""

        if image is None and video is None:
            return 0

        updates = []
        params: list[int | str] = []
        if image is not None:
            updates.append("image_credits = ?")
            params.append(image)
        if video is not None:
            updates.append("video_credits = ?")
            params.append(video)

        id_list = list(user_ids)
        if not id_list:
            return 0

        placeholders = ",".join("?" for _ in id_list)
        params.extend(id_list)

        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id IN ({placeholders})"

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

    def delete_users(self, user_ids: Iterable[int]) -> int:
        ids = list(user_ids)
        if not ids:
            return 0
        placeholders = ",".join("?" for _ in ids)
        query = f"DELETE FROM users WHERE user_id IN ({placeholders})"
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, ids)
            conn.commit()
            return cursor.rowcount

