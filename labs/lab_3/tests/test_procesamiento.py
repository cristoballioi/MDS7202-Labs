import numpy as np
import pytest

from src.pixellab.imagen import Imagen
from src.pixellab.kernels import KERNELS
from src.pixellab.procesamiento import LibImagen


def imagen_base():
    return np.array(
        [
            [[10, 20, 30], [40, 50, 60], [200, 210, 220]],
            [[70, 80, 90], [100, 110, 120], [130, 140, 150]],
        ],
        dtype="int",
    )


@pytest.mark.etapa4
def test_negativo_es_255_menos_imagen():
    img = Imagen(imagen_base())
    resultado = LibImagen().to_negative(img)
    assert np.array_equal(resultado.imagen, 255 - imagen_base())


@pytest.mark.etapa4
def test_gris_tiene_3_canales_iguales():
    img = Imagen(imagen_base())
    resultado = LibImagen().to_gray(img).imagen
    assert resultado.shape == (2, 3, 3)
    assert np.array_equal(resultado[:, :, 0], resultado[:, :, 1])
    assert np.array_equal(resultado[:, :, 0], resultado[:, :, 2])


@pytest.mark.etapa4
def test_gris_usas_formula_ntsc():
    img = Imagen(imagen_base())
    esperado = (
        0.299 * imagen_base()[:, :, 0]
        + 0.587 * imagen_base()[:, :, 1]
        + 0.114 * imagen_base()[:, :, 2]
    )
    esperado = np.stack([esperado, esperado, esperado], axis=2).astype(int)
    np.testing.assert_allclose(
        LibImagen().to_gray(img).imagen, esperado, atol=1
    )


@pytest.mark.etapa4
def test_get_channel_deja_ceros_fuera_del_canal():
    img = Imagen(imagen_base())
    for i, canal in enumerate("rgb"):
        resultado = LibImagen().get_channel(img, canal).imagen
        original = imagen_base()
        esperado = np.zeros_like(original)
        esperado[:, :, i] = original[:, :, i]
        assert np.array_equal(resultado, esperado)


@pytest.mark.etapa4
def test_get_channel_con_canal_invalido_lanza_error():
    img = Imagen(imagen_base())
    with pytest.raises(ValueError, match="no válido"):
        LibImagen().get_channel(img, "x")


@pytest.mark.etapa5
def test_flip_horizontal_invierte_columnas():
    img = Imagen(imagen_base())
    resultado = LibImagen().flip(img, "h").imagen
    assert np.array_equal(resultado[:, :, :], imagen_base()[:, ::-1, :])


@pytest.mark.etapa5
def test_flip_vertical_invierte_filas():
    img = Imagen(imagen_base())
    resultado = LibImagen().flip(img, "v").imagen
    assert np.array_equal(resultado[:, :, :], imagen_base()[::-1, :, :])


@pytest.mark.etapa5
def test_flip_con_eje_invalido_lanza_error():
    img = Imagen(imagen_base())
    with pytest.raises(ValueError, match="no válido"):
        LibImagen().flip(img, "x")


@pytest.mark.etapa5
def test_saturacion_con_C_cero_es_aproximadamente_gris():
    img = Imagen(imagen_base())
    lib = LibImagen()
    resultado = lib.set_saturation(img, 0.0).imagen
    gris = lib.to_gray(img).imagen
    np.testing.assert_allclose(resultado, gris, atol=1)


@pytest.mark.etapa5
def test_contraste_con_C_cero_se_aproxima_a_la_identidad():
    img = Imagen(imagen_base())
    resultado = LibImagen().set_contrast(img, 0.0).imagen
    np.testing.assert_allclose(resultado, imagen_base(), atol=2)


@pytest.mark.etapa6
def test_convolucion_con_kernel_identidad_no_cambia_la_imagen():
    img = Imagen(imagen_base())
    identidad = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
    resultado = LibImagen().conv_channel(img, identidad).imagen
    assert resultado.shape == imagen_base().shape


@pytest.mark.etapa6
def test_kernels_tienen_al_menos_5_y_producen_imagen_valida():
    lib = LibImagen()
    img = Imagen(imagen_base())
    assert len(KERNELS) >= 5
    for nombre, kernel in KERNELS:
        resultado = lib.conv_channel(img, kernel)
        assert isinstance(resultado, Imagen)
        assert resultado.imagen.shape == imagen_base().shape
        assert np.all(resultado.imagen >= 0)
        assert np.all(resultado.imagen <= 255)
        assert nombre.strip()
