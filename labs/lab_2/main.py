"""Punto de entrada de AgroAlerta.

Uso:
    uv run python main.py --fecha 2026-06-15
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agroalerta.datos import cargar_lecturas
from agroalerta.reporte import contar_riesgos
from agroalerta.sensores import SensorHumedad, SensorTemperatura, SensorViento

RUTA_DATOS = Path(__file__).parent / "data" / "lecturas.csv"
NOMBRE_ESTACION = "Estación Parcela Norte"

# Rangos físicamente posibles para cada sensor (no confundir con el umbral
# de riesgo: esto solo distingue una lectura real de una lectura imposible,
# como -300 °C o 999 km/h de viento, típica de una falla de sensor).
RANGOS_VALIDOS = {
    "temperatura": (-50.0, 60.0),
    "viento": (0.0, 150.0),
    "humedad": (0.0, 100.0),
}


class LecturaInvalidaError(Exception):
    """Se levanta cuando una lectura está fuera del rango físico posible."""


def validar_lectura(sensor: str, valor: float) -> None:
    minimo, maximo = RANGOS_VALIDOS[sensor]
    if valor < minimo or valor > maximo:
        raise LecturaInvalidaError(
            f"Lectura de {sensor} fuera de rango físico: {valor}"
        )


def descartar_lecturas_invalidas(
    lecturas: dict[str, list[float]],
) -> dict[str, list[float]]:
    """Recorre las lecturas y descarta las que son físicamente imposibles."""
    validas: dict[str, list[float]] = {}
    for sensor, valores in lecturas.items():
        validas[sensor] = []
        for valor in valores:
            try:
                validar_lectura(sensor, valor)
            except LecturaInvalidaError:
                continue
            validas[sensor].append(valor)
    return validas


def main() -> None:
    parser = argparse.ArgumentParser(description="AgroAlerta")
    parser.add_argument("--fecha", default="2026-06-15")
    args = parser.parse_args()

    sensores = [
        SensorTemperatura(0, 40),
        SensorViento(25),
        SensorHumedad(85),
    ]

    lecturas = cargar_lecturas(RUTA_DATOS, args.fecha)
    lecturas = descartar_lecturas_invalidas(lecturas)
    conteo = contar_riesgos(sensores, lecturas)

    print(f"{NOMBRE_ESTACION} — {args.fecha}")
    for sensor in sensores:
        cantidad = conteo.get(sensor.nombre, 0)
        print(f"{sensor.nombre.capitalize():<15}{cantidad} lecturas en riesgo")

    total = sum(conteo.values())
    print(f"\nTotal: {total} situaciones de riesgo")


if __name__ == "__main__":
    main()
