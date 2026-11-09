from datetime import datetime, timedelta

import numpy as np
import polars as pl
import pytest

from src.agroweather.features import build_features

ZONA = "America/Santiago"


@pytest.fixture
def crear_horas():
    """Devuelve una función que arma una columna `hora` en hora local."""

    def _crear(inicio: str, periodos: int) -> pl.Series:
        desde = datetime.fromisoformat(inicio)
        return pl.datetime_range(
            desde,
            desde + timedelta(hours=periodos - 1),
            interval="1h",
            time_zone=ZONA,
            eager=True,
        ).alias("hora")

    return _crear


@pytest.fixture
def estacion_sintetica(crear_horas) -> pl.DataFrame:
    """Ocho días horarios con ciclo diario, humedad y viento reproducibles."""
    hora = crear_horas("2020-05-01", 24 * 8)
    hora_del_dia = hora.dt.hour().to_numpy()
    posicion = np.arange(hora.len())
    temp = (
        9
        + 7 * np.sin(2 * np.pi * (hora_del_dia - 9) / 24)
        + 0.4 * np.sin(posicion / 17)
    )
    return pl.DataFrame(
        {
            "hora": hora,
            "temp": temp,
            "rhum": 70 + 15 * np.sin(posicion / 11),
            "pres": 1015 + 2 * np.sin(posicion / 29),
            "wspd": 8 + 3 * np.cos(posicion / 7),
            "wdir": ((posicion * 37) % 360).astype(float),
            "cldc": (posicion % 9).astype(float),
            "coco": [5.0 if p % 13 == 0 else None for p in posicion],
        }
    )


@pytest.fixture
def features_sinteticas(estacion_sintetica: pl.DataFrame) -> pl.DataFrame:
    return build_features(
        estacion_sintetica,
        lags=(0, 1, 2, 3, 6, 12, 24),
        ventanas=(3, 6, 12, 24),
    )
