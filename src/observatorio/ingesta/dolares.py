import json
from datetime import datetime

import requests
from loguru import logger
from pydantic import BaseModel

from observatorio.db import get_connection


class CotizacionDolar(BaseModel):
    """Una cotización individual dentro de la respuesta de Bluelytics."""

    value_avg: float
    value_sell: float
    value_buy: float


class BluelyticsResponse(BaseModel):
    """Shape esperado de la respuesta de https://api.bluelytics.com.ar/v2/latest.

    Solo declaramos los campos que nos interesan; los extras (`oficial_euro`,
    `blue_euro`) se ignoran silenciosamente.
    """

    oficial: CotizacionDolar
    blue: CotizacionDolar
    last_update: datetime


def get_fuente_info(nombre):
    """Devuelve (id, url_origen) de una fuente, o None si no existe."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, url_origen FROM fuentes WHERE nombre = %s",
                (nombre,),
            )
            return cur.fetchone()


def fetch_bluelytics(url) -> BluelyticsResponse:
    """GET a Bluelytics, valida con pydantic y devuelve la respuesta tipada."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return BluelyticsResponse(**response.json())


def get_dolar(name):
    """Trae la cotización de un dólar específico (oficial, blue) lista para insertar."""
    nombre_interno = f"dolar_{name}"
    info = get_fuente_info(nombre_interno)
    if info is None:
        raise ValueError(f"Fuente '{nombre_interno}' no existe en la tabla fuentes")

    fuente_id, url_origen = info
    logger.debug(f"fetching {nombre_interno} desde {url_origen}")
    parsed = fetch_bluelytics(url_origen)

    cotizacion: CotizacionDolar = getattr(parsed, name)

    return {
        "fuente_id": fuente_id,
        "ts": parsed.last_update,
        "valor": cotizacion.value_sell,
        "metadata": {
            "compra": cotizacion.value_buy,
            "promedio": cotizacion.value_avg,
        },
    }


def guardar_cotizacion(dolar_dict):
    """Inserta una cotización. Devuelve 1 si insertó, 0 si ya existía (ON CONFLICT)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO cotizaciones (fuente_id, ts, valor, metadata)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (fuente_id, ts) DO NOTHING
                """,
                (
                    dolar_dict["fuente_id"],
                    dolar_dict["ts"],
                    dolar_dict["valor"],
                    json.dumps(dolar_dict["metadata"]),
                ),
            )
            return cur.rowcount


def run(nombres=("oficial", "blue")):
    """Entry point: scrapea los dólares pasados y los persiste.

    Por default scrapea oficial y blue. Pasale una tupla/lista para limitar
    o cambiar el conjunto: por ejemplo `run(("oficial",))` o `run(["blue"])`.
    """
    logger.info(f"ingesta de dólares: iniciando ({len(nombres)} fuente/s: {list(nombres)})")
    for nombre in nombres:
        try:
            cot = get_dolar(nombre)
            inserted = guardar_cotizacion(cot)
            if inserted:
                logger.info(
                    f"dolar_{nombre}: insertado (valor={cot['valor']}, ts={cot['ts']})"
                )
            else:
                logger.info(f"dolar_{nombre}: ya existía, sin cambios")
        except Exception as e:
            logger.exception(f"dolar_{nombre}: falló - {e}")
    logger.info("ingesta de dólares: terminada")


if __name__ == "__main__":
    run()
