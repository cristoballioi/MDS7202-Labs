"""Métricas de regresión para la biomasa de pradera."""

import numpy as np

from src.pasturecam.contratos import AREA_CUADRANTE_M2, PESOS_OBJETIVOS


def r2_log_ponderado(
    y_real: dict[str, np.ndarray],
    y_pred: dict[str, np.ndarray],
    pesos: dict[str, float] = PESOS_OBJETIVOS,
) -> float:
    """R² sobre `log1p` de cada objetivo, combinado con `pesos`.

    `y_real` y `y_pred` son diccionarios `{nombre_objetivo: valores}`, con
    las mismas claves que `pesos` (por omisión, las cinco de
    `PESOS_OBJETIVOS`). Cada valor se recorta a 0 antes de aplicar
    `log1p`, porque una predicción negativa de biomasa no tiene sentido
    físico y `log1p` de un número menor que -1 no está definido. El
    resultado es la suma ponderada de los R² por objetivo; vale 1,0 si las
    predicciones son idénticas a los valores reales.
    """
    raise NotImplementedError(
        "Completen r2_log_ponderado antes de ejecutar el programa."
    )


def gramos_a_kg_ha(gramos: float) -> float:
    """Convierte gramos por cuadrante de 70 x 30 cm a kilogramos por hectárea.

    Un cuadrante mide `AREA_CUADRANTE_M2` m². Una hectárea tiene 10 000 m².
    `gramos_a_kg_ha(1)` da aproximadamente 47,6: un gramo en el cuadrante
    equivale a esa cantidad de kilogramos repartidos en una hectárea.
    """
    raise NotImplementedError(
        "Completen gramos_a_kg_ha antes de ejecutar el programa."
    )
