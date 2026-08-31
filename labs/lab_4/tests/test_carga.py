"""Pruebas de lectura CSV y lazy."""

from pathlib import Path

import polars as pl
import pytest

from src.meteolab.carga import (
    escanear_temperaturas,
    leer_temperaturas,
)
from tests.conftest import CSV_DEL_CURSO, FILAS_CRUDAS

pytestmark = pytest.mark.etapa2


CSV_PEQUENO = """country,iso_alpha2,iso_alpha3,year,period,temperature_c,parameter,units,source_file
Chile,CL,CHL,2024,JAN,10.0,Mean Temperature,degrees Celsius,source.per
Chile,CL,CHL,2024,FEB,,Mean Temperature,degrees Celsius,source.per
"""


@pytest.fixture
def csv_pequeno(tmp_path: Path) -> Path:
    ruta = tmp_path / "temperaturas.csv"
    ruta.write_text(CSV_PEQUENO, encoding="utf-8")
    return ruta


def test_la_lectura_conserva_tipos_y_nulos(csv_pequeno):
    temperaturas = leer_temperaturas(csv_pequeno)

    assert temperaturas.schema["year"] == pl.Int64
    assert temperaturas.schema["temperature_c"] == pl.Float64
    assert temperaturas["temperature_c"].null_count() == 1


def test_la_lectura_lazy_no_materializa_hasta_collect(csv_pequeno):
    consulta = escanear_temperaturas(csv_pequeno)

    assert isinstance(consulta, pl.LazyFrame)
    assert consulta.collect().equals(leer_temperaturas(csv_pequeno))


def test_la_ruta_inexistente_es_reportada(tmp_path):
    with pytest.raises(FileNotFoundError, match="no_existe"):
        leer_temperaturas(tmp_path / "no_existe.csv")


def test_el_archivo_del_curso_tiene_todas_sus_filas(crudas):
    assert crudas.height == FILAS_CRUDAS
    assert CSV_DEL_CURSO.exists()
