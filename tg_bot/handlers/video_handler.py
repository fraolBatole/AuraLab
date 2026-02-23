from __future__ import annotations

import logging
import tempfile
from pathlib import Path
import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from services.gemini_video import GeminiVideoService
from tg_bot.user_settings import user_settings, has_video_credits, deduct_video_credit, get_user_credits
from tg_bot.translations import get_translation
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

log = logging.getLogger(__name__)

VIDEO_CHOICE_TEXT = "📝 Text Only"
VIDEO_CHOICE_IMAGE = "🖼️ With Image"

def get_video_choice_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Creates keyboard for video generation choice."""
    language = user_settings.get_language(user_id)

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=get_translation(VIDEO_CHOICE_TEXT, language),
            callback_data="video_choice:text"
        )],
        [InlineKeyboardButton(
            text=get_translation(VIDEO_CHOICE_IMAGE, language),
            callback_data="video_choice:image"
        )]
    ])


async def begin_video_generation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the video generation process by offering choice between text-only or image-based."""
    user_id = update.effective_user.id if update.effective_user else 0
    language = user_settings.get_language(user_id)

    if not has_video_credits(user_id):
        await update.effective_message.reply_text(
            get_translation("insufficient_video_credits", language)
        )
        return

    user_settings.set_awaiting_video_choice(user_id)
    await update.effective_message.reply_text(
        get_translation("video_generation_choice", language),
        reply_markup=get_video_choice_keyboard(user_id)
    )


