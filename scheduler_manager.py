import os
import json
from datetime import datetime, timedelta
import pytz
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    _SCHED_AVAILABLE = True
except Exception:
    # Minimal fallback scheduler for test environments
    class BackgroundScheduler:
        def __init__(self, timezone=None):
            self.timezone = timezone
        def start(self):
            pass
        def add_job(self, *args, **kwargs):
            pass
    _SCHED_AVAILABLE = False
from config import Config
from trend_collector import fetch_trending_topics
from topic_classifier import classify_topic
from content_generator import generate_tweets_for_topic
from storage_utils import write_json, read_json
from admin_notifier import notify_admin
from poster import post_tweet as publish_tweet

SCHED = BackgroundScheduler(timezone=Config.TZ)

DAILY_DRAFTS_PATH = os.path.join("storage", "drafts")

def ensure_dirs():
    for d in ["storage/drafts", "storage/posts", "storage/topics"]:
        os.makedirs(d, exist_ok=True)

def create_draft(draft_id: str, topic: str, category: str, content: str, scheduled_at: str):
    draft = {
        "id": draft_id,
        "topic": topic,
        "category": category,
        "content": content,
        "scheduled_at": scheduled_at,
        "approved": True,
        "posted": False,
        "created_at": datetime.now(pytz.timezone(Config.TZ)).isoformat()
    }
    path = os.path.join(DAILY_DRAFTS_PATH, f"{draft_id}.json")
    write_json(path, draft)
    return path

def admin_preview(draft_path: str):
    draft = read_json(draft_path)
    if not draft:
        return
    notify_admin(draft, draft_path=draft_path)

def _notify_posted(draft: dict):
    """Send a Telegram message confirming a tweet was successfully posted."""
    token = Config.TELEGRAM_BOT_TOKEN
    chat_id = Config.TELEGRAM_CHAT_ID
    if not token or not chat_id:
        return
    text = (
        f"✅ Tweet posted!\n\n"
        f"📝 {draft.get('content')}\n\n"
        f"🏷 {draft.get('topic')} ({draft.get('category')}) · {draft.get('scheduled_at')}"
    )
    try:
        import requests as _req
        _req.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": text},
            timeout=5,
        )
    except Exception as e:
        print(f"[scheduler] Telegram post-notify error: {e}")

def publish_if_approved(draft_path: str):
    draft = read_json(draft_path)
    if not draft:
        return
    if draft.get("approved") is True and not draft.get("posted"):
        ok = publish_tweet(draft["content"])
        if ok:
            draft["posted"] = True
            draft["posted_at"] = datetime.now(pytz.timezone(Config.TZ)).isoformat()
            write_json(draft_path, draft)
            _notify_posted(draft)
        else:
            # Notify failure via Telegram
            token = Config.TELEGRAM_BOT_TOKEN
            chat_id = Config.TELEGRAM_CHAT_ID
            if token and chat_id:
                try:
                    import requests as _req
                    _req.post(
                        f"https://api.telegram.org/bot{token}/sendMessage",
                        data={"chat_id": chat_id, "text": f"❌ Failed to post tweet for {draft.get('scheduled_at')}. Check Twitter app permissions."},
                        timeout=5,
                    )
                except Exception:
                    pass

def plan_today():
    ensure_dirs()
    # fetch trends and create 5 posts at fixed times
    topics = fetch_trending_topics(limit=5)
    times = [
        Config.MORNING_TIME,
        Config.MIDDAY_TIME,
        Config.AFTERNOON_TIME,
        Config.EVENING_TIME,
        Config.NIGHT_TIME,
    ]
    drafts_created = []
    for idx, topic in enumerate(topics[:5]):
        category = topic if topic else "General"
        try:
            from topic_classifier import classify_topic
            category = classify_topic(topic)
        except Exception:
            category = "General"
        target_style = "discussion" if idx < 2 else "default"
        tweets = generate_tweets_for_topic(topic, category, count=2, style=target_style)
        scheduled = times[min(idx, len(times)-1)]
        content = tweets[0] if tweets else topic
        draft_id = f"draft_{datetime.now().strftime('%Y%m%d')}_{idx+1}"
        path = create_draft(draft_id, topic, category, content, scheduled)
        drafts_created.append(path)
        # schedule admin preview 30 minutes before
        try:
            sched = pytz.timezone(Config.TZ)
            today_str = datetime.now().strftime("%Y-%m-%d")
            # Convert to datetime objects
            def to_datetime(date_str, time_str):
                dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                # pytz-like tz object may not implement localize in minimal envs;
                # fall back to naive dt with tzinfo attached.
                if hasattr(sched, 'localize'):
                    try:
                        return sched.localize(dt)
                    except Exception:
                        pass
                return dt.replace(tzinfo=sched if isinstance(sched, object) else None)
            publish_dt = to_datetime(today_str, scheduled)
            preview_dt = publish_dt - timedelta(minutes=Config.MINUTES_BEFORE_POST)
            from datetime import timezone as _tz
            now_utc = datetime.utcnow().replace(tzinfo=_tz.utc)
            if preview_dt > now_utc:
                SCHED.add_job(lambda p=path: admin_preview(p), trigger='date', run_date=preview_dt)
            if publish_dt > now_utc:
                SCHED.add_job(lambda p=path: publish_if_approved(p), trigger='date', run_date=publish_dt)
        except Exception:
            pass
    return drafts_created

def start():
    # In test/dev envs without APScheduler, just ensure the object exists
    if hasattr(SCHED, 'start'):
        try:
            SCHED.start()
        except Exception:
            pass
