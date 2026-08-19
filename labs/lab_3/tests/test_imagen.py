import numpy as np
import pytest

from src.pixellab.imagen import Imagen


def imagen_base():
    """Imagen sintética pequeña con valores distribuidos en [0, 255]."""
    return np.array(
        [
            [[10, 20, 30], [40, 50, 60], [200, 210, 220]],
            [[70, 80, 90], [100, 110, 120], [130, 140, 150]],
        ],
        dtype="int",
    )


@pytest.mark.etapa2
def test_constructor_acepta_ndarray_valido():
    img = Imagen(imagen_base())
    assert np.array_equal(img.imagen, imagen_base())


@pytest.mark.etapa2
def test_constructor_rechaza_tipo_no_ndarray():
    with pytest.raises(TypeError):
        Imagen([[1, 2], [3, 4]])


@pytest.mark.etapa2
def test_constructor_rechaza_menos_de_3_dimensiones():
    with pytest.raises(ValueError, match="3 dimensiones"):
        Imagen(np.zeros((4, 5)))


@pytest.mark.etapa2
def test_constructor_rechaza_distintos_de_3_canales():
    with pytest.raises(ValueError, match="3 canales"):
        Imagen(np.zeros((4, 5, 2)))


@pytest.mark.etapa3
def test_suma_satura_por_arriba():
    img = Imagen(imagen_base())
    assert np.max((img + 1000).imagen) == 255


@pytest.mark.etapa3
def test_multiplicacion_satura_por_arriba():
    img = Imagen(imagen_base())
    assert np.max((img * 555555).imagen) == 255


@pytest.mark.etapa3
def test_resta_satura_por_abajo():
    img = Imagen(imagen_base())
    assert np.min((img - 1000).imagen) == 0


@pytest.mark.etapa3
def test_multiplicacion_negativa_satura_por_abajo():
    img = Imagen(imagen_base())
    assert np.min((img * -555555).imagen) == 0


@pytest.mark.etapa3
def test_radd_es_conmutativa():
    img = Imagen(imagen_base())
    assert np.array_equal((img + 10).imagen, (10 + img).imagen)


@pytest.mark.etapa3
def test_rmul_es_conmutativa():
    img = Imagen(imagen_base())
    assert np.array_equal((img * 2).imagen, (2 * img).imagen)


@pytest.mark.etapa3
def test_rsub_no_es_lo_mismo_que_sub():
    img = Imagen(imagen_base())
    assert not np.array_equal((img - 50).imagen, (50 - img).imagen)


@pytest.mark.etapa3
def test_error_por_dimensiones_distintas_entre_imagenes():
    img = Imagen(imagen_base())
    otra = Imagen(np.zeros((5, 5, 3), dtype="int"))
    with pytest.raises(ValueError, match="no calzan"):
        img + otra


@pytest.mark.etapa3
def test_operacion_entre_imagenes_iguales():
    img = Imagen(imagen_base())
    resultado = img + img
    assert np.all(resultado.imagen >= img.imagen)


@pytest.mark.parametrize("escalar", [2, 1.5, 0.5])
@pytest.mark.etapa3
def test_operaciones_retornan_enteros(escalar):
    """Un escalar flotante no debe dejar la imagen en punto flotante.

    Es el caso que rompe la visualización: matplotlib y Streamlit
    interpretan los arreglos flotantes en el rango [0.0, 1.0].
    """
    img = Imagen(imagen_base())
    assert np.issubdtype((img * escalar).imagen.dtype, np.integer)
    assert np.issubdtype((img + escalar).imagen.dtype, np.integer)
    assert np.issubdtype((img - escalar).imagen.dtype, np.integer)
    assert np.issubdtype((escalar - img).imagen.dtype, np.integer)


@pytest.mark.etapa3
def test_operacion_no_muta_la_imagen_original():
    original = imagen_base()
    img = Imagen(original)
    img + 100
    img - 100
    img * 2
    assert np.array_equal(img.imagen, original)
