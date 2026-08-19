"""Smoke test de la app Streamlit. Este archivo lo entrega el curso.

Pasa cuando la librería de los estudiantes está completa. No basta con que la
app cargue: también se ejercitan las operaciones, porque varias solo se
aplican cuando se seleccionan en el pipeline.
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

RUTA_APP = Path(__file__).resolve().parent.parent / "app.py"

pytestmark = pytest.mark.etapa7

TIEMPO_LIMITE = 90

OPERACIONES_DEL_PIPELINE = [
    "Negativo",
    "Escala de grises",
    "Canal",
    "Volteo",
    "Convolución",
    "Suma",
    "Resta",
    "Multiplicación",
    "Saturación",
    "Contraste",
]


@pytest.fixture
def app():
    at = AppTest.from_file(RUTA_APP)
    at.run(timeout=TIEMPO_LIMITE)
    return at


def test_app_no_lanza_excepciones(app):
    assert not app.exception


def test_pipeline_completo_se_aplica_sin_avisos(app):
    """Con la librería terminada, ninguna operación debe fallar."""
    app.sidebar.multiselect[0].set_value(OPERACIONES_DEL_PIPELINE)
    app.run(timeout=TIEMPO_LIMITE)

    assert not app.exception
    assert not app.warning, [aviso.value for aviso in app.warning]
    assert app.success


def test_mezclar_imagenes_de_distinto_tamano_avisa_en_vez_de_caerse(app):
    """Operar dos `Imagen` de dimensiones distintas debe lanzar ValueError.

    La app lo convierte en un aviso: si no aparece, falta la validación de
    dimensiones de la Etapa 3.
    """
    app.sidebar.multiselect[0].set_value(["Mezcla con otra imagen"])
    app.run(timeout=TIEMPO_LIMITE)

    assert not app.exception
    assert any("no calzan" in aviso.value for aviso in app.warning)


def test_reordenar_el_pipeline_cambia_el_orden_de_aplicacion(app):
    """Los controles de orden reordenan las operaciones del pipeline."""
    app.sidebar.multiselect[0].set_value(["Negativo", "Escala de grises"])
    app.run(timeout=TIEMPO_LIMITE)

    bajar = [
        boton
        for boton in app.sidebar.button
        if boton.proto.label == ":material/keyboard_arrow_down:"
    ]
    bajar[0].click()
    app.run(timeout=TIEMPO_LIMITE)

    assert not app.exception
    assert app.session_state["operaciones"] == [
        "Escala de grises",
        "Negativo",
    ]


def test_operar_por_la_derecha_no_rompe_la_app(app):
    """`__radd__` y `__rsub__` se ejercitan desde el sidebar."""
    app.sidebar.multiselect[0].set_value(["Suma", "Resta"])
    app.run(timeout=TIEMPO_LIMITE)

    for casilla in app.sidebar.checkbox:
        casilla.set_value(True)
    app.run(timeout=TIEMPO_LIMITE)

    assert not app.exception
    assert not app.warning, [aviso.value for aviso in app.warning]
