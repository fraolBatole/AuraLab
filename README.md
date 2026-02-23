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

### Project Structure
```
AuraLabs/
├── core/                    # Core application logic
│   ├── __init__.py
│   ├── app.py              # Main bot application
│   └── utils/
│       ├── __init__.py
│       ├── config.py       # Configuration management
│       └── logging.py      # Logging setup
├── services/               # External service integrations
│   ├── __init__.py
│   ├── gemini_image.py     # Image generation service
│   └── gemini_video.py     # Video generation service
├── tg_bot/                 # Telegram bot specific logic
│   ├── __init__.py
│   ├── handlers/           # Message and callback handlers
│   │   ├── __init__.py
│   │   ├── image_handler.py
│   │   ├── video_handler.py
│   │   └── prompt_handler.py
│   ├── keyboards.py        # Inline keyboards
│   ├── translations.py     # Multi-language support
│   └── user_settings.py    # User preferences and credits
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── bot_database.db         # SQLite database (auto-created)
├── tests/                  # Unit tests
│   ├── __init__.py
│   ├── test_gemini_image.py
│   └── test_imports.py
└── README.md
```
## Pricing
 - Image Gen costs $0.04 per image (around 6 birr per image)
   - if we sell one image for 12 birr: profit = 6 birr, margin = **50%**
   - if we sell one image for 18 birr: profit = 12 birr, margin = **66.7%**
 - Video Gen costs $0.15 per second, so for 8 seconds it would be $1.20 (around 180 birr)
   - if we sell 8 sec video for 360 birr: profit = 180 birr, margin = **50%**
   
- **Margin Calculation Examples:**
    - Margin (%) = (Profit / Selling Price) × 100
    - If you sell at 15 birr: cost = 6 birr, profit = 9 birr, margin = 60%
    - If you sell at 20 birr: cost = 6 birr, profit = 14 birr, margin = 70%
    - If you sell at 25 birr: cost = 6 birr, profit = 19 birr, margin = 76%
    - If you sell at 30 birr: cost = 6 birr, profit = 24 birr, margin = 80%
    - For video (8 sec, cost 180 birr):
        - Sell at 250 birr: profit = 70 birr, margin ≈ 28%
        - Sell at 300 birr: profit = 120 birr, margin = 40%
        - Sell at 400 birr: profit = 220 birr, margin = 55%
        - Sell at 500 birr: profit = 320 birr, margin = 64%
    - **Formula:**  
      `margin = (selling_price - cost) / selling_price × 100%`

### Other Costs

- **Hosting:** Free for the next 6-7 months (covered by current cloud credits or free tier).
- **Database:** SQLite is used, which is free and requires no paid hosting or maintenance.
- **Domain:** No custom domain cost (using default service domain or Telegram username).
- **Maintenance/Support:** No paid staff or support costs at this stage.
- **Development:** All development is done in-house, so no outsourcing or contractor expenses.
- **Other Services:** No additional paid third-party services are currently used.

> **Summary:**  
> For the next 6-7 months, your only direct cost is the API usage (image/video generation). All infrastructure, database, and operational costs are effectively zero due to free tiers or credits.

## Credit System
- Users start with 10 free image credits upon first use
- Each image generation (text-to-image, image-to-image, or preset) deducts 1 credit
- Video generation requires credits (currently set to 10, so unavailable)
- When credits run out, users see a message to top up
- All credit management is handled through SQLite database 

### Database
- User credits and preferences are stored in SQLite (`bot_database.db`)
- Database is automatically created on first run
- User settings (language, aspect ratio) are stored in-memory and reset on restart

### Development
- Run tests: `python -m pytest tests/`
- Add new translations in `tg_bot/translations.py`
- Add new keyboard buttons in `tg_bot/keyboards.py`

