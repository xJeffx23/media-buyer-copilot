"""Base de datos local (SQLite). Fácil de migrar a Supabase/Postgres más adelante."""
from __future__ import annotations

import csv
import json
import re
import sqlite3
import unicodedata
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
        if v in (None, "", [], {}):
            continue
        if k == "raw" and isinstance(v, dict) and merged.get("raw"):
            v = {**json.loads(merged["raw"]), **v}  # conserva los datos de la otra fuente
        if k == "source" and merged.get("source") and v not in merged["source"].split("+"):
            v = f"{merged['source']}+{v}"  # google_maps+meta_ads
        merged[k] = json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
    merged["updated_at"] = now()
    cols = ", ".join(merged)
    marks = ", ".join("?" for _ in merged)
    conn.execute(f"INSERT OR REPLACE INTO leads ({cols}) VALUES ({marks})", list(merged.values()))
    conn.commit()


STATUSES = ("nuevo", "contactado", "respondió", "reunión", "cliente", "descartado")


def _simple(text: str | None) -> str:
    """Nombre sin tildes, mayúsculas ni signos, para comparar el mismo negocio entre fuentes."""
    t = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()
    t = re.sub(r"\b(costa rica|cr|s\.?a\.?)\b", " ", t)
    return re.sub(r"[^a-z0-9]+", "", t)


def find_same_business(conn: sqlite3.Connection, lead: dict) -> str | None:
    """Busca un lead ya guardado del mismo negocio (mismo Instagram o mismo nombre) en el mismo nicho."""
    if lead.get("instagram"):
        row = conn.execute("SELECT id FROM leads WHERE lower(instagram) = lower(?) AND niche = ?",
                           (lead["instagram"], lead["niche"])).fetchone()
        if row:
            return row["id"]
    name = _simple(lead.get("name"))
    if len(name) < 5:
        return None
    for row in conn.execute("SELECT id, name FROM leads WHERE niche = ? AND id != ?", (lead["niche"], lead["id"])):
        if _simple(row["name"]) == name:
            return row["id"]
    return None


def import_status(conn: sqlite3.Connection, path: Path) -> int:
    """Lee el CSV que editaste a mano y guarda en la base los cambios de 'status'.

    Sin esto, la siguiente corrida regeneraba el CSV desde la base y borraba tus cambios.
    Acepta el CSV guardado por Excel (separador ; o , y codificación de Windows).
    """
    if not path.exists():
        return 0
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    sample = text[:5000]
    delimiter = ";" if sample.count(";") > sample.count(",") else ","
    changed = 0
    for row in csv.DictReader(text.splitlines(), delimiter=delimiter):
        lead_id, status = (row.get("id") or "").strip(), (row.get("status") or "").strip().lower()
        if not lead_id or not status:
            continue
        if status not in STATUSES:
            print(f"  ! status '{status}' no válido para {lead_id} (usa: {', '.join(STATUSES)})")
            continue
        cur = conn.execute("UPDATE leads SET status = ?, updated_at = ? WHERE id = ? AND status != ?",
                           (status, now(), lead_id, status))
        changed += cur.rowcount
    conn.commit()
    return changed


def latest_leads_csv(reports_dir: Path) -> Path | None:
    files = sorted(reports_dir.glob("*_leads.csv"))
    return files[-1] if files else None


def export_csv(conn: sqlite3.Connection, path: Path, query: str = "SELECT * FROM leads ORDER BY score DESC") -> Path:
    rows = conn.execute(query).fetchall()
    path.parent.mkdir(exist_ok=True)
    # utf-8-sig: Excel abre bien las tildes
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        if rows:
            writer = csv.writer(f)
            writer.writerow([c for c in rows[0].keys() if c != "raw"])
            for r in rows:
                writer.writerow([r[c] for c in r.keys() if c != "raw"])
    return path
