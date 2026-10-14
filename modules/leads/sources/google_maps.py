"""Fuente 1: negocios locales desde Google Maps (actor de Apify compass/crawler-google-places)."""
from __future__ import annotations

from core.apify import run_actor

ACTOR = "compass/crawler-google-places"


def search(niche: dict, location: str, max_places: int, language: str = "es") -> list[dict]:
    if not niche["search_terms"]:
        return []
    items = run_actor(
        ACTOR,
        {
            "searchStringsArray": niche["search_terms"],
            "locationQuery": location,
            "maxCrawledPlacesPerSearch": max_places,
            "language": language,
            "skipClosedPlaces": True,
        },
    )
    leads = []
    for it in items:
        website = (it.get("website") or "").strip()
        key = website or it.get("placeId") or it.get("url")
        if not key:
            continue
        leads.append(
            {
                "id": normalize_key(key),
                "source": "google_maps",
                "niche": niche["id"],
                "name": it.get("title"),
                "city": it.get("city") or location,
                "phone": it.get("phone"),
                "website": website,
                "rating": it.get("totalScore"),
                "reviews": it.get("reviewsCount"),
                "raw": {k: it.get(k) for k in ("address", "categoryName", "url", "placeId")},
            }
        )
    return leads


def normalize_key(value: str) -> str:
    v = value.lower().strip()
    for prefix in ("https://", "http://", "www."):
        v = v.removeprefix(prefix)
    return v.rstrip("/")
