"""Fixtures compartidos: un modelo sintético pequeño y servicios de prueba.

Ninguna prueba necesita Docker, red ni los modelos entrenados en `models/`.
Los fixtures no usan código que escribe el equipo, salvo el que cada prueba
declara probar.
"""

import os
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
import pytest
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline, make_pipeline

from src.aguaapr.config import Settings, get_settings
from src.aguaapr.constants import FEATURES, RANGOS
from src.aguaapr.contracts import Servicios

RAIZ = Path(__file__).resolve().parent.parent
CSV_REAL = RAIZ / "data" / "raw" / "water_potability.csv"
CLAVE = "clave-de-prueba"


def hacer_settings(**cambios: Any) -> Settings:
    valores: dict[str, Any] = {
        "model_dir": Path("models"),
        "api_key": CLAVE,
        "log_level": "INFO",
        "grupo": "Grupo de prueba",
    }
    valores.update(cambios)
    return leer_settings(**valores)


def leer_settings(env_file: Path | None = None, **campos: Any) -> Settings:
    """Crea `Settings` sin leer el `.env` de quien ejecuta la prueba.

    Los campos que no se pasan salen del entorno y, si se indica, de `env_file`.
    """
    # El verificador de tipos no ve que `Settings` completa sus campos desde el
    # entorno ni que acepta `_env_file`.
    return Settings(_env_file=env_file, **campos)  # pyright: ignore[reportCallIssue]


@pytest.fixture(autouse=True)
def entorno_de_prueba(monkeypatch: pytest.MonkeyPatch) -> None:
    """Un entorno conocido: sin variables `APR_` ajenas y con la caché limpia."""
    for nombre in list(os.environ):
        if nombre.startswith("APR_"):
            monkeypatch.delenv(nombre)
    monkeypatch.setenv("APR_API_KEY", CLAVE)
    monkeypatch.setenv("APR_GRUPO", "Grupo de prueba")
    get_settings.cache_clear()


def filas_sinteticas(n: int, semilla: int = 0) -> np.ndarray:
    """Mediciones dentro de rango; una de cada diez con `ph` ausente."""
    azar = np.random.default_rng(semilla)
    columnas = [
        azar.uniform(minimo, maximo, n) for minimo, maximo in RANGOS.values()
    ]
    matriz = np.column_stack(columnas)
    matriz[::10, 0] = np.nan
    return matriz


@pytest.fixture(scope="session")
def modelo_sintetico() -> Pipeline:
    matriz = filas_sinteticas(300)
    etiquetas = (np.nan_to_num(matriz[:, 1]) > 250).astype(int)
    modelo = make_pipeline(
        SimpleImputer(strategy="median"),
        RandomForestClassifier(n_estimators=20, random_state=0, n_jobs=1),
    )
    # Con una tabla de polars el pipeline recuerda los nombres de columna.
    return modelo.fit(
        pl.DataFrame(matriz, schema=FEATURES, orient="row"), etiquetas
    )


@pytest.fixture
def metadata() -> dict[str, Any]:
    return {
        "sklearn_version": sklearn.__version__,
        "features": list(FEATURES),
        "metricas_validacion": {"exactitud": 0.9, "f1": 0.8},
    }


@pytest.fixture
def servicios(
    modelo_sintetico: Pipeline, metadata: dict[str, Any]
) -> Servicios:
    return Servicios(
        settings=hacer_settings(), modelo=modelo_sintetico, metadata=metadata
    )


@pytest.fixture
def cabeceras() -> dict[str, str]:
    return {"X-API-Key": CLAVE}


@pytest.fixture
def medicion_valida() -> dict[str, float | None]:
    return {
        "ph": 7.1,
        "Hardness": 190.0,
        "Solids": 21000.0,
        "Chloramines": 7.2,
        "Sulfate": 330.0,
        "Conductivity": 420.0,
        "Organic_carbon": 14.0,
        "Trihalomethanes": 66.0,
        "Turbidity": 3.9,
    }
