"""Clustering sin etiquetas: elección de k, estabilidad, perfiles y equivalentes."""

from itertools import combinations

import numpy as np
import polars as pl
from sklearn.cluster import KMeans
from sklearn.metrics import (
    adjusted_rand_score,
    pairwise_distances,
    silhouette_score,
)


def elegir_k(X: np.ndarray, ks: list[int], semilla: int = 0) -> pl.DataFrame:
    """Ajusta K-Means para cada `k` y reporta inercia y silhouette.

    Usa `KMeans(n_clusters=k, n_init=10, random_state=semilla)`. Devuelve una
    fila por `k`, en el orden de `ks`, con las columnas `k`, `inercia` y
    `silhouette`. Cada `k` debe estar entre 2 y el número de filas menos uno,
    porque el silhouette no está definido fuera de ese rango.
    """
    filas = []
    for k in ks:
        # n_init=10 corre K-Means 10 veces con distintos centroides iniciales
        # y se queda con el mejor (menor inercia), para no depender de una
        # única inicialización con random_state=semilla.
        modelo = KMeans(n_clusters=k, n_init=10, random_state=semilla)
        etiquetas = modelo.fit_predict(X)
        filas.append(
            {
                "k": k,
                "inercia": float(modelo.inertia_),
                "silhouette": float(silhouette_score(X, etiquetas)),
            }
        )
    return pl.DataFrame(filas)


def estabilidad(X: np.ndarray, k: int, semillas: list[int]) -> float:
    """Promedio del ARI entre las particiones de K-Means con cada semilla.

    Ajusta `KMeans(n_clusters=k, n_init=1, random_state=s)` para cada `s` de
    `semillas` y promedia el ARI de todos los pares de particiones. Vale 1 si
    todas coinciden, aunque numeren los grupos distinto, y cerca de 0 si
    coinciden como lo harían al azar. `n_init=1` hace que cada semilla
    muestre su propio resultado.
    """
    # n_init=1: cada semilla produce exactamente una partición (sin elegir la
    # mejor de varias), así que las diferencias entre semillas reflejan la
    # sensibilidad real del algoritmo a la inicialización.
    particiones = [
        KMeans(n_clusters=k, n_init=1, random_state=semilla).fit_predict(X)
        for semilla in semillas
    ]
    # ARI es invariante a cómo se numeran los clusters, así que compara
    # agrupamientos, no etiquetas exactas.
    aris = [adjusted_rand_score(a, b) for a, b in combinations(particiones, 2)]
    return float(np.mean(aris))


def perfil_clusters(
    features: pl.DataFrame, etiquetas: np.ndarray, columnas: list[str]
) -> pl.DataFrame:
    """Una fila por grupo con su tamaño y el promedio de `columnas`.

    `etiquetas` trae el grupo de cada fila de `features`. Columnas: `cluster`,
    `n` y una por cada elemento de `columnas`, ordenadas por `cluster`.
    """
    tabla = features.select(columnas).with_columns(
        pl.Series("cluster", etiquetas)
    )
    perfil = (
        tabla.group_by("cluster")
        .agg(pl.len().alias("n"), *[pl.col(c).mean() for c in columnas])
        .sort("cluster")
    )
    return perfil.select("cluster", "n", *columnas)


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
    nombres = personajes["name"].to_list()
    creadores = personajes["creator"].to_list()
    if consulta not in nombres:
        raise KeyError(f"'{consulta}' no está en 'personajes'.")
    indice_consulta = nombres.index(consulta)

    distancias = pairwise_distances(X, metric=metrica)[indice_consulta]
    orden = np.argsort(distancias)

    seleccionados = []
    for i in orden:
        if i == indice_consulta:
            continue
        # creators[i] es None cuando no hay editorial registrada: al no
        # haber evidencia de que sea "excluir_creator", no se descarta.
        if creadores[i] == excluir_creator:
            continue
        seleccionados.append(i)
        if len(seleccionados) == k:
            break

    return pl.DataFrame(
        {
            "name": [nombres[i] for i in seleccionados],
            "creator": [creadores[i] for i in seleccionados],
            "distancia": [float(distancias[i]) for i in seleccionados],
        }
    )
