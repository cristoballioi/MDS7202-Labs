"""Preprocesador tabular reutilizable para el catálogo y los personajes nuevos."""

from sklearn.pipeline import Pipeline


def construir_preprocesador(
    puntajes: list[str],
    medidas: list[str],
    categoricas: list[str],
    binarias: list[str],
    min_frequency: int = 10,
) -> Pipeline:
    """Arma el preprocesador por familia de columnas, sin ajustarlo.

    - `puntajes`: imputación por mediana y estandarización.
    - `medidas`: imputación por mediana, `log1p` y escalamiento robusto, para
      variables sesgadas con colas largas como el peso.
    - `categoricas`: nulo como categoría `"desconocido"` y one-hot; las
      categorías con menos de `min_frequency` apariciones comparten una
      columna de infrecuentes. Las nuevas usan esa columna si existe;
      si no, el bloque de esa variable queda en ceros.
    - `binarias`: columnas `poder_*` generadas con el encoder ajustado
      al catálogo; pasan sin cambios.

    El resultado es un `Pipeline` con un único paso, `"columnas"`, que es un
    `ColumnTransformer` con `verbose_feature_names_out=False`. Su salida es un
    DataFrame de Polars: las columnas numéricas y binarias conservan su
    nombre, y las one-hot se llaman `<columna>_<categoría>`, con
    `<columna>_infrequent_sklearn` para las infrecuentes.
    """
    raise NotImplementedError(
        "Completen construir_preprocesador antes de ejecutar el programa."
    )
