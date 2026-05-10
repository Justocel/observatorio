"""Clase abstracta `Fuente` que comparten todos los scrapers.

Subclases deben:
- Definir el atributo `nombre` (string que coincide con `fuentes.nombre` en la DB),
  ya sea como atributo de clase o seteado en __init__.
- Implementar `fetch_y_parsear(url_origen)` devolviendo un dict con
  las claves `ts`, `valor` y `metadata`.
"""

import json
from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from observatorio.db import get_connection


class Fuente(ABC):
    nombre: str

    def _obtener_info(self) -> tuple[int, str]:
        """Lookup de (id, url_origen) por nombre en la tabla fuentes."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, url_origen FROM fuentes WHERE nombre = %s",
                    (self.nombre,),
                )
                row = cur.fetchone()
        if row is None:
            raise ValueError(f"Fuente '{self.nombre}' no existe en la tabla fuentes")
        return row

    @abstractmethod
    def fetch_y_parsear(self, url_origen: str) -> dict[str, Any]:
        """Dada la URL de la fuente, retorna un dict con `ts`, `valor` y `metadata`."""
        ...

    def _guardar(self, fuente_id: int, parsed: dict[str, Any]) -> int:
        """INSERT ... ON CONFLICT DO NOTHING. Devuelve rowcount (1 nuevo, 0 duplicado)."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO cotizaciones (fuente_id, ts, valor, metadata)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (fuente_id, ts) DO NOTHING
                    """,
                    (
                        fuente_id,
                        parsed["ts"],
                        parsed["valor"],
                        json.dumps(parsed["metadata"]),
                    ),
                )
                return cur.rowcount

    def run(self) -> None:
        """Orquestación completa: lookup → fetch+parse → save → log."""
        try:
            fuente_id, url_origen = self._obtener_info()
            logger.debug(f"{self.nombre}: fetching desde {url_origen}")
            parsed = self.fetch_y_parsear(url_origen)
            inserted = self._guardar(fuente_id, parsed)
            if inserted:
                logger.info(
                    f"{self.nombre}: insertado (valor={parsed['valor']}, ts={parsed['ts']})"
                )
            else:
                logger.info(f"{self.nombre}: ya existía, sin cambios")
        except Exception as e:
            logger.exception(f"{self.nombre}: falló - {e}")
