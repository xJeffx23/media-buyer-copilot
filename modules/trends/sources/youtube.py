"""YouTube Data API v3: videos en tendencia y búsquedas recientes por tema (opcional)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import requests

from core.config import env

API = "https://www.googleapis.com/youtube/v3"


def _get(path: str, **params) -> list[dict]:
    key = env("YOUTUBE_API_KEY", required=False)
    if not key:
        return []
    r = requests.get(f"{API}/{path}", params={**params, "key": key}, timeout=20)
    r.raise_for_status()
    return r.json().get("items", [])


def trending(region: str, limit: int = 15) -> list[dict]:
    items = _get("videos", part="snippet,statistics", chart="mostPopular", regionCode=region, maxResults=limit)
    return [
        {
            "source": f"YouTube tendencias {region}",
            "title": v["snippet"]["title"],
            "channel": v["snippet"]["channelTitle"],
            "views": v.get("statistics", {}).get("viewCount"),
        }
        for v in items
    ]


def search_recent(queries: list[str], per_query: int = 5) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = []
    for q in queries:
        for v in _get("search", part="snippet", q=q, type="video", order="viewCount",
                      publishedAfter=since, maxResults=per_query):
            out.append({
                "source": f"YouTube '{q}'",
                "title": v["snippet"]["title"],
                "channel": v["snippet"]["channelTitle"],
                "url": f"https://youtu.be/{v['id']['videoId']}",
            })
    return out
