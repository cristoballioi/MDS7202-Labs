"""Funciones de lectura del CSV que deben completar ustedes."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from src.meteolab.constantes import RUTA_CSV


def leer_temperaturas(ruta: Path = RUTA_CSV) -> pl.DataFrame:
    """Lee el CSV CRU con sus tipos y valores faltantes."""
    raise NotImplementedError(
        "Completen leer_temperaturas antes de ejecutar el programa."
    )


def escanear_temperaturas(ruta: Path = RUTA_CSV) -> pl.LazyFrame:
    """Construye una consulta lazy sobre el CSV."""
    raise NotImplementedError(
        "Completen escanear_temperaturas antes de ejecutar el programa."
    )
