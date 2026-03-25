"""
Playwright-based Twitter automation for posting tweets without using the Twitter API.
Handles auto-login, session saving, natural typing, and explicit error retries.
"""
import asyncio
import os
import random
import time
from playwright.async_api import async_playwright
from config import Config

SESSION_FILE = os.path.join("storage", "twitter_session.json")

# -- Helper for human-like delays --
async def _human_delay(min_ms=1000, max_ms=3000):
    await asyncio.sleep(random.uniform(min_ms, max_ms) / 1000.0)

async def _slow_type(element, text: str):
    """Simulate human typing speed."""
    for char in text:
        await element.type(char, delay=random.randint(30, 150))

async def init_browser(p, headless=True):
    """Launch the browser with reasonable anti-detection args."""
    browser = await p.chromium.launch(
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--window-size=1280,800"
        ]
    )
    return browser

async def login(page):
    """Log into Twitter and handle username/email flows."""
    print("[poster] Navigating to Twitter login...")
    await page.goto("https://twitter.com/i/flow/login")
    await _human_delay(2000, 4000)

    # 1. Email step
    email_input = page.locator('input[autocomplete="username"]')
    await email_input.wait_for(state="visible", timeout=15000)
    await _slow_type(email_input, Config.TWITTER_EMAIL)
    await _human_delay()
    await page.locator('text="Next"').click()
    await _human_delay(1500, 3000)

    # 2. Potential Username verification step
    if await page.locator('input[data-testid="ocfEnterTextTextInput"]').is_visible():
        print("[poster] Twitter asked for username verification...")
        username_input = page.locator('input[data-testid="ocfEnterTextTextInput"]')
        await _slow_type(username_input, Config.TWITTER_USERNAME)
        await _human_delay()
        await page.locator('text="Next"').click()
        await _human_delay(1500, 3000)

    # 3. Password step
    password_input = page.locator('input[name="password"]')
    await password_input.wait_for(state="visible", timeout=15000)
    await _slow_type(password_input, Config.TWITTER_PASSWORD)
    await _human_delay()
    await page.locator('button[data-testid="LoginForm_Login_Button"]').click()
    
    # 4. Wait for home page to confirm login
    await page.wait_for_selector('a[data-testid="AppTabBar_Home_Link"]', timeout=20000)
    print("[poster] Login successful!")

async def _do_post_tweet(page, content: str) -> bool:
    """The actual UI interaction to post a tweet."""
    print("[poster] Opening tweet composer...")
    # Click the large "Post" button on the left sidebar
    post_button = page.locator('a[data-testid="SideNav_NewTweet_Button"]')
    if not await post_button.is_visible():
        print("[poster] Left sidebar post button not found, trying inline composer...")
        # Fallback to inline composer
        post_input = page.locator('div[data-testid="tweetTextarea_0"]')
    else:
        await post_button.click()
        await _human_delay(1000, 2000)
        post_input = page.locator('div[data-testid="tweetTextarea_0"]')

    await post_input.wait_for(state="visible", timeout=10000)
    
    # Type the tweet
    print(f"[poster] Typing tweet: {content[:30]}...")
    await _slow_type(post_input, content)
    await _human_delay(1000, 3000)

    # Click Post
    confirm_btn = page.locator('button[data-testid="tweetButton"]')
    await confirm_btn.click()
    
    # Wait for the toast notification or modal to disappear
    await _human_delay(3000, 5000)
    print("[poster] Tweet posted successfully via UI!")
    return True

async def post_tweet_async(content: str) -> bool:
    """Main entrypoint for posting a tweet with retries and session management."""
    if not hasattr(Config, 'TWITTER_EMAIL') or not Config.TWITTER_EMAIL:
        print("[poster] Error: TWITTER_EMAIL not set in .env")
        return False

    headless = os.environ.get("HEADLESS", "true").lower() == "true"
    
    for attempt in range(1, 4):
        print(f"[poster] Post attempt {attempt}/3...")
        try:
            async with async_playwright() as p:
                browser = await init_browser(p, headless=headless)
                
                # Check for existing session
                context = None
                if os.path.exists(SESSION_FILE):
                    try:
                        context = await browser.new_context(storage_state=SESSION_FILE)
                        print("[poster] Loaded existing session.")
                    except Exception as e:
                        print(f"[poster] Failed to load session: {e}")
                
                if not context:
                    context = await browser.new_context()

                page = await context.new_page()

                # Navigate to home to check if logged in
                await page.goto("https://twitter.com/home")
                await _human_delay(2000, 4000)

                # Check if we are redirected to login or if home link exists
                if not await page.locator('a[data-testid="AppTabBar_Home_Link"]').is_visible():
                    print("[poster] Session invalid or missing. Logging in...")
                    await login(page)
                    # Save session after successful login
                    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
                    await context.storage_state(path=SESSION_FILE)
                    print("[poster] Saved new session state.")

                # Proceed to post
                success = await _do_post_tweet(page, content)
                
                await context.close()
                await browser.close()
                
                if success:
                    return True

        except Exception as e:
            print(f"[poster] Attempt {attempt} failed: {e}")
            await _human_delay(5000, 10000) # Wait before retry

    return False

def post_tweet(content: str) -> bool:
    """Synchronous wrapper for the scheduler."""
    return asyncio.run(post_tweet_async(content))
