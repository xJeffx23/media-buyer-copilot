"""Instagram API con Instagram Login (funciona con cuentas de Creador y Empresa,
no requiere página de Facebook). Docs: developers.facebook.com/docs/instagram-platform
"""
from __future__ import annotations

import requests

from core.config import env, settings

MEDIA_FIELDS = "id,caption,media_type,media_product_type,timestamp,like_count,comments_count,permalink"
# Las métricas disponibles cambian según el tipo de publicación; se prueban en orden.
MEDIA_METRICS = ["reach,saved,shares,total_interactions,views", "reach,saved,shares,total_interactions", "reach"]


class IGError(Exception):
    pass


def _get(path: str, **params) -> dict:
    version = settings()["ig_audit"]["graph_api_version"]
    r = requests.get(
        f"https://graph.instagram.com/{version}/{path}",
        params={**params, "access_token": env("IG_ACCESS_TOKEN")},
        timeout=30,
    )
    body = r.json()
    if "error" in body:
        raise IGError(body["error"].get("message"))
    return body


def profile() -> dict:
    try:
        return _get("me", fields="user_id,username,name,account_type,biography,website,followers_count,follows_count,media_count")
    except IGError:
        return _get("me", fields="user_id,username,account_type,followers_count,media_count")


def media(limit: int) -> list[dict]:
    posts, page = [], _get("me/media", fields=MEDIA_FIELDS, limit=min(limit, 50))
    while True:
        posts += page.get("data", [])
        nxt = page.get("paging", {}).get("next")
        if len(posts) >= limit or not nxt:
            break
        page = requests.get(nxt, timeout=30).json()
    return posts[:limit]


def media_insights(media_id: str) -> dict:
    for metrics in MEDIA_METRICS:
        try:
            data = _get(f"{media_id}/insights", metric=metrics)["data"]
            return {m["name"]: m["values"][0]["value"] for m in data}
        except IGError:
            continue
    return {}


def follower_demographics() -> dict:
    out = {}
    for breakdown in ("age", "gender", "city", "country"):
        try:
            data = _get("me/insights", metric="follower_demographics", period="lifetime",
                        metric_type="total_value", breakdown=breakdown)["data"]
            results = data[0]["total_value"]["breakdowns"][0]["results"]
            top = sorted(results, key=lambda x: x["value"], reverse=True)[:8]
            out[breakdown] = {r["dimension_values"][0]: r["value"] for r in top}
        except (IGError, KeyError, IndexError):
            continue
    return out
