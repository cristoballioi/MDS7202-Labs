"""Funciones para revisar nulos y claves temporales."""

from __future__ import annotations

import polars as pl

from src.meteolab.constantes import Tabla


def resumen_de_nulos(temperaturas: pl.DataFrame) -> pl.DataFrame:
    """Devuelve conteos y porcentajes de nulos por columna."""
    raise NotImplementedError(
        "Completen resumen_de_nulos antes de ejecutar el programa."
    )


def claves_repetidas(temperaturas: Tabla) -> Tabla:
    """Cuenta repeticiones de país, año y periodo."""
    raise NotImplementedError(
        "Completen claves_repetidas antes de ejecutar el programa."
    )


def limpiar_temperaturas(temperaturas: Tabla) -> Tabla:
    """Conserva el contrato de periodos y los nulos válidos."""
    raise NotImplementedError(
        "Completen limpiar_temperaturas antes de ejecutar el programa."
    )
