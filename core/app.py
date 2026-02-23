from __future__ import annotations

import logging
from typing import Final

from telegram import Update, BotCommand
from telegram.ext import (
	Application,
	ApplicationBuilder,
	CallbackQueryHandler,
	CommandHandler,
	ContextTypes,
	MessageHandler,
	filters,
)
from telegram.request import HTTPXRequest

from core import AppConfig, configure_logging, load_config
from core.database import bot_db
from tg_bot.keyboards import (
	MAIN_BUTTONS,
	main_menu_keyboard,
	image_aspect_ratio_keyboard,
	video_aspect_ratio_keyboard,
	language_keyboard,
	settings_keyboard,
	welcome_language_keyboard,
	BTN_IMAGE,
	BTN_VIDEO,
	BTN_BALANCE,
	BTN_HELP,
	BTN_SETTINGS,
	BTN_TOP_UP,
	CB_PREFIX_IMAGE_RATIO,
	CB_PREFIX_VIDEO_RATIO,
	CB_PREFIX_LANGUAGE,
	CB_SETTINGS_IMAGE_RATIO,
	CB_SETTINGS_VIDEO_RATIO,
	CB_SETTINGS_LANGUAGE,
	CB_SETTINGS_MAIN,
	CB_BACK_TO_SETTINGS,
	CB_WELCOME_LANGUAGE,
	CB_PRESET_PAGE,
	CB_PRESET_SELECT,
	CB_PRESET_RETRY,
	CB_NAV_VIDEO,
	CB_NAV_IMAGE,
	CB_NAV_PRESETS,
)
from tg_bot.user_settings import (
	user_settings,
	AspectRatio,
	VideoAspectRatio,
	Language,
	detect_language_from_telegram,
	has_video_credits,
)
from tg_bot.translations import get_translation
from tg_bot.handlers.image_handler import begin_prompt, handle_prompt_text, handle_image_choice_callback, handle_image_upload_for_image_gen
from services.gemini_image import GeminiImageService
from services.gemini_video import GeminiVideoService
from tg_bot.handlers.video_handler import begin_video_generation, handle_image_upload, handle_video_prompt_text, handle_video_choice_callback
from tg_bot.handlers.prompt_handler import (
	show_presets,
	handle_preset_page_callback,
	handle_preset_select_callback,
	handle_preset_retry_callback,
)
from tg_bot.handlers.balance_handler import show_balance


log = logging.getLogger(__name__)


def init_db() -> None:
	"""Initialize the SQLite database and create the users table if it doesn't exist."""
	bot_db.initialize_database()


BTN_IMAGE, BTN_VIDEO, BTN_BALANCE, BTN_HELP, BTN_SETTINGS, BTN_TOP_UP = MAIN_BUTTONS

# mention the users name here
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	user = update.effective_user
	if not user:
		return

	# Handle user data in database
	existing_user_data = bot_db.get_user_preferences(user.id)
	is_new_user = existing_user_data is None

	chat_id = update.effective_chat.id if update.effective_chat else user.id

	try:
		if is_new_user:
			from tg_bot.user_settings import detect_language_from_telegram, Language, AspectRatio

			language_pref = (
				detect_language_from_telegram(user.language_code)
				if getattr(user, "language_code", None)
				else Language.ENGLISH
			)
			image_ratio_pref = AspectRatio.RATIO_9_16
			video_ratio_pref = VideoAspectRatio.RATIO_9_16

			bot_db.create_user(
				user_id=user.id,
				first_name=user.first_name,
				username=user.username,
				chat_id=chat_id,
				language=language_pref.value,
				image_ratio=image_ratio_pref.value,
				video_ratio=video_ratio_pref.value,
			)
		else:
			bot_db.update_user_basic_info(
				user_id=user.id,
				first_name=user.first_name,
				username=user.username,
				chat_id=chat_id,
			)
	except Exception as e:
		log.error("Database error for user %s: %s", user.id, e)
		is_new_user = False

	# Sync in-memory preferences from DB
	try:
		user_settings.sync_from_db(user.id)
	except Exception as exc:  # pragma: no cover - defensive
		log.debug("Failed to sync preferences for user %s: %s", user.id, exc)

	# Check if this is a new user
	if is_new_user:
		# Show language selection for new users
		welcome_message = get_translation("welcome_language_select", Language.ENGLISH)
		await update.effective_message.reply_text(
			welcome_message, reply_markup=welcome_language_keyboard()
		)
	else:
		# Show main menu for returning users
		language = user_settings.get_language(user.id)
		welcome_message = get_translation("welcome", language, user_name=user.first_name)
		await update.effective_message.reply_text(
			welcome_message, reply_markup=main_menu_keyboard(user.id)
		)
		# Also surface preset suggestions right after welcome
		await show_presets(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	user_id = update.effective_user.id if update.effective_user else 0
	language = user_settings.get_language(user_id)
	help_message = get_translation("help_message", language)
	await update.effective_message.reply_text(help_message)


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	user_id = update.effective_user.id if update.effective_user else 0
	language = user_settings.get_language(user_id)
	settings_message = get_translation("settings_message", language)
	await update.effective_message.reply_text(
		settings_message,
		reply_markup=settings_keyboard(user_id)
	)


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	await show_balance(update, context)


async def handle_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, cfg: AppConfig) -> None:
	text = (update.effective_message.text or "").strip()
	user_id = update.effective_user.id if update.effective_user else 0
	language = user_settings.get_language(user_id)

	# Get translated button texts
	btn_image_text = get_translation(BTN_IMAGE, language)
	btn_video_text = get_translation(BTN_VIDEO, language)
	btn_balance_text = get_translation(BTN_BALANCE, language)
	btn_help_text = get_translation(BTN_HELP, language)
	btn_settings_text = get_translation(BTN_SETTINGS, language)
	btn_top_up_text = get_translation(BTN_TOP_UP, language)
	
	if text == btn_image_text:
		await begin_prompt(update, context)
		return
	if text == btn_video_text:
		if not has_video_credits(user_id):
			await update.effective_message.reply_text(
				get_translation("insufficient_video_credits", language)
			)
			return
		await begin_video_generation(update, context)
		return
	if text == btn_balance_text:
		await show_balance(update, context)
		return
	if text == btn_help_text:
		help_message = get_translation("help_message", language)
		await update.effective_message.reply_text(help_message)
		return
	if text == btn_settings_text:
		settings_message = get_translation("settings_message", language)
		await update.effective_message.reply_text(
			settings_message,
			reply_markup=settings_keyboard(user_id)
		)
		return
	if text == btn_top_up_text:
		coming_soon_message = get_translation("coming_soon", language)
		await update.effective_message.reply_text(coming_soon_message)
		return
	# Check if user is awaiting video prompt
	if user_settings.is_awaiting_video_prompt(user_id):
		await handle_video_prompt_text(update, context, cfg.gemini_api_key)
		return

	# Fallback: if awaiting image prompt, treat as prompt text
	await handle_prompt_text(update, context, cfg.gemini_api_key)


