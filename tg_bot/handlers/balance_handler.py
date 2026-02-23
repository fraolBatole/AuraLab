from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from tg_bot.user_settings import get_user_credits, user_settings
from tg_bot.translations import get_translation

log = logging.getLogger(__name__)


async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's current credit balance for both images and videos."""
    user_id = update.effective_user.id if update.effective_user else 0
    language = user_settings.get_language(user_id)

    # Get user's credits from database
    image_credits, video_credits = get_user_credits(user_id)

    # Display balance message
    balance_message = get_translation("balance_display", language, image_credits=image_credits, video_credits=video_credits)
    await update.effective_message.reply_text(balance_message)
