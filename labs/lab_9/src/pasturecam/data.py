"""Transformaciones de la tabla de mediciones de biomasa."""

import polars as pl

from src.pasturecam.contratos import OBJETIVOS


def a_formato_ancho(df_largo: pl.DataFrame) -> pl.DataFrame:
    """Pivotea la tabla de mediciones de formato largo a ancho.

    `df_largo` trae una fila por imagen y objetivo: `target_name` nombra el
    objetivo, `target` trae su valor, `sample_id` identifica esa fila
    (imagen + objetivo) y el resto de las columnas (incluido `image_path`)
    se repite igual en las cinco filas de una misma imagen. El resultado
    trae una fila por imagen, con una columna por cada nombre de
    `OBJETIVOS` y los metadatos conservados sin duplicar.
    """
    columnas_indice = [
        col
        for col in df_largo.columns
        if col not in ["sample_id", "target_name", "target"]
    ]

    df_pivoteado = df_largo.pivot(
        index=columnas_indice, on="target_name", values="target"
    )

    # Usamos OBJETIVOS para ordenar las columnas finales y así evitamos que el editor borre la importación
    return df_pivoteado.select(columnas_indice + OBJETIVOS)
