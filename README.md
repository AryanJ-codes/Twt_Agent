# AI Twitter Growth Agent 🤖🐦

A fully automated, autonomous Twitter (X) agent that identifies real-time trending topics, generates context-aware, humorous, and relatable Hinglish tweets using cloud LLMs, and posts them entirely via headless browser automation.

Built to run 24/7 on low-memory cloud tiers (e.g., Railway Free Tier) while completely bypassing X's expensive paywalled API.

## 🌟 Key Features
- **Trend Awareness:** Pulls live Google Trends data localized to India to ensure tweets are always highly relevant.
- **LLM-Powered Content:** Generates authentic, Gen Z-style Hinglish tweets using Groq's high-speed Llama 3 models (with HuggingFace Mistral as fallback).
- **Human-like Browser Automation:** Uses Python Playwright to log in, bypass captchas (using stored sessions), simulate variable-speed human typing, and click UI elements to post.
- **Auto-Approval Flow:** Drafts are generated ahead of time, previewed automatically via Telegram, and published seamlessly unless explicitly vetoed by the admin.
- **Intelligent Responding:** Dislike a draft? Reply "no" on Telegram, and the agent instantly cycles to a new comedic style (funny → sarcastic → hot take → relatable) and regenerates the draft.

## 🏗 System Architecture & Pipeline

The system is composed of localized, specialized modules that run via a unified scheduler:

1. **`trend_collector.py` & `topic_classifier.py`**
   Fetches top 5 trending topics using Google Trends (`pytrends`) and categorizes them (Entertainment, Tech, Sports, etc.).
2. **`llm_service.py`**
   The core brain. Prompts Llama 3 (via Groq API) using style modifiers to generate organic Hinglish tweets within the 280-character limit. Falls back to pre-defined templated jokes if no API is reachable.
3. **`content_generator.py`**
   Coordinates the trend data with the LLM service to produce an array of candidate drafts.
4. **`scheduler_manager.py` (The Conductor)**
   Runs via APScheduler. Automatically plans out the day's post times (09:00, 11:30, 13:00, 19:30, 21:30), creating local `.json` drafts and queuing preview/publish jobs.
5. **`bot_responder.py` & `admin_notifier.py`**
   The Telegram communication layer. Sends interactive previews of upcoming tweets and listens concurrently for admin vetos/regeneration requests.
6. **`poster.py`**
   The Playwright module. Replaces the legacy `publisher.py` (which relied on OAuth 1.0). Handles headless Chrome initialization, login, session retention cookies, human typing emulation, and error resets.

## ⚙️ Setup & Execution

### 1. Credentials
Copy `.env.example` to `.env` (or create a new `.env`) and populate:
- `TWITTER_EMAIL`, `TWITTER_USERNAME`, `TWITTER_PASSWORD`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- `GROQ_API_KEY` (Get for free at console.groq.com)
- `HF_API_KEY` (Get for free at huggingface.co)

### 2. Local Installation
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Running
To boot the full autonomous loop:
```bash
python main.py
```
*(Tip: Set `TEST_MODE=true` in `.env` to ignore scheduling and immediately post all 5 drafts concurrently for rapid testing).*

## ☁️ Deployment (Railway)
This project is configured natively for Nixpacks on Railway.
1. Deploy from GitHub to Railway.
2. In Railway settings, add all your variables from the `.env` file.
3. The `railway.json` file automatically instructs the environment to download Chromium binaries. The agent will run infinitely.

## 🚀 Future Scope
- **Image/Meme Generation:** Integrate Stable Diffusion or DALL-E to generate macro-image memes that pair with the generated text.
- **Engagement Harvesting:** Have Playwright actively scrape top replies on other viral tweets and drop contextual, witty replies to siphon impressions.
- **Multi-Account Farm:** Expand `poster.py` to accept rotating cookie sessions and proxy endpoints to run a coordinated network of growth agents.
