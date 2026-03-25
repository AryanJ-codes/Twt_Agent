import os
os.environ.setdefault("TEST_MODE", "1")
os.environ.setdefault("DRY_RUN", "true")
from scheduler_manager import plan_today

def main():
    drafts = plan_today()
    print("Drafts created:", drafts)

if __name__ == "__main__":
    main()
