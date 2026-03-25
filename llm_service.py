"""
LLM Service — AI tweet generation using free cloud APIs.

Primary:   Groq (Llama 3.3-70B) — https://console.groq.com
Secondary: HuggingFace Inference API (Mistral-7B-Instruct)
Fallback:  Template-based generation (content_generator.py)
"""
import json
import os
try:
    import requests as _requests
    _HAS_REQUESTS = True
except Exception:
    _requests = None
    _HAS_REQUESTS = False

from config import Config

STYLES = {
    "discussion": "Write a Hinglish tweet addressing a current affair, important issue, or news topic. Subtly start a discussion. It can be serious, thought-provoking, or lightly critical, but must end with an open question or a hook to make people reply.",
    "funny": "Write a genuinely funny, witty Hinglish tweet. Use wordplay, absurdist humor, or an unexpected angle. Make it laugh-out-loud funny.",
    "sarcastic": "Write a sarcastic, dry-humored Hinglish tweet. Sound mildly done with the world, like someone who's seen too much.",
    "hot_take": "Write a spicy hot take or controversial (but safe) opinion in Hinglish. Be bold, confident, slightly provocative.",
    "relatable": "Write a deeply relatable Hinglish tweet. Hit that 'omg this is so me' feeling. Everyday struggles, campus life, doomscrolling vibes.",
    "default": "Write an engaging, humorous Hinglish tweet with a Gen Z voice. Balance wit, relatability, and a fresh take.",
}

STYLE_CYCLE = ["discussion", "default", "funny", "sarcastic", "hot_take", "relatable"]

_SYSTEM_PROMPT = """You are a viral Indian Gen Z Twitter personality who writes in Hinglish (Hindi + English mix).

Language rules — STRICT:
- Write in HINGLISH: roughly 60% Hindi words (in Roman script, NOT Devanagari) and 40% English words
- Example ratio: "Yaar ye AI chips wale sach mein OP hain, mera laptop ab chai maangta hai aur raise bhi"
- Hindi words to use naturally: yaar, bhai, matlab, bilkul, sach mein, seedha, bas, abhi, kyun, kaafi, zyada, ekdum, hoga, hai, nahi, kya, toh, woh, aur, lekin, magar, accha, theek, sun, dekh, lag raha, chal, ho gaya, ek dum, bakwaas, bindaas, pagal, dil, dimag, aisa, waisa
- English words for tech/pop culture/punchline delivery
- NEVER use Devanagari script — Roman Hinglish only
- Sounds like how Gen Z Indians actually type on WhatsApp and Twitter

Tone rules:
- Funny, sarcastic, relatable — never try-hard or forced
- Relevant to Indian campus life, cricket, tech, Bollywood, jobs
- STRICTLY under 280 characters
- No hashtags unless part of the joke
- No emojis unless they add to the punchline
- Never preachy

Output ONLY the tweet text. No quotes, no explanations, no preamble."""


def _build_prompt(topic: str, style: str) -> str:
    style_instruction = STYLES.get(style, STYLES["default"])
    return (
        f"{style_instruction}\n\n"
        f"Topic: {topic}\n\n"
        f"IMPORTANT: Output must be UNDER 280 characters total. Count carefully.\n"
        f"Hinglish tweet (Roman script only, 60% Hindi 40% English):"
    )


def _clean_tweet(text: str) -> str:
    """Strip quotes, leading/trailing whitespace, ensure ≤280 chars."""
    text = text.strip().strip('"').strip("'").strip()
    # Remove common prefixes models sometimes add
    for prefix in ("Tweet:", "tweet:", "Here's a tweet:", "Here is a tweet:"):
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix):].strip()
    if len(text) > 280:
        text = text[:277] + "..."
    return text


def _call_groq(prompt: str) -> str | None:
    """Call Groq's OpenAI-compatible API with Llama 3.3-70B."""
    api_key = getattr(Config, 'GROQ_API_KEY', None)
    if not api_key or not _HAS_REQUESTS:
        return None
    try:
        resp = _requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 100,
                "temperature": 0.9,
            },
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            return _clean_tweet(text)
        else:
            print(f"[llm_service] Groq error {resp.status_code}: {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"[llm_service] Groq exception: {e}")
        return None


def _call_huggingface(prompt: str) -> str | None:
    """Call HuggingFace Inference API with Mistral-7B-Instruct."""
    api_key = getattr(Config, 'HF_API_KEY', None)
    if not api_key or not _HAS_REQUESTS:
        return None
    # Format as Mistral instruct template
    full_prompt = f"<s>[INST] {_SYSTEM_PROMPT}\n\n{prompt} [/INST]"
    try:
        resp = _requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": 100,
                    "temperature": 0.9,
                    "return_full_text": False,
                },
            },
            timeout=20,
        )
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and data:
                text = data[0].get("generated_text", "")
                return _clean_tweet(text) if text else None
        else:
            print(f"[llm_service] HuggingFace error {resp.status_code}: {resp.text[:200]}")
        return None
    except Exception as e:
        print(f"[llm_service] HuggingFace exception: {e}")
        return None


def generate_tweet(topic: str, style: str = "default") -> str | None:
    """
    Generate a tweet using LLMs with automatic fallback.

    Args:
        topic: The trending topic or subject to write about.
        style: One of 'funny', 'sarcastic', 'hot_take', 'relatable', 'default'.

    Returns:
        Tweet text (≤280 chars) or None if all LLMs unavailable.
    """
    prompt = _build_prompt(topic, style)

    # 1. Try Groq (primary)
    result = _call_groq(prompt)
    if result:
        print(f"[llm_service] Generated via Groq ({style}): {result[:60]}...")
        return result

    # 2. Try HuggingFace (secondary)
    result = _call_huggingface(prompt)
    if result:
        print(f"[llm_service] Generated via HuggingFace ({style}): {result[:60]}...")
        return result

    print(f"[llm_service] All LLMs unavailable, caller should use template fallback.")
    return None


def get_next_style(current_style: str) -> str:
    """Return the next style in the cycle — useful for regeneration retries."""
    try:
        idx = STYLE_CYCLE.index(current_style)
        return STYLE_CYCLE[(idx + 1) % len(STYLE_CYCLE)]
    except ValueError:
        return "funny"
