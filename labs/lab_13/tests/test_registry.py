"""Etapa 1: la carga del artefacto rechaza lo que no calza con el contrato."""

import json
from pathlib import Path

import pytest

from src.aguaapr.artifacts import ErrorArtefacto, guardar_artefacto
from src.aguaapr.registry import cargar_modelo

from .conftest import RAIZ

pytestmark = pytest.mark.etapa1


@pytest.fixture
def directorio(tmp_path: Path, modelo_sintetico, metadata) -> Path:
    return guardar_artefacto(modelo_sintetico, metadata, tmp_path)


def test_carga_el_modelo_y_devuelve_su_metadata(directorio: Path):
    modelo, metadata = cargar_modelo(directorio)
    assert "features" in metadata
    assert hasattr(modelo, "predict_proba")


def test_el_artefacto_entregado_carga_y_pesa_poco():
    modelos = RAIZ / "models"
    modelo, _ = cargar_modelo(modelos)
    assert hasattr(modelo, "predict_proba")
    peso_mb = (modelos / "model.joblib").stat().st_size / 1e6
    assert peso_mb < 5, f"El modelo pesa {peso_mb:.1f} MB"


def test_rechaza_variables_en_otro_orden(directorio: Path):
    archivo = directorio / "metadata.json"
    metadata = json.loads(archivo.read_text())
    metadata["features"] = metadata["features"][::-1]
    archivo.write_text(json.dumps(metadata))
    with pytest.raises(ErrorArtefacto, match="variables"):
        cargar_modelo(directorio)


def test_rechaza_otra_version_de_scikit_learn(directorio: Path):
    archivo = directorio / "metadata.json"
    metadata = json.loads(archivo.read_text())
    metadata["sklearn_version"] = "0.0.1"
    archivo.write_text(json.dumps(metadata))
    with pytest.raises(ErrorArtefacto, match=r"scikit-learn.*0\.0\.1"):
        cargar_modelo(directorio)


def test_una_carpeta_sin_artefacto_se_informa(tmp_path: Path):
    with pytest.raises(ErrorArtefacto, match="No existe"):
        cargar_modelo(tmp_path / "no-existe")
