"""Perfiles públicos de cuentas de referencia (actor de Apify apify/instagram-profile-scraper)."""
from __future__ import annotations

from statistics import mean

from core.apify import run_actor

ACTOR = "apify/instagram-profile-scraper"


def analyze(usernames: list[str]) -> list[dict]:
    if not usernames:
        return []
    out = []
    for p in run_actor(ACTOR, {"usernames": usernames}):
        posts = p.get("latestPosts") or []
        followers = p.get("followersCount") or 0
        likes = [x.get("likesCount") or 0 for x in posts]
        comments = [x.get("commentsCount") or 0 for x in posts]
        types: dict[str, int] = {}
        for x in posts:
            t = x.get("productType") or x.get("type") or "?"
            types[t] = types.get(t, 0) + 1
        top_posts = sorted(posts, key=lambda x: (x.get("likesCount") or 0) + (x.get("commentsCount") or 0), reverse=True)[:3]
        out.append({
            "username": p.get("username"),
            "followers": followers,
            "posts": p.get("postsCount"),
            "bio": p.get("biography"),
            "avg_likes": round(mean(likes)) if likes else 0,
            "avg_comments": round(mean(comments)) if comments else 0,
            "engagement_rate_pct": round(100 * (mean(likes) + mean(comments)) / followers, 2) if posts and followers else None,
            "format_mix": types,
            "top_posts": [{"type": x.get("type"), "likes": x.get("likesCount"),
                           "caption": (x.get("caption") or "")[:200], "url": x.get("url")} for x in top_posts],
        })
    return out
