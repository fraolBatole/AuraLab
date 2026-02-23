def test_imports():
    # Expanded imports for full project coverage
    from core.utils.config import load_config
    from core.utils.logging import configure_logging
    from services.gemini_image import GeminiImageService
    from services.gemini_video import GeminiVideoService
    from tg_bot.handlers.image_handler import begin_prompt, handle_prompt_text, handle_image_choice_callback, handle_image_upload_for_image_gen
    from tg_bot.handlers.video_handler import begin_video_generation, handle_image_upload, handle_video_prompt_text, handle_video_choice_callback
    from tg_bot.keyboards import main_menu_keyboard, image_aspect_ratio_keyboard, video_aspect_ratio_keyboard, language_keyboard, settings_keyboard, welcome_language_keyboard
    from tg_bot.translations import get_translation
    from tg_bot.user_settings import user_settings, AspectRatio, Language, detect_language_from_telegram

    # Add asserts for the new imports
    assert GeminiImageService is not None
    assert GeminiVideoService is not None
    assert begin_prompt is not None
    assert handle_prompt_text is not None
    assert handle_image_choice_callback is not None
    assert handle_image_upload_for_image_gen is not None
    assert begin_video_generation is not None
    assert handle_image_upload is not None
    assert handle_video_prompt_text is not None
    assert handle_video_choice_callback is not None
    assert main_menu_keyboard is not None
    assert image_aspect_ratio_keyboard is not None
    assert video_aspect_ratio_keyboard is not None
    assert language_keyboard is not None
    assert settings_keyboard is not None
    assert welcome_language_keyboard is not None
    assert get_translation is not None
    assert user_settings is not None
    assert AspectRatio is not None
    assert Language is not None
    assert detect_language_from_telegram is not None

