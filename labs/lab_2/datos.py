"""Carga de datos. Este módulo lo entrega el curso: no hay que modificarlo."""

import csv
from pathlib import Path


def cargar_lecturas(ruta: Path, fecha: str) -> dict[str, list[float]]:
    """Lee el CSV y devuelve las lecturas de esa fecha, agrupadas por sensor.

    El resultado tiene la forma:
        {"temperatura": [2.1, -1.2, ...], "viento": [...], "humedad": [...]}
    """
    lecturas: dict[str, list[float]] = {}
    with ruta.open(encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):
            if fila["fecha"] != fecha:
                continue
            lecturas.setdefault(fila["sensor"], []).append(float(fila["valor"]))
    return lecturas
