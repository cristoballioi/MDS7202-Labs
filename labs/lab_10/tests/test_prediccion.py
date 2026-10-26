import pytest

from src.radio_fcfm.contratos import FRANJAS
from src.radio_fcfm.pipeline import construir_pipeline
from src.radio_fcfm.prediccion import predecir_animo

pytestmark = pytest.mark.etapa4


@pytest.fixture
def modelo(corpus_sintetico):
    letras, estados = corpus_sintetico
    return construir_pipeline().fit(letras, estados)


def test_predecir_animo_devuelve_una_fila_por_letra(modelo):
    letras = ["sol baile risa", "fuego guerra odio", "lluvia adios frio"]

    tabla = predecir_animo(modelo, letras)

    assert list(tabla.columns) == ["animo", "franja", "confianza"]
    assert len(tabla) == 3


def test_predecir_animo_elige_la_clase_mas_probable(modelo):
    letras = ["sol baile risa fiesta", "fuego guerra odio furia"]

    tabla = predecir_animo(modelo, letras)

    assert list(tabla["animo"]) == ["happy", "angry"]


def test_la_franja_corresponde_al_animo_predicho(modelo):
    tabla = predecir_animo(modelo, ["lluvia adios frio", "sol baile risa"])

    for animo, franja in zip(tabla["animo"], tabla["franja"], strict=True):
        assert franja == FRANJAS[animo]


def test_la_confianza_es_la_probabilidad_de_la_clase_elegida(modelo):
    letras = ["sol baile risa", "calma brisa luna", "yo tu ayer"]

    tabla = predecir_animo(modelo, letras)

    assert tabla["confianza"].between(0, 1).all()
    maximos = modelo.predict_proba(letras).max(axis=1)
    assert tabla["confianza"].to_numpy() == pytest.approx(maximos)


def test_predecir_animo_limpia_las_marcas_de_la_letra(modelo):
    # Las palabras entre corchetes están en el vocabulario del modelo: si la
    # función no las quitara, cambiarían la predicción de la primera letra.
    con_marcas = "[fuego guerra odio]\nsol   baile"
    sin_marcas = "sol baile"

    tabla = predecir_animo(modelo, [con_marcas, sin_marcas])

    assert tabla["confianza"][0] == pytest.approx(tabla["confianza"][1])
