"""Pruebas de fechas nativas."""

from datetime import date

import polars as pl
import pytest

from src.meteolab.derivadas import (
    agregar_fecha_mensual,
)

pytestmark = pytest.mark.etapa5


def test_agregar_fecha_mensual_produce_date(muestra):
    mensuales = agregar_fecha_mensual(muestra)

    assert mensuales.schema["fecha"] == pl.Date
    assert mensuales.schema["month"] == pl.Int8
    assert mensuales["fecha"].to_list() == [
        date(1901, 1, 1),
        date(1901, 2, 1),
        date(1902, 1, 1),
        date(1901, 1, 1),
    ]


def test_agregar_fecha_mensual_tambien_funciona_en_lazy(muestra):
    resultado = agregar_fecha_mensual(muestra.lazy()).collect()

    assert resultado.schema["fecha"] == pl.Date