async def cancel_user_video_task(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Cancel any running video generation task for a user."""
    try:
        if hasattr(context, 'user_data') and f'video_task_{user_id}' in context.user_data:
            task = context.user_data[f'video_task_{user_id}']
            if not task.done():
                task.cancel()
                log.info("Cancelled video generation task for user %s", user_id)
                return True
    except Exception as e:
        log.warning("Failed to cancel video task for user %s: %s", user_id, e)
    return False


async def handle_video_choice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle video generation choice selection."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id if update.effective_user else 0
    language = user_settings.get_language(user_id)

    if not user_settings.is_awaiting_video_choice(user_id):
        return

    choice = query.data.split(":")[1] if ":" in query.data else ""

    if choice == "text":
        # Text-only video generation
        user_settings.clear_awaiting_video_choice(user_id)
        user_settings.set_awaiting_video_prompt(user_id)
        user_settings.set_video_mode_text_only(user_id)
        await query.edit_message_text(
            get_translation("video_text_only_prompt", language)
        )

    elif choice == "image":
        # Image-based video generation
        user_settings.clear_awaiting_video_choice(user_id)
        user_settings.set_awaiting_image_upload(user_id)
        user_settings.set_video_mode_with_image(user_id)
        await query.edit_message_text(
            get_translation("video_generation_prompt", language)
        )


async def handle_image_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle uploaded images for video generation."""
    user_id = update.effective_user.id if update.effective_user else 0
    language = user_settings.get_language(user_id)

    if not user_settings.is_awaiting_image_upload(user_id):
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
        tmp_dir = tempfile.mkdtemp(prefix="videogen_upload_")
        image_path = Path(tmp_dir) / f"user_{user_id}_upload.jpg"

        file_obj = await context.bot.get_file(photo.file_id)
        await file_obj.download_to_drive(str(image_path))

        # Store the image path
        user_settings.set_uploaded_image_path(user_id, str(image_path))
        user_settings.clear_awaiting_image_upload(user_id)
        user_settings.set_awaiting_video_prompt(user_id)

        await update.effective_message.reply_text(
            get_translation("image_upload_success_prompt", language)
        )

    except Exception as exc:
        log.exception("Failed to process uploaded image: %s", exc)
        await update.effective_message.reply_text(
            get_translation("image_processing_error_message", language)
        )


async def handle_video_prompt_text(update: Update, context: ContextTypes.DEFAULT_TYPE, api_key: str | None = None) -> None:
    """Handle the video prompt text for both text-only and image-based video generation."""
    user_id = update.effective_user.id if update.effective_user else 0
    language = user_settings.get_language(user_id)

    if not user_settings.is_awaiting_video_prompt(user_id):
        return

    text = (update.effective_message.text or "").strip()
    if not text:
        await update.effective_message.reply_text(get_translation("video_description_prompt", language))
        return

    # Check if user has video credits (will always be false since video credits stay at 0)
    if not has_video_credits(user_id):
        await update.effective_message.reply_text(get_translation("insufficient_video_credits", language))
        user_settings.clear_awaiting_video_prompt(user_id)
        return

    # Cancel any existing video generation task for this user
    if await cancel_user_video_task(user_id, context):
        await update.effective_message.reply_text(
            get_translation("video_generation_cancelled_previous", language)
        )

    await update.effective_message.reply_text(
        get_translation("video_generation_in_progress_message", language)
    )

    # Check if this is text-only or image-based video generation
    is_text_only = user_settings.is_video_mode_text_only(user_id)

    if is_text_only:
        # Text-only video generation
        image_path = None
    else:
        # Image-based video generation - get the uploaded image path
        image_path = user_settings.get_uploaded_image_path(user_id)
        if not image_path:
            await update.effective_message.reply_text(
                get_translation("uploaded_image_not_found_message", language)
            )
            user_settings.clear_awaiting_video_prompt(user_id)
            return

    # Prefer application-scoped service, fall back to constructing one
    video_service: GeminiVideoService | None = context.application.bot_data.get("gemini_video_service") if context.application else None
    if video_service is None:
        if not api_key:
            await update.effective_message.reply_text(get_translation("video_generation_not_configured_message", language))
            user_settings.clear_awaiting_video_prompt(user_id)
            return
        video_service = GeminiVideoService(api_key=api_key)

    # Generate video in a background task to avoid blocking
    task = asyncio.create_task(
        generate_video_background(
            update, context, video_service, image_path, text, user_id, language
        )
    )

    # Add timeout protection for the entire task
    try:
        await asyncio.wait_for(asyncio.sleep(0), timeout=0)  # Just to ensure task starts
    except asyncio.TimeoutError:
        pass  # Task is running in background, this is expected

    # Store task reference for potential cancellation (optional enhancement)
    if not hasattr(context, 'user_data'):
        context.user_data = {}
    context.user_data[f'video_task_{user_id}'] = task

    # Add a callback to cleanup the task reference when done
    def cleanup_task(task_ref):
        try:
            if hasattr(context, 'user_data') and f'video_task_{user_id}' in context.user_data:
                del context.user_data[f'video_task_{user_id}']
        except Exception as e:
            log.debug("Failed to cleanup task reference: %s", e)

    # Schedule cleanup when task completes
    task.add_done_callback(lambda t: cleanup_task(t))


async def generate_video_background(
    update: Update,
    context: ContextTypes,
    video_service: GeminiVideoService,
    image_path: str | None,
    prompt: str,
    user_id: int,
    language: str
) -> None:
    """Generate video in the background and send result. Handles task cancellation gracefully."""
    video_path = None
    try:
        tmp_dir = tempfile.mkdtemp(prefix="videogen_output_")
        output_path = Path(tmp_dir) / f"video_{user_id}.mp4"

        # Progress callback to send updates to user (less frequent to avoid timeouts)
        progress_counter = 0
        last_progress_time = 0

        async def send_progress(message: str):
            nonlocal progress_counter, last_progress_time
            import time

            current_time = time.time()
            # Only send progress updates every 2 minutes (120 seconds) or for major milestones
            if current_time - last_progress_time < 120 and not any(keyword in message.lower() for keyword in ['complete', 'ready', 'finished']):
                return

            try:
                progress_counter += 1
                last_progress_time = current_time
                await context.bot.send_message(
                    chat_id=user_id,
                    text=get_translation("video_progress", language, progress=message)
                )
            except Exception as e:
                log.warning("Failed to send progress update (attempt %d): %s", progress_counter, e)
                # Don't retry progress updates to avoid compounding timeout issues

        # Generate the video - choose method based on whether we have an image
        if image_path:
            # Image-based video generation
            video_path = await video_service.generate_video_from_image_and_prompt(
                image_path, prompt, str(output_path), progress_callback=send_progress
            )
        else:
            # Text-only video generation
            video_path = await video_service.generate_video_from_prompt(
                prompt, str(output_path), progress_callback=send_progress
            )

        # Check if task was cancelled after generation
        if asyncio.current_task().cancelled():
            log.info("Video generation task was cancelled for user %s", user_id)
            return

        if video_path and Path(video_path).exists():
            # Send the video
            caption_text = get_translation("video_ready_caption", language, prompt=f"{prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            with open(video_path, "rb") as f:
                await update.effective_message.reply_video(
                    video=f,
                    caption=caption_text
                )

            # Deduct video credit and send confirmation
            if deduct_video_credit(user_id):
                _, video_credits = get_user_credits(user_id)
                await update.effective_message.reply_text(
                    get_translation("video_credit_deducted", language, remaining=video_credits)
                )
        else:
            await update.effective_message.reply_text(
                get_translation("video_generation_failed_message", language)
            )

    except asyncio.TimeoutError:
        log.warning("Video generation timed out for user %s", user_id)
        await update.effective_message.reply_text(
            get_translation("video_generation_timeout_message", language)
        )
    except asyncio.CancelledError:
        log.info("Video generation task was cancelled for user %s", user_id)
        # Don't send a message for cancelled tasks as the user started a new request
        return
    except Exception as exc:
        log.exception("Video generation failed: %s", exc)
        # Provide more specific error messages based on exception type
        if "timeout" in str(exc).lower() or "timed out" in str(exc).lower():
            error_message = get_translation("video_generation_timeout_message", language)
        elif "quota" in str(exc).lower() or "limit" in str(exc).lower():
            error_message = get_translation("video_generation_quota_message", language)
        else:
            error_message = get_translation("video_generation_error_message", language)

        try:
            await update.effective_message.reply_text(error_message)
        except Exception as send_error:
            log.error("Failed to send error message to user %s: %s", user_id, send_error)

    finally:
        # Clean up states and temporary files
        user_settings.clear_awaiting_video_prompt(user_id)
        user_settings.clear_uploaded_image_path(user_id)
        user_settings.clear_video_mode(user_id)

        # Clean up temporary files
        try:
            paths_to_cleanup = []
            if image_path:
                paths_to_cleanup.append(image_path)
            if video_path:
                paths_to_cleanup.append(video_path)

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