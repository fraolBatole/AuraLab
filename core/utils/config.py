import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    telegram_bot_token: str
    gemini_api_key: str


def load_config() -> AppConfig:
    load_dotenv()
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    if not gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    return AppConfig(telegram_bot_token=telegram_bot_token, gemini_api_key=gemini_api_key)

