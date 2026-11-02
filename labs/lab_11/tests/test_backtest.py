from datetime import datetime, timedelta

import numpy as np
import polars as pl
import pytest

from src.agroweather.backtest import (
    climatology_forecast,
    costo_alerta,
    daily_persistence_forecast,
    mae,
    make_expanding_folds,
    mejor_umbral,
    persistence_forecast,
    recall_evento,
    reporte_reglas,
    rmse,
    tasa_falsas_alarmas,
    temporal_split,
)


def _datos(crear_horas, cantidad: int = 1000) -> tuple[pl.DataFrame, pl.Series]:
    X = pl.DataFrame(
        {
            "hora": crear_horas("2020-01-01", cantidad),
            "temp_lag_0": np.linspace(5, 20, cantidad),
            "temp_lag_24": np.linspace(4, 19, cantidad),
        }
    )
    y = pl.Series("temp_objetivo", np.linspace(6, 21, cantidad))
    return X, y


@pytest.mark.etapa3
@pytest.mark.parametrize("horizonte", [1, 12, 24])
def test_temporal_split_respeta_el_orden_y_la_purga(crear_horas, horizonte):
    X, y = _datos(crear_horas)
    horas = X["hora"]
    partes = temporal_split(X, y, horas[400], horas[700], horizonte)

    assert set(partes) == {"train", "validation", "test"}
    train_X, train_y = partes["train"]
    validation_X, validation_y = partes["validation"]
    test_X, test_y = partes["test"]
    adelanto = timedelta(hours=horizonte)

    assert train_X.height + validation_X.height + test_X.height == (
        X.height - 2 * horizonte
    )
    assert train_X["hora"].max() + adelanto < validation_X["hora"].min()
    assert validation_X["hora"].max() + adelanto < test_X["hora"].min()
    assert validation_X["hora"].min() + adelanto == horas[400]
    assert test_X["hora"].min() + adelanto == horas[700]
    for datos, target in partes.values():
        posiciones = ((datos["hora"] - horas[0]).dt.total_hours()).to_list()
        assert target.to_list() == y[posiciones].to_list()
    assert train_y.len() == train_X.height
    assert validation_y.len() == validation_X.height
    assert test_y.len() == test_X.height


@pytest.mark.etapa3
def test_temporal_split_rechaza_cortes_invertidos(crear_horas):
    X, y = _datos(crear_horas)
    with pytest.raises(ValueError, match="posterior"):
        temporal_split(X, y, X["hora"][700], X["hora"][400])


@pytest.mark.etapa3
def test_temporal_split_rechaza_particion_vacia(crear_horas):
    X, y = _datos(crear_horas)
    with pytest.raises(ValueError, match="vacía"):
        temporal_split(X, y, X["hora"][0], X["hora"][500])


@pytest.mark.etapa3
def test_rmse_y_mae_calculan_lo_esperado():
    real = pl.Series([1.0, 2.0, 3.0])
    pred = pl.Series([1.0, 1.0, 3.0])

    assert rmse(real, pred) == pytest.approx(np.sqrt(1 / 3))
    assert mae(real, pred) == pytest.approx(1 / 3)


@pytest.mark.etapa3
def test_persistence_forecast_repite_el_origen(crear_horas):
    X, _ = _datos(crear_horas, 5)
    pronostico = persistence_forecast(X)

    assert pronostico.name == "pronostico"
    assert pronostico.to_list() == X["temp_lag_0"].to_list()


@pytest.mark.etapa3
def test_daily_persistence_usa_la_hora_del_target_de_ayer(crear_horas):
    horas = crear_horas("2020-01-01", 48)
    temperaturas = pl.DataFrame(
        {"hora": horas, "temp": np.arange(48, dtype=float)}
    )
    # Origen 2020-01-02 00:00; con horizonte 12, el target es a las 12:00 y
    # ayer a esa hora corresponde a la fila 12 de temperaturas.
    X = pl.DataFrame({"hora": horas[24:26]})

    assert daily_persistence_forecast(X, temperaturas, 12).to_list() == [
        12.0,
        13.0,
    ]
    assert daily_persistence_forecast(X, temperaturas, 24).to_list() == [
        24.0,
        25.0,
    ]


@pytest.mark.etapa3
def test_daily_persistence_conserva_los_huecos(crear_horas):
    horas = crear_horas("2020-01-01", 27)
    temperaturas = pl.DataFrame(
        {"hora": horas, "temp": [5.0, None, 7.0] + [10.0] * 24}
    )
    X = pl.DataFrame({"hora": horas[12:15]})

    pronostico = daily_persistence_forecast(X, temperaturas, 12)

    assert pronostico.len() == 3
    assert pronostico[0] == 5.0
    assert pronostico[1] is None
    assert pronostico[2] == 7.0


