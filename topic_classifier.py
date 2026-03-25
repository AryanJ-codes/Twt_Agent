def classify_topic(topic: str) -> str:
    text = topic.lower()
    if any(k in text for k in ["india", "india's", "economy", "election", "policy", "pak", "us", "china", "world"]):
        return "Indian and international affairs"
    if any(k in text for k in ["bollywood", "film", "tv", "series", "splitsvilla", "roadies", "reality"]):
        return "Bollywood/Entertainment"
    if any(k in text for k in ["student", "college", "university", "exam", "campus", "campus"]):
        return "Student life"
    if any(k in text for k in ["tech", "coding", "software", "ai", "machine learning", "startup"]):
        return "Tech/Work"
    if any(k in text for k in ["job", "career", "office", "salary", "work"]):
        return "Jobs"
    if any(k in text for k in ["sport", "cricket", "football", "basketball", "tennis"]):
        return "Sports"
    return "General"
