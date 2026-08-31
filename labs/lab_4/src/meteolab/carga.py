"""Funciones de lectura del CSV que deben completar ustedes."""

from __future__ import annotations

import polars as pl


def leer_temperaturas(ruta):
    # Usamos read_csv para leer el archivo de forma eager
    # Aplicamos schema_overrides para forzar los tipos de dato de año y temperatura
    return pl.read_csv(
        str(ruta),
        schema_overrides={"year": pl.Int64, "temperature_c": pl.Float64},
    )


def escanear_temperaturas(ruta):
    # Usamos scan_csv para crear un plan de consulta de forma lazy
    # Tambien aplicamos schema_overrides para mantener consistencia con la lectura eager
    return pl.scan_csv(
        str(ruta),
        schema_overrides={"year": pl.Int64, "temperature_c": pl.Float64},
    )
