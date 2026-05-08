"""Helpers para la conexión a Postgres."""

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection() -> psycopg.Connection:
    """Devuelve una nueva conexión a Postgres leyendo DATABASE_URL del .env."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL no está definida. ¿Existe el .env y tiene la variable?"
        )
    return psycopg.connect(url)
