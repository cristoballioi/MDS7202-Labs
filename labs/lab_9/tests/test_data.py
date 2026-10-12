import polars as pl
import pytest

from src.pasturecam.data import OBJETIVOS, a_formato_ancho

pytestmark = pytest.mark.etapa1


def test_a_formato_ancho_una_fila_por_imagen(mediciones_largo):
    ancho = a_formato_ancho(mediciones_largo)
    assert ancho.height == 3
    assert set(ancho["image_path"]) == {
        "imagenes/A.jpg",
        "imagenes/B.jpg",
        "imagenes/C.jpg",
    }
    for objetivo in OBJETIVOS:
        assert objetivo in ancho.columns
    assert "target_name" not in ancho.columns
    assert "target" not in ancho.columns


def test_a_formato_ancho_conserva_metadatos(mediciones_largo):
    ancho = a_formato_ancho(mediciones_largo)
    fila_a = ancho.filter(pl.col("image_path") == "imagenes/A.jpg")
    assert fila_a["Sampling_Date"].item() == "2020/1/1"
    assert fila_a["State"].item() == "Tas"
    assert fila_a["Height_Ave_cm"].item() == 5.0
