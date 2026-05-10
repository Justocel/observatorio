"""Scraper del BCRA. Por ahora solo dolar mayorista, fácil de extender a otras
monedas o variables monetarias."""

from datetime import datetime
from typing import Any

import requests
import urllib3
from loguru import logger
from pydantic import BaseModel

from observatorio.ingesta.base import Fuente

# BCRA usa un certificado SSL que el bundle de `certifi` no reconoce.
# Suprimimos el warning que requests emite cada vez que verify=False.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CotizacionBCRA(BaseModel):
    """Una entrada del array `detalle` en la respuesta de BCRA."""

    codigoMoneda: str
    descripcion: str
    tipoPase: float
    tipoCotizacion: float


class CotizacionDia(BaseModel):
    """Cotizaciones de un día (BCRA agrupa por fecha)."""

    fecha: datetime
    detalle: list[CotizacionBCRA]


class CotizacionesUSDResponse(BaseModel):
    """Shape de https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Cotizaciones/USD."""

    results: list[CotizacionDia]


class FuenteBCRAMayorista(Fuente):
    """Scraper para el TC mayorista USD/ARS publicado por el BCRA (1 vez por día)."""

    nombre = "dolar_mayorista"

    def fetch_y_parsear(self, url_origen: str) -> dict[str, Any]:
        response = requests.get(url_origen, timeout=10, verify=False)
        response.raise_for_status()
        parsed = CotizacionesUSDResponse(**response.json())

        if not parsed.results:
            raise ValueError(f"BCRA no devolvió cotizaciones para {self.nombre}")

        # Tomamos la fecha máxima por las dudas (BCRA podría cambiar el orden).
        ultimo = max(parsed.results, key=lambda r: r.fecha)

        cotizacion = next(
            (d for d in ultimo.detalle if d.codigoMoneda == "USD"),
            None,
        )
        if cotizacion is None:
            raise ValueError("La respuesta no contiene USD en el detalle")

        return {
            "ts": ultimo.fecha,
            "valor": cotizacion.tipoCotizacion,
            "metadata": {
                "tipo_pase": cotizacion.tipoPase,
                "moneda": cotizacion.codigoMoneda,
                "descripcion": cotizacion.descripcion,
            },
        }


def run() -> None:
    """Entry point: scrapea el dólar mayorista del BCRA."""
    logger.info("ingesta BCRA: iniciando")
    FuenteBCRAMayorista().run()
    logger.info("ingesta BCRA: terminada")


if __name__ == "__main__":
    run()
