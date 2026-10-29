---
name: inmobiliaria
description: Busca y califica leads del nicho Inmobiliarias y desarrolladores (tier A). Uso /inmobiliaria [no-ai] [maps|ads|web ...]
argument-hint: "[no-ai] [maps|ads|web ...]"
disable-model-invocation: true
---

# Leads: Inmobiliarias y desarrolladores (tier A)

- Búsqueda en Maps: inmobiliaria, agencia inmobiliaria, desarrollos inmobiliarios
- Ad Library: departamentos en preventa, casas en venta, invierte en
- Pitch: Leads calificados con formularios instantáneos y filtros de presupuesto.

## Pasos

1. Arma el comando a partir de los argumentos: `$ARGUMENTS`
   - Base: `.venv/bin/python main.py leads --niche inmobiliaria`
   - Si incluyen `no-ai` → agrega `--no-ai`.
   - Si incluyen alguna de `maps`, `ads`, `web` → agrega `--source` con esas fuentes.
2. Antes de correr, avisa cuántas búsquedas de Maps hará (ciudades en `config/settings.yaml` × `max_places_per_search`) porque gasta crédito de Apify. Si sin `no-ai` falta `ANTHROPIC_API_KEY` en `.env`, dilo y sugiere `no-ai`.
3. Córrelo desde la raíz del proyecto.
4. Abre el CSV más reciente de `reports/` y resume los 10 mejores leads de `inmobiliaria`: nombre, score, contacto y, si existe, la mayor oportunidad que detectó la IA.
