"""Fuente 3: revisa el sitio web del negocio.

Detecta si tiene Pixel de Meta, Google Tag o Pixel de TikTok, y extrae email e Instagram.
Sin píxel = no puede medir ni hacer retargeting, lo cual es un argumento de venta directo.
"""
from __future__ import annotations

import re

import requests

from modules.leads.links import instagram_handle, is_social

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
IGNORED_EMAIL_DOMAINS = ("sentry", "wixpress", "example.", "domain.", "email.com")


def check(website: str) -> dict:
    if not website or is_social(website):  # un perfil de Facebook/Instagram no es su web
        return {}
    url = website if website.startswith("http") else f"https://{website}"
    try:
        html = requests.get(url, headers=HEADERS, timeout=15).text
    except requests.RequestException:
        return {}

    emails = [
        e for e in dict.fromkeys(EMAIL_RE.findall(html))
        if not any(d in e.lower() for d in IGNORED_EMAIL_DOMAINS) and not e.lower().endswith((".png", ".jpg", ".webp"))
    ]

    return {
        "has_meta_pixel": int("connect.facebook.net" in html or "fbq(" in html),
        "has_google_tag": int("googletagmanager.com" in html or "gtag(" in html),
        "has_tiktok_pixel": int("analytics.tiktok.com" in html or "ttq.load" in html),
        "email": emails[0] if emails else None,
        "instagram": instagram_handle(html),
    }
