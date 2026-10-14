"""Cliente de Claude compartido por todos los módulos."""
from __future__ import annotations

from typing import TypeVar

import anthropic
from pydantic import BaseModel

from core.config import settings

T = TypeVar("T", bound=BaseModel)

_client: anthropic.Anthropic | None = None

# Si el modelo principal rechaza una petición, la API la reintenta con el modelo
# de respaldo recomendado por Anthropic dentro de la misma llamada.
_FALLBACK = {
    "betas": ["server-side-fallback-2026-07-01"],
    "extra_body": {"fallbacks": "default"},
}


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()  # lee ANTHROPIC_API_KEY del entorno
    return _client


def _common() -> dict:
    cfg = settings()["ai"]
    return {
        "model": cfg["model"],
        "output_config": {"effort": cfg.get("effort", "medium")},
        **_FALLBACK,
    }


def ask_structured(system: str, prompt: str, schema: type[T], max_tokens: int = 16000) -> T:
    """Pide a Claude una respuesta validada contra un modelo Pydantic."""
    response = client().beta.messages.parse(
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
        output_format=schema,
        **_common(),
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("Claude rechazó la petición")
    return response.parsed_output


def ask_text(system: str, prompt: str, max_tokens: int = 64000) -> str:
    """Respuesta libre en texto (markdown). Usa streaming para salidas largas."""
    with client().beta.messages.stream(
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
        **_common(),
    ) as stream:
        message = stream.get_final_message()
    if message.stop_reason == "refusal":
        raise RuntimeError("Claude rechazó la petición")
    return "".join(b.text for b in message.content if b.type == "text")
