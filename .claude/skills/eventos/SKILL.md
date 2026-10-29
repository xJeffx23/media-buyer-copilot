---
name: eventos
description: Busca y califica leads del nicho Salones de eventos, bodas, fotógrafos (tier C). Uso /eventos [no-ai] [maps|ads|web ...]
argument-hint: "[no-ai] [maps|ads|web ...]"
disable-model-invocation: true
---

# Leads: Salones de eventos, bodas, fotógrafos (tier C)

- Búsqueda en Maps: salón de eventos, wedding planner, fotógrafo de bodas
- Ad Library: boda, eventos, fotografía
- Pitch: Llenar el calendario de temporada alta con anticipación.

## Pasos

1. Arma el comando a partir de los argumentos: `$ARGUMENTS`
   - Base: `.venv/bin/python main.py leads --niche eventos`
   - Si incluyen `no-ai` → agrega `--no-ai`.
   - Si incluyen alguna de `maps`, `ads`, `web` → agrega `--source` con esas fuentes.
2. Antes de correr, avisa cuántas búsquedas de Maps hará (ciudades en `config/settings.yaml` × `max_places_per_search`) porque gasta crédito de Apify. Si sin `no-ai` falta `ANTHROPIC_API_KEY` en `.env`, dilo y sugiere `no-ai`.
3. Córrelo desde la raíz del proyecto.
4. Abre el CSV más reciente de `reports/` y resume los 10 mejores leads de `eventos`: nombre, score, contacto y, si existe, la mayor oportunidad que detectó la IA.
