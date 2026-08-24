"""Pruebas de nulos y de la grilla temporal."""

import polars as pl
import pytest

from src.meteolab.limpieza import (
    claves_repetidas,
    limpiar_temperaturas,
    resumen_de_nulos,
)

pytestmark = pytest.mark.etapa4


def test_el_resumen_de_nulos_entrega_conteo_y_porcentaje(muestra):
    resumen = resumen_de_nulos(
        muestra.with_columns(pl.lit(None, dtype=pl.Float64).alias("faltante"))
    )

    assert resumen.columns == ["columna", "nulos", "porcentaje"]
    assert resumen.filter(pl.col("columna") == "faltante")["nulos"].item() == 4


def test_las_claves_repetidas_se_pueden_inspeccionar(muestra):
    repetida = pl.concat([muestra, muestra.head(1)])

    resultado = claves_repetidas(repetida)

    assert resultado.height == 1
    assert resultado["len"].item() == 2


def test_limpiar_conserva_solo_meses_y_valores_disponibles(muestra):
    con_periodos = pl.concat(
        [
            muestra,
            muestra.head(1).with_columns(pl.lit("DJF").alias("period")),
            muestra.head(1).with_columns(pl.lit("ANN").alias("period")),
        ]
    ).with_columns(
        pl.when(pl.col("period") == "FEB")
        .then(None)
        .otherwise(pl.col("temperature_c"))
        .alias("temperature_c")
    )

    resultado = limpiar_temperaturas(con_periodos)

    assert set(resultado["period"].unique()) <= {
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
    }
    assert resultado["temperature_c"].null_count() == 0
