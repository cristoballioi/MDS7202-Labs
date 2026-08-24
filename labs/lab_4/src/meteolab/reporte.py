"""Pipelines lazy para analizar únicamente temperaturas mensuales."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from src.meteolab.constantes import PAISES_COMPARACION, RUTA_CSV


def pipeline_mensual(
    ruta: Path = RUTA_CSV,
    paises: list[str] | tuple[str, ...] = PAISES_COMPARACION,
) -> pl.LazyFrame:
    """Construye el flujo mensual sin ejecutarlo."""
    raise NotImplementedError(
        "Completen pipeline_mensual antes de ejecutar el programa."
    )


def pipeline_resumen_mensual(
    ruta: Path = RUTA_CSV,
    paises: list[str] | tuple[str, ...] = PAISES_COMPARACION,
) -> pl.LazyFrame:
    """Construye la climatología mensual."""
    raise NotImplementedError(
        "Completen pipeline_resumen_mensual antes de ejecutar el programa."
    )


def pipeline_resumen_anual(
    ruta: Path = RUTA_CSV,
    paises: list[str] | tuple[str, ...] = PAISES_COMPARACION,
) -> pl.LazyFrame:
    """Calcula medias anuales desde meses limpios."""
    raise NotImplementedError(
        "Completen pipeline_resumen_anual antes de ejecutar el programa."
    )


def pipeline_anomalias(
    ruta: Path = RUTA_CSV,
    paises: list[str] | tuple[str, ...] = PAISES_COMPARACION,
    umbral: float = 2.0,
) -> pl.LazyFrame:
    """Construye el flujo de anomalías mensuales."""
    raise NotImplementedError(
        "Completen pipeline_anomalias antes de ejecutar el programa."
    )


def ejecutar_reporte(
    ruta: Path = RUTA_CSV,
    paises: list[str] | tuple[str, ...] = PAISES_COMPARACION,
) -> pl.DataFrame:
    """Materializa la climatología mensual."""
    raise NotImplementedError(
        "Completen ejecutar_reporte antes de ejecutar el programa."
    )


def plan_de_ejecucion(
    ruta: Path = RUTA_CSV,
    paises: list[str] | tuple[str, ...] = PAISES_COMPARACION,
    optimizado: bool = True,
) -> str:
    """Devuelve el plan lazy como texto."""
    raise NotImplementedError(
        "Completen plan_de_ejecucion antes de ejecutar el programa."
    )
