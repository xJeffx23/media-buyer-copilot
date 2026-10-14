"""Fuente 2: negocios que YA anuncian en Meta (Biblioteca de Anuncios vía Apify).

Por qué Apify y no la API oficial: la Ad Library API de Meta solo devuelve anuncios
comerciales que se muestran en la UE; fuera de ahí solo da anuncios políticos.

Un negocio que ya invierte en anuncios es el mejor prospecto: ya tiene presupuesto,
solo hay que demostrarle que puede rendir más.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from urllib.parse import quote_plus

from core.apify import run_actor
from modules.leads.sources.google_maps import normalize_key

ACTOR = "apify/facebook-ads-scraper"


def library_url(keyword: str, country: str) -> str:
    return (
        "https://www.facebook.com/ads/library/?active_status=active&ad_type=all"
        f"&country={country}&q={quote_plus(keyword)}&search_type=keyword_unordered&media_type=all"
    )


def search(niche: dict, country: str, max_ads: int) -> list[dict]:
    if not niche["ad_keywords"]:
        return []
    items = run_actor(
        ACTOR,
        {
            "startUrls": [{"url": library_url(k, country)} for k in niche["ad_keywords"]],
            "resultsLimit": max_ads,
        },
    )
    return group_by_page(items, niche["id"])


def _get(d: dict, *keys, default=None):
    """El actor puede devolver camelCase o snake_case según la versión."""
    for k in keys:
        if d.get(k) not in (None, ""):
            return d[k]
    return default


def group_by_page(items: list[dict], niche_id: str) -> list[dict]:
    pages: dict[str, dict] = {}
    formats: dict[str, dict] = defaultdict(lambda: defaultdict(int))
    oldest: dict[str, int] = {}
    now = datetime.now(timezone.utc)

    for ad in items:
        snap = ad.get("snapshot") or {}
        page_id = str(_get(ad, "pageId", "page_id", default="") or _get(snap, "page_id", default=""))
        if not page_id:
            continue
        name = _get(ad, "pageName", "page_name") or _get(snap, "page_name")
        page_url = _get(snap, "page_profile_uri") or f"https://www.facebook.com/{page_id}"
        link = _get(snap, "link_url", default="")

        fmt = (_get(snap, "display_format", default="") or "").lower()
        if not fmt:
            fmt = "video" if snap.get("videos") else "carousel" if len(snap.get("cards") or []) > 1 else "image"
        formats[page_id][fmt] += 1

        start = _get(ad, "startDate", "start_date")
        if isinstance(start, (int, float)):
            days = (now - datetime.fromtimestamp(start, timezone.utc)).days
            oldest[page_id] = max(oldest.get(page_id, 0), days)

        if page_id not in pages:
            website = link if link and "facebook.com" not in link else ""
            pages[page_id] = {
                # misma clave que Google Maps cuando hay web, para fusionar ambos registros
                "id": normalize_key(website) if website else f"fb:{page_id}",
                "source": "meta_ads",
                "niche": niche_id,
                "name": name,
                "facebook_page": page_url,
                "website": website,
                "raw": {"sample_ad_text": ((snap.get("body") or {}).get("text") or "")[:500]},
            }

    leads = []
    for page_id, lead in pages.items():
        lead["active_ads"] = sum(formats[page_id].values())
        lead["ad_formats"] = dict(formats[page_id])
        lead["oldest_ad_days"] = oldest.get(page_id)
        leads.append(lead)
    return leads
