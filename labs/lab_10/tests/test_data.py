import numpy as np
import pytest

from src.radio_fcfm.data import limpiar_letra, separar_test

pytestmark = pytest.mark.etapa1


def test_limpiar_letra_quita_las_marcas_de_estructura():
    letra = "[Verse 1]\nHola mundo\n[Chorus]\nLa la la"
    assert limpiar_letra(letra) == "Hola mundo La la la"


def test_limpiar_letra_quita_marcas_a_mitad_de_linea():
    assert limpiar_letra("Hola [x2] mundo") == "Hola mundo"


def test_limpiar_letra_conserva_el_texto_y_normaliza_espacios():
    assert limpiar_letra("Hola   mundo\ncomo  estás") == "Hola mundo como estás"


def test_limpiar_letra_no_toca_los_parentesis():
    # Los paréntesis suelen ser coros ("(oh oh)"): son parte de la letra.
    assert limpiar_letra("(oh oh) hola") == "(oh oh) hola"


def test_limpiar_letra_quita_las_marcas_de_seccion_entre_parentesis():
    letra = "Hola (Chorus) mundo (chorus 2x) (Instrumental break) fin"
    assert limpiar_letra(letra) == "Hola mundo fin"


def test_limpiar_letra_conserva_parentesis_que_solo_se_parecen_a_una_marca():
    # "Introducing" empieza con "intro", pero no es una marca de sección.
    assert limpiar_letra("(Introducing love) hola") == "(Introducing love) hola"


def test_limpiar_letra_con_texto_vacio_devuelve_vacio():
    assert limpiar_letra("") == ""
    assert limpiar_letra("[Intro]") == ""
    assert limpiar_letra("(Chorus)") == ""


def test_limpiar_letra_es_idempotente():
    letra = "[Verse 1]\nHola   mundo\n[Chorus]\n(oh oh) la la"
    una_vez = limpiar_letra(letra)
    assert limpiar_letra(una_vez) == una_vez


@pytest.fixture
def artistas_y_estados() -> tuple[np.ndarray, np.ndarray]:
    """Doscientas canciones: cuatro estados, veinticinco artistas por estado
    y dos canciones por artista, de modo que ningún artista cambia de estado.
    """
    artistas, estados = [], []
    for estado in ["happy", "relaxed", "sad", "angry"]:
        for i in range(25):
            artistas += [f"{estado}-{i}"] * 2
            estados += [estado] * 2
    return np.array(artistas), np.array(estados)


def test_separar_test_no_comparte_artistas(artistas_y_estados):
    artistas, estados = artistas_y_estados

    train_val, test = separar_test(artistas, estados)

    assert not set(artistas[train_val]) & set(artistas[test])


def test_separar_test_reparte_todas_las_canciones_una_vez(
    artistas_y_estados,
):
    artistas, estados = artistas_y_estados

    train_val, test = separar_test(artistas, estados)

    assert sorted([*train_val, *test]) == list(range(len(artistas)))


def test_separar_test_aparta_cerca_del_veinte_por_ciento(
    artistas_y_estados,
):
    artistas, estados = artistas_y_estados

    _, test = separar_test(artistas, estados)

    assert len(test) / len(artistas) == pytest.approx(0.2, abs=0.05)


def test_separar_test_deja_los_cuatro_estados_en_el_test(
    artistas_y_estados,
):
    artistas, estados = artistas_y_estados

    _, test = separar_test(artistas, estados)

    assert set(estados[test]) == set(estados)


def test_separar_test_es_reproducible(artistas_y_estados):
    artistas, estados = artistas_y_estados

    primera = separar_test(artistas, estados)
    segunda = separar_test(artistas, estados)

    assert (primera[0] == segunda[0]).all()
    assert (primera[1] == segunda[1]).all()
