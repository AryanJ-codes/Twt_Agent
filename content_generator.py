import random

# ─── Template fallback (used when LLM is unavailable) ────────────────────────
TEMPLATES = {
    "Indian and international affairs": [
        "Hot take on {topic}: it's trending, so obviously we should talk about it today.",
        "{topic} is everywhere right now. My two cents: stay curious, stay informed.",
        "If {topic} had a meme, it would be me trying to understand it.",
        "{topic} entering the chat like it owns the place 💀",
    ],
    "Bollywood/Entertainment": [
        "{topic} just dropped and I'm watching it with snacks. Opinions welcome.",
        "Plot twist: {topic} is the plot twist we didn't know we needed.",
        "{topic} — peak content or cry? Can't decide.",
    ],
    "Student life": [
        "Student hack: {topic}. Works... sometimes.",
        "If only exams could be as trending as {topic}.",
        "{topic} — the topic that ruins sleep schedules and somehow wins memes.",
        "Me pretending to understand {topic} in front of my professor 🙂",
    ],
    "Tech/Work": [
        "Tech take: {topic} is changing how we code and commute.",
        "{topic} is trending in the dev world; time to pretend we understand it.",
        "{topic} enters the chat. Half the internet: 'finally'. Other half: 'what?'",
    ],
    "Jobs": [
        "Career thought: {topic}—the thing that keeps us grinding every Monday.",
        "{topic} in the job market right now seems wild but exciting.",
        "Recruiter: 5 years exp in {topic}. Job posting date: 2 years ago.",
    ],
    "Sports": [
        "{topic} update: the scoreboard isn't the only thing trending here.",
        "My fantasy team approves of {topic} today.",
        "{topic} and Twitter going absolutely feral rn and I'm here for it.",
    ],
    "General": [
        "{topic} is buzzing. Here's my take: relatable and light.",
        "Nobody: \nAbsolutely nobody: \n{topic}: exists and takes over the internet.",
        "{topic}: the perfect meme fuel for today.",
    ],
}


def _template_fallback(topic: str, category: str) -> str:
    templates = TEMPLATES.get(category, TEMPLATES["General"])
    text = random.choice(templates).format(topic=topic)
    if len(text) > 280:
        text = text[:277] + "..."
    return text


def generate_tweets_for_topic(topic: str, category: str, count: int = 2, style: str = "default"):
    """
    Generate tweet drafts for a topic.
    Tries LLM first (Groq → HuggingFace), falls back to templates.
    """
    tweets = []
    from llm_service import generate_tweet, STYLE_CYCLE

    for i in range(count):
        # Cycle through styles for variety
        current_style = STYLE_CYCLE[i % len(STYLE_CYCLE)] if style == "default" else style
        result = generate_tweet(topic, style=current_style)
        if result:
            tweets.append(result)
        else:
            tweets.append(_template_fallback(topic, category))

    return tweets
