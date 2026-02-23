from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from admin.cli import AdminCLI
from admin.db import AdminDatabase, UserRecord


@pytest.fixture()
def temp_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "bot_database.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                username TEXT,
                chat_id INTEGER,
                image_credits INTEGER DEFAULT 0,
                video_credits INTEGER DEFAULT 0,
                language TEXT,
                image_aspect_ratio TEXT,
                video_aspect_ratio TEXT,
                current_plan TEXT,
                plan_expiry_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            INSERT INTO users (user_id, first_name, username, chat_id, image_credits, video_credits, language, image_aspect_ratio, video_aspect_ratio, current_plan, plan_expiry_date, created_at)
            VALUES (1, 'Alice', 'alice', 1001, 5, 0, 'English', '16:9', '9:16', 'None', NULL, '2024-01-01T00:00:00')
            """
        )
        conn.execute(
            """
            INSERT INTO users (user_id, first_name, username, chat_id, image_credits, video_credits, language, image_aspect_ratio, video_aspect_ratio, current_plan, plan_expiry_date, created_at)
            VALUES (2, 'Bob', NULL, 1002, 2, 1, 'English', '1:1', '16:9', 'Pro', '2024-12-31', '2024-02-01T00:00:00')
            """
        )
        conn.commit()
    return db_path


def test_iter_users(temp_db: Path) -> None:
    db = AdminDatabase(temp_db)
    users = list(db.iter_users())
    assert len(users) == 2
    assert users[0].user_id == 2  # Ordered by created_at DESC
    assert users[1].user_id == 1


def test_reset_credits(temp_db: Path) -> None:
    db = AdminDatabase(temp_db)
    count = db.reset_credits([1, 2], image=10, video=3)
    assert count == 2

    users = list(db.iter_users())
    assert users[0].image_credits == 10
    assert users[0].video_credits == 3


def test_delete_users(temp_db: Path) -> None:
    db = AdminDatabase(temp_db)
    count = db.delete_users([1])
    assert count == 1
    assert len(list(db.iter_users())) == 1


def test_admin_cli_list(capsys, temp_db: Path) -> None:
    cli = AdminCLI(temp_db)
    cli.list_users()
    captured = capsys.readouterr()
    assert "user_id=2" in captured.out
    assert "user_id=1" in captured.out


def test_admin_cli_reset(capsys, temp_db: Path) -> None:
    cli = AdminCLI(temp_db)
    cli.reset([1], image=7, video=None)
    captured = capsys.readouterr()
    assert "Updated credits for 1 user" in captured.out

    db = AdminDatabase(temp_db)
    users = list(db.iter_users())
    assert users[-1].image_credits == 7


def test_admin_cli_delete(capsys, temp_db: Path) -> None:
    cli = AdminCLI(temp_db)
    cli.delete([2])
    captured = capsys.readouterr()
    assert "Deleted 1 user" in captured.out

    db = AdminDatabase(temp_db)
    users = list(db.iter_users())
    assert len(users) == 1
    assert users[0].user_id == 1
