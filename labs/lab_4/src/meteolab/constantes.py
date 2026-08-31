"""Constantes y contratos básicos del dataset CRU."""

from __future__ import annotations

from pathlib import Path

import polars as pl

Tabla = pl.DataFrame | pl.LazyFrame

RUTA_DATOS = Path("data")
RUTA_CSV = RUTA_DATOS / "cru_country_tmp_tidy.csv"

PERIODOS_MENSUALES = (
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
)
PERIODOS_ESTACIONALES = ("DJF", "MAM", "JJA", "SON")
PERIODO_ANUAL = "ANN"
PERIODOS_VALIDOS = (*PERIODOS_MENSUALES, *PERIODOS_ESTACIONALES, "ANN")

PAISES_COMPARACION = (
    "CHL",
    "ARG",
    "BOL",
    "BRA",
    "PER",
    "CAN",
    "EGY",
)

MESES = {
    periodo: numero for numero, periodo in enumerate(PERIODOS_MENSUALES, 1)
}

ESQUEMA_CRU: dict[str, pl.DataType] = {
    "country": pl.String,
    "iso_alpha2": pl.String,
    "iso_alpha3": pl.String,
    "year": pl.Int64,
    "period": pl.String,
    "temperature_c": pl.Float64,
    "parameter": pl.String,
    "units": pl.String,
    "source_file": pl.String,
}


def ruta_existente(ruta: Path) -> Path:
    """Devuelve una ruta existente o levanta un error explicativo."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo '{ruta}'.")
    return ruta
