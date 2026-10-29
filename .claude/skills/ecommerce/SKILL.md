---
name: ecommerce
description: Busca y califica leads del nicho E-commerce / marcas DTC (tier B). Uso /ecommerce [no-ai] [maps|ads|web ...]
argument-hint: "[no-ai] [maps|ads|web ...]"
disable-model-invocation: true
---

# Leads: E-commerce / marcas DTC (tier B)

- Búsqueda en Maps: —
- Ad Library: envío gratis, compra ahora, tienda online
- Pitch: Escalar ROAS con testing de creativos y catálogo dinámico.

Este nicho no tiene `search_terms`: no aparece en Google Maps, así que solo rinde con la fuente `ads`.

## Pasos

1. Arma el comando a partir de los argumentos: `$ARGUMENTS`
   - Base: `.venv/bin/python main.py leads --niche ecommerce`
   - Si incluyen `no-ai` → agrega `--no-ai`.
   - Si incluyen alguna de `maps`, `ads`, `web` → agrega `--source` con esas fuentes.
2. Antes de correr, avisa cuántas búsquedas de Maps hará (ciudades en `config/settings.yaml` × `max_places_per_search`) porque gasta crédito de Apify. Si sin `no-ai` falta `ANTHROPIC_API_KEY` en `.env`, dilo y sugiere `no-ai`.
3. Córrelo desde la raíz del proyecto.
4. Abre el CSV más reciente de `reports/` y resume los 10 mejores leads de `ecommerce`: nombre, score, contacto y, si existe, la mayor oportunidad que detectó la IA.
