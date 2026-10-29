---
name: servicios-hogar
description: Busca y califica leads del nicho Servicios para el hogar (paneles solares, remodelación, HVAC) (tier B). Uso /servicios-hogar [no-ai] [maps|ads|web ...]
argument-hint: "[no-ai] [maps|ads|web ...]"
disable-model-invocation: true
---

# Leads: Servicios para el hogar (paneles solares, remodelación, HVAC) (tier B)

- Búsqueda en Maps: paneles solares, remodelaciones, aire acondicionado instalación
- Ad Library: paneles solares, cotización gratis, remodelación
- Pitch: Cotizaciones locales con formularios y llamadas directas.

## Pasos

1. Arma el comando a partir de los argumentos: `$ARGUMENTS`
   - Base: `.venv/bin/python main.py leads --niche servicios_hogar`
   - Si incluyen `no-ai` → agrega `--no-ai`.
   - Si incluyen alguna de `maps`, `ads`, `web` → agrega `--source` con esas fuentes.
2. Antes de correr, avisa cuántas búsquedas de Maps hará (ciudades en `config/settings.yaml` × `max_places_per_search`) porque gasta crédito de Apify. Si sin `no-ai` falta `ANTHROPIC_API_KEY` en `.env`, dilo y sugiere `no-ai`.
3. Córrelo desde la raíz del proyecto.
4. Abre el CSV más reciente de `reports/` y resume los 10 mejores leads de `servicios_hogar`: nombre, score, contacto y, si existe, la mayor oportunidad que detectó la IA.
