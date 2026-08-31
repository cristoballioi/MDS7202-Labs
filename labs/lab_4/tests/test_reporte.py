"""Pruebas de los pipelines lazy mensuales."""

import polars as pl
import pytest

from src.meteolab.reporte import (
    ejecutar_reporte,
    pipeline_anomalias,
    pipeline_mensual,
    pipeline_resumen_anual,
    pipeline_resumen_mensual,
    plan_de_ejecucion,
)
from tests.conftest import CSV_DEL_CURSO

pytestmark = pytest.mark.etapa7


def test_el_pipeline_mensual_no_ejecuta_hasta_collect():
    consulta = pipeline_mensual(CSV_DEL_CURSO, ["CHL"])

    assert isinstance(consulta, pl.LazyFrame)


def test_el_plan_contiene_el_scan_y_el_filtro():
    plan = plan_de_ejecucion(CSV_DEL_CURSO, ["CHL"])

    assert "SCAN" in plan.upper()
    assert "CHL" in plan
    assert "DJF" not in plan


def test_el_pipeline_mensual_descarta_periodos_no_mensuales():
    resultado = pipeline_mensual(CSV_DEL_CURSO, ["CHL"]).collect()

    assert resultado.height == 1500
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


def test_el_resumen_mensual_entrega_doce_filas_por_pais():
    resultado = pipeline_resumen_mensual(CSV_DEL_CURSO, ["CHL"]).collect()

    assert resultado.height == 12
    assert resultado["iso_alpha3"].unique().to_list() == ["CHL"]


def test_el_resumen_anual_se_calcula_desde_meses():
    resultado = pipeline_resumen_anual(CSV_DEL_CURSO, ["CHL"]).collect()

    assert resultado.height == 125
    assert resultado["meses_disponibles"].unique().to_list() == [12]


def test_el_pipeline_de_anomalias_es_lazy():
    consulta = pipeline_anomalias(CSV_DEL_CURSO, ["CHL"])

    assert isinstance(consulta, pl.LazyFrame)
    assert consulta.collect()["is_anomaly"].null_count() == 0


def test_ejecutar_reporte_materializa_el_resumen():
    reporte = ejecutar_reporte(CSV_DEL_CURSO, ["CHL"])

    assert isinstance(reporte, pl.DataFrame)
    assert reporte.height == 12
