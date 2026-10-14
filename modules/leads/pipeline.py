"""Pipeline completo de leads:
1. Google Maps (negocios locales)  2. Biblioteca de Anuncios de Meta (quién ya anuncia)
3. Revisión de sitio web (píxeles y contacto)  -> scoring -> diagnóstico IA -> CSV
"""
from __future__ import annotations

import json
from datetime import date

from core import storage
from core.config import REPORTS_DIR, niches, settings
from core.notify import telegram
from modules.leads import outreach, scoring
from modules.leads.sources import google_maps, meta_ads, website_check


def select_niches(tiers: list[str] | None, niche_ids: list[str] | None) -> list[dict]:
    all_niches = niches()
    if niche_ids:
        return [n for n in all_niches if n["id"] in niche_ids]
    tiers = tiers or settings()["leads"]["tiers"]
    return [n for n in all_niches if n["tier"] in tiers]


def run(
    tiers: list[str] | None = None,
    niche_ids: list[str] | None = None,
    sources: tuple[str, ...] = ("maps", "ads", "web"),
    use_ai: bool = True,
) -> None:
    cfg = settings()["leads"]
    conn = storage.connect()
    selected = select_niches(tiers, niche_ids)
    print(f"Nichos: {', '.join(n['id'] for n in selected)}")

    for niche in selected:
        found: list[dict] = []
        if "maps" in sources:
            for loc in cfg["locations"]:
                print(f"  [maps] {niche['id']} en {loc}…")
                found += google_maps.search(niche, loc, cfg["max_places_per_search"], settings()["me"]["language"])
        if "ads" in sources:
            print(f"  [ads] {niche['id']} en Ad Library…")
            found += meta_ads.search(niche, cfg["ad_library_country"], cfg["max_ads_per_keyword"])

        for lead in found:
            if "web" in sources and lead.get("website"):
                lead.update({k: v for k, v in website_check.check(lead["website"]).items() if v is not None})
            lead["score"], _ = scoring.score(lead, niche)
            storage.upsert_lead(conn, lead)
        print(f"  {len(found)} leads guardados para {niche['id']}")

    if use_ai:
        enrich_with_ai(conn, cfg["ai_top_n"])

    out = storage.export_csv(conn, REPORTS_DIR / f"{date.today().isoformat()}_leads.csv")
    top = conn.execute("SELECT name, niche, score FROM leads ORDER BY score DESC LIMIT 10").fetchall()
    summary = "Top leads de hoy:\n" + "\n".join(f"- {r['name']} ({r['niche']}): {r['score']}" for r in top)
    print(f"\nCSV: {out}\n{summary}")
    telegram(summary)


def enrich_with_ai(conn, top_n: int) -> None:
    by_id = {n["id"]: n for n in niches()}
    rows = conn.execute(
        "SELECT * FROM leads WHERE ai_diagnosis IS NULL AND status = 'nuevo' ORDER BY score DESC LIMIT ?",
        (top_n,),
    ).fetchall()
    print(f"\nDiagnóstico con IA de {len(rows)} leads…")
    for row in rows:
        lead = dict(row)
        niche = by_id.get(lead["niche"])
        if not niche:
            continue
        _, reasons = scoring.score(lead, niche)
        try:
            a = outreach.analyze(lead, niche, reasons)
        except Exception as e:  # un lead fallido no debe detener el resto
            print(f"  ! {lead['name']}: {e}")
            continue
        storage.upsert_lead(
            conn,
            {
                "id": lead["id"],
                "ai_diagnosis": json.dumps(
                    {"fit": a.fit_score, "observations": a.observations, "opportunity": a.opportunity},
                    ensure_ascii=False,
                ),
                "ai_message": f"DM:\n{a.dm_message}\n\nEMAIL — {a.email_subject}\n{a.email_body}",
            },
        )
        print(f"  ✓ {lead['name']} (fit {a.fit_score}/10)")
