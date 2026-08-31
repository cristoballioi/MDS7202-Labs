"""Funciones para declarar y validar el esquema CRU."""

from __future__ import annotations

import pandera.polars as pa
import polars as pl

from src.meteolab.constantes import ESQUEMA_CRU, PERIODOS_VALIDOS

ESQUEMA_TEMPERATURAS = pa.DataFrameSchema(
    {
        "country": pa.Column(pl.String),
        "iso_alpha2": pa.Column(pl.String),
        "iso_alpha3": pa.Column(pl.String),
        "year": pa.Column(pl.Int64, pa.Check.between(1901, 2025)),
        "period": pa.Column(pl.String, pa.Check.isin(PERIODOS_VALIDOS)),
        "temperature_c": pa.Column(pl.Float64, nullable=True),
        "parameter": pa.Column(
            pl.String, pa.Check.equal_to("Mean Temperature")
        ),
        "units": pa.Column(pl.String, pa.Check.equal_to("degrees Celsius")),
        "source_file": pa.Column(pl.String),
    }
)


def comparar_esquema(temperaturas: pl.DataFrame) -> list[str]:
    """Devuelve diferencias entre el esquema real y el esperado."""
    esquema_real = temperaturas.schema
    diferencias = []
    for columna, tipo_esperado in ESQUEMA_CRU.items():
        tipo_real = esquema_real.get(columna)
        if tipo_real is None:
            diferencias.append(f"Falta la columna '{columna}'.")
        elif tipo_real != tipo_esperado:
            diferencias.append(
                f"La columna '{columna}' tiene tipo {tipo_real}; se "
                f"esperaba {tipo_esperado}."
            )
    return diferencias


def validar_esquema(temperaturas: pl.DataFrame) -> None:
    """Comprueba los nombres y tipos de las columnas."""
    diferencias = comparar_esquema(temperaturas)
    if diferencias:
        raise ValueError("\n".join(diferencias))


def validar_datos(temperaturas: pl.DataFrame) -> pl.DataFrame:
    """Valida tipos, periodos, unidades y valores faltantes."""
    return ESQUEMA_TEMPERATURAS.validate(temperaturas)


def casos_que_fallan(temperaturas: pl.DataFrame) -> pl.DataFrame:
    """Devuelve los incumplimientos sin ocultar sus columnas."""
    try:
        ESQUEMA_TEMPERATURAS.validate(temperaturas, lazy=True)
    except pa.errors.SchemaErrors as errores:
        return errores.failure_cases
    return pl.DataFrame(
        schema={
            "schema_context": pl.String,
            "column": pl.String,
            "check": pl.String,
            "check_number": pl.Int64,
            "failure_case": pl.String,
            "index": pl.Int64,
        }
    )
