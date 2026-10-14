"""Carga de configuración (YAML) y secretos (.env)."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"

load_dotenv(ROOT / ".env")


@lru_cache
def settings() -> dict:
    with open(ROOT / "config" / "settings.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache
def niches() -> list[dict]:
    with open(ROOT / "config" / "niches.yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f)["niches"]
    for n in data:
        n["priority"] = sum(n["scores"].values())
    return sorted(data, key=lambda n: n["priority"], reverse=True)


def env(name: str, required: bool = True) -> str | None:
    value = os.getenv(name) or None
    if required and not value:
        raise SystemExit(f"Falta la variable {name} en .env (mira .env.example)")
    return value
