import numpy as np
import pytest

from src.radio_fcfm.contratos import ESTADOS
from src.radio_fcfm.evaluation import a_franja, acierto_por_franja

pytestmark = pytest.mark.etapa3


def test_a_franja_cubre_los_cuatro_estados():
    assert a_franja("happy") == "mañana"
    assert a_franja("angry") == "hora del taco"
    assert a_franja("sad") == "noche"
    assert a_franja("relaxed") == "noche"


def test_a_franja_rechaza_un_estado_desconocido():
    with pytest.raises(ValueError, match="euforico"):
        a_franja("euforico")


def test_acierto_por_franja_cuenta_como_acierto_confundir_sad_con_relaxed():
    real = ["happy", "sad", "angry", "relaxed"]
    predicho = ["happy", "relaxed", "sad", "relaxed"]

    # sad -> relaxed sigue siendo "noche": cuenta. angry -> sad cambia de
    # franja: no cuenta.
    assert acierto_por_franja(real, predicho) == pytest.approx(0.75)
    # El mismo resultado, medido con los cuatro estados, solo acierta dos.
    assert np.mean(np.array(real) == np.array(predicho)) == pytest.approx(0.5)


def test_acierto_por_franja_con_predicciones_perfectas_es_uno():
    real = ["happy", "sad", "angry", "relaxed"]
    assert acierto_por_franja(real, real) == 1.0


def test_agrupar_en_franjas_nunca_baja_el_acierto():
    rng = np.random.default_rng(0)
    for _ in range(20):
        real = rng.choice(ESTADOS, size=100)
        predicho = rng.choice(ESTADOS, size=100)
        acierto_cuatro_estados = np.mean(real == predicho)
        assert acierto_por_franja(real, predicho) >= acierto_cuatro_estados


def test_acierto_por_franja_exige_el_mismo_numero_de_canciones():
    # El contrato es el tipo de error; su mensaje depende de la implementación.
    with pytest.raises(ValueError):  # noqa: PT011
        acierto_por_franja(["happy", "sad"], ["happy"])
