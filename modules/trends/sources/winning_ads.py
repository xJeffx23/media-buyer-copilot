"""Anuncios de referencia: los anuncios activos que más tiempo llevan corriendo en
la Biblioteca de Meta. Si un anuncio lleva meses activo, casi seguro es rentable.
"""
from __future__ import annotations

from datetime import datetime, timezone

from core.apify import run_actor
from modules.leads.sources.meta_ads import ACTOR, _get, library_url


def longest_running(keywords: list[str], country: str = "ALL", per_keyword: int = 20, top: int = 15) -> list[dict]:
    items = run_actor(
        ACTOR,
        {"startUrls": [{"url": library_url(k, country)} for k in keywords], "resultsLimit": per_keyword},
    )
    now = datetime.now(timezone.utc)
    ads = []
    for ad in items:
        snap = ad.get("snapshot") or {}
        start = ad.get("startDate") or ad.get("start_date")
        if not isinstance(start, (int, float)):
            continue
        ads.append({
            "source": "Meta Ad Library",
            "page": _get(ad, "pageName", "page_name") or _get(snap, "pageName", "page_name"),
            "days_running": (now - datetime.fromtimestamp(start, timezone.utc)).days,
            "format": _get(snap, "displayFormat", "display_format"),
            "text": ((snap.get("body") or {}).get("text") or "")[:400],
        })
    return sorted(ads, key=lambda a: a["days_running"], reverse=True)[:top]
