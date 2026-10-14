"""Radar semanal: junta lo que se mueve en el mundo y lo convierte en ideas de contenido."""
from __future__ import annotations

import json

from core.ai import ask_text
from core.config import env, settings
from core.notify import save_report, telegram
from modules.trends.sources import feeds, winning_ads, youtube

SYSTEM = """Eres el estratega de contenido de {name}, un {service} que está construyendo su marca personal.
Su objetivo: crecer en Instagram y atraer negocios que quieran vender más con anuncios.
Escribe en {language}. Sé concreto y accionable; nada de consejos genéricos."""

PROMPT = """Estos son los datos recolectados esta semana (titulares, tendencias y anuncios de referencia):

{data}

Pilares de contenido de la marca:
{pillars}

Entrega un reporte en markdown con estas secciones:

## 1. Lo que se está moviendo (5 min de lectura)
Las 5-7 tendencias más relevantes (marketing, ads, redes, cultura) y por qué importan para un media buyer.

## 2. Ideas de contenido (10 ideas)
Reparte las ideas entre los pilares. Para cada una:
- **Pilar** y **formato** (reel, carrusel, historia, post)
- **Hook** (primeros 3 segundos / primera línea)
- **Guion corto** (3-6 bullets)
- **CTA**

## 3. Anuncios propios para conseguir clientes (3 ideas)
Inspirados en los anuncios que más tiempo llevan activos. Ángulo, hook, copy y a qué nicho apuntan.

## 4. Trend para subirse esta semana
Una tendencia viral concreta y cómo adaptarla al nicho de ads sin que se vea forzado.
"""


def collect() -> dict[str, list[dict]]:
    cfg = settings()["trends"]
    data = {
        "reddit": feeds.reddit(cfg["subreddits"]),
        "newsletters": feeds.rss(cfg["rss_feeds"]),
        "google_trends": feeds.google_trends(cfg["region"]),
        "youtube_trending": youtube.trending(cfg["region"]),
        "youtube_topics": youtube.search_recent(cfg["youtube_queries"]),
    }
    if env("APIFY_TOKEN", required=False):
        data["winning_ads"] = winning_ads.longest_running(["agencia de marketing", "media buyer", "meta ads"])
    for k, v in data.items():
        print(f"  {k}: {len(v)} items")
    return data


def run() -> None:
    me = settings()["me"]
    print("Recolectando tendencias…")
    data = collect()
    report = ask_text(
        SYSTEM.format(**me),
        PROMPT.format(
            data=json.dumps(data, ensure_ascii=False, indent=1),
            pillars="\n".join(f"- {p}" for p in settings()["trends"]["content_pillars"]),
        ),
    )
    path = save_report("radar_tendencias", report)
    print(f"Reporte: {path}")
    telegram(report)
