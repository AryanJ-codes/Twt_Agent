import time
from scheduler_manager import plan_today, start
import threading
from bot_responder import main_loop as _bot_main_loop
from config import Config

def main():
    print("Twitter Growth Bot - MVP starting...")
    # Initialize and plan today's drafts
    drafts = plan_today()
    # Print generated tweets to console
    import json as _json
    print("\n── Generated Tweets ──────────────────────────")
    for path in drafts:
        try:
            d = _json.load(open(path, encoding='utf-8'))
            print(f"[{d.get('scheduled_at')}] ({d.get('category')})")
            print(f"  {d.get('content')}\n")
        except Exception:
            pass
    print("──────────────────────────────────────────────\n")
    if Config.TEST_MODE:
        print("[TEST_MODE] Posting all approved drafts immediately...")
        from scheduler_manager import admin_preview, publish_if_approved
        for path in drafts:
            admin_preview(path)
            publish_if_approved(path)
    # Start scheduler loop (handles live scheduled posts)
    start()
    # Start Telegram bot responder in background if enabled
    try:
        t = threading.Thread(target=_bot_main_loop, daemon=True)
        t.start()
    except Exception:
        pass
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()
