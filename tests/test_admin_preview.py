import os
from scheduler_manager import admin_preview

def run_all():
    drafts = [
        'storage/drafts/draft_20260324_1.json',
        'storage/drafts/draft_20260324_2.json',
        'storage/drafts/draft_20260324_3.json',
    ]
    for d in drafts:
        if os.path.exists(d):
            print(f"Previewing {d}")
            admin_preview(d)
        else:
            print(f"Missing draft: {d}")

if __name__ == '__main__':
    run_all()
