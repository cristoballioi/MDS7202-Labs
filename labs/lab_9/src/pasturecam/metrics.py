"""Métricas de regresión para la biomasa de pradera."""

import numpy as np
from sklearn.metrics import r2_score

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

    def r2_log_de(nombre: str) -> float:
        # Recortamos a 0 antes del logaritmo: una biomasa negativa no existe
        # y `log1p(x)` no está definido para x < -1. Se hace sobre lo real y
        # lo predicho para tratarlos igual.
        real_log = np.log1p(np.clip(y_real[nombre], 0, None))
        pred_log = np.log1p(np.clip(y_pred[nombre], 0, None))
        # R² en escala logarítmica: mide el error relativo, no el absoluto.
        return r2_score(real_log, pred_log)

    # Suma ponderada de los R² por objetivo: cada R² se multiplica por su peso
    # (p. ej. 0,5 para `Dry_Total_g`). Se recorren los objetivos de `pesos`,
    # así la función también sirve con un subconjunto de ellos.
    return float(
        sum(peso * r2_log_de(nombre) for nombre, peso in pesos.items())
    )


def gramos_a_kg_ha(gramos: float) -> float:
    """Convierte gramos por cuadrante de 70 x 30 cm a kilogramos por hectárea.

    Un cuadrante mide `AREA_CUADRANTE_M2` m². Una hectárea tiene 10 000 m².
    `gramos_a_kg_ha(1)` da aproximadamente 47,6: un gramo en el cuadrante
    equivale a esa cantidad de kilogramos repartidos en una hectárea.
    """
    # Gramos -> kilogramos (1 kg = 1000 g).
    kilogramos = gramos / 1000
    # Regla de tres: si el cuadrante tiene AREA_CUADRANTE_M2 m² y una hectárea
    # tiene 10 000 m², se multiplica por cuántos cuadrantes caben en la
    # hectárea (10 000 / AREA_CUADRANTE_M2).
    return kilogramos * 10_000 / AREA_CUADRANTE_M2
