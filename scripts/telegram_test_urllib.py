import os
import urllib.request
import urllib.parse

def main():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    text = os.environ.get('TELEGRAM_TEST_TEXT', 'Telegram test (urllib) from Twt_Agent MVP')
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(url, data=data)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            print("Telegram urllib response:", resp.status, body[:300])
    except Exception as e:
        print("Telegram urllib test failed:", e)

if __name__ == '__main__':
    main()
