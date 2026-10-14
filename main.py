"""Media Buyer Copilot — punto de entrada.

Ejemplos:
  python main.py nichos
  python main.py leads                      # tiers por defecto de settings.yaml
  python main.py leads --tier A B --no-ai
  python main.py leads --niche dental --source ads web
  python main.py tendencias
  python main.py instagram
"""
from __future__ import annotations

import argparse


def cmd_nichos(_args) -> None:
    from core.config import niches

    for n in niches():
        print(f"[{n['tier']}] {n['priority']:>2} pts  {n['id']:<20} {n['name']}")


def cmd_leads(args) -> None:
    from modules.leads import pipeline

    pipeline.run(tiers=args.tier, niche_ids=args.niche, sources=tuple(args.source), use_ai=not args.no_ai)


def cmd_tendencias(_args) -> None:
    from modules.trends import radar

    radar.run()


def cmd_instagram(_args) -> None:
    from modules.ig_audit import audit

    audit.run()


def main() -> None:
    parser = argparse.ArgumentParser(description="Copiloto de IA para media buyers")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("nichos", help="Lista los nichos priorizados").set_defaults(func=cmd_nichos)

    p = sub.add_parser("leads", help="Busca y califica prospectos")
    p.add_argument("--tier", nargs="+", choices=["A", "B", "C"])
    p.add_argument("--niche", nargs="+", help="ids de config/niches.yaml")
    p.add_argument("--source", nargs="+", choices=["maps", "ads", "web"], default=["maps", "ads", "web"])
    p.add_argument("--no-ai", action="store_true", help="Solo scoring heurístico, sin costo de IA")
    p.set_defaults(func=cmd_leads)

    sub.add_parser("tendencias", help="Radar de tendencias e ideas de contenido").set_defaults(func=cmd_tendencias)
    sub.add_parser("instagram", help="Auditoría de tu cuenta de Instagram").set_defaults(func=cmd_instagram)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
