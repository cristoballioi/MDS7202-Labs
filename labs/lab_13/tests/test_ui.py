"""Etapa 2: la interfaz gráfica de Streamlit, con la API simulada.

Usa el entorno de pruebas de Streamlit: no abre un navegador ni necesita la API.
"""

import os
import subprocess
import sys

import pytest
from streamlit.testing.v1 import AppTest

from src.aguaapr import ui_cliente
from src.aguaapr.constants import FEATURES, OPCIONALES

from .conftest import RAIZ

pytestmark = pytest.mark.etapa2

UI = str(RAIZ / "src" / "aguaapr" / "ui.py")


def _abrir() -> AppTest:
    return AppTest.from_file(UI, default_timeout=30).run()


def test_el_formulario_trae_un_campo_por_medicion():
    app = _abrir()
    assert not app.exception
    assert len(app.number_input) == len(FEATURES)


def test_los_campos_parten_dentro_de_su_rango():
    app = _abrir()
    for campo in app.number_input:
        minimo, maximo, valor = campo.min, campo.max, campo.value
        assert minimo is not None
        assert maximo is not None
        assert valor is not None
        assert minimo <= valor <= maximo


def test_una_prediccion_potable_se_muestra(monkeypatch: pytest.MonkeyPatch):
    recibido = {}

    def falsa(url, clave, medicion):
        recibido.update(medicion)
        return {"prediccion": 1, "probabilidad": 0.83}

    monkeypatch.setattr(ui_cliente, "consultar_api", falsa)
    app = _abrir()
    app.button[0].click().run()
    assert not app.exception
    assert "Potable" in app.success[0].value
    assert set(recibido) == set(FEATURES)


def test_marcar_sin_dato_envia_un_valor_ausente(
    monkeypatch: pytest.MonkeyPatch,
):
    recibido = {}

    def falsa(url, clave, medicion):
        recibido.update(medicion)
        return {"prediccion": 0, "probabilidad": 0.2}

    monkeypatch.setattr(ui_cliente, "consultar_api", falsa)
    app = _abrir()
    app.checkbox(key="sin_ph").check()
    app.button[0].click().run()
    assert recibido["ph"] is None
    assert all(
        recibido[nombre] is not None
        for nombre in FEATURES
        if nombre not in OPCIONALES
    )
    assert "No potable" in app.warning[0].value


def test_el_error_de_la_api_se_muestra_en_vez_de_una_prediccion(
    monkeypatch: pytest.MonkeyPatch,
):
    def falsa(url, clave, medicion):
        raise ui_cliente.ErrorApi(
            "La API rechazó la medición (422). ph: fuera de rango"
        )

    monkeypatch.setattr(ui_cliente, "consultar_api", falsa)
    app = _abrir()
    app.button[0].click().run()
    assert "ph" in app.error[0].value
    assert not app.success


def test_el_grupo_se_muestra_desde_la_variable_de_entorno(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("APR_GRUPO", "Juanito y Pepito")
    app = _abrir()
    assert [c.value for c in app.caption] == ["Grupo: Juanito y Pepito"]


def test_sin_el_grupo_la_interfaz_avisa_que_falta_la_variable(
    monkeypatch: pytest.MonkeyPatch, tmp_path
):
    monkeypatch.delenv("APR_GRUPO")
    # Desde una carpeta sin `.env`, para que no lo lea del computador de quien corre.
    monkeypatch.chdir(tmp_path)
    app = _abrir()
    assert not app.exception
    assert "APR_GRUPO" in app.error[0].value
    assert len(app.number_input) == 0


def _casilla(app: AppTest, etiqueta: str):
    return next(c for c in app.checkbox if c.label == etiqueta)


def test_permitir_valores_fuera_de_rango_quita_los_limites():
    app = _abrir()
    _casilla(app, "Permitir valores fuera de rango").check().run()
    assert all(c.min is None and c.max is None for c in app.number_input)


def test_con_los_limites_quitados_un_ph_de_15_llega_a_la_api(
    monkeypatch: pytest.MonkeyPatch,
):
    recibido = {}

    def falsa(url, clave, medicion):
        recibido.update(medicion)
        return {"prediccion": 0, "probabilidad": 0.1}

    monkeypatch.setattr(ui_cliente, "consultar_api", falsa)
    app = _abrir()
    _casilla(app, "Permitir valores fuera de rango").check().run()
    app.number_input(key="ph").set_value(15.0)
    app.button[0].click().run()
    assert recibido["ph"] == 15.0


def test_la_interfaz_abre_desde_otra_carpeta_sin_pythonpath(tmp_path):
    """Reproduce lo que pasa en el contenedor: Streamlit no pone la raíz del
    proyecto en el path, y el script debe encontrar `src` por su cuenta."""
    codigo = (
        "from streamlit.testing.v1 import AppTest\n"
        f"app = AppTest.from_file({UI!r}, default_timeout=30).run()\n"
        "assert not app.exception, app.exception\n"
        "assert len(app.number_input) == 9\n"
    )
    entorno = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    resultado = subprocess.run(
        [sys.executable, "-c", codigo],
        cwd=tmp_path,
        env=entorno,
        capture_output=True,
        text=True,
    )
    assert resultado.returncode == 0, resultado.stderr
