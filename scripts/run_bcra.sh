#!/bin/bash
# Ejecuta la ingesta del BCRA. Pensado para correr 1 vez por día desde cron.

set -euo pipefail

cd /home/justo/proyectos/observatorio
exec /home/justo/.local/bin/uv run python -m observatorio.ingesta.bcra
