#!/usr/bin/env python3
import argparse
import os

ENV_PATH = ".env"

def write_env(vals: dict):
    lines = []
    # Preserve existing non-token lines if possible by rewriting the file
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            existing = f.read()
        # We'll append/overwrite keys we control; simple approach: rewrite all keys we manage
        # Collect existing keys we care about to preserve their order
        lines = existing.splitlines()
        keys_to_update = {
            'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID', 'SLACK_WEBHOOK',
            'TZ', 'MORNING_TIME', 'AFTERNOON_TIME', 'EVENING_TIME',
            'MINUTES_BEFORE_POST', 'DRY_RUN', 'TEST_MODE'
        }
        new_lines = []
        seen = set()
        for line in lines:
            if '=' in line:
                k = line.split('=',1)[0].strip()
                if k in keys_to_update:
                    continue
            new_lines.append(line)
        lines = new_lines

    # Build new content from provided values, preserving any non-covered existing lines
    header = []
    if 'TELEGRAM_BOT_TOKEN' in vals:
        header.append(f"TELEGRAM_BOT_TOKEN={vals['TELEGRAM_BOT_TOKEN']}")
    if 'TELEGRAM_CHAT_ID' in vals:
        header.append(f"TELEGRAM_CHAT_ID={vals['TELEGRAM_CHAT_ID']}")
    if 'SLACK_WEBHOOK' in vals:
        header.append(f"SLACK_WEBHOOK={vals['SLACK_WEBHOOK']}")
    if 'TZ' in vals:
        header.append(f"TZ={vals['TZ']}")
    if 'MORNING_TIME' in vals:
        header.append(f"MORNING_TIME={vals['MORNING_TIME']}")
    if 'AFTERNOON_TIME' in vals:
        header.append(f"AFTERNOON_TIME={vals['AFTERNOON_TIME']}")
    if 'EVENING_TIME' in vals:
        header.append(f"EVENING_TIME={vals['EVENING_TIME']}")
    if 'MINUTES_BEFORE_POST' in vals:
        header.append(f"MINUTES_BEFORE_POST={vals['MINUTES_BEFORE_POST']}")
    if 'DRY_RUN' in vals:
        header.append(f"DRY_RUN={vals['DRY_RUN']}")
    if 'TEST_MODE' in vals:
        header.append(f"TEST_MODE={vals['TEST_MODE']}")

    content = "\n".join(header) + "\n"
    with open(ENV_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Wrote {ENV_PATH} with provided values.")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--token', help='Telegram bot token')
    ap.add_argument('--chat_id', help='Telegram chat/channel id (e.g., @channel or numeric chat_id)')
    ap.add_argument('--tz', help='Timezone, e.g., Asia/Kolkata')
    ap.add_argument('--morning', help='Morning posting time HH:MM')
    ap.add_argument('--afternoon', help='Afternoon posting time HH:MM')
    ap.add_argument('--evening', help='Evening posting time HH:MM')
    ap.add_argument('--dry_run', help='DRY_RUN (true/false)')
    ap.add_argument('--test_mode', help='TEST_MODE (true/false)')
    ap.add_argument('--slack', help='Slack webhook url (optional)')
    args = ap.parse_args()

    vals = {}
    if args.token:
        vals['TELEGRAM_BOT_TOKEN'] = args.token
    if args.chat_id:
        vals['TELEGRAM_CHAT_ID'] = args.chat_id
    if args.slack:
        vals['SLACK_WEBHOOK'] = args.slack
    if args.tz:
        vals['TZ'] = args.tz
    if args.morning:
        vals['MORNING_TIME'] = args.morning
    if args.afternoon:
        vals['AFTERNOON_TIME'] = args.afternoon
    if args.evening:
        vals['EVENING_TIME'] = args.evening
    if args.dry_run:
        vals['DRY_RUN'] = args.dry_run
    if args.test_mode:
        vals['TEST_MODE'] = args.test_mode

    if not vals:
        print("No values provided. Use --token and --chat_id at a minimum.")
        return
    write_env(vals)

if __name__ == '__main__':
    main()
