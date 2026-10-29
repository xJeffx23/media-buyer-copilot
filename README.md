# Media Buyer Copilot

Sistema de IA + automatización para un media buyer independiente:

1. **Leads**: encuentra negocios a los que venderles servicios de anuncios, los califica y escribe borradores de mensajes personalizados.
2. **Tendencias**: radar semanal de lo que se mueve en marketing, redes y cultura, convertido en ideas de contenido para tu marca personal.
3. **Instagram**: auditoría semanal de tu cuenta con plan de acción para crecer.

```
config/          niches.yaml (nichos priorizados) · settings.yaml (ciudades, fuentes, competidores)
core/            IA (Claude), Apify, base de datos SQLite, reportes y Telegram
modules/leads/   Google Maps + Biblioteca de Anuncios de Meta + revisión de webs → scoring → IA
modules/trends/  Reddit, newsletters, Google Trends, YouTube, anuncios ganadores → ideas
modules/ig_audit/ Instagram API + perfiles de referencia → auditoría
reports/         Salidas: CSV de leads y reportes en markdown
```

## Instalación

Requiere **Python 3.11+** (en Mac: `brew install python@3.12`).

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # y llena tus claves
```

## Claves que necesitas

| Variable | Para qué | Dónde se obtiene |
|---|---|---|
| `ANTHROPIC_API_KEY` | Todo el análisis con IA | console.anthropic.com → API Keys |
| `APIFY_TOKEN` | Google Maps, Ad Library, perfiles de IG | console.apify.com → Settings → Integrations |
| `IG_ACCESS_TOKEN` | Auditoría de tu Instagram | Ver abajo |
| `YOUTUBE_API_KEY` | Tendencias de YouTube (opcional) | Google Cloud Console → YouTube Data API v3 |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | Recibir reportes en el móvil (opcional) | @BotFather en Telegram |

### Token de Instagram (cuenta de Creador o Empresa)

1. En la app de Instagram: Configuración → Tipo de cuenta → confirma que sea **Creador** o **Empresa**.
2. Entra a developers.facebook.com → Mis apps → Crear app → tipo **Empresa**.
3. Agrega el producto **Instagram** → "API setup with Instagram login".
4. En "Generate access tokens", agrega tu cuenta y genera el token. Pide los permisos `instagram_business_basic` e `instagram_business_manage_insights`.
5. Pega el token en `IG_ACCESS_TOKEN`. Dura 60 días; renuévalo antes de que venza.

## Uso

```bash
python main.py nichos                           # ver nichos priorizados
python main.py leads --no-ai                    # primera prueba barata: sin IA
python main.py leads                            # completo, tiers de settings.yaml
python main.py leads --niche dental --source ads web
python main.py crm                              # guarda los status que editaste en el CSV
python main.py tendencias                       # radar + ideas de contenido
python main.py instagram                        # auditoría de tu cuenta
```

Antes de correr `leads`, edita `config/settings.yaml`: tus ciudades, tu país en `ad_library_country` y tu @ de Instagram.

## Cómo se califica un lead

| Señal | Puntos |
|---|---|
| Nicho tier A / B / C | 25 / 15 / 5 |
| Ya tiene anuncios activos en Meta | +20 |
| …pero sin video | +10 |
| …pocos y viejos (no testea creativos) | +10 |
| No anuncia, pero tiene ≥4.3★ y ≥50 reseñas | +15 |
| Su web no tiene Pixel de Meta | +10 |
| Tiene email, teléfono o Instagram | +10 |
| 100+ reseñas | +5 |

Los `ai_top_n` mejores pasan por Claude, que escribe 2-3 observaciones concretas, la mayor oportunidad, un DM y un email. Todo queda en `reports/AAAA-MM-DD_leads.csv` y en `data/copilot.db`. La columna `status` sirve como mini CRM: cámbiala en el CSV (`nuevo`, `contactado`, `respondió`, `reunión`, `cliente`, `descartado`), guárdalo y corre `python main.py crm`. `leads` también importa esos cambios antes de regenerar el CSV, así que no se pierden.

En la Biblioteca de Anuncios, `ad_page_categories` y `ad_exclude_cta` de `niches.yaml` descartan tiendas y proveedores que no son el negocio objetivo, y `max_page_likes` descarta marcas enormes.

## Costos aproximados

- **Apify**: el plan gratis trae $5/mes de crédito. Google Maps cuesta unos $4 por 1000 lugares.
- **Claude**: cada diagnóstico de lead y cada reporte cuesta centavos. Ajusta `ai.effort` y `leads.ai_top_n` para controlarlo.

## Reglas importantes

- **No automatices el envío de DMs.** Meta bloquea las cuentas que envían mensajes masivos. El sistema prepara los mensajes y tú los envías.
- Usa solo datos públicos de negocios. Si prospectas en la UE, respeta el RGPD (base legal e identificación clara del remitente).
- Los nombres de campos de los actores de Apify pueden cambiar. Si una fuente devuelve 0 resultados, revisa el dataset del run en la consola de Apify.

## Automatización

`.github/workflows/weekly.yml` corre `tendencias` e `instagram` cada lunes y guarda los reportes como artefactos (y los manda por Telegram si lo configuraste). Agrega tus claves en GitHub → Settings → Secrets and variables → Actions.

## Próximos pasos

- [ ] Migrar SQLite → Supabase para tener histórico en la nube y un panel
- [ ] Dashboard en Streamlit con los leads y su estado
- [ ] TikTok Creative Center como fuente de tendencias
- [ ] Generación de borradores de creativos (imagen/video) a partir de las ideas
- [ ] Seguimiento de respuestas de prospectos
