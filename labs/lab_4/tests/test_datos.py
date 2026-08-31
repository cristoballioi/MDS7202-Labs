"""Invariantes del archivo CRU entregado por el curso."""

import polars as pl
import pytest

from tests.conftest import ANIOS, CSV_DEL_CURSO, FILAS_CRUDAS, PAISES, PERIODOS

pytestmark = pytest.mark.etapa1


@pytest.fixture(scope="module")
def datos_crudos():
    """Lee directamente el CSV para probar sus invariantes iniciales."""
    return pl.read_csv(CSV_DEL_CURSO)


def test_el_archivo_tiene_las_dimensiones_y_columnas_declaradas(datos_crudos):
    assert datos_crudos.shape == (FILAS_CRUDAS, 9)
    assert datos_crudos.columns == [
        "country",
        "iso_alpha2",
        "iso_alpha3",
        "year",
        "period",
        "temperature_c",
        "parameter",
        "units",
        "source_file",
    ]


def test_el_archivo_cubre_paises_anios_y_periodos(datos_crudos):
    assert datos_crudos["iso_alpha3"].n_unique() == PAISES
    assert datos_crudos["year"].n_unique() == ANIOS
    assert datos_crudos["period"].n_unique() == PERIODOS
    assert datos_crudos["year"].min() == 1901
    assert datos_crudos["year"].max() == 2025


def test_cada_pais_tiene_la_grilla_completa_de_periodos_salvo_el_nulo(
    datos_crudos,
):
    conteos = datos_crudos.group_by("iso_alpha3").len()

    assert conteos["len"].unique().to_list() == [2125]
    assert datos_crudos.filter(pl.col("temperature_c").is_null()).height == 192
    assert datos_crudos.filter(pl.col("temperature_c").is_null()).select(
        "year", "period"
    ).unique().rows() == [(2025, "DJF")]
