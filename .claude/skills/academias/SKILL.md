---
name: academias
description: Busca y califica leads del nicho Academias y escuelas (idiomas, oficios, cursos presenciales) (tier B). Uso /academias [no-ai] [maps|ads|web ...]
argument-hint: "[no-ai] [maps|ads|web ...]"
disable-model-invocation: true
---

# Leads: Academias y escuelas (idiomas, oficios, cursos presenciales) (tier B)

- Búsqueda en Maps: academia de inglés, escuela de barbería, academia de maquillaje
- Ad Library: inscripciones abiertas, curso, academia
- Pitch: Llenar cohortes antes de la fecha de inicio.

## Pasos

1. Arma el comando a partir de los argumentos: `$ARGUMENTS`
   - Base: `.venv/bin/python main.py leads --niche academias`
   - Si incluyen `no-ai` → agrega `--no-ai`.
   - Si incluyen alguna de `maps`, `ads`, `web` → agrega `--source` con esas fuentes.
2. Antes de correr, avisa cuántas búsquedas de Maps hará (ciudades en `config/settings.yaml` × `max_places_per_search`) porque gasta crédito de Apify. Si sin `no-ai` falta `ANTHROPIC_API_KEY` en `.env`, dilo y sugiere `no-ai`.
3. Córrelo desde la raíz del proyecto.
4. Abre el CSV más reciente de `reports/` y resume los 10 mejores leads de `academias`: nombre, score, contacto y, si existe, la mayor oportunidad que detectó la IA.
