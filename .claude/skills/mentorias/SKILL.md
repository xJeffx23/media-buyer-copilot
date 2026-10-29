---
name: mentorias
description: Busca y califica leads del nicho Mentorías, coaches e infoproductos (tier A). Uso /mentorias [no-ai] [maps|ads|web ...]
argument-hint: "[no-ai] [maps|ads|web ...]"
disable-model-invocation: true
---

# Leads: Mentorías, coaches e infoproductos (tier A)

- Búsqueda en Maps: —
- Ad Library: mentoría, masterclass gratis, programa de coaching, webinar gratuito
- Pitch: Embudos de webinar/VSL y escalado de creativos que ya convierten.

Este nicho no tiene `search_terms`: no aparece en Google Maps, así que solo rinde con la fuente `ads`.

## Pasos

1. Arma el comando a partir de los argumentos: `$ARGUMENTS`
   - Base: `.venv/bin/python main.py leads --niche mentorias`
   - Si incluyen `no-ai` → agrega `--no-ai`.
   - Si incluyen alguna de `maps`, `ads`, `web` → agrega `--source` con esas fuentes.
2. Antes de correr, avisa cuántas búsquedas de Maps hará (ciudades en `config/settings.yaml` × `max_places_per_search`) porque gasta crédito de Apify. Si sin `no-ai` falta `ANTHROPIC_API_KEY` en `.env`, dilo y sugiere `no-ai`.
3. Córrelo desde la raíz del proyecto.
4. Abre el CSV más reciente de `reports/` y resume los 10 mejores leads de `mentorias`: nombre, score, contacto y, si existe, la mayor oportunidad que detectó la IA.
