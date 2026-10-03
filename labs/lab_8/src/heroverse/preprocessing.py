"""Preprocesador tabular reutilizable para el catálogo y los personajes nuevos."""

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    FunctionTransformer,
    OneHotEncoder,
    RobustScaler,
    StandardScaler,
)


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
    # Puntajes: mediana para los nulos (sin ficha) y luego estandarización
    # (media 0, desviación 1), estándar para variables ya acotadas 0-100.
    pipeline_puntajes = Pipeline(
        steps=[
            ("imputar", SimpleImputer(strategy="median")),
            ("escalar", StandardScaler()),
        ]
    )

    # Medidas (peso, altura): mediana para los nulos, log1p para comprimir
    # colas largas (pesos extremos) y RobustScaler, menos sensible a
    # outliers que StandardScaler porque usa mediana/IQR en vez de media/std.
    # feature_names_out="one-to-one" deja que ColumnTransformer nombre bien
    # las columnas de salida pese a que log1p no aprende nombres por sí solo.
    pipeline_medidas = Pipeline(
        steps=[
            ("imputar", SimpleImputer(strategy="median")),
            (
                "log",
                FunctionTransformer(np.log1p, feature_names_out="one-to-one"),
            ),
            ("escalar", RobustScaler()),
        ]
    )

    # Categóricas: los nulos se tratan como una categoría explícita
    # "desconocido" (no información ausente sino un valor más), y luego
    # one-hot. Las categorías raras (< min_frequency apariciones) se agrupan
    # en una columna infrecuente; una categoría nueva en datos futuros cae
    # ahí si existe, o queda en ceros si todas las categorías eran frecuentes.
    pipeline_categoricas = Pipeline(
        steps=[
            (
                "imputar",
                # Un nulo de una columna de texto de Polars llega a sklearn
                # como `None`, no como `NaN`: missing_values=None es
                # necesario para que SimpleImputer lo reconozca y lo
                # reemplace por "desconocido".
                SimpleImputer(
                    missing_values=None,
                    strategy="constant",
                    fill_value="desconocido",
                ),
            ),
            (
                "codificar",
                OneHotEncoder(
                    min_frequency=min_frequency,
                    handle_unknown="infrequent_if_exist",
                    sparse_output=False,
                ),
            ),
        ]
    )

    columnas = ColumnTransformer(
        transformers=[
            ("puntajes", pipeline_puntajes, puntajes),
            ("medidas", pipeline_medidas, medidas),
            ("categoricas", pipeline_categoricas, categoricas),
            # Las binarias ya son 0/1 (poder_*): pasan tal cual.
            ("binarias", "passthrough", binarias),
        ],
        verbose_feature_names_out=False,
    ).set_output(transform="polars")

    return Pipeline(steps=[("columnas", columnas)])
