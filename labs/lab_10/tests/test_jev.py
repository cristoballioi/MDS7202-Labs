import threading

import pytest

from src.radio_fcfm import jev
from src.radio_fcfm.contratos import ESTADOS
from src.radio_fcfm.jev import clasificar_con_jev

pytestmark = pytest.mark.etapa4

LETRAS = ["sol baile risa", "fuego guerra odio", "lluvia adios frio", "calma"]


def _preguntar_falso(letra: str) -> tuple[str, float]:
    return ("happy" if "sol" in letra else "sad"), float(len(letra))


def test_los_criterios_son_los_cuatro_animos_del_dataset():
    assert set(jev.CRITERIOS) == set(ESTADOS)


def test_devuelve_un_animo_y_una_confianza_por_letra_en_orden():
    animos, confianzas = clasificar_con_jev(LETRAS, _preguntar_falso, hilos=3)

    assert animos == ["happy", "sad", "sad", "sad"]
    assert confianzas == [float(len(letra)) for letra in LETRAS]


def test_llama_una_sola_vez_por_letra():
    llamadas = []
    cerrojo = threading.Lock()

    def preguntar(letra):
        with cerrojo:
            llamadas.append(letra)
        return "happy", 0.5

    clasificar_con_jev(LETRAS, preguntar, hilos=4)

    assert sorted(llamadas) == sorted(LETRAS)


def test_una_llamada_que_falla_deja_none_y_no_detiene_a_las_demas():
    def preguntar(letra):
        if "fuego" in letra:
            raise RuntimeError("sin red")
        return "happy", 0.9

    animos, confianzas = clasificar_con_jev(LETRAS, preguntar)

    assert animos == ["happy", None, "happy", "happy"]
    assert confianzas[1] is None


def test_con_cache_no_vuelve_a_llamar_a_la_api(tmp_path):
    ruta = tmp_path / "datos" / "jev.csv"
    llamadas = []

    def preguntar(letra):
        llamadas.append(letra)
        return "angry", 0.7

    primera = clasificar_con_jev(LETRAS, preguntar, ruta_cache=ruta)
    segunda = clasificar_con_jev(LETRAS, preguntar, ruta_cache=ruta)

    assert len(llamadas) == len(LETRAS)
    assert primera == segunda


def test_el_cache_se_descarta_si_cambian_las_letras(tmp_path):
    ruta = tmp_path / "jev.csv"
    llamadas = []

    def preguntar(letra):
        llamadas.append(letra)
        return "angry", 0.7

    clasificar_con_jev(LETRAS, preguntar, ruta_cache=ruta)
    clasificar_con_jev([*LETRAS[:-1], "otra letra"], preguntar, ruta_cache=ruta)

    assert len(llamadas) == 2 * len(LETRAS)


def test_con_fallas_no_se_guarda_el_cache(tmp_path):
    ruta = tmp_path / "jev.csv"

    def preguntar(letra):
        raise RuntimeError("sin red")

    clasificar_con_jev(LETRAS, preguntar, ruta_cache=ruta)

    assert not ruta.exists()
