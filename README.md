# Observatorio Financiero Argentino

Pipeline de ingesta y análisis de indicadores económicos argentinos.
Proyecto didáctico: scrapea cotizaciones de dólar a intervalos regulares y las
persiste en PostgreSQL.

## Estado actual (v0.2.0)

- Schema versionado con dos tablas: `fuentes` (catálogo) y `cotizaciones` (datos).
- Scraper de [Bluelytics](https://api.bluelytics.com.ar/v2/latest) que ingiere
  dólar oficial y dólar blue.
- Validación de respuesta con `pydantic` (errores explícitos si la API cambia).
- Logs estructurados con `loguru`.
- Persistencia idempotente (`ON CONFLICT DO NOTHING` por `fuente_id, ts`).
- Schedule via cron cada 15 minutos.

## Stack

| Capa | Herramienta |
|---|---|
| Lenguaje | Python 3.11+ |
| Manager de paquetes | [uv](https://docs.astral.sh/uv/) |
| Base de datos | PostgreSQL 16 |
| Cliente Postgres | psycopg 3 |
| HTTP | requests |
| Validación | pydantic |
| Logs | loguru |
| Lint + format | ruff |
| Tests | pytest (todavía sin tests escritos) |

## Setup desde cero

Pensado para Linux / WSL2 con Ubuntu 24.04+.

### 1. Dependencias del sistema

```bash
sudo apt update
sudo apt install -y postgresql-16 postgresql-contrib
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### 2. Base de datos

```bash
# Crear rol y database (ajustá la password)
sudo -u postgres psql <<EOF
CREATE USER observatorio WITH PASSWORD 'TU_PASSWORD_FUERTE';
CREATE DATABASE observatorio_dev OWNER observatorio;
EOF

# Aplicar schema y seed
export DATABASE_URL="postgresql://observatorio:TU_PASSWORD_FUERTE@localhost:5432/observatorio_dev"
psql "$DATABASE_URL" -f sql/01_schema.sql
psql "$DATABASE_URL" -f sql/seeds/01_fuentes.sql
```

### 3. Variables de entorno

```bash
cp .env.example .env
# Editá .env con tu DATABASE_URL real
```

### 4. Dependencias Python

```bash
uv sync
```

Esto crea `.venv/` e instala todo lo declarado en `pyproject.toml` + `uv.lock`.

### 5. Verificar conexión

```bash
uv run python -c "
from observatorio.db import get_connection
with get_connection() as conn:
    print(conn.execute('SELECT version()').fetchone()[0])
"
```

### 6. Correr el scraper una vez

```bash
uv run python -m observatorio.ingesta.dolares
```

### 7. Programarlo con cron

```bash
crontab -e
# Sumar:
*/15 * * * * /ruta/absoluta/al/proyecto/scripts/run_ingesta.sh >> /ruta/absoluta/al/proyecto/logs/ingesta.log 2>&1
```

## Estructura

```
observatorio/
├── pyproject.toml          # config del proyecto y deps
├── .env.example            # plantilla de variables (copiá a .env)
├── README.md
├── src/observatorio/
│   ├── db.py               # helper get_connection()
│   └── ingesta/
│       └── dolares.py      # scraper de Bluelytics
├── sql/
│   ├── 01_schema.sql       # tablas fuentes y cotizaciones
│   └── seeds/
│       └── 01_fuentes.sql  # catálogo inicial
├── scripts/
│   └── run_ingesta.sh      # entry point para cron
└── logs/                   # logs de ejecución (gitignored)
```

## Comandos útiles

```bash
# Ver últimas cotizaciones
psql "$DATABASE_URL" -c "
  SELECT f.nombre, c.ts, c.valor, c.metadata
  FROM cotizaciones c
  JOIN fuentes f ON c.fuente_id = f.id
  ORDER BY c.ts DESC LIMIT 20;
"

# Tail del log de cron
tail -f logs/ingesta.log

# Linter
uv run ruff check .

# Formatter
uv run ruff format .
```

## Roadmap

- [ ] Tests con pytest contra fixture de Bluelytics.
- [ ] Sumar fuentes: BCRA (reservas), yfinance (Merval).
- [ ] Refactor a clase abstracta `Fuente`.
- [ ] TimescaleDB sobre `cotizaciones` (hypertable + compresión).
- [ ] EDA en notebook + sentiment de noticias.
- [ ] Forecasting (statsforecast / prophet).
- [ ] API REST (FastAPI) y dashboard (Streamlit).
- [ ] Deploy en VPS con backups.
