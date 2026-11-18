"""Etapa 2: la clave de API se compara de forma segura."""

import pytest
from fastapi import HTTPException

from src.aguaapr.security import verificar_api_key

pytestmark = pytest.mark.etapa2


def test_una_clave_correcta_pasa():
    assert verificar_api_key("secreta", "secreta") is None


@pytest.mark.parametrize("recibida", [None, "", "otra", "secreta "])
def test_una_clave_ausente_o_distinta_responde_401(recibida):
    with pytest.raises(HTTPException) as error:
        verificar_api_key(recibida, "secreta")
    assert error.value.status_code == 401
