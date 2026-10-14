"""Diagnóstico personalizado y borrador de mensaje con IA para los mejores leads.

Los mensajes son BORRADORES: revísalos y envíalos tú. El envío masivo automático
de DMs en Instagram hace que Meta bloquee la cuenta.
"""
from __future__ import annotations

import json

from pydantic import BaseModel, Field

from core.ai import ask_structured
from core.config import settings


class LeadAnalysis(BaseModel):
    fit_score: int = Field(description="1-10: qué tan buen prospecto es para servicios de media buying")
    observations: list[str] = Field(description="2-3 observaciones concretas y verificables sobre su marketing actual")
    opportunity: str = Field(description="La mayor oportunidad de mejora en una frase")
    dm_message: str = Field(description="DM corto para Instagram (máx. 450 caracteres)")
    email_subject: str
    email_body: str = Field(description="Email en frío corto (máx. 120 palabras)")


SYSTEM = """Eres un media buyer senior que prepara prospección en frío para {name}, que ofrece: {service}.

Reglas para los mensajes:
- Escribe en {language}, tono cercano y profesional, sin sonar a plantilla ni a vendedor agresivo.
- Abre con una observación específica del negocio (algo que solo diría alguien que revisó sus anuncios o su web).
- Nada de promesas de resultados concretos ni cifras inventadas.
- Una sola llamada a la acción de bajo compromiso (por ejemplo, "¿te mando un análisis de 3 puntos por aquí?").
- Basa las observaciones SOLO en los datos dados. Si un dato falta, no lo supongas."""


def analyze(lead: dict, niche: dict, reasons: list[str]) -> LeadAnalysis:
    me = settings()["me"]
    data = {k: v for k, v in lead.items() if k not in ("ai_diagnosis", "ai_message") and v not in (None, "")}
    if isinstance(data.get("raw"), str):
        data["raw"] = json.loads(data["raw"])
    prompt = (
        f"Nicho: {niche['name']}\nÁngulo de venta sugerido: {niche['pitch']}\n"
        f"Señales detectadas: {'; '.join(reasons)}\n\n"
        f"Datos del negocio:\n{json.dumps(data, ensure_ascii=False, indent=2)}"
    )
    return ask_structured(SYSTEM.format(**me), prompt, LeadAnalysis)
