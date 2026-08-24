"""Fixtures compartidas del dataset CRU."""

from pathlib import Path

import polars as pl
import pytest

from src.meteolab.carga import leer_temperaturas
from src.meteolab.constantes import RUTA_CSV

RUTA_PROYECTO = Path(__file__).resolve().parent.parent
CSV_DEL_CURSO = RUTA_PROYECTO / RUTA_CSV
FILAS_CRUDAS = 408_000
PAISES = 192
ANIOS = 125
PERIODOS = 17


@pytest.fixture(scope="session")
def crudas() -> pl.DataFrame:
    return leer_temperaturas(CSV_DEL_CURSO)


@pytest.fixture
def muestra() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "country": ["Chile", "Chile", "Chile", "Peru"],
            "iso_alpha2": ["CL", "CL", "CL", "PE"],
            "iso_alpha3": ["CHL", "CHL", "CHL", "PER"],
            "year": [1901, 1901, 1902, 1901],
            "period": ["JAN", "FEB", "JAN", "JAN"],
            "temperature_c": [10.0, 12.0, 11.0, 20.0],
            "parameter": ["Mean Temperature"] * 4,
            "units": ["degrees Celsius"] * 4,
            "source_file": ["source.per"] * 4,
        }
    )
