"""Tres lecturas de la importancia de las variables de un modelo ajustado."""

from __future__ import annotations

import warnings

import numpy as np
import polars as pl
import shap
from sklearn.inspection import permutation_importance


def native_importance(
    modelo,
    tipo: str = "gain",
) -> pl.DataFrame:
    """Importancia nativa de LightGBM, ordenada de mayor a menor.

    `gain` suma la reducción de error que aporta cada variable en todos los
    cortes; `split` cuenta cuántas veces se usó. Se calcula sobre el modelo
    ajustado y no dice cuánto ayuda la variable a predecir datos nuevos.
    """
    if tipo not in ("gain", "split"):
        raise ValueError("tipo debe ser 'gain' o 'split'")

    booster = modelo.booster_
    tabla = pl.DataFrame(
        {
            "variable": booster.feature_name(),
            "importancia": booster.feature_importance(importance_type=tipo),
        }
    )
    return tabla.sort("importancia", descending=True)


def permutation_importance_table(
    modelo,
    X: pl.DataFrame,
    y: pl.Series,
    n_repeats: int = 5,
    seed: int = 42,
) -> pl.DataFrame:
    """Importancia por permutación sobre un período no usado para ajustar.

    `X` contiene solo las variables que vio el modelo, sin la columna `hora`.

    Usa `sklearn.inspection.permutation_importance` con
    `scoring="neg_mean_absolute_error"`. Como sklearn maximiza el score y el
    MAE se minimiza, el score es negativo: un aumento positivo de
    `importances_mean` significa que el MAE subió. Documentación:
    https://scikit-learn.org/stable/modules/generated/sklearn.inspection.permutation_importance.html

    Permutar una columna rompe su relación con el objetivo; si el MAE sube
    mucho, la variable importaba. Con lags y rolling windows correlacionados, una
    columna puede parecer irrelevante porque su vecina entrega la misma
    información. La tabla ordena por el aumento medio del MAE.
    """
    if n_repeats < 1:
        raise ValueError("n_repeats debe ser al menos 1")

    # sklearn baraja `X` como arreglo y LightGBM avisa que ya no hay nombres
    # de columna; el orden de las columnas no cambia, así que el aviso sobra.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="X does not have valid")
        resultado = permutation_importance(
            modelo,
            X,
            y,
            scoring="neg_mean_absolute_error",
            n_repeats=n_repeats,
            random_state=seed,
            n_jobs=1,
        )
    tabla = pl.DataFrame(
        {
            "variable": X.columns,
            "aumento_mae": resultado.importances_mean,
            "desviacion": resultado.importances_std,
        }
    )
    return tabla.sort("aumento_mae", descending=True)


def shap_values(modelo, X: pl.DataFrame) -> pl.DataFrame:
    """Valores SHAP de cada variable para cada fila de `X`.

    `X` contiene solo las variables que vio el modelo, sin la columna `hora`.
    Para un modelo de árboles, `shap.TreeExplainer` reparte la diferencia
    entre la predicción y el valor base entre las variables. Devuelve una
    tabla con las mismas filas y las mismas columnas que `X`.
    """
    explicador = shap.TreeExplainer(modelo)
    valores = explicador.shap_values(X)
    return pl.DataFrame(np.asarray(valores), schema=X.columns, orient="row")
