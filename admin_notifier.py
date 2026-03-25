import json
import os
try:
    import requests
except Exception:
    class _RequestsFallback:
        def post(self, *args, **kwargs):
            return None
        def get(self, *args, **kwargs):
            return None
    requests = _RequestsFallback()
from config import Config

LAST_PREVIEWED_PATH = os.path.join("storage", "last_previewed.json")

def _save_last_previewed(draft: dict, draft_path: str):
    try:
        os.makedirs("storage", exist_ok=True)
        with open(LAST_PREVIEWED_PATH, "w", encoding="utf-8") as f:
            json.dump({"draft_id": draft.get("id"), "draft_path": draft_path}, f)
    except Exception:
        pass

def notify_admin(draft: dict, draft_path: str = None):
    text = (
        f"📅 Scheduled: {draft['scheduled_at']}\n"
        f"🏷 Topic: {draft['topic']} ({draft['category']})\n\n"
        f"📝 Tweet:\n{draft['content']}\n\n"
        f"✅ Auto-approved. Reply with 'no', 'nope', 'try again', etc. to reject and get a new one."
    )
    # Slack webhook (optional)
    if Config.SLACK_WEBHOOK:
        try:
            requests.post(Config.SLACK_WEBHOOK, json={"text": text}, timeout=10)
        except Exception:
            pass
    # Telegram: use plain HTTP API (works with all library versions)
    if Config.TELEGRAM_BOT_TOKEN and Config.TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
            resp = requests.post(url, data={"chat_id": Config.TELEGRAM_CHAT_ID, "text": text}, timeout=5)
            if resp is not None:
                print(f"[Telegram Preview] HTTP status={resp.status_code}")
                if draft_path:
                    _save_last_previewed(draft, draft_path)
        except Exception as e:
            print(f"[Telegram Preview] HTTP error: {e}")

