from __future__ import annotations

import logging
import tempfile
from pathlib import Path
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.gemini_image import GeminiImageService
from tg_bot.user_settings import user_settings, has_image_credits, deduct_image_credit, get_user_credits
from tg_bot.translations import get_translation


log = logging.getLogger(__name__)

IMAGE_CHOICE_TEXT = "📝 Text Only"
IMAGE_CHOICE_IMAGE = "🖼️ With Image"


def get_image_choice_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Creates keyboard for image generation choice."""
    language = user_settings.get_language(user_id)

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=get_translation(IMAGE_CHOICE_TEXT, language),
            callback_data="image_choice:text"
        )],
        [InlineKeyboardButton(
            text=get_translation(IMAGE_CHOICE_IMAGE, language),
            callback_data="image_choice:image"
        )]
    ])


async def begin_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the image generation process by offering choice between text-only or image-based."""
    user_id = update.effective_user.id if update.effective_user else 0
    language = user_settings.get_language(user_id)

    # Offer choice between text-only and image-based generation
    user_settings.set_awaiting_image_choice(user_id)
    await update.effective_message.reply_text(
        get_translation("image_generation_choice", language),
        reply_markup=get_image_choice_keyboard(user_id)
    )


async def handle_image_choice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle image generation choice selection."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id if update.effective_user else 0
    language = user_settings.get_language(user_id)

    if not user_settings.is_awaiting_image_choice(user_id):
        return

    choice = query.data.split(":")[1] if ":" in query.data else ""

    if choice == "text":
        # Text-only image generation
        user_settings.clear_awaiting_image_choice(user_id)
        user_settings.set_awaiting_prompt(user_id)
        user_settings.set_image_mode_text_only(user_id)
        await query.edit_message_text(
            get_translation("image_prompt_message", language)
        )

    elif choice == "image":
        # Image-based image generation
        user_settings.clear_awaiting_image_choice(user_id)
        user_settings.set_awaiting_image_upload_for_image_gen(user_id)
        user_settings.set_image_mode_with_image(user_id)
        await query.edit_message_text(
            get_translation("image_to_image_upload_prompt", language)
        )


async def handle_image_upload_for_image_gen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle uploaded images for image-to-image generation."""
    user_id = update.effective_user.id if update.effective_user else 0
    language = user_settings.get_language(user_id)

    if not user_settings.is_awaiting_image_upload_for_image_gen(user_id):
        return

    # Get the photo from the message
    if not update.effective_message.photo:
        await update.effective_message.reply_text(
            get_translation("upload_photo_prompt", language)
        )
        return

    await update.effective_message.reply_text(get_translation("processing_image_message", language))

    try:
        # Get the largest photo size
        photo = update.effective_message.photo[-1]

        # Download the photo
        tmp_dir = tempfile.mkdtemp(prefix="imagegen_upload_")
        image_path = Path(tmp_dir) / f"user_{user_id}_upload_img.jpg"

        file_obj = await context.bot.get_file(photo.file_id)
        await file_obj.download_to_drive(str(image_path))

        # Store the image path
        user_settings.set_uploaded_image_path(user_id, str(image_path))
        user_settings.clear_awaiting_image_upload_for_image_gen(user_id)
        user_settings.set_awaiting_prompt(user_id)

        await update.effective_message.reply_text(
            get_translation("image_upload_success_prompt_for_image_gen", language)
        )

    except Exception as exc:
        log.exception("Failed to process uploaded image: %s", exc)
        await update.effective_message.reply_text(
            get_translation("image_processing_error_message", language)
        )


async def handle_prompt_text(update: Update, context: ContextTypes.DEFAULT_TYPE, api_key: str | None = None) -> None:
    """Handle the image prompt text for both text-only and image-based image generation."""
    user_id = update.effective_user.id if update.effective_user else 0
    language = user_settings.get_language(user_id)
    
    if not user_settings.is_awaiting_prompt(user_id):
        return
    
    text = (update.effective_message.text or "").strip()
    if not text:
        await update.effective_message.reply_text(get_translation("empty_description_message", language))
        return

    # Check if user has image credits
    if not has_image_credits(user_id):
        await update.effective_message.reply_text(get_translation("insufficient_image_credits", language))
        user_settings.clear_awaiting_prompt(user_id)
        return

    await update.effective_message.reply_text(get_translation("in_progress_message", language))
    ratio = user_settings.get_ratio(user_id).value

    # Check if this is text-only or image-based generation
    is_text_only = user_settings.is_image_mode_text_only(user_id)

    if is_text_only:
        # Text-only image generation (original functionality)
        image_path = None
    else:
        # Image-based generation - get the uploaded image path
        image_path = user_settings.get_uploaded_image_path(user_id)
        if not image_path:
            await update.effective_message.reply_text(
                get_translation("uploaded_image_not_found_message", language)
            )
            user_settings.clear_awaiting_prompt(user_id)
            return

    # Prefer application-scoped service, fall back to constructing one
    service: GeminiImageService | None = context.application.bot_data.get("gemini_service") if context.application else None
    if service is None:
        if not api_key:
            await update.effective_message.reply_text(get_translation("image_generation_not_configured_message", language))
            user_settings.clear_awaiting_prompt(user_id)
            return
        service = GeminiImageService(api_key=api_key)

    tmp_dir = tempfile.mkdtemp(prefix="imagegen_")
    out_path = Path(tmp_dir) / "image.jpg"

    try:
        # Generate image based on mode
        if image_path:
            # Image-to-image generation
            path = await asyncio.to_thread(
                service.generate_image_from_image_and_text, image_path, text, str(out_path)
            )
        else:
            # Text-only generation
            path = await asyncio.to_thread(
                service.generate_image_file, text, str(out_path), ratio
            )

        if path:
            with open(path, "rb") as f:
                await update.effective_message.reply_photo(photo=f)

            # Deduct credit and send confirmation
            if deduct_image_credit(user_id):
                image_credits, _ = get_user_credits(user_id)
                await update.effective_message.reply_text(
                    get_translation("image_credit_deducted", language, remaining=image_credits)
                )
        else:
            await update.effective_message.reply_text(get_translation("image_generation_failed_message", language))
    
    finally:
        # Clean up states and temporary files
        user_settings.clear_awaiting_prompt(user_id)
        user_settings.clear_uploaded_image_path(user_id)
        user_settings.clear_image_mode(user_id)
        
        try:
            paths_to_cleanup = []
            if image_path:
                paths_to_cleanup.append(image_path)
            if out_path.exists():
                paths_to_cleanup.append(str(out_path))

            for path_str in paths_to_cleanup:
                if path_str:
                    path = Path(path_str)
                    if path.exists():
                        path.unlink()
                    # Try to remove the temp directory
                    if path.parent.exists() and "tmp" in str(path.parent):
                        try:
                            path.parent.rmdir()
                        except:
                            pass
        except Exception:
            log.debug("Failed to cleanup temp files", exc_info=True)

