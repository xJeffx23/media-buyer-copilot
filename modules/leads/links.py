"""Clasifica enlaces: muchos negocios ponen su Facebook, Instagram o WhatsApp donde
debería ir su sitio web. Tratarlos como web da falsos "sin Pixel" y claves duplicadas.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

SOCIAL_DOMAINS = ("facebook.com", "fb.com", "fb.me", "instagram.com", "tiktok.com", "linktr.ee",
                  "wa.me", "whatsapp.com", "youtube.com", "twitter.com", "x.com", "linkedin.com")
IG_RE = re.compile(r"instagram\.com/([A-Za-z0-9_.]{2,30})")
IGNORED_IG = {"p", "reel", "reels", "explore", "accounts", "stories",
              "wix", "squarespace", "shopify", "wordpress", "godaddy", "instagram", "meta"}


def normalize_key(value: str) -> str:
    v = value.lower().strip()
    for prefix in ("https://", "http://", "www."):
        v = v.removeprefix(prefix)
    return v.rstrip("/")


def domain(url: str) -> str:
    host = urlparse(url if "://" in url else f"https://{url}").netloc.lower()
    return host.removeprefix("www.")


def is_social(url: str) -> bool:
    d = domain(url)
    return any(d == s or d.endswith("." + s) for s in SOCIAL_DOMAINS)


def instagram_handle(text: str) -> str | None:
    for h in IG_RE.findall(text or ""):
        if h.lower() not in IGNORED_IG:
            return h
    return None


def split_link(url: str | None) -> dict:
    """Devuelve el campo correcto para un enlace: website, instagram, facebook_page o whatsapp."""
    url = (url or "").strip()
    if not url:
        return {}
    if not is_social(url):
        return {"website": url}
    d = domain(url)
    if "instagram.com" in d:
        handle = instagram_handle(url)
        return {"instagram": handle} if handle else {}
    if d in ("facebook.com", "fb.com", "fb.me") or d.endswith(".facebook.com"):
        return {"facebook_page": url}
    if d in ("wa.me", "whatsapp.com") or d.endswith(".whatsapp.com"):
        return {"whatsapp": True}
    return {}
