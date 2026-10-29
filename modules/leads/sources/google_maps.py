"""Fuente 1: negocios locales desde Google Maps (actor de Apify compass/crawler-google-places)."""
from __future__ import annotations

from core.apify import run_actor
from modules.leads.links import normalize_key, split_link

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
        link = split_link(website)  # si "website" es su Facebook o Instagram, va a su campo
        leads.append(
            {
                "id": normalize_key(key),
                "source": "google_maps",
                "niche": niche["id"],
                "name": it.get("title"),
                "city": it.get("city") or location,
                "phone": it.get("phone"),
                "website": link.get("website", ""),
                "instagram": link.get("instagram"),
                "facebook_page": link.get("facebook_page"),
                "rating": it.get("totalScore"),
                "reviews": it.get("reviewsCount"),
                "raw": {k: it.get(k) for k in ("address", "categoryName", "url", "placeId")},
            }
        )
    return leads
