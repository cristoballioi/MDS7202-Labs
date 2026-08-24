"""Visualizaciones interactivas con Plotly para el dataset CRU."""

from __future__ import annotations

import plotly.express as px
import polars as pl
from plotly.graph_objects import Figure


def _datos(tabla: pl.DataFrame) -> pl.DataFrame:
    """Deja la tabla Polars en el formato nativo que acepta Plotly Express."""
    return tabla


def nulos_por_columna(resumen: pl.DataFrame) -> Figure:
    """Muestra el conteo de valores ausentes por columna."""
    datos = resumen.sort("nulos", descending=True)
    figura = px.bar(
        _datos(datos),
        x="columna",
        y="nulos",
        text="nulos",
        title="Valores ausentes en el archivo CRU",
        labels={"columna": "Columna", "nulos": "Valores ausentes"},
    )
    return figura.update_layout(showlegend=False)


def serie_mensual(
    mensuales: pl.DataFrame,
    paises: list[str],
) -> Figure:
    """Dibuja la serie mensual de los países seleccionados."""
    datos = mensuales.filter(pl.col("iso_alpha3").is_in(paises)).sort("fecha")
    return px.line(
        _datos(datos),
        x="fecha",
        y="temperature_c",
        color="country",
        hover_data=["iso_alpha3", "year", "period"],
        title="Temperaturas medias mensuales",
        labels={
            "fecha": "Fecha",
            "temperature_c": "Temperatura (°C)",
            "country": "País",
        },
    )


def climatologia_mensual(
    resumen: pl.DataFrame,
    paises: list[str],
) -> Figure:
    """Compara la media histórica de cada mes entre países."""
    datos = resumen.filter(pl.col("iso_alpha3").is_in(paises))
    return px.line(
        _datos(datos),
        x="month",
        y="temperature_mean",
        color="country",
        markers=True,
        title="Climatología mensual por país",
        labels={
            "month": "Mes",
            "temperature_mean": "Temperatura media (°C)",
            "country": "País",
        },
    )


def serie_anual(
    anuales: pl.DataFrame,
    paises: list[str],
) -> Figure:
    """Dibuja medias anuales calculadas desde observaciones mensuales."""
    datos = anuales.filter(pl.col("iso_alpha3").is_in(paises)).sort("year")
    return px.line(
        _datos(datos),
        x="year",
        y="temperature_mean",
        color="country",
        title="Temperatura media anual calculada desde meses",
        labels={
            "year": "Año",
            "temperature_mean": "Temperatura media (°C)",
            "country": "País",
        },
    )


def anomalias(
    datos: pl.DataFrame,
    paises: list[str],
) -> Figure:
    """Dibuja las anomalías estandarizadas de las filas mensuales."""
    datos = datos.filter(pl.col("iso_alpha3").is_in(paises)).sort("fecha")
    return px.scatter(
        _datos(datos),
        x="fecha",
        y="standardized_anomaly",
        color="is_anomaly",
        facet_row="country",
        hover_data=["iso_alpha3", "period", "temperature_c"],
        title="Anomalías estandarizadas por país y mes",
        labels={
            "fecha": "Fecha",
            "standardized_anomaly": "Anomalía estandarizada",
            "is_anomaly": "¿Anómala?",
            "country": "País",
        },
    )
