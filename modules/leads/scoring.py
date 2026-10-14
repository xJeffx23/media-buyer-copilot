"""Puntuación heurística de leads (0-100), sin costo de IA.

Ajusta los pesos según lo que veas que convierte mejor en tus cierres.
"""
from __future__ import annotations

import json

TIER_POINTS = {"A": 25, "B": 15, "C": 5}


def score(lead: dict, niche: dict) -> tuple[int, list[str]]:
    pts = TIER_POINTS.get(niche["tier"], 0)
    reasons = [f"Nicho tier {niche['tier']}"]

    formats = lead.get("ad_formats") or {}
    if isinstance(formats, str):
        formats = json.loads(formats)
    active = lead.get("active_ads") or 0

    if active:
        pts += 20
        reasons.append(f"Ya invierte en anuncios ({active} activos)")
        if "video" not in formats:
            pts += 10
            reasons.append("No usa video en sus anuncios")
        if active <= 3 and (lead.get("oldest_ad_days") or 0) > 60:
            pts += 10
            reasons.append("Pocos anuncios y viejos: no está testeando creativos")
    elif (lead.get("rating") or 0) >= 4.3 and (lead.get("reviews") or 0) >= 50:
        pts += 15
        reasons.append("Negocio establecido con buenas reseñas que no se ve anunciando")

    if lead.get("website") and lead.get("has_meta_pixel") == 0:
        pts += 10
        reasons.append("Su web no tiene Pixel de Meta")

    if lead.get("email") or lead.get("phone") or lead.get("instagram"):
        pts += 10
        reasons.append("Tiene datos de contacto")

    if (lead.get("reviews") or 0) >= 100:
        pts += 5
        reasons.append("Volumen alto de clientes (100+ reseñas)")

    return min(pts, 100), reasons
