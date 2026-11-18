"""Etapa 4: la imagen está lista para la nube.

En la nube no hay una carpeta del computador del equipo que montar como volumen,
así que el modelo debe viajar dentro de la imagen. Son pruebas estáticas: leen
los archivos, no ejecutan Docker.
"""

import re

import pytest

from .conftest import RAIZ

pytestmark = pytest.mark.etapa4


def _leer(nombre: str) -> str:
    texto = (RAIZ / nombre).read_text()
    return "\n".join(
        linea
        for linea in texto.splitlines()
        if not linea.lstrip().startswith("#")
    )


def test_el_dockerfile_copia_el_modelo_a_la_imagen():
    assert re.search(
        r"^COPY\s+models\s+\S*models", _leer("Dockerfile"), re.MULTILINE
    ), "El Dockerfile no copia la carpeta models."


def test_el_dockerignore_no_excluye_el_modelo():
    lineas = {linea.strip() for linea in _leer(".dockerignore").splitlines()}
    assert lineas, "El .dockerignore está vacío."
    assert "models" not in lineas, "El .dockerignore excluye models."


def test_la_imagen_sigue_sin_llevar_credenciales():
    lineas = {linea.strip() for linea in _leer(".dockerignore").splitlines()}
    assert ".env" in lineas, "El .dockerignore ya no excluye .env."
