---
name: salud-especialistas
description: Busca y califica leads del nicho Especialistas médicos (dermatología, nutrición, fisioterapia) (tier B). Uso /salud-especialistas [no-ai] [maps|ads|web ...]
argument-hint: "[no-ai] [maps|ads|web ...]"
disable-model-invocation: true
---

# Leads: Especialistas médicos (dermatología, nutrición, fisioterapia) (tier B)

- Búsqueda en Maps: dermatólogo, nutriólogo, fisioterapia
- Ad Library: agenda tu cita, consulta, nutrición
- Pitch: Agenda llena con campañas locales de citas.

## Pasos

1. Arma el comando a partir de los argumentos: `$ARGUMENTS`
   - Base: `.venv/bin/python main.py leads --niche salud_especialistas`
   - Si incluyen `no-ai` → agrega `--no-ai`.
   - Si incluyen alguna de `maps`, `ads`, `web` → agrega `--source` con esas fuentes.
2. Antes de correr, avisa cuántas búsquedas de Maps hará (ciudades en `config/settings.yaml` × `max_places_per_search`) porque gasta crédito de Apify. Si sin `no-ai` falta `ANTHROPIC_API_KEY` en `.env`, dilo y sugiere `no-ai`.
3. Córrelo desde la raíz del proyecto.
4. Abre el CSV más reciente de `reports/` y resume los 10 mejores leads de `salud_especialistas`: nombre, score, contacto y, si existe, la mayor oportunidad que detectó la IA.
