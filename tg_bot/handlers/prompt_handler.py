from __future__ import annotations

import asyncio
import logging
import tempfile
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from tg_bot.user_settings import user_settings, has_image_credits, deduct_image_credit, get_user_credits
from tg_bot.translations import get_translation, get_prompt_by_id
from tg_bot.keyboards import (
    prompt_presets_keyboard,
    followup_navigation_keyboard,
    CB_PRESET_PAGE,
    CB_PRESET_SELECT,
    CB_PRESET_RETRY,
)
from services.gemini_image import GeminiImageService


log = logging.getLogger(__name__)


async def show_presets(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0, edit: bool = False) -> None:
    user_id = update.effective_user.id if update.effective_user else 0
    language = user_settings.get_language(user_id)

    message = get_translation("choose_preset_message", language)
    keyboard = prompt_presets_keyboard(user_id, page=page)

    if edit and update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=keyboard)
    else:
        await context.bot.send_message(chat_id=user_id, text=message, reply_markup=keyboard)


async def handle_preset_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    try:
        parts = (query.data or "").split(":")
        page_str = parts[-1]
        page = int(page_str)
    except Exception:
        page = 0
    await show_presets(update, context, page=page, edit=True)


async def handle_preset_select_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, api_key: str | None = None) -> None:
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id if update.effective_user else 0
    language = user_settings.get_language(user_id)

    # Parse prompt id
    try:
        parts = (query.data or "").split(":")
        prompt_id = parts[-1]
        log.debug("Callback data: %s, Parsed prompt_id: %s", query.data, prompt_id)
    except Exception as e:
        log.exception("Failed to parse prompt_id from callback data: %s", query.data)
        prompt_id = ""

    prompt_text = get_prompt_by_id(prompt_id, language)
    log.debug("Prompt ID: %s, Language: %s, Prompt text: %r", prompt_id, language, prompt_text)
    if not prompt_text:
        log.warning("No prompt found for ID: %s, language: %s", prompt_id, language)
        await query.edit_message_text(get_translation("image_generation_failed_message", language))
        return

    # Check if user has image credits
    if not has_image_credits(user_id):
        await query.edit_message_text(get_translation("insufficient_image_credits", language))
        return

    # Indicate progress
    await query.edit_message_text(get_translation("in_progress_message", language))

    ratio = user_settings.get_ratio(user_id).value

    # Prefer application-scoped service
    service: GeminiImageService | None = context.application.bot_data.get("gemini_service") if context.application else None
    if service is None:
        if not api_key:
            await context.bot.send_message(
                chat_id=user_id,
                text=get_translation("image_generation_not_configured_message", language),
            )
            return
        service = GeminiImageService(api_key=api_key)

    tmp_dir = tempfile.mkdtemp(prefix="imagegen_preset_")
    out_path = Path(tmp_dir) / "image.jpg"

    try:
        path = await asyncio.to_thread(service.generate_image_file, prompt_text, str(out_path), ratio)
        if path:
            with open(path, "rb") as f:
                await context.bot.send_photo(chat_id=user_id, photo=f)

            # Deduct credit and send confirmation
            if deduct_image_credit(user_id):
                image_credits, _ = get_user_credits(user_id)
                await context.bot.send_message(
                    chat_id=user_id,
                    text=get_translation("image_credit_deducted", language, remaining=image_credits)
                )

            # Follow-up navigation
            followup_text = get_translation("image_generated_followup", language)
            await context.bot.send_message(
                chat_id=user_id,
                text=followup_text,
                reply_markup=followup_navigation_keyboard(user_id),
            )
        else:
            # Friendly retry with quick actions
            retry_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=get_translation("retry_button", language), callback_data=f"{CB_PRESET_RETRY}:{prompt_id}")],
                [InlineKeyboardButton(text=get_translation("browse_presets_button", language), callback_data=f"{CB_PRESET_PAGE}:0")],
            ])
            await context.bot.send_message(
                chat_id=user_id,
                text=get_translation("image_generation_failed_message", language),
                reply_markup=retry_kb,
            )
    except Exception as exc:
        log.exception("Preset generation failed: %s", exc)
        retry_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=get_translation("retry_button", language), callback_data=f"{CB_PRESET_RETRY}:{prompt_id}")],
            [InlineKeyboardButton(text=get_translation("browse_presets_button", language), callback_data=f"{CB_PRESET_PAGE}:0")],
        ])
        await context.bot.send_message(
            chat_id=user_id,
            text=get_translation("image_generation_failed_message", language),
            reply_markup=retry_kb,
        )
    finally:
        try:
            if out_path.exists():
                out_path.unlink()
            if out_path.parent.exists() and "tmp" in str(out_path.parent):
                try:
                    out_path.parent.rmdir()
                except Exception:
                    pass
        except Exception:
            log.debug("Failed to cleanup preset temp files", exc_info=True)


async def handle_preset_retry_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, api_key: str | None = None) -> None:
    # Re-route to the select handler with same prompt id
    query = update.callback_query
    await query.answer()
    # Convert retry:ID to select:ID and reuse logic
    try:
        parts = (query.data or "").split(":")
        prompt_id = parts[-1]
    except Exception:
        prompt_id = ""
    query.data = f"{CB_PRESET_SELECT}:{prompt_id}"
    await handle_preset_select_callback(update, context, api_key=api_key)


