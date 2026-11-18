"""Lectura y escritura del artefacto del modelo.

El artefacto vive en una carpeta con dos archivos: `model.joblib` (el pipeline
entrenado) y `metadata.json` (cómo se entrenó).
"""

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import polars as pl
from sklearn.pipeline import Pipeline

from src.aguaapr.constants import FEATURES
from src.aguaapr.validation import MedicionAgua


class ErrorArtefacto(Exception):
    """El artefacto no existe o no calza con el contrato del servicio."""


def guardar_artefacto(
    modelo: Pipeline, metadata: dict[str, Any], directorio: Path
) -> Path:
    directorio.mkdir(parents=True, exist_ok=True)
    # compress=3 reduce el bosque de 16 MB a unos 4 MB sin cambiar el tiempo de
    # carga: el artefacto se versiona en Git y viaja en el material.
    joblib.dump(modelo, directorio / "model.joblib", compress=3)
    texto = json.dumps(metadata, indent=2, ensure_ascii=False)
    (directorio / "metadata.json").write_text(texto + "\n", encoding="utf-8")
    return directorio


def leer_metadata(directorio: Path) -> dict[str, Any]:
    archivo = directorio / "metadata.json"
    if not archivo.exists():
        raise ErrorArtefacto(
            f"No existe un artefacto en {directorio}. "
            "Entrenen el modelo con `python -m src.aguaapr.training`."
        )
    return json.loads(archivo.read_text(encoding="utf-8"))


def a_tabla(mediciones: Sequence[MedicionAgua]) -> pl.DataFrame:
    """Convierte mediciones validadas en una tabla con una columna por variable.

    Las columnas siguen el orden de `FEATURES` y una medición ausente queda
    como nulo. Con los nombres a la vista, scikit-learn rechaza una tabla cuyas
    columnas no coincidan con las del entrenamiento.
    """
    return pl.DataFrame(
        [m.model_dump() for m in mediciones],
        schema=dict.fromkeys(FEATURES, pl.Float64),
    )


def predecir(modelo: Pipeline, tabla: pl.DataFrame) -> tuple[np.ndarray, ...]:
    """Devuelve (clases, probabilidades de ser potable) para cada fila."""
    probabilidades = modelo.predict_proba(tabla)[:, 1]
    return (probabilidades > 0.5).astype(int), probabilidades
