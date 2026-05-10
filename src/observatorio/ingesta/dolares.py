"""Scraper de Bluelytics. Una sola clase sirve para los distintos dólares
(oficial, blue) que la API devuelve en una sola respuesta."""

from datetime import datetime
from typing import Any

import requests
from loguru import logger
from pydantic import BaseModel

from observatorio.ingesta.base import Fuente


class CotizacionDolar(BaseModel):
    """Una cotización individual dentro de la respuesta de Bluelytics."""

    value_avg: float
    value_sell: float
    value_buy: float


class BluelyticsResponse(BaseModel):
    """Shape esperado de https://api.bluelytics.com.ar/v2/latest."""

    oficial: CotizacionDolar
    blue: CotizacionDolar
    last_update: datetime


class FuenteBluelytics(Fuente):
    """Scraper para Bluelytics. Sirve para 'dolar_oficial' y 'dolar_blue'.

    La API devuelve los dos dólares en una sola response, así que la URL es
    la misma — lo que cambia es qué clave del JSON tomamos.
    """

    def __init__(self, clave_api: str) -> None:
        self.clave_api = clave_api  # "oficial" o "blue"
        self.nombre = f"dolar_{clave_api}"

    def fetch_y_parsear(self, url_origen: str) -> dict[str, Any]:
        response = requests.get(url_origen, timeout=10)
        response.raise_for_status()
        parsed = BluelyticsResponse(**response.json())
        cotizacion: CotizacionDolar = getattr(parsed, self.clave_api)
        return {
            "ts": parsed.last_update,
            "valor": cotizacion.value_sell,
            "metadata": {
                "compra": cotizacion.value_buy,
                "promedio": cotizacion.value_avg,
            },
        }


def run(claves: tuple[str, ...] = ("oficial", "blue")) -> None:
    """Entry point: scrapea los dólares pasados (oficial, blue, ...)."""
    logger.info(f"ingesta de dólares: iniciando ({len(claves)} fuente/s: {list(claves)})")
    for clave in claves:
        FuenteBluelytics(clave).run()
    logger.info("ingesta de dólares: terminada")


if __name__ == "__main__":
    run()
