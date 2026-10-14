"""Salidas: guardar reportes en markdown y (opcional) enviarlos por Telegram."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import requests

from core.config import REPORTS_DIR, env


def save_report(name: str, content: str) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    path = REPORTS_DIR / f"{date.today().isoformat()}_{name}.md"
    path.write_text(content, encoding="utf-8")
    return path


def telegram(text: str) -> None:
    """Envía un mensaje si TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID están configurados."""
    token = env("TELEGRAM_BOT_TOKEN", required=False)
    chat_id = env("TELEGRAM_CHAT_ID", required=False)
    if not (token and chat_id):
        return
    # Telegram limita los mensajes a 4096 caracteres
    for i in range(0, len(text), 4000):
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text[i : i + 4000]},
            timeout=30,
        )
