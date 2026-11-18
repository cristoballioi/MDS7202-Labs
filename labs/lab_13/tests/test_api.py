"""Etapa 2: la API de inferencia cumple su contrato."""

import json
import logging

import pytest
from fastapi.testclient import TestClient

from src.aguaapr.app import crear_app
from src.aguaapr.constants import FEATURES

pytestmark = pytest.mark.etapa2


@pytest.fixture
def cliente(servicios) -> TestClient:
    return TestClient(crear_app(servicios), raise_server_exceptions=False)


def test_la_ruta_de_informacion_describe_el_modelo(cliente: TestClient):
    cuerpo = cliente.get("/").json()
    assert set(cuerpo["entrada"]) == set(FEATURES)
    assert "metricas_validacion" in cuerpo


def test_la_ruta_de_vida_es_publica(cliente: TestClient):
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}


def test_la_prediccion_responde_con_el_contrato(
    cliente: TestClient, cabeceras: dict, medicion_valida: dict
):
    respuesta = cliente.post(
        "/predict", json=medicion_valida, headers=cabeceras
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["prediccion"] in (0, 1)
    assert 0.0 <= cuerpo["probabilidad"] <= 1.0
    assert set(cuerpo) == {"prediccion", "probabilidad"}


def test_la_prediccion_acepta_valores_ausentes_opcionales(
    cliente: TestClient, cabeceras: dict, medicion_valida: dict
):
    medicion_valida.update(ph=None, Sulfate=None, Trihalomethanes=None)
    respuesta = cliente.post(
        "/predict", json=medicion_valida, headers=cabeceras
    )
    assert respuesta.status_code == 200


def test_una_medicion_fuera_de_rango_responde_422_con_el_campo(
    cliente: TestClient, cabeceras: dict, medicion_valida: dict
):
    medicion_valida["ph"] = 15
    respuesta = cliente.post(
        "/predict", json=medicion_valida, headers=cabeceras
    )
    assert respuesta.status_code == 422
    assert "ph" in str(respuesta.json()["detail"])


def test_una_columna_obligatoria_ausente_responde_422(
    cliente: TestClient, cabeceras: dict, medicion_valida: dict
):
    del medicion_valida["Hardness"]
    respuesta = cliente.post(
        "/predict", json=medicion_valida, headers=cabeceras
    )
    assert respuesta.status_code == 422


@pytest.mark.parametrize("cabecera", [{}, {"X-API-Key": "incorrecta"}])
def test_sin_clave_valida_responde_401_y_no_ejecuta_el_modelo(
    servicios, medicion_valida: dict, cabecera: dict
):
    class ModeloQueNoDebeLlamarse:
        def predict_proba(self, matriz):  # pragma: no cover
            raise AssertionError("El modelo no debía ejecutarse.")

    servicios.modelo = ModeloQueNoDebeLlamarse()
    cliente = TestClient(crear_app(servicios), raise_server_exceptions=False)
    respuesta = cliente.post("/predict", json=medicion_valida, headers=cabecera)
    assert respuesta.status_code == 401


def test_un_error_interno_responde_500_sin_exponer_el_detalle(
    servicios, cabeceras: dict, medicion_valida: dict
):
    class ModeloRoto:
        def predict_proba(self, matriz):
            raise RuntimeError("detalle-interno-secreto")

    servicios.modelo = ModeloRoto()
    cliente = TestClient(crear_app(servicios), raise_server_exceptions=False)
    respuesta = cliente.post(
        "/predict", json=medicion_valida, headers=cabeceras
    )
    assert respuesta.status_code == 500
    assert "detalle-interno-secreto" not in respuesta.text


def test_el_detalle_del_error_interno_queda_en_el_registro(
    servicios, cabeceras: dict, medicion_valida: dict, caplog
):
    class ModeloRoto:
        def predict_proba(self, matriz):
            raise RuntimeError("detalle-interno-secreto")

    servicios.modelo = ModeloRoto()
    cliente = TestClient(crear_app(servicios), raise_server_exceptions=False)
    with caplog.at_level("ERROR", logger="aguaapr"):
        cliente.post("/predict", json=medicion_valida, headers=cabeceras)
    errores = [r for r in caplog.records if r.exc_info]
    assert errores
    assert "detalle-interno-secreto" in str(errores[0].exc_info[1])


def test_cada_solicitud_deja_un_registro_json_con_su_identificador(
    cliente: TestClient, caplog: pytest.LogCaptureFixture
):
    with caplog.at_level(logging.INFO, logger="aguaapr"):
        respuesta = cliente.get("/health", headers={"X-Request-ID": "abc123"})
    assert respuesta.headers["X-Request-ID"] == "abc123"
    campos = [
        r.__dict__["campos"] for r in caplog.records if "campos" in r.__dict__
    ]
    assert campos[-1]["id_solicitud"] == "abc123"
    assert campos[-1]["estado"] == 200
    assert json.dumps(campos[-1])  # serializable como una línea JSON
