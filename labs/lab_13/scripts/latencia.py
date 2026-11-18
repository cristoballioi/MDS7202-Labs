"""Mide cuánto tarda el servicio en responder, solicitud por solicitud.

Sirve para ver el arranque en frío: si la aplicación escaló a cero, la primera
respuesta tarda mucho más que las siguientes. Uso, desde la raíz del laboratorio:

    uv run python scripts/latencia.py --url https://mi-app.azurecontainerapps.io --ruta /_stcore/health
    uv run python scripts/latencia.py --url http://localhost:8000 --solicitudes 8

Consulta una ruta pública (`/health` por defecto; para la interfaz de Streamlit,
`--ruta /_stcore/health`) y no necesita clave.
"""

import argparse
import sys
import time

import httpx


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--solicitudes", type=int, default=5)
    parser.add_argument("--ruta", default="/health")
    args = parser.parse_args()
    http = httpx.Client(base_url=args.url, timeout=120)

    for numero in range(1, args.solicitudes + 1):
        inicio = time.perf_counter()
        try:
            respuesta = http.get(args.ruta)
        except httpx.HTTPError as error:
            print(f"Solicitud {numero}: falló ({error})")
            return 1
        duracion = time.perf_counter() - inicio
        print(
            f"Solicitud {numero}: {respuesta.status_code} en {duracion:.2f} s"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
