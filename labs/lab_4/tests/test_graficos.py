"""Pruebas de las visualizaciones Plotly provistas."""

import plotly.graph_objects as go
import pytest

from src.meteolab import graficos
from src.meteolab.derivadas import agregar_fecha_mensual
from src.meteolab.limpieza import limpiar_temperaturas, resumen_de_nulos
from src.meteolab.metricas import resumen_mensual


@pytest.mark.etapa4
def test_grafico_de_nulos(crudas):
    figura = graficos.nulos_por_columna(resumen_de_nulos(crudas))

    assert isinstance(figura, go.Figure)


@pytest.mark.etapa5
def test_grafico_mensual(crudas):
    mensuales = agregar_fecha_mensual(limpiar_temperaturas(crudas))
    figura = graficos.serie_mensual(mensuales.head(100), ["CHL"])

    assert isinstance(figura, go.Figure)


@pytest.mark.etapa5
def test_grafico_de_climatologia_mensual(crudas):
    mensuales = agregar_fecha_mensual(limpiar_temperaturas(crudas))
    resumen = resumen_mensual(mensuales, ["CHL"])
    figura = graficos.climatologia_mensual(resumen, ["CHL"])

    assert isinstance(figura, go.Figure)
