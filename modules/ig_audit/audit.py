"""Auditoría semanal de tu Instagram: métricas propias + comparación con referentes + plan de acción."""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from statistics import mean

from core import storage
from core.ai import ask_text
from core.config import env, settings
from core.notify import save_report, telegram
from modules.ig_audit import competitors, instagram_api as ig

DAYS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]

SYSTEM = """Eres un estratega de crecimiento en Instagram auditando la cuenta de {name}, un {service}.
Objetivo doble: ganar seguidores calificados y conseguir clientes (negocios que quieren vender más con anuncios).
Escribe en {language}. Basa cada conclusión en los números dados; si un dato falta, dilo en vez de suponer."""

PROMPT = """Datos de la cuenta:

{data}

Entrega una auditoría en markdown:

## Resumen (3 líneas)
## Perfil
Bio, nombre, enlace: ¿se entiende en 3 segundos qué ofrece y para quién? Propón una bio mejorada (2 opciones).
## Qué funciona y qué no
Formatos, temas y horarios, apoyado en las métricas (alcance, guardados, compartidos, engagement).
## Comparación con referentes
Qué hacen ellos que aquí no se hace.
## Evolución
Cambio de seguidores respecto a auditorías anteriores (si hay historial).
## Plan de la próxima semana
Exactamente 3 acciones concretas y medibles, y un calendario de 5 publicaciones con formato y tema.
"""


def post_stats(posts: list[dict]) -> dict:
    for p in posts:
        p["insights"] = ig.media_insights(p["id"])
        reach = p["insights"].get("reach") or 0
        inter = p["insights"].get("total_interactions") or (
            (p.get("like_count") or 0) + (p.get("comments_count") or 0)
            + (p["insights"].get("saved") or 0) + (p["insights"].get("shares") or 0)
        )
        p["engagement_rate_pct"] = round(100 * inter / reach, 2) if reach else None
        p["caption"] = (p.get("caption") or "")[:200]

    def avg(group: list[dict], key: str):
        vals = [x["insights"].get(key) or 0 for x in group]
        return round(mean(vals)) if vals else 0

    by_format, by_day = defaultdict(list), defaultdict(list)
    for p in posts:
        by_format[p.get("media_product_type") or p.get("media_type")].append(p)
        dt = datetime.fromisoformat(p["timestamp"].replace("+0000", "+00:00"))
        by_day[DAYS[dt.weekday()]].append(p)

    ranked = sorted([p for p in posts if p["insights"].get("reach")], key=lambda p: p["insights"]["reach"], reverse=True)
    slim = lambda p: {k: p.get(k) for k in ("timestamp", "media_product_type", "caption", "insights", "engagement_rate_pct", "permalink")}
    return {
        "by_format": {f: {"posts": len(g), "avg_reach": avg(g, "reach"), "avg_saved": avg(g, "saved"),
                          "avg_shares": avg(g, "shares")} for f, g in by_format.items()},
        "by_weekday": {d: {"posts": len(g), "avg_reach": avg(g, "reach")} for d, g in by_day.items()},
        "top_5": [slim(p) for p in ranked[:5]],
        "bottom_5": [slim(p) for p in ranked[-5:]],
    }


def run() -> None:
    cfg, me = settings()["ig_audit"], settings()["me"]
    print("Leyendo tu cuenta de Instagram…")
    prof = ig.profile()
    posts = ig.media(cfg["posts_to_analyze"])

    conn = storage.connect()
    history = [dict(r) for r in conn.execute(
        "SELECT taken_at, followers, media_count FROM ig_snapshots ORDER BY taken_at DESC LIMIT 8")]
    conn.execute("INSERT OR REPLACE INTO ig_snapshots VALUES (?, ?, ?, ?, ?)",
                 (storage.now(), prof.get("username"), prof.get("followers_count"), prof.get("media_count"),
                  json.dumps(prof, ensure_ascii=False)))
    conn.commit()

    data = {
        "profile": prof,
        "follower_history": history,
        "audience": ig.follower_demographics(),
        "posts": post_stats(posts),
        "competitors": competitors.analyze(cfg["competitors"]) if env("APIFY_TOKEN", required=False) else [],
    }
    print("Generando auditoría…")
    report = ask_text(SYSTEM.format(**me), PROMPT.format(data=json.dumps(data, ensure_ascii=False, indent=1)))
    path = save_report("auditoria_instagram", report)
    print(f"Reporte: {path}")
    telegram(report)
