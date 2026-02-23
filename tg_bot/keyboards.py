from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from tg_bot.user_settings import AspectRatio, VideoAspectRatio, Language, user_settings
from tg_bot.translations import get_translation, get_prompt_presets


BTN_IMAGE = "🖼 Create Image"
BTN_VIDEO = "🎥 Create Video"
BTN_HELP = "❓ Help"
BTN_SETTINGS = "⚙️ Settings"
BTN_TOP_UP = "➕ Top Up"
BTN_BALANCE = "💰 Balance"

CB_PREFIX_IMAGE_RATIO = "ratio:image:"
CB_PREFIX_VIDEO_RATIO = "ratio:video:"
CB_PREFIX_LANGUAGE = "language:"
CB_SETTINGS_IMAGE_RATIO = "settings:ratio:image"
CB_SETTINGS_VIDEO_RATIO = "settings:ratio:video"
CB_SETTINGS_LANGUAGE = "settings:language"
CB_SETTINGS_MAIN = "settings:main"
CB_BACK_TO_SETTINGS = "settings:back"
CB_WELCOME_LANGUAGE = "welcome:language"

# Preset and navigation callback prefixes
CB_PRESET_SELECT = "preset:select"
CB_PRESET_PAGE = "preset:page"
CB_PRESET_RETRY = "preset:retry"
CB_NAV_VIDEO = "nav:video"
CB_NAV_IMAGE = "nav:image"
CB_NAV_PRESETS = "nav:presets"

MAIN_BUTTONS = [
    BTN_IMAGE,
    BTN_VIDEO,
    BTN_BALANCE,
    BTN_HELP,
    BTN_SETTINGS,
    BTN_TOP_UP,
]


def main_menu_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """Creates the main menu keyboard with translated button texts."""
    language = user_settings.get_language(user_id)

    buttons = [
        [KeyboardButton(get_translation(BTN_IMAGE, language)), KeyboardButton(get_translation(BTN_VIDEO, language))],
        [KeyboardButton(get_translation(BTN_BALANCE, language)), KeyboardButton(get_translation(BTN_HELP, language))],
        [KeyboardButton(get_translation(BTN_SETTINGS, language)), KeyboardButton(get_translation(BTN_TOP_UP, language))],
    ]

    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def image_aspect_ratio_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Keyboard for selecting image aspect ratio with a translated back button."""
    language = user_settings.get_language(user_id)
    rows = []
    for ratio in AspectRatio:
        rows.append([
            InlineKeyboardButton(text=ratio.value, callback_data=f"{CB_PREFIX_IMAGE_RATIO}{ratio.name}")
        ])
    back_button_text = get_translation("⬅️ Back to Settings", language)
    rows.append([InlineKeyboardButton(text=back_button_text, callback_data=CB_BACK_TO_SETTINGS)])
    return InlineKeyboardMarkup(rows)


def video_aspect_ratio_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Keyboard for selecting video aspect ratio with a translated back button."""
    language = user_settings.get_language(user_id)
    rows = []
    for ratio in VideoAspectRatio:
        rows.append([
            InlineKeyboardButton(text=ratio.value, callback_data=f"{CB_PREFIX_VIDEO_RATIO}{ratio.name}")
        ])
    back_button_text = get_translation("⬅️ Back to Settings", language)
    rows.append([InlineKeyboardButton(text=back_button_text, callback_data=CB_BACK_TO_SETTINGS)])
    return InlineKeyboardMarkup(rows)


def settings_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Main settings menu with options to choose what to configure."""
    img_ratio = user_settings.get_ratio(user_id).value
    video_ratio = user_settings.get_video_ratio(user_id).value
    language = user_settings.get_language(user_id)
    current_language_display = language.value

    img_ratio_text = get_translation("📐 Image Aspect Ratio", language)
    video_ratio_text = get_translation("🎞️ Video Aspect Ratio", language)
    language_text = get_translation("🌐 Language", language)

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text=f"{img_ratio_text} ({img_ratio})", callback_data=CB_SETTINGS_IMAGE_RATIO)],
        [InlineKeyboardButton(text=f"{video_ratio_text} ({video_ratio})", callback_data=CB_SETTINGS_VIDEO_RATIO)],
        [InlineKeyboardButton(text=f"{language_text} ({current_language_display})", callback_data=CB_SETTINGS_LANGUAGE)]
    ])


def language_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Keyboard for selecting language with a translated back button."""
    language = user_settings.get_language(user_id)
    rows = []
    for lang in Language:
        rows.append([
            InlineKeyboardButton(text=lang.value, callback_data=f"{CB_PREFIX_LANGUAGE}{lang.name}")
        ])
    # Add back button
    back_button_text = get_translation("⬅️ Back to Settings", language)
    rows.append([InlineKeyboardButton(text=back_button_text, callback_data=CB_BACK_TO_SETTINGS)])
    return InlineKeyboardMarkup(rows)


def welcome_language_keyboard() -> InlineKeyboardMarkup:
    """Creates the welcome language selection keyboard."""
    rows = []
    for lang in Language:
        rows.append([
            InlineKeyboardButton(text=lang.value, callback_data=f"{CB_WELCOME_LANGUAGE}:{lang.name}")
        ])
    return InlineKeyboardMarkup(rows)


def prompt_presets_keyboard(user_id: int, page: int = 0, page_size: int = 5) -> InlineKeyboardMarkup:
    """Inline keyboard for browsing/selecting image prompt presets with pagination."""
    language = user_settings.get_language(user_id)
    presets = get_prompt_presets(language)
    total = len(presets)
    if page_size <= 0:
        page_size = 5
    max_page = (total - 1) // page_size if total else 0
    page = max(0, min(page, max_page))

    start = page * page_size
    end = min(start + page_size, total)

    rows = []
    for item in presets[start:end]:
        rows.append([
            InlineKeyboardButton(
                text=item["label"],
                callback_data=f"{CB_PRESET_SELECT}:{item['id']}"
            )
        ])

    # Pagination controls
    nav_row = []
    prev_text = get_translation("presets_prev", language)
    next_text = get_translation("presets_next", language)
    if page > 0:
        nav_row.append(InlineKeyboardButton(text=prev_text, callback_data=f"{CB_PRESET_PAGE}:{page-1}"))
    if page < max_page:
        nav_row.append(InlineKeyboardButton(text=next_text, callback_data=f"{CB_PRESET_PAGE}:{page+1}"))
    if nav_row:
        rows.append(nav_row)

    return InlineKeyboardMarkup(rows)


def followup_navigation_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Inline keyboard for quick navigation after an operation completes."""
    language = user_settings.get_language(user_id)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text=get_translation(BTN_VIDEO, language), callback_data=CB_NAV_VIDEO)],
        [InlineKeyboardButton(text=get_translation(BTN_IMAGE, language), callback_data=CB_NAV_IMAGE)],
    ])

