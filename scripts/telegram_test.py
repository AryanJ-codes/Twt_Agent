import os
import requests

def main():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    text = os.environ.get('TELEGRAM_TEST_TEXT', 'Telegram test message from Twt_Agent MVP')
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set. Aborting test.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        resp = requests.post(url, data=payload, timeout=10)
        print("Telegram response:", resp.status_code, resp.text)
    except Exception as e:
        print("Telegram test failed:", e)

if __name__ == '__main__':
    main()