async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	query = update.callback_query
	if not query:
		return

	user = update.effective_user
	if not user:
		return

	data = query.data or ""
	user_id = update.effective_user.id if update.effective_user else 0
	language = user_settings.get_language(user_id)

	if data.startswith(CB_PREFIX_IMAGE_RATIO):
		name = data.split(":", 2)[2]
		try:
			ratio = AspectRatio[name]
			user_settings.set_ratio(user_id, ratio)
			await query.answer(get_translation("aspect_ratio_set_message", language))
			confirmation_message = get_translation("aspect_ratio_set_confirmation", language, ratio_value=ratio.value)
			await query.edit_message_text(
				confirmation_message,
				reply_markup=settings_keyboard(user_id)
			)
		except KeyError:
			await query.answer(get_translation("unknown_ratio_message", language), show_alert=True)
	elif data.startswith(CB_PREFIX_VIDEO_RATIO):
		name = data.split(":", 2)[2]
		try:
			ratio = VideoAspectRatio[name]
			user_settings.set_video_ratio(user_id, ratio)
			await query.answer(get_translation("video_ratio_set_message", language))
			confirmation_message = get_translation("video_ratio_set_confirmation", language, ratio_value=ratio.value)
			await query.edit_message_text(
				confirmation_message,
				reply_markup=settings_keyboard(user_id)
			)
		except KeyError:
			await query.answer(get_translation("unknown_ratio_message", language), show_alert=True)
	elif data.startswith(CB_PREFIX_LANGUAGE):
		name = data.split(":", 1)[1]
		try:
			new_language = Language[name]
			user_settings.set_language(user_id, new_language)
			await query.answer(get_translation("language_set_message", new_language))
			
			# Also update the main menu to reflect the language change
			confirmation_message = get_translation("language_set_confirmation", new_language, language_value=new_language.value)
			await context.bot.send_message(
				chat_id=user_id,
				text=confirmation_message.split('\n')[0],  # Send only the first line as a follow-up
				reply_markup=main_menu_keyboard(user_id)
			)
			await query.edit_message_text(
				confirmation_message,
				reply_markup=settings_keyboard(user_id)
			)
		except KeyError:
			await query.answer(get_translation("unknown_language_message", language), show_alert=True)
	elif data.startswith(CB_WELCOME_LANGUAGE):
		# Handle welcome language selection for new users
		name = data.split(":", 2)[2]  # CB_WELCOME_LANGUAGE:language:ENGLISH/AMHARIC
		try:
			selected_language = Language[name]
			user_settings.set_language(user_id, selected_language)
			
			# Send welcome message with the selected language and show main menu
			user = query.from_user
			welcome_message = get_translation("welcome", selected_language, user_name=user.first_name if user else 'User')
			await query.edit_message_text(welcome_message)
			
			# Send main menu as a new message
			await context.bot.send_message(
				chat_id=user_id,
				text=get_translation("choose_action", selected_language),
				reply_markup=main_menu_keyboard(user_id)
			)
			# Immediately show preset suggestions
			await show_presets(update, context)
		except KeyError:
			await query.answer("Unknown language", show_alert=True)
	elif data == CB_SETTINGS_IMAGE_RATIO:
		message = get_translation("choose_image_aspect_ratio_message", language)
		await query.edit_message_text(message, reply_markup=image_aspect_ratio_keyboard(user_id))
	elif data == CB_SETTINGS_VIDEO_RATIO:
		message = get_translation("choose_video_aspect_ratio_message", language)
		await query.edit_message_text(message, reply_markup=video_aspect_ratio_keyboard(user_id))
	elif data == CB_SETTINGS_LANGUAGE:
		message = get_translation("choose_language_message", language)
		await query.edit_message_text(message, reply_markup=language_keyboard(user_id))
	elif data == CB_BACK_TO_SETTINGS:
		message = get_translation("settings_title", language)
		await query.edit_message_text(message, reply_markup=settings_keyboard(user_id))
	elif data.startswith("video_choice:"):
		await handle_video_choice_callback(update, context)
	elif data.startswith("image_choice:"):
		await handle_image_choice_callback(update, context)
	elif data.startswith(CB_PRESET_PAGE):
		await handle_preset_page_callback(update, context)
	elif data.startswith(CB_PRESET_SELECT):
		cfg = context.application.bot_data.get("cfg") if context.application else None
		api_key = cfg.gemini_api_key if cfg else None
		await handle_preset_select_callback(update, context, api_key=api_key)
	elif data.startswith(CB_PRESET_RETRY):
		cfg = context.application.bot_data.get("cfg") if context.application else None
		api_key = cfg.gemini_api_key if cfg else None
		await handle_preset_retry_callback(update, context, api_key=api_key)
	elif data == CB_NAV_VIDEO:
		if not has_video_credits(user_id):
			await context.bot.send_message(
				chat_id=user_id,
				text=get_translation("insufficient_video_credits", language),
			)
			return
		await begin_video_generation(update, context)
	elif data == CB_NAV_IMAGE:
		await begin_prompt(update, context)
	elif data == CB_NAV_PRESETS:
		await show_presets(update, context)


