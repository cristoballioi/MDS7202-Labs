"""Generación del reporte de riesgos de AgroAlerta."""

from agroalerta.sensores import Sensor


def contar_riesgos(
    sensores: list[Sensor],
    lecturas: dict[str, list[float]],
) -> dict[str, int]:
    """Cuenta, por sensor, cuántas lecturas están en situación de riesgo.

    Recorre `sensores` y, para cada uno, revisa las lecturas asociadas a su
    `nombre` en `lecturas`. Si un sensor no tiene lecturas para la fecha
    consultada, su conteo queda en 0.

    No se usa `isinstance`: cada sensor sabe evaluar su propia regla de
    riesgo mediante `es_riesgo`, sin importar de qué tipo concreto es.
    """
    conteo: dict[str, int] = {}
    for sensor in sensores:
        valores = lecturas.get(sensor.nombre, [])
        conteo[sensor.nombre] = sum(
            1 for valor in valores if sensor.es_riesgo(valor)
        )
    return conteo
