"""Pruebas del contrato de tipos y valores."""

import polars as pl
import pytest

from src.meteolab.esquema import (
    casos_que_fallan,
    comparar_esquema,
    validar_datos,
    validar_esquema,
)

pytestmark = pytest.mark.etapa3


def test_el_archivo_cumple_el_esquema_de_polars(crudas):
    assert comparar_esquema(crudas) == []
    validar_esquema(crudas)


def test_el_nulo_de_djf_2025_es_valido(crudas):
    validado = validar_datos(crudas)

    assert validado.height == crudas.height


def test_un_periodo_desconocido_se_reporta(muestra):
    invalida = muestra.with_columns(pl.lit("XYZ").alias("period"))

    fallas = casos_que_fallan(invalida)

    assert isinstance(fallas, pl.DataFrame)
    assert fallas.height > 0
    assert "period" in fallas["column"].to_list()


def test_un_tipo_incorrecto_se_reporta(muestra):
    mal_tipada = muestra.with_columns(pl.col("temperature_c").cast(pl.String))

    with pytest.raises(ValueError, match="temperature_c"):
        validar_esquema(mal_tipada)
