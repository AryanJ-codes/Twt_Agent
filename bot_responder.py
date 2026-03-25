import json
import time
import os
try:
    import requests
    _HAS_REQUESTS = True
except Exception:
    requests = None
    _HAS_REQUESTS = False
from config import Config

TOKEN = getattr(Config, 'TELEGRAM_BOT_TOKEN', None)
CHAT_ID_DEFAULT = getattr(Config, 'TELEGRAM_CHAT_ID', None)
OFFSET_PATH = os.path.join('storage', 'bot_offset.json')
LAST_PREVIEWED_PATH = os.path.join('storage', 'last_previewed.json')

# Keywords that mean the user wants a different tweet
DISAPPROVAL_KEYWORDS = [
    'no', 'nope', 'nah', 'not this', 'not good', 'not ok',
    'disapproved', 'disapprove', 'reject', 'rejected',
    'try again', 'try something else', 'another one',
    'change it', 'change this', 'different', 'redo',
    'bad', 'terrible', 'awful', 'dont like', "don't like",
    'skip', 'next', 'pass',
]

def load_offset():
    try:
        with open(OFFSET_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return int(data.get('offset', 0))
    except FileNotFoundError:
        return 0
    except Exception:
        return 0

def save_offset(offset: int):
    with open(OFFSET_PATH, 'w', encoding='utf-8') as f:
        json.dump({'offset': offset}, f)

def send_message(chat_id, text):
    if not TOKEN or not chat_id:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        resp = requests.post(url, data={'chat_id': chat_id, 'text': text}, timeout=5)
        if resp is not None:
            print(f"[bot_responder] sent message status={resp.status_code}")
    except Exception as e:
        print(f"[bot_responder] failed to send message: {e}")

def is_disapproval(text: str) -> bool:
    t = text.lower().strip()
    return any(kw in t for kw in DISAPPROVAL_KEYWORDS)

def load_last_previewed():
    try:
        with open(LAST_PREVIEWED_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def regenerate_draft(draft_path: str, chat_id) -> bool:
    """Generate a new tweet for the given draft, save it, and send preview to Telegram."""
    try:
        with open(draft_path, 'r', encoding='utf-8') as f:
            draft = json.load(f)
    except Exception:
        send_message(chat_id, "⚠️ Couldn't find the draft to regenerate. It may have already been posted.")
        return False

    if draft.get('posted'):
        send_message(chat_id, "⚠️ This draft has already been posted — can't regenerate.")
        return False

    topic = draft.get('topic', '')
    category = draft.get('category', 'General')
    # Cycle to the next style for genuine variety on each rejection
    current_style = draft.get('last_style', 'default')
    try:
        from llm_service import get_next_style, generate_tweet
        next_style = get_next_style(current_style)
        new_content = generate_tweet(topic, style=next_style)
    except Exception:
        next_style = 'default'
        new_content = None

    if not new_content:
        # Fallback to template
        try:
            from content_generator import _template_fallback
            old_content = draft.get('content', '')
            new_content = _template_fallback(topic, category)
            # Ensure it's actually different
            if new_content == old_content:
                new_content = _template_fallback(topic, category)
        except Exception as e:
            send_message(chat_id, f"⚠️ Couldn't generate a new tweet: {e}")
            return False

    draft['content'] = new_content
    draft['approved'] = True
    draft['last_style'] = next_style

    try:
        with open(draft_path, 'w', encoding='utf-8') as f:
            json.dump(draft, f, indent=2, ensure_ascii=False)
            f.write('\n')
    except Exception as e:
        send_message(chat_id, f"⚠️ Couldn't save regenerated draft: {e}")
        return False

    send_message(
        chat_id,
        f"🔄 New tweet ({next_style} style) for {draft.get('scheduled_at', 'scheduled time')}:\n\n"
        f"📝 {new_content}\n\n"
        f"✅ Auto-approved. Reply with 'no', 'nope', etc. to try another style."
    )
    print(f"[bot_responder] Regenerated draft ({next_style}): {draft_path}")
    return True

def generate_reply(user_text: str) -> str:
    t = user_text.lower()
    if any(w in t for w in ['hello', 'hi', 'hey']):
        return "Hello! 👋 I'm your Twitter bot manager. I'll send you tweet previews before they post — just reply with 'no' or 'try again' to reject any."
    if 'help' in t:
        return "I send you tweet previews 30 min before posting. Reply with 'no', 'nope', 'try again', etc. to reject and get a new one. Approved tweets post automatically."
    if 'status' in t:
        return "Bot is running. Tweets post at 09:00, 11:30, 13:00, 19:30, 21:30 IST unless you reject them."
    return f"Got it! I'll keep that in mind. (Send 'help' to see what I can do.)"

def run_once():
    if not TOKEN:
        print("[bot_responder] No Telegram token configured; exiting.")
        return
    last_seen = load_offset()
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_seen+1}"
            resp = requests.get(url, timeout=5)
            if resp.status_code != 200:
                time.sleep(5)
                continue
            data = resp.json()
            results = data.get('result', []) or []
            for item in results:
                upd_id = int(item.get('update_id', 0))
                msg = item.get('message')
                if not msg:
                    last_seen = upd_id
                    continue
                # Ignore messages from bots
                if msg.get('from', {}).get('is_bot'):
                    last_seen = upd_id
                    continue
                chat = msg.get('chat', {})
                chat_id = chat.get('id')
                chat_type = chat.get('type', 'private')
                if chat_type != 'private' or not chat_id:
                    last_seen = upd_id
                    continue
                text = msg.get('text') or ''
                if text:
                    if is_disapproval(text):
                        # Try to regenerate the last previewed draft
                        previewed = load_last_previewed()
                        if previewed and previewed.get('draft_path'):
                            regenerate_draft(previewed['draft_path'], chat_id)
                        else:
                            send_message(chat_id, "⚠️ No draft is currently pending preview to regenerate.")
                    else:
                        reply = generate_reply(text)
                        send_message(chat_id, reply)
                last_seen = upd_id
            if results:
                save_offset(last_seen)
        except Exception as e:
            print(f"[bot_responder] error: {e}")
        time.sleep(2)

def main_loop():
    if not Config.REPLY_TO_MESSAGES:
        print("[bot_responder] Replying is disabled by config.")
        return
    run_once()

if __name__ == '__main__':
    main_loop()
