"""Clustering sin etiquetas: elección de k, estabilidad, perfiles y equivalentes."""

import numpy as np
import polars as pl


def elegir_k(X: np.ndarray, ks: list[int], semilla: int = 0) -> pl.DataFrame:
    """Ajusta K-Means para cada `k` y reporta inercia y silhouette.

    Usa `KMeans(n_clusters=k, n_init=10, random_state=semilla)`. Devuelve una
    fila por `k`, en el orden de `ks`, con las columnas `k`, `inercia` y
    `silhouette`. Cada `k` debe estar entre 2 y el número de filas menos uno,
    porque el silhouette no está definido fuera de ese rango.
    """
    raise NotImplementedError(
        "Completen elegir_k antes de ejecutar el programa."
    )


def estabilidad(X: np.ndarray, k: int, semillas: list[int]) -> float:
    """Promedio del ARI entre las particiones de K-Means con cada semilla.

    Ajusta `KMeans(n_clusters=k, n_init=1, random_state=s)` para cada `s` de
    `semillas` y promedia el ARI de todos los pares de particiones. Vale 1 si
    todas coinciden, aunque numeren los grupos distinto, y cerca de 0 si
    coinciden como lo harían al azar. `n_init=1` hace que cada semilla
    muestre su propio resultado.
    """
    raise NotImplementedError(
        "Completen estabilidad antes de ejecutar el programa."
    )


def perfil_clusters(
    features: pl.DataFrame, etiquetas: np.ndarray, columnas: list[str]
) -> pl.DataFrame:
    """Una fila por grupo con su tamaño y el promedio de `columnas`.

    `etiquetas` trae el grupo de cada fila de `features`. Columnas: `cluster`,
    `n` y una por cada elemento de `columnas`, ordenadas por `cluster`.
    """
    raise NotImplementedError(
        "Completen perfil_clusters antes de ejecutar el programa."
    )


def equivalentes(
    X: np.ndarray,
    personajes: pl.DataFrame,
    consulta: str,
    k: int = 5,
    excluir_creator: str = "Marvel Comics",
    metrica: str = "cosine",
) -> pl.DataFrame:
    """Los `k` personajes más cercanos a `consulta` fuera de `excluir_creator`.

    `personajes` tiene las columnas `name` y `creator` en el mismo orden que
    las filas de `X`. Un `creator` nulo no se excluye: no hay evidencia de que
    sea de esa editorial. El resultado tiene `name`, `creator` y `distancia`,
    en distancia creciente.
    """
    raise NotImplementedError(
        "Completen equivalentes antes de ejecutar el programa."
    )
