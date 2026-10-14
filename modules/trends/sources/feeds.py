"""Fuentes gratuitas sin API key: Reddit, newsletters (RSS) y Google Trends."""
from __future__ import annotations

import feedparser
import requests

UA = {"User-Agent": "media-buyer-copilot/0.1"}


def _parse(url: str):
    # feedparser no manda un User-Agent que Reddit acepte, así que descargamos con requests
    try:
        return feedparser.parse(requests.get(url, headers=UA, timeout=20).content)
    except requests.RequestException:
        return feedparser.parse("")


def reddit(subreddits: list[str], per_sub: int = 8) -> list[dict]:
    items = []
    for sub in subreddits:
        feed = _parse(f"https://www.reddit.com/r/{sub}/top/.rss?t=week")
        for e in feed.entries[:per_sub]:
            items.append({"source": f"r/{sub}", "title": e.get("title"), "url": e.get("link")})
    return items


def rss(urls: list[str], per_feed: int = 6) -> list[dict]:
    items = []
    for url in urls:
        feed = _parse(url)
        name = feed.feed.get("title", url)
        for e in feed.entries[:per_feed]:
            summary = (e.get("summary") or "")[:300]
            items.append({"source": name, "title": e.get("title"), "url": e.get("link"), "summary": summary})
    return items


def google_trends(region: str, limit: int = 20) -> list[dict]:
    feed = _parse(f"https://trends.google.com/trending/rss?geo={region}")
    return [
        {"source": f"Google Trends {region}", "title": e.get("title"), "traffic": e.get("ht_approx_traffic")}
        for e in feed.entries[:limit]
    ]
