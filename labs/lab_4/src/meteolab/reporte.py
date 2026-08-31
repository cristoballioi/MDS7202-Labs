"""Pipelines lazy para analizar únicamente temperaturas mensuales."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from src.meteolab.carga import escanear_temperaturas
from src.meteolab.constantes import (
    PAISES_COMPARACION,
    PERIODOS_MENSUALES,
    RUTA_CSV,
)
from src.meteolab.derivadas import agregar_fecha_mensual
from src.meteolab.metricas import (
    anomalias_mensuales,
    resumen_anual_desde_mensuales,
    resumen_mensual,
)


def pipeline_mensual(
    ruta: Path = RUTA_CSV,
    paises: list[str] | tuple[str, ...] = PAISES_COMPARACION,
) -> pl.LazyFrame:
    """Construye el flujo mensual sin ejecutarlo."""
    consulta = escanear_temperaturas(ruta).filter(
        pl.col("period").is_in(PERIODOS_MENSUALES)
        & pl.col("temperature_c").is_not_null()
        & pl.col("iso_alpha3").is_in(paises)
    )
    return agregar_fecha_mensual(consulta).sort("iso_alpha3", "fecha")


def pipeline_resumen_mensual(
    ruta: Path = RUTA_CSV,
    paises: list[str] | tuple[str, ...] = PAISES_COMPARACION,
) -> pl.LazyFrame:
    """Construye la climatología mensual."""
    return resumen_mensual(pipeline_mensual(ruta, paises))


def pipeline_resumen_anual(
    ruta: Path = RUTA_CSV,
    paises: list[str] | tuple[str, ...] = PAISES_COMPARACION,
) -> pl.LazyFrame:
    """Calcula medias anuales desde meses limpios."""
    return resumen_anual_desde_mensuales(pipeline_mensual(ruta, paises))


def pipeline_anomalias(
    ruta: Path = RUTA_CSV,
    paises: list[str] | tuple[str, ...] = PAISES_COMPARACION,
    umbral: float = 2.0,
) -> pl.LazyFrame:
    """Construye el flujo de anomalías mensuales."""
    return anomalias_mensuales(pipeline_mensual(ruta, paises), umbral=umbral)


def ejecutar_reporte(
    ruta: Path = RUTA_CSV,
    paises: list[str] | tuple[str, ...] = PAISES_COMPARACION,
) -> pl.DataFrame:
    """Materializa la climatología mensual."""
    return pipeline_resumen_mensual(ruta, paises).collect()


def plan_de_ejecucion(
    ruta: Path = RUTA_CSV,
    paises: list[str] | tuple[str, ...] = PAISES_COMPARACION,
    optimizado: bool = True,
) -> str:
    """Devuelve el plan lazy como texto."""
    return pipeline_mensual(ruta, paises).explain(optimized=optimizado)
