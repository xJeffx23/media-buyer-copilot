"""Base de datos local (SQLite). Fácil de migrar a Supabase/Postgres más adelante."""
from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from core.config import DATA_DIR

DB_PATH = DATA_DIR / "copilot.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id              TEXT PRIMARY KEY,     -- clave estable: sitio web, página de FB o place id
    source          TEXT,                 -- google_maps | meta_ads
    niche           TEXT,
    name            TEXT,
    city            TEXT,
    phone           TEXT,
    email           TEXT,
    website         TEXT,
    instagram       TEXT,
    facebook_page   TEXT,
    rating          REAL,
    reviews         INTEGER,
    active_ads      INTEGER,
    ad_formats      TEXT,                 -- json: {"image": 3, "video": 1}
    oldest_ad_days  INTEGER,
    has_meta_pixel  INTEGER,
    has_google_tag  INTEGER,
    has_tiktok_pixel INTEGER,
    score           INTEGER,
    ai_diagnosis    TEXT,
    ai_message      TEXT,
    status          TEXT DEFAULT 'nuevo', -- nuevo | contactado | respondió | reunión | cliente | descartado
    raw             TEXT,
    created_at      TEXT,
    updated_at      TEXT
);
CREATE TABLE IF NOT EXISTS ig_snapshots (
    taken_at    TEXT PRIMARY KEY,
    username    TEXT,
    followers   INTEGER,
    media_count INTEGER,
    raw         TEXT
);
"""


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def upsert_lead(conn: sqlite3.Connection, lead: dict) -> None:
    """Inserta o fusiona un lead: los campos nuevos no vacíos sobrescriben a los viejos."""
    existing = conn.execute("SELECT * FROM leads WHERE id = ?", (lead["id"],)).fetchone()
    merged = dict(existing) if existing else {"created_at": now(), "status": "nuevo"}
    for k, v in lead.items():
        if v not in (None, "", [], {}):
            merged[k] = json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
    merged["updated_at"] = now()
    cols = ", ".join(merged)
    marks = ", ".join("?" for _ in merged)
    conn.execute(f"INSERT OR REPLACE INTO leads ({cols}) VALUES ({marks})", list(merged.values()))
    conn.commit()


def export_csv(conn: sqlite3.Connection, path: Path, query: str = "SELECT * FROM leads ORDER BY score DESC") -> Path:
    rows = conn.execute(query).fetchall()
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        if rows:
            writer = csv.writer(f)
            writer.writerow([c for c in rows[0].keys() if c != "raw"])
            for r in rows:
                writer.writerow([r[c] for c in r.keys() if c != "raw"])
    return path
