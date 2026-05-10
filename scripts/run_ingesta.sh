#!/bin/bash
# Ejecuta la ingesta de cotizaciones. Pensado para correr desde cron.
#
# Cron tiene PATH minimal y arranca en /, así que:
#  - cd al proyecto (para que .env y .venv se encuentren)
#  - usar paths absolutos para uv
#
# Logs: stderr (loguru) + stdout van al archivo que apunte el cron.

set -euo pipefail

cd /home/justo/proyectos/observatorio
exec /home/justo/.local/bin/uv run python -m observatorio.ingesta.dolares
