"""Optimización de hiperparámetros de LightGBM con Optuna."""

from __future__ import annotations

import optuna
import polars as pl

from .backtest import mae, make_model, walk_forward


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
    # El orden de las sugerencias importa: TPE con semilla fija propone los
    # mismos valores solo si el espacio se declara siempre en el mismo orden.
    return {
        # Hojas por árbol: escala log porque importa el cambio relativo.
        "num_leaves": trial.suggest_int("num_leaves", 8, 64, log=True),
        "learning_rate": trial.suggest_float(
            "learning_rate", 0.01, 0.2, log=True
        ),
        # Cantidad de árboles, de 50 en 50.
        "n_estimators": trial.suggest_int("n_estimators", 100, 600, step=50),
        "min_child_samples": trial.suggest_int("min_child_samples", 10, 100),
        # Fracción de filas y de features que ve cada árbol.
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        # Regularización L2: varía en varios órdenes de magnitud (escala log).
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
    }


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
    # Hiperparámetros propuestos por Optuna para este trial.
    parametros = suggest_params(trial)
    # Backtest con ventana expansiva sobre el período de desarrollo (nunca
    # test): cada fold ajusta un modelo nuevo con esos parámetros.
    resultados = walk_forward(X, y, make_model(**parametros), folds)
    # MAE global: todas las predicciones fuera de fold juntas, de modo que un
    # fold con más filas pesa más sin ponderar a mano.
    return mae(resultados["real"], resultados["pronostico"])


def tune_model(
    X: pl.DataFrame,
    y: pl.Series,
    folds: list[tuple],
    n_trials: int = 30,
    seed: int = 42,
) -> optuna.Study:
    """Crea y ejecuta un estudio Optuna que minimiza el MAE fuera de fold."""
    if n_trials < 1:
        raise ValueError("n_trials debe ser al menos 1")

    # Estudio que minimiza el MAE, con TPE y semilla fija para que la
    # búsqueda sea reproducible.
    estudio = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=seed),
    )
    estudio.optimize(
        lambda trial: objective(trial, X, y, folds), n_trials=n_trials
    )
    return estudio
