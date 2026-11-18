"""Etapa 1: el entrenamiento deja un artefacto completo y reproducible."""

import json
from pathlib import Path

import pytest

from src.aguaapr.constants import FEATURES
from src.aguaapr.training import entrenar

from .conftest import CSV_REAL

pytestmark = pytest.mark.etapa1

CAMPOS = {
    "entrenado_en",
    "sklearn_version",
    "features",
    "hiperparametros",
    "semilla",
    "metricas_validacion",
    "filas_entrenamiento",
    "huella_datos",
}


@pytest.fixture(scope="module")
def artefacto(tmp_path_factory: pytest.TempPathFactory) -> Path:
    directorio = tmp_path_factory.mktemp("modelo")
    entrenar(CSV_REAL, directorio)
    return directorio


def test_el_artefacto_trae_modelo_y_metadata_completa(artefacto: Path):
    assert (artefacto / "model.joblib").exists()
    metadata = json.loads((artefacto / "metadata.json").read_text())
    assert set(metadata) >= CAMPOS
    assert metadata["features"] == FEATURES


def test_el_entrenamiento_es_reproducible(artefacto: Path, tmp_path: Path):
    _, repetida = entrenar(CSV_REAL, tmp_path)
    original = json.loads((artefacto / "metadata.json").read_text())
    assert repetida["metricas_validacion"] == original["metricas_validacion"]
    assert repetida["huella_datos"] == original["huella_datos"]
