import requests
from observatorio.db import get_connection
import json

def get_fuente_info(nombre):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, url_origen FROM fuentes WHERE nombre = %s",
                (nombre,),
            )
            return cur.fetchone()

def fetch_bluelytics(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

def get_dolar(name):
    nombre_interno = f"dolar_{name}"
    info = get_fuente_info(nombre_interno)
    if info is None:
        raise ValueError(f"Fuente '{nombre_interno}' no existe en la tabla fuentes")

    fuente_id, url_origen = info

    data = fetch_bluelytics(url_origen)

    dolar_dict ={
        "fuente_id": fuente_id,
        "ts": data["last_update"],
        "valor": data[name]["value_sell"],
        "metadata": {
            "compra": data[name]["value_buy"],
            "promedio": data[name]["value_avg"],
        },
    }

    return dolar_dict

def guardar_cotizacion(dolar_dict):
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


if __name__ == "__main__":
    for nombre in ("oficial", "blue"):
        cot = get_dolar(nombre)
        guardar_cotizacion(cot)
        print("Guardado:", cot)

