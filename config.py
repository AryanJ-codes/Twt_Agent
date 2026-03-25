import os

def _load_dotenv(path: str = ".env"):
    # Lightweight .env loader (no external dependency required)
    try:
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and not os.environ.get(key):
                    os.environ[key] = val
    except Exception:
        pass

_load_dotenv()

class Config:
    # Time zone for scheduling (e.g., 'Asia/Kolkata')
    TZ: str = os.environ.get("TZ", "Asia/Kolkata")

    # Daily posting times in 24h format (local time in TZ)
    MORNING_TIME: str = os.environ.get("MORNING_TIME", "09:00")
    # Midday slot
    MIDDAY_TIME: str = os.environ.get("MIDDAY_TIME", "11:30")
    # Afternoon slot adjusted for peak engagement window
    AFTERNOON_TIME: str = os.environ.get("AFTERNOON_TIME", "13:00")
    # Evening slot adjusted for peak engagement window
    EVENING_TIME: str = os.environ.get("EVENING_TIME", "19:30")
    # Night slot
    NIGHT_TIME: str = os.environ.get("NIGHT_TIME", "21:30")

    # Admin notification channel (optional)
    SLACK_WEBHOOK: str = os.environ.get("SLACK_WEBHOOK")

    # Twitter API credentials (should be set as env vars; do not commit keys)
    TW_CONSUMER_KEY: str = os.environ.get("TW_CONSUMER_KEY")
    TW_CONSUMER_SECRET: str = os.environ.get("TW_CONSUMER_SECRET")
    TW_BEARER_TOKEN: str = os.environ.get("TW_BEARER_TOKEN")
    TW_ACCESS_TOKEN: str = os.environ.get("TW_ACCESS_TOKEN")
    TW_ACCESS_TOKEN_SECRET: str = os.environ.get("TW_ACCESS_TOKEN_SECRET")
    TW_CLIENT_ID: str = os.environ.get("TW_CLIENT_ID")
    TW_CLIENT_SECRET: str = os.environ.get("TW_CLIENT_SECRET")

    # Playwright Automation Credentials
    TWITTER_USERNAME: str = os.environ.get("TWITTER_USERNAME")
    TWITTER_EMAIL: str = os.environ.get("TWITTER_EMAIL")
    TWITTER_PASSWORD: str = os.environ.get("TWITTER_PASSWORD")

    # Trend data source region (used by Google Trends via pytrends)
    TREND_TZ: str = os.environ.get("TREND_TZ", "IN")

    # LLM API keys (free tier — see README for setup)
    GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY")
    HF_API_KEY: str = os.environ.get("HF_API_KEY")

    # Admin pre-approval window (minutes before publish)
    MINUTES_BEFORE_POST: int = int(os.environ.get("MINUTES_BEFORE_POST", "30"))

    # Dry-run mode: when True, do not actually publish to Twitter; useful for testing
    # Default to True if not specified to avoid accidental posts during development
    DRY_RUN: bool = str(os.environ.get("DRY_RUN", "true")).lower() in ("1", "true", "yes", "on")

    # Telegram notifier (optional)
    TELEGRAM_BOT_TOKEN: str = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: str = os.environ.get("TELEGRAM_CHAT_ID")
    # TEST mode (internal test harness)
    TEST_MODE: bool = str(os.environ.get("TEST_MODE", "false")).lower() in ("1", "true", "yes", "on")

    # Auto-reply to user messages (Telegram) - free, simple responder
    REPLY_TO_MESSAGES: bool = str(os.environ.get("REPLY_TO_MESSAGES", "true")).lower() in ("1", "true", "yes", "on")
