"""Administrative utilities for managing AuraLabs data."""

from __future__ import annotations

__all__ = ["DEFAULT_DB_PATH"]

from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "bot_database.db"

