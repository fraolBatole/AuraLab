## AuraLabs (Telegram Bot)

Minimal, modular Telegram bot that generates images and videos with Google Gemini. Powered by AuraLabs.

### Features
- 🖼️ Generate images from text prompts
- 🎥 Create videos from text or images
- 📐 Multiple aspect ratios (1:1, 9:16, 16:9, 4:3, 3:4)
- 🌍 Multi-language support (English/Amharic)
- 💰 Credit-based usage system (2 free images per user)
- 🎨 Preset prompt suggestions for quick generation
- 🔄 Image-to-image generation
- ⚙️ User settings (language, aspect ratio preferences)

### User Flow
1. Start bot with `/start` - select language if new user
2. Choose between Image or Video generation
3. For images: Select text-only or upload reference image
4. Enter prompt or use preset suggestions
5. Bot generates content and deducts credits
6. Repeat until credits exhausted, then top-up message appears

### Setup
1. Python 3.10+
2. Create and activate a virtualenv
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Create `.env` (see `.env.example`) and set:
   - `TELEGRAM_BOT_TOKEN`
   - `GEMINI_API_KEY`

Example `.env`:
```bash
TELEGRAM_BOT_TOKEN=123456789:ABCDEF
GEMINI_API_KEY=your_gemini_api_key
```

### Run
```bash
python main.py
```

#### Admin Dashboard

Install Streamlit (already in `requirements.txt`), then run:
```bash
streamlit run admin/dashboard.py
```
The dashboard lets you:
- View user list with credits and plan details.
- Reset image/video credits for selected users.

You can also use the CLI:
```bash
python -m admin.cli list --limit 20
python -m admin.cli reset-credits 12345 --image 5 --video 1
python -m admin.cli delete 12345
```

### Database
- User credits and preferences are stored in SQLite (`bot_database.db`)
- Database is automatically created on first run
- User settings (language, aspect ratio) are stored in-memory and reset on restart

### Development
- Run tests: `python -m pytest tests/`
- Add new translations in `tg_bot/translations.py`
- Add new keyboard buttons in `tg_bot/keyboards.py`

