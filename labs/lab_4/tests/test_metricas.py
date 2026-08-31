"""Pruebas de las agregaciones sobre meses."""

import polars as pl
import pytest

from src.meteolab.derivadas import agregar_fecha_mensual
from src.meteolab.metricas import (
    anomalias_mensuales,
    resumen_anual_desde_mensuales,
    resumen_mensual,
)


@pytest.mark.etapa5
def test_resumen_mensual_agrupa_por_pais_y_mes(muestra):
    mensuales = agregar_fecha_mensual(muestra)
    resultado = resumen_mensual(mensuales)

    assert resultado.filter(pl.col("iso_alpha3") == "CHL").height == 2
    assert resultado.filter(pl.col("month") == 1)[
        "temperature_mean"
    ].to_list() == [10.5, 20.0]


@pytest.mark.etapa5
def test_resumen_anual_se_calcula_desde_filas_mensuales(muestra):
    mensuales = agregar_fecha_mensual(muestra)
    resultado = resumen_anual_desde_mensuales(mensuales)

    chile = resultado.filter(pl.col("iso_alpha3") == "CHL")

    assert chile.height == 2
    assert chile["meses_disponibles"].to_list() == [2, 1]


@pytest.mark.etapa6
def test_anomalias_mensuales_usa_una_ventana_por_pais_y_mes(muestra):
    datos = pl.DataFrame(
        {
            "iso_alpha3": ["CHL"] * 4,
            "country": ["Chile"] * 4,
            "year": [1901, 1902, 1903, 1904],
            "period": ["JAN"] * 4,
            "month": [1] * 4,
            "fecha": pl.date_range(
                pl.date(1901, 1, 1),
                pl.date(1904, 1, 1),
                interval="1y",
                eager=True,
            ),
            "temperature_c": [10.0, 10.0, 10.0, 30.0],
        }
    )

    resultado = anomalias_mensuales(datos, umbral=1.0)

    assert "standardized_anomaly" in resultado.columns
    assert resultado["is_anomaly"].null_count() == 0
    assert resultado.filter(pl.col("is_anomaly")).height == 1
