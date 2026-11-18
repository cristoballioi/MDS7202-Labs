"""Etapa 2: la configuración se lee del entorno y no expone secretos."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from src.aguaapr.config import Settings, get_settings

from .conftest import RAIZ, leer_settings

pytestmark = pytest.mark.etapa2


def test_aplica_los_valores_por_defecto():
    settings = leer_settings()
    assert settings.model_dir == Path("models")
    assert settings.log_level == "INFO"


def test_lee_las_variables_con_prefijo(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APR_GRUPO", "Juanito y Pepito")
    monkeypatch.setenv("APR_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("APR_MODEL_DIR", "/modelos")
    settings = leer_settings()
    assert settings.grupo == "Juanito y Pepito"
    assert settings.log_level == "DEBUG"
    assert settings.model_dir == Path("/modelos")


@pytest.mark.parametrize(
    ("variable", "campo"),
    [("APR_API_KEY", "api_key"), ("APR_GRUPO", "grupo")],
)
def test_sin_una_variable_obligatoria_falla_nombrando_el_campo(
    monkeypatch: pytest.MonkeyPatch, variable: str, campo: str
):
    monkeypatch.delenv(variable)
    with pytest.raises(ValidationError, match=campo):
        leer_settings()


def test_una_variable_obligatoria_vacia_no_vale(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("APR_GRUPO", "")
    # Sin `env_ignore_empty`, una variable vacía llegaría como texto vacío.
    with pytest.raises(ValidationError, match="grupo"):
        leer_settings()


def test_la_clave_es_un_secreto(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APR_API_KEY", "clave-secreta")
    settings = leer_settings()
    assert "clave-secreta" not in repr(settings)
    assert "clave-secreta" not in str(settings)
    assert settings.api_key.get_secret_value() == "clave-secreta"


def test_lee_el_archivo_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("APR_GRUPO")
    archivo = tmp_path / ".env"
    archivo.write_text("APR_GRUPO=Desde el archivo\nAPR_OTRA=ignorada\n")
    assert leer_settings(archivo).grupo == "Desde el archivo"


def test_una_variable_del_entorno_gana_al_archivo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("APR_GRUPO", "Desde el entorno")
    archivo = tmp_path / ".env"
    archivo.write_text("APR_GRUPO=Desde el archivo\n")
    assert leer_settings(archivo).grupo == "Desde el entorno"


def test_lee_el_env_de_la_carpeta_de_trabajo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """`Settings` debe encontrar sola el `.env`, como lo hacen uvicorn y streamlit."""
    monkeypatch.delenv("APR_API_KEY")
    monkeypatch.delenv("APR_GRUPO")
    (tmp_path / ".env").write_text(
        "APR_API_KEY=clave-del-archivo\nAPR_GRUPO=Juanito y Pepito\n"
    )
    monkeypatch.chdir(tmp_path)
    settings = Settings()  # pyright: ignore[reportCallIssue]
    assert settings.grupo == "Juanito y Pepito"
    assert settings.api_key.get_secret_value() == "clave-del-archivo"


def test_get_settings_lee_una_sola_vez(monkeypatch: pytest.MonkeyPatch):
    primera = get_settings()
    monkeypatch.setenv("APR_GRUPO", "Otro grupo")
    assert get_settings() is primera


def test_el_archivo_de_ejemplo_no_trae_secretos_reales():
    ejemplo = RAIZ / ".env.example"
    assert ejemplo.exists(), "Falta el archivo .env.example."
    texto = ejemplo.read_text()
    valores = {
        linea.split("=", 1)[0]: linea.split("=", 1)[1]
        for linea in texto.splitlines()
        if "=" in linea and not linea.startswith("#")
    }
    for nombre in ("APR_API_KEY", "APR_GRUPO", "APR_LOG_LEVEL"):
        assert nombre in valores, f"Falta {nombre} en el .env.example."
    for nombre in ("APR_API_KEY", "APR_GRUPO"):
        assert valores[nombre].startswith("cambiar"), (
            f"El valor de {nombre} debe empezar con `cambiar`."
        )
