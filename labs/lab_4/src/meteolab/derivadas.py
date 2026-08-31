"""Funciones para construir fechas mensuales."""

from __future__ import annotations

import polars as pl

from src.meteolab.constantes import MESES, Tabla


def agregar_fecha_mensual(mensuales: Tabla) -> Tabla:
    """Agrega month y una fecha nativa de Polars."""
    return mensuales.with_columns(
        pl.col("period")
        .replace_strict(MESES, return_dtype=pl.Int8)
        .alias("month")
    ).with_columns(pl.date(pl.col("year"), pl.col("month"), 1).alias("fecha"))