@pytest.mark.etapa3
def test_daily_persistence_rechaza_horizontes_fuera_de_rango(crear_horas):
    horas = crear_horas("2020-01-01", 3)
    temperaturas = pl.DataFrame({"hora": horas, "temp": [1.0, 2.0, 3.0]})

    with pytest.raises(ValueError, match="horizonte"):
        daily_persistence_forecast(
            pl.DataFrame({"hora": horas}), temperaturas, 25
        )


@pytest.mark.etapa3
def test_climatology_forecast_usa_la_hora_del_objetivo(crear_horas):
    horas = crear_horas("2020-01-01", 48)
    X_train = pl.DataFrame({"hora": horas})
    hora_objetivo = (horas + timedelta(hours=12)).dt.hour()
    y_train = hora_objetivo.cast(pl.Float64).alias("temp_objetivo")
    X = pl.DataFrame({"hora": horas.head(4), "temp_lag_0": [0.0] * 4})

    pronostico = climatology_forecast(X_train, y_train, X, horizonte=12)

    esperado = (horas.head(4) + timedelta(hours=12)).dt.hour()
    assert pronostico.to_list() == pytest.approx(esperado.to_list())


@pytest.mark.etapa4
def test_make_expanding_folds_deja_purga_entre_train_y_validation():
    indice = pl.datetime_range(
        datetime(2018, 1, 1), datetime(2020, 12, 31, 23), "1d", eager=True
    )

    folds = make_expanding_folds(indice, anios=(2019, 2020), purga_horas=24)

    assert len(folds) == 2
    for indices_train, indices_validation in folds:
        ultimo_train = indice[int(indices_train[-1])]
        primer_validation = indice[int(indices_validation[0])]
        assert ultimo_train + timedelta(hours=24) < primer_validation
        assert indices_train.max() < indices_validation.min()
        assert indice[indices_validation].dt.year().n_unique() == 1


@pytest.mark.etapa4
def test_make_expanding_folds_rechaza_un_anio_sin_train():
    indice = pl.datetime_range(
        datetime(2019, 1, 1), datetime(2019, 12, 31, 23), "1d", eager=True
    )
    with pytest.raises(ValueError, match="vacío"):
        make_expanding_folds(indice, anios=(2019,))


@pytest.mark.etapa3
def test_reporte_reglas_descarta_las_filas_marcadas():
    reales = pl.Series([1.0, 2.0, 3.0])
    pronosticos = pl.DataFrame(
        {
            "diaria": [1.0, None, 2.0],
            "otra": [1.0, 2.0, 3.0],
        }
    )
    descartados = pronosticos["diaria"].is_null()

    tabla = reporte_reglas(pronosticos, reales, descartados=descartados)

    assert tabla["n"].to_list() == [2, 2]
    assert tabla["MAE"].to_list() == pytest.approx([0.5, 0.0])
    assert tabla["RMSE"].to_list() == pytest.approx([np.sqrt(0.5), 0.0])


@pytest.mark.etapa3
def test_reporte_reglas_rechaza_mascara_de_otro_largo():
    reales = pl.Series([1.0, 2.0])
    pronosticos = pl.DataFrame({"diaria": [1.0, 2.0]})

    with pytest.raises(ValueError, match="descartados debe tener el mismo"):
        reporte_reglas(pronosticos, reales, descartados=pl.Series([False]))


@pytest.mark.etapa3
def test_reporte_reglas_rechaza_pronosticos_faltantes():
    reales = pl.Series([1.0, 2.0])
    pronosticos = pl.DataFrame({"diaria": [1.0, None]})

    with pytest.raises(ValueError, match="Quedan pronósticos faltantes"):
        reporte_reglas(
            pronosticos, reales, descartados=pl.Series([False, False])
        )


@pytest.mark.etapa3
def test_reporte_reglas_rechaza_sin_filas_comparables():
    reales = pl.Series([1.0, 2.0])
    pronosticos = pl.DataFrame({"diaria": [1.0, 2.0]})

    with pytest.raises(ValueError, match="No quedan filas para evaluar"):
        reporte_reglas(pronosticos, reales, descartados=pl.Series([True, True]))


@pytest.mark.etapa5
def test_metricas_de_alerta_calculan_lo_esperado():
    real = pl.Series([True, True, False, False])
    alerta = pl.Series([True, False, True, False])

    assert recall_evento(real, alerta) == pytest.approx(0.5)
    assert tasa_falsas_alarmas(real, alerta) == pytest.approx(0.5)
    assert costo_alerta(real, alerta) == pytest.approx(20_800_000.0)


@pytest.mark.etapa5
def test_mejor_umbral_elige_el_costo_minimo():
    real = pl.Series([True, True, False, False])
    pronostico = pl.Series([0.0, 1.0, 5.0, 6.0])

    umbral, costo = mejor_umbral(
        real,
        pronostico,
        costo_por_alerta=1.0,
        costo_helada=10.0,
    )

    assert umbral == pytest.approx(5.0)
    assert costo == pytest.approx(2.0)
