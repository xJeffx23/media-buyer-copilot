---
name: fitness
description: Busca y califica leads del nicho Gimnasios boutique, CrossFit, entrenadores (tier B). Uso /fitness [no-ai] [maps|ads|web ...]
argument-hint: "[no-ai] [maps|ads|web ...]"
disable-model-invocation: true
---

# Leads: Gimnasios boutique, CrossFit, entrenadores (tier B)

- Búsqueda en Maps: gimnasio, crossfit, estudio de pilates, entrenador personal
- Ad Library: clase gratis, reto 30 días, pilates reformer
- Pitch: Ofertas de prueba que llenan el estudio en semanas.

## Pasos

1. Arma el comando a partir de los argumentos: `$ARGUMENTS`
   - Base: `.venv/bin/python main.py leads --niche fitness`
   - Si incluyen `no-ai` → agrega `--no-ai`.
   - Si incluyen alguna de `maps`, `ads`, `web` → agrega `--source` con esas fuentes.
2. Antes de correr, avisa cuántas búsquedas de Maps hará (ciudades en `config/settings.yaml` × `max_places_per_search`) porque gasta crédito de Apify. Si sin `no-ai` falta `ANTHROPIC_API_KEY` en `.env`, dilo y sugiere `no-ai`.
3. Córrelo desde la raíz del proyecto.
4. Abre el CSV más reciente de `reports/` y resume los 10 mejores leads de `fitness`: nombre, score, contacto y, si existe, la mayor oportunidad que detectó la IA.
