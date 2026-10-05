"""Búsqueda de vecinos más cercanos sobre una representación."""

import numpy as np
import polars as pl
from sklearn.metrics import pairwise_distances


def vecinos_mas_cercanos(
    X: np.ndarray,
    nombres: list[str],
    consulta: str,
    k: int = 5,
    metrica: str = "euclidean",
) -> pl.DataFrame:
    """Devuelve los `k` personajes más cercanos a `consulta`.

    `X` tiene una fila por personaje, en el mismo orden que `nombres`; puede
    ser un arreglo de NumPy o una matriz dispersa, como la de TF-IDF. El
    resultado tiene las columnas `name` y `distancia`, ordenadas de menor a
    mayor distancia, y no incluye a la consulta. Si `consulta` no está en
    `nombres`, levanta `KeyError`.
    """
    if consulta not in nombres:
        raise KeyError(f"'{consulta}' no está en la lista de nombres.")
    indice_consulta = nombres.index(consulta)

    # pairwise_distances soporta arreglos densos y matrices dispersas (TF-IDF)
    # con cualquier métrica de sklearn/scipy (euclidean, cosine, jaccard...).
    distancias = pairwise_distances(X, metric=metrica)[indice_consulta]

    # Ordenamos por distancia ascendente, descartando la propia consulta
    # (distancia 0 a sí misma), y nos quedamos con los primeros k.
    orden = np.argsort(distancias)
    seleccionados = [i for i in orden if i != indice_consulta][:k]

    return pl.DataFrame(
        {
            "name": [nombres[i] for i in seleccionados],
            "distancia": [float(distancias[i]) for i in seleccionados],
        }
    )
