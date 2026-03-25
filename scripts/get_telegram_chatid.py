#!/usr/bin/env python3
import json
import os
import urllib.request
import ssl
import urllib.parse

def _load_env(path: str = ".env"):
    if not os.path.exists(path):
        return
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and not os.environ.get(k):
                    os.environ[k] = v
    except Exception:
        pass

def main():
    _load_env()
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN is not set in env.")
        return
    url = f"https://api.telegram.org/bot{token}/getUpdates?limit=50"
    try:
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        except Exception:
            ctx = None
        if ctx:
            with urllib.request.urlopen(url, timeout=15, context=ctx) as resp:
                data = json.loads(resp.read().decode())
        else:
            with urllib.request.urlopen(url, timeout=15) as resp:
                data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"Failed to fetch updates: {e}")
        return

    results = data.get('result', [])
    chat_ids = {}
    for item in results:
        msg = item.get('message') or item.get('callback_query')
        if not msg:
            continue
        chat = msg.get('chat')
        if not chat:
            continue
        cid = chat.get('id')
        ctype = chat.get('type')
        if cid is not None:
            chat_ids[cid] = ctype

    if not chat_ids:
        print("No chat_id found in updates yet. Send a message to the bot or join the channel to generate updates.")
        return

    print("Detected channel/user chat_ids (id -> type):")
    for cid, ctype in sorted(chat_ids.items()):
        print(f"- {cid} ({ctype})")

    # If there's a single channel, suggest using -100... as chat_id
    if len(chat_ids) == 1:
        only_id = list(chat_ids.keys())[0]
        print(f"Recommended TELEGRAM_CHAT_ID to use: {only_id}")

if __name__ == '__main__':
    main()
