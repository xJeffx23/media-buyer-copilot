"""Atajo para ejecutar actores de Apify y obtener sus resultados."""
from __future__ import annotations

from apify_client import ApifyClient

from core.config import env

_client: ApifyClient | None = None


def run_actor(actor_id: str, run_input: dict) -> list[dict]:
    global _client
    if _client is None:
        _client = ApifyClient(env("APIFY_TOKEN"))
    run = _client.actor(actor_id).call(run_input=run_input)
    if not run:
        return []
    return list(_client.dataset(run.default_dataset_id).iterate_items())
