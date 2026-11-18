"""Etapa 3: los archivos de Docker cumplen lo que el enunciado declara.

Son pruebas estáticas: leen los archivos, no ejecutan Docker. Que la imagen
construya y el contenedor responda se comprueba a mano (ver el notebook).
"""

import re

import pytest

from .conftest import RAIZ

pytestmark = pytest.mark.etapa3


def _leer(nombre: str) -> str:
    texto = (RAIZ / nombre).read_text()
    sin_comentarios = [
        linea
        for linea in texto.splitlines()
        if not linea.lstrip().startswith("#")
    ]
    return "\n".join(sin_comentarios)


def test_el_dockerignore_excluye_secretos_y_entornos():
    lineas = {linea.strip() for linea in _leer(".dockerignore").splitlines()}
    for patron in (".env", ".venv"):
        assert patron in lineas, f"El .dockerignore no excluye {patron}."


def test_el_dockerfile_fija_la_version_de_las_imagenes():
    desde = re.findall(r"^FROM\s+(\S+)", _leer("Dockerfile"), re.MULTILINE)
    assert desde, "El Dockerfile no tiene FROM."
    for imagen in desde:
        assert ":" in imagen, f"{imagen} no fija una versión."
        assert not imagen.endswith(":latest"), imagen


def test_el_dockerfile_instala_solo_el_grupo_servicio_desde_el_lock():
    comando = re.search(r"RUN\s+(uv sync[^\n]*)", _leer("Dockerfile"))
    assert comando, "El Dockerfile no instala con `uv sync`."
    assert "--locked" in comando.group(1)
    assert "--only-group servicio" in comando.group(1)


def test_el_dockerfile_no_copia_todo_el_contexto():
    assert _leer("Dockerfile"), "El Dockerfile está vacío."
    assert not re.search(r"^COPY\s+\.\s+\S+", _leer("Dockerfile"), re.MULTILINE)


def test_el_dockerfile_no_corre_como_superusuario():
    usuarios = re.findall(r"^USER\s+(\S+)", _leer("Dockerfile"), re.MULTILINE)
    assert usuarios, "El Dockerfile no define USER."
    assert usuarios[-1] not in {"root", "0"}


def test_el_dockerfile_declara_su_comprobacion_de_salud():
    assert "HEALTHCHECK" in _leer("Dockerfile")


def test_el_dockerfile_no_trae_credenciales_literales():
    assert _leer("Dockerfile"), "El Dockerfile está vacío."
    literal = re.search(
        r"(KEY|SECRET|PASSWORD|TOKEN)\w*\s*[=:]\s*[^\s$\"'{]{4,}",
        _leer("Dockerfile"),
        re.IGNORECASE,
    )
    assert literal is None, f"Hay una credencial literal: {literal.group(0)}"


def test_el_dockerfile_ejecuta_la_api_y_la_interfaz():
    dockerfile = _leer("Dockerfile")
    assert "uvicorn" in dockerfile, "El Dockerfile no ejecuta la API."
    assert "streamlit" in dockerfile, "El Dockerfile no ejecuta la interfaz."


def test_el_dockerfile_expone_los_dos_puertos():
    expuestos = re.findall(
        r"^EXPOSE\s+(.+)$", _leer("Dockerfile"), re.MULTILINE
    )
    assert expuestos, "El Dockerfile no tiene EXPOSE."
    assert {"8000", "8501"} <= set(" ".join(expuestos).split())
