"""Fuente 2: negocios que YA anuncian en Meta (Biblioteca de Anuncios vía Apify).

Por qué Apify y no la API oficial: la Ad Library API de Meta solo devuelve anuncios
comerciales que se muestran en la UE; fuera de ahí solo da anuncios políticos.

Un negocio que ya invierte en anuncios es el mejor prospecto: ya tiene presupuesto,
solo hay que demostrarle que puede rendir más.
"""
from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timezone
from urllib.parse import quote_plus

from core.apify import run_actor
from modules.leads.links import domain, normalize_key, split_link

ACTOR = "apify/facebook-ads-scraper"
# Teléfonos escritos en el texto del anuncio (+506 8888-8888, 2222 3333, etc.)
# Categorías de página que nunca son un negocio de servicios (aunque digan "beauty" o "health")
STORE_CATEGORIES = ("suppl", "shopping", "retail", "store", "tienda", "household", "product/service")
PHONE_RE = re.compile(r"(?<![\d.,])(?:\+\d{1,3}[\s.-]?)?(?:\d{2,4}[\s.-]){1,2}\d{4}(?![\d.,])")


def library_url(keyword: str, country: str) -> str:
    return (
        "https://www.facebook.com/ads/library/?active_status=active&ad_type=all"
        f"&country={country}&q={quote_plus(keyword)}&search_type=keyword_unordered&media_type=all"
    )


def search(niche: dict, country: str, max_ads: int, max_page_likes: int | None = None) -> list[dict]:
    if not niche["ad_keywords"]:
        return []
    items = run_actor(
        ACTOR,
        {
            "startUrls": [{"url": library_url(k, country)} for k in niche["ad_keywords"]],
            "resultsLimit": max_ads,
        },
    )
    return group_by_page(items, niche, max_page_likes)


def _get(d: dict, *keys, default=None):
    """El actor ha devuelto camelCase o snake_case según la versión: se prueban ambos."""
    for k in keys:
        if d.get(k) not in (None, ""):
            return d[k]
    return default


def find_phone(text: str) -> str | None:
    for m in PHONE_RE.findall(text or ""):
        if 8 <= sum(c.isdigit() for c in m) <= 13:
            return m.strip()
    return None


def is_target(niche: dict, categories: list[str], cta: str, likes: int | None, max_page_likes: int | None) -> bool:
    """Descarta proveedores, tiendas y marcas grandes que se cuelan en la búsqueda por palabra clave.

    Filtros opcionales por nicho en niches.yaml: ad_page_categories (la página debe tener
    alguna categoría que contenga uno de esos textos) y ad_exclude_cta (p. ej. SHOP_NOW).
    """
    if cta and cta in (niche.get("ad_exclude_cta") or []):
        return False
    if max_page_likes and likes and likes > max_page_likes:
        return False
    allowed = [a.lower() for a in niche.get("ad_page_categories") or []]
    if allowed and categories:
        cats = [c.lower() for c in categories]
        if any(x in c for c in cats for x in STORE_CATEGORIES):
            return False
        return any(a in c for c in cats for a in allowed)
    return True


def group_by_page(items: list[dict], niche: dict, max_page_likes: int | None = None) -> list[dict]:
    pages: dict[str, dict] = {}
    formats: dict[str, dict] = defaultdict(lambda: defaultdict(int))
    oldest: dict[str, int] = {}
    skipped: set[str] = set()
    now = datetime.now(timezone.utc)

    for ad in items:
        snap = ad.get("snapshot") or {}
        page_id = str(_get(ad, "pageId", "page_id", default="") or _get(snap, "pageId", "page_id", default=""))
        if not page_id or page_id in skipped:
            continue
        categories = _get(snap, "pageCategories", "page_categories", default=[]) or []
        cta = _get(snap, "ctaType", "cta_type", default="")
        likes = _get(snap, "pageLikeCount", "page_like_count")
        if page_id not in pages and not is_target(niche, categories, cta, likes, max_page_likes):
            skipped.add(page_id)
            continue

        fmt = (_get(snap, "displayFormat", "display_format", default="") or "").lower()
        if not fmt or fmt == "dco":
            fmt = "video" if snap.get("videos") else "carousel" if len(snap.get("cards") or []) > 1 else "image"
        formats[page_id][fmt] += 1

        start = _get(ad, "startDate", "start_date")
        if isinstance(start, (int, float)):
            days = (now - datetime.fromtimestamp(start, timezone.utc)).days
            oldest[page_id] = max(oldest.get(page_id, 0), days)

        text = (snap.get("body") or {}).get("text") or ""
        link = split_link(_get(snap, "linkUrl", "link_url", default=""))
        if page_id not in pages:
            website = link.get("website", "")
            if website:  # solo el dominio: así coincide con la web que da Google Maps
                website = f"https://{domain(website)}"
            pages[page_id] = {
                # misma clave que Google Maps cuando hay web, para fusionar ambos registros
                "id": normalize_key(website) if website else f"fb:{page_id}",
                "source": "meta_ads",
                "niche": niche["id"],
                "name": _get(ad, "pageName", "page_name") or _get(snap, "pageName", "page_name"),
                "facebook_page": _get(snap, "pageProfileUri", "page_profile_uri") or f"https://www.facebook.com/{page_id}",
                "website": website,
                "raw": {
                    "sample_ad_text": text[:500],
                    "page_categories": categories,
                    "page_likes": likes,
                    "cta": cta,
                },
            }
        lead = pages[page_id]
        lead["instagram"] = lead.get("instagram") or link.get("instagram")
        lead["phone"] = lead.get("phone") or find_phone(text)
        if link.get("whatsapp"):
            lead["raw"]["whatsapp"] = True

    if skipped:
        print(f"    descartadas {len(skipped)} páginas que no son {niche['id']} (tiendas, proveedores, marcas grandes)")
    leads = []
    for page_id, lead in pages.items():
        lead["active_ads"] = sum(formats[page_id].values())
        lead["ad_formats"] = dict(formats[page_id])
        lead["oldest_ad_days"] = oldest.get(page_id)
        leads.append(lead)
    return leads
