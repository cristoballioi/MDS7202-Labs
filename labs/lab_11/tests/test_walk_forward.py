from typing import ClassVar

import numpy as np
import polars as pl
import pytest
from sklearn.dummy import DummyRegressor

from src.agroweather.backtest import make_model, walk_forward

pytestmark = pytest.mark.etapa4


def _datos(crear_horas, cantidad: int = 200):
    X = pl.DataFrame(
        {"hora": crear_horas("2020-01-01", cantidad), "x": np.arange(cantidad)}
    )
    y = pl.Series("objetivo", np.arange(cantidad) / 100)
    return X, y


def test_make_model_usa_los_parametros_pedidos():
    modelo = make_model(n_estimators=50, num_leaves=8, learning_rate=0.1)

    assert modelo.n_estimators == 50
    assert modelo.num_leaves == 8
    assert modelo.learning_rate == pytest.approx(0.1)
    assert modelo.n_jobs == 1


def test_walk_forward_predice_todos_los_folds(crear_horas):
    X, y = _datos(crear_horas)
    folds = [
        (np.arange(0, 100), np.arange(100, 150)),
        (np.arange(0, 150), np.arange(150, 200)),
    ]

    resultados = walk_forward(X, y, DummyRegressor(strategy="mean"), folds)

    assert resultados.height == 100
    assert set(resultados.columns) == {"hora", "fold", "real", "pronostico"}
    assert resultados.filter(pl.col("fold") == 1).height == 50
    assert resultados.filter(pl.col("fold") == 2).height == 50
    assert resultados["hora"].equals(X["hora"][100:])
    assert sum(resultados.null_count().row(0)) == 0


class Registrador:
    """Estimador mínimo que anota qué filas y columnas recibe cada fit."""

    registros: ClassVar[list[tuple[list[str], int, int]]] = []

    def get_params(self, deep=True):
        return {}

    def set_params(self, **params):
        return self

    def fit(self, X, y):
        self.registros.append((X.columns, X["x"].min(), X["x"].max()))
        return self

    def predict(self, X):
        return np.zeros(X.height)


def test_walk_forward_entrena_solo_con_el_pasado(crear_horas):
    X, y = _datos(crear_horas)
    folds = [
        (np.arange(0, 100), np.arange(100, 150)),
        (np.arange(0, 150), np.arange(150, 200)),
    ]
    Registrador.registros.clear()

    walk_forward(X, y, Registrador(), folds)

    assert len(Registrador.registros) == len(folds)
    for (indices_train, indices_validation), registro in zip(
        folds, Registrador.registros, strict=True
    ):
        columnas, primero, ultimo = registro
        assert columnas == ["x"]
        assert (primero, ultimo) == (indices_train[0], indices_train[-1])
        assert ultimo < indices_validation[0]


def test_walk_forward_rechaza_folds_invalidos(crear_horas):
    X, y = _datos(crear_horas, 20)
    folds_invalidos = [(np.arange(0, 10), np.arange(9, 15))]

    with pytest.raises(ValueError, match="no puede incluir validation"):
        walk_forward(X, y, DummyRegressor(), folds_invalidos)
