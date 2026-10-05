import numpy as np
import pytest
import torch
from PIL import Image

from src.pasturecam.embeddings import dividir_en_tiles, extraer_embeddings

pytestmark = pytest.mark.etapa2


def _color_promedio(lote: torch.Tensor) -> torch.Tensor:
    """Modelo falso: el "embedding" es el color promedio de cada imagen."""
    return lote.mean(dim=(2, 3))


def _a_tensor(imagen: Image.Image) -> torch.Tensor:
    """Transformación falsa: convierte a tensor sin redimensionar."""
    arreglo = np.asarray(imagen, dtype=np.float32)
    return torch.from_numpy(arreglo).permute(2, 0, 1)


@pytest.fixture
def colores() -> list[tuple[int, int, int]]:
    return [
        (200, 0, 0),
        (0, 200, 0),
        (0, 0, 200),
        (100, 100, 100),
        (50, 50, 50),
    ]


@pytest.fixture
def rutas_sinteticas(tmp_path, colores):
    rutas = []
    for i, color in enumerate(colores):
        imagen = Image.new("RGB", (8, 8), color)
        # PNG es sin pérdida: un .jpg introduciría artefactos de compresión
        # que alteran el color exacto y romperían la comparación de abajo.
        ruta = tmp_path / f"cuadrante_{i}.png"
        imagen.save(ruta)
        rutas.append(ruta)
    return rutas


def test_dividir_en_tiles_cubre_la_imagen_completa_sin_solape():
    imagen = Image.new("RGB", (100, 50), (0, 0, 0))
    tiles = dividir_en_tiles(imagen, 2)
    assert len(tiles) == 2
    assert all(t.height == 50 for t in tiles)
    assert sum(t.width for t in tiles) == 100


def test_dividir_en_tiles_el_ultimo_tile_llega_al_borde():
    # 101 no es divisible por 3: el último tile absorbe el resto.
    imagen = Image.new("RGB", (101, 10), (0, 0, 0))
    tiles = dividir_en_tiles(imagen, 3)
    anchos = [t.width for t in tiles]
    assert sum(anchos) == 101
    assert anchos[0] == anchos[1] == 101 // 3


def test_extraer_embeddings_forma_y_orden(rutas_sinteticas, colores):
    embeddings = extraer_embeddings(
        rutas_sinteticas, _color_promedio, _a_tensor, tamano_lote=2
    )
    assert embeddings.shape == (5, 3)
    for fila, color in zip(embeddings, colores, strict=True):
        assert np.allclose(fila, color, atol=1e-5)


def test_extraer_embeddings_no_depende_del_tamano_de_lote(rutas_sinteticas):
    por_lotes_chicos = extraer_embeddings(
        rutas_sinteticas, _color_promedio, _a_tensor, tamano_lote=1
    )
    por_lote_grande = extraer_embeddings(
        rutas_sinteticas, _color_promedio, _a_tensor, tamano_lote=100
    )
    assert np.allclose(por_lotes_chicos, por_lote_grande)
