import os
try:
    from pytrends.request import TrendReq
except Exception:
    TrendReq = None
from datetime import datetime
from storage_utils import read_json, write_json
from config import Config

def fetch_trending_topics(limit: int = 6):
    # TEST_MODE: return a deterministic sample list to allow quick test runs without network
    if os.environ.get("TEST_MODE") in ("1", "true", "yes"):
        sample = [
            "AI chips taking over",
            "Bollywood new release",
            "Campus placements 2026",
            " IPL 2026",
            "Ind-EU policy debate",
            "Cricket world cup",
        ]
        return sample[:limit]
    """Fetch trending topics using Google Trends (India region by default)."""
    tz = Config.TREND_TZ
    if TrendReq is None:
        return []
    pytrend = TrendReq(hl='en-US', tz=tz)
    topics = []
    try:
        df = pytrend.trending_searches(pn='india')
        if df is not None:
            # df is a DataFrame with a single column of topics
            try:
                col = df.columns[0]
                topics = df[col].astype(str).tolist()
            except Exception:
                # fallback if structure differs
                topics = list(df[0].astype(str))
    except Exception:
        topics = []
    # unique preserving order and apply limit
    uniq = []
    for t in topics:
        t = t.strip()
        if t and t not in uniq:
            uniq.append(t)
            if len(uniq) >= limit:
                break
    return uniq
