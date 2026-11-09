import numpy as np
import optuna
import polars as pl
import pytest

from src.agroweather.tuning import objective, suggest_params, tune_model

pytestmark = pytest.mark.etapa5


def _datos(crear_horas, cantidad: int = 240):
    X = pl.DataFrame(
        {
            "hora": crear_horas("2020-01-01", cantidad),
            "temp_lag_0": np.sin(np.arange(cantidad) / 12),
            "temp_lag_1": np.cos(np.arange(cantidad) / 12),
        }
    )
    y = (X["temp_lag_0"] * 0.8 + 0.1).alias("temp_objetivo")
    folds = [
        (np.arange(0, 120), np.arange(120, 180)),
        (np.arange(0, 180), np.arange(180, 240)),
    ]
    return X, y, folds


def test_suggest_params_respeta_los_rangos():
    estudio = optuna.create_study(direction="minimize")
    trial = estudio.ask()

    params = suggest_params(trial)

    assert 8 <= params["num_leaves"] <= 64
    assert 0.01 <= params["learning_rate"] <= 0.2
    assert 100 <= params["n_estimators"] <= 600
    assert 10 <= params["min_child_samples"] <= 100
    assert 0.6 <= params["subsample"] <= 1.0
    assert 0.6 <= params["colsample_bytree"] <= 1.0
    assert 1e-3 <= params["reg_lambda"] <= 10.0


def test_objective_devuelve_un_error_finito_y_no_modifica_X(crear_horas):
    X, y, folds = _datos(crear_horas)
    copia = X.clone()
    trial = optuna.trial.FixedTrial(
        {
            "num_leaves": 15,
            "learning_rate": 0.05,
            "n_estimators": 100,
            "min_child_samples": 20,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "reg_lambda": 1.0,
        }
    )

    valor = objective(trial, X, y, folds)

    assert np.isfinite(valor)
    assert valor >= 0
    assert X.equals(copia)


def test_tune_model_registra_los_trials(crear_horas):
    X, y, folds = _datos(crear_horas)

    estudio = tune_model(X, y, folds, n_trials=2, seed=7)

    assert len(estudio.trials) == 2
    assert np.isfinite(estudio.best_value)
    assert estudio.best_value >= 0


def test_tune_model_rechaza_cero_trials(crear_horas):
    X, y, folds = _datos(crear_horas)
    with pytest.raises(ValueError, match="n_trials"):
        tune_model(X, y, folds, n_trials=0)
