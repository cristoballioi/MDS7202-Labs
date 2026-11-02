"""Optimización de hiperparámetros de LightGBM con Optuna."""

from __future__ import annotations

import optuna
import polars as pl


def suggest_params(trial: optuna.Trial) -> dict:
    """Define el espacio de búsqueda de LightGBM.

    Busca estos hiperparámetros, con los rangos entre paréntesis:

    - `num_leaves` (8 a 64, escala logarítmica): cantidad máxima de hojas.
    - `learning_rate` (0,01 a 0,2, escala logarítmica): cuánto aporta cada
      árbol.
    - `n_estimators` (100 a 600, paso 50): cantidad de árboles.
    - `min_child_samples` (10 a 100): mínimo de observaciones por hoja.
    - `subsample` (0,6 a 1,0): fracción de filas por árbol.
    - `colsample_bytree` (0,6 a 1,0): fracción de features por árbol.
    - `reg_lambda` (0,001 a 10, escala logarítmica): regularización L2.

    No se buscan los lags ni las rolling windows: esas decisiones se tomaron
    al construir las variables y se mantienen fijas para que la comparación
    entre trials sea justa.
    """
    raise NotImplementedError(
        "Completen suggest_params antes de ejecutar esta celda."
    )


def objective(
    trial: optuna.Trial,
    X: pl.DataFrame,
    y: pl.Series,
    folds: list[tuple],
) -> float:
    """Devuelve el MAE global del backtest con los parámetros del trial.

    `X`, `y` y `folds` vienen del período de desarrollo, que incluye train y
    validation pero nunca test: si test entrara aquí, la búsqueda elegiría los
    hiperparámetros mirando el examen. El MAE se calcula sobre todas las
    predicciones fuera de fold juntas: un fold con más horas aporta más filas
    al promedio, sin que haya que ponderar nada a mano.
    """
    raise NotImplementedError(
        "Completen objective antes de ejecutar esta celda."
    )


def tune_model(
    X: pl.DataFrame,
    y: pl.Series,
    folds: list[tuple],
    n_trials: int = 30,
    seed: int = 42,
) -> optuna.Study:
    """Crea y ejecuta un estudio Optuna que minimiza el MAE fuera de fold."""
    raise NotImplementedError(
        "Completen tune_model antes de ejecutar esta celda."
    )
