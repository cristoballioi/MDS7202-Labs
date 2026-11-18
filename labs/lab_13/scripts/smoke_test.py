"""Comprueba por HTTP el contrato del servicio, sin importar dónde corra.

Es el mismo contrato para el servidor local y el contenedor. Uso,
desde la raíz del laboratorio:

    uv run python scripts/smoke_test.py
    uv run python scripts/smoke_test.py --ui --url http://localhost:8501

Sin `--ui` verifica la API (necesita la clave: de `--clave`, de `APR_API_KEY` o
de su archivo `.env`);
con `--ui` verifica la interfaz de Streamlit, que es lo que se publica en la
nube. Termina con código 0 si todo pasa y 1 si algo falla.
"""

import argparse
import os
import sys
from collections.abc import Callable

import httpx
from dotenv import dotenv_values

MEDICION = {
    "ph": 7.1,
    "Hardness": 190.0,
    "Solids": 21000.0,
    "Chloramines": 7.2,
    "Sulfate": 330.0,
    "Conductivity": 420.0,
    "Organic_carbon": 14.0,
    "Trihalomethanes": 66.0,
    "Turbidity": 3.9,
}


def comprobar(nombre: str, prueba: Callable[[], None]) -> bool:
    try:
        prueba()
    except (AssertionError, httpx.HTTPError) as error:
        print(f"  ✗ {nombre}: {error}")
        return False
    print(f"  ✓ {nombre}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://localhost:8000")
    clave = os.environ.get("APR_API_KEY") or dotenv_values(".env").get(
        "APR_API_KEY"
    )
    parser.add_argument("--clave", default=clave or "")
    parser.add_argument(
        "--ui",
        action="store_true",
        help="comprueba la interfaz de Streamlit en vez de la API",
    )
    args = parser.parse_args()
    cabeceras = {"X-API-Key": args.clave}
    http = httpx.Client(base_url=args.url, timeout=30)
    resultados: list[bool] = []

    def informacion() -> None:
        cuerpo = http.get("/").json()
        assert "metricas_validacion" in cuerpo, cuerpo

    def vida() -> None:
        respuesta = http.get("/health")
        assert respuesta.status_code == 200, respuesta.status_code

    def prediccion() -> None:
        respuesta = http.post("/predict", json=MEDICION, headers=cabeceras)
        assert respuesta.status_code == 200, respuesta.text
        assert respuesta.json()["prediccion"] in (0, 1)

    def fuera_de_rango() -> None:
        respuesta = http.post(
            "/predict", json={**MEDICION, "ph": 15}, headers=cabeceras
        )
        assert respuesta.status_code == 422, respuesta.status_code
        assert "ph" in respuesta.text

    def sin_clave() -> None:
        respuesta = http.post("/predict", json=MEDICION)
        assert respuesta.status_code == 401, respuesta.status_code

    def interfaz_viva() -> None:
        respuesta = http.get("/_stcore/health")
        assert respuesta.status_code == 200, respuesta.status_code
        assert respuesta.text.strip() == "ok", respuesta.text

    def interfaz_abre() -> None:
        respuesta = http.get("/")
        assert respuesta.status_code == 200, respuesta.status_code
        assert "streamlit" in respuesta.text.lower(), "no es Streamlit"

    print(f"Servicio en {args.url}")
    if args.ui:
        resultados += [
            comprobar("GET /_stcore/health responde ok", interfaz_viva),
            comprobar("GET / abre la interfaz de Streamlit", interfaz_abre),
        ]
        return 0 if all(resultados) else 1
    resultados += [
        comprobar("GET / describe el modelo", informacion),
        comprobar("GET /health responde 200", vida),
        comprobar("POST /predict responde 200", prediccion),
        comprobar("ph=15 responde 422 y nombra ph", fuera_de_rango),
        comprobar("sin clave responde 401", sin_clave),
    ]

    return 0 if all(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