async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE, cfg: AppConfig) -> None:
	"""Handle all types of messages including text and photos."""
	user = update.effective_user
	if not user:
		return

	# Handle photo uploads
	if update.effective_message.photo:
		user_id = update.effective_user.id if update.effective_user else 0

		# Check if waiting for image upload for video generation
		if user_settings.is_awaiting_image_upload(user_id):
			await handle_image_upload(update, context)
			return

		# Check if waiting for image upload for image-to-image generation
		if user_settings.is_awaiting_image_upload_for_image_gen(user_id):
			await handle_image_upload_for_image_gen(update, context)
			return

	# Handle text messages
	if update.effective_message.text:
		await handle_text_buttons(update, context, cfg)


async def post_init(application: Application) -> None:
	try:
		await application.bot.set_my_commands([
			BotCommand("start", "Open AuraLabs menu"),
			BotCommand("help", "How AuraLabs works"),
			BotCommand("balance", "Check remaining credits"),
			BotCommand("settings", "Update preferences"),
		])
		log.info("Bot commands registered")
	except Exception as exc:
		log.warning("Failed to register bot commands: %s", exc)


def build_app(cfg: AppConfig) -> Application:
	# Configure request with longer timeouts for AI operations
	request = HTTPXRequest(
		connection_pool_size=20,
		read_timeout=900,  # 15 minutes (increased for video generation)
		write_timeout=900,  # 15 minutes (increased for video generation)
		connect_timeout=60,  # 60 seconds (increased connection timeout)
		pool_timeout=60,   # 60 seconds (increased pool timeout)
	)
	
	app = (
		ApplicationBuilder()
		.token(cfg.telegram_bot_token)
		.request(request)
		.post_init(post_init)
		.build()
	)
	# Application-scoped services for reuse
	app.bot_data["gemini_service"] = GeminiImageService(api_key=cfg.gemini_api_key)
	app.bot_data["gemini_video_service"] = GeminiVideoService(api_key=cfg.gemini_api_key)
	app.bot_data["cfg"] = cfg

	app.add_handler(CommandHandler("start", start))
	app.add_handler(CommandHandler("help", help_command))
	app.add_handler(CommandHandler("balance", balance_command))
	app.add_handler(CommandHandler("settings", settings_command))
	app.add_handler(CallbackQueryHandler(handle_callbacks))
	# Route all messages to a wrapper that has access to cfg
	app.add_handler(MessageHandler(
		(filters.TEXT | filters.PHOTO) & ~filters.COMMAND,
		lambda u, c: handle_all_messages(u, c, cfg)
	))
	return app


def run() -> None:
	configure_logging()
	cfg = load_config()
	log.info("Starting AuraLabs bot")
	init_db()
	app = build_app(cfg)
	app.run_polling(close_loop=False)


if __name__ == "__main__":
	run()

