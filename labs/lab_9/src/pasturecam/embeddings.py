"""Extracción de embeddings de imágenes con un extractor preentrenado."""

from collections.abc import Callable
from pathlib import Path

import numpy as np
import torch
from PIL import Image


def dividir_en_tiles(imagen: Image.Image, n: int) -> list[Image.Image]:
    """Divide `imagen` en `n` tiles verticales, sin solape y sin perder nada.

    Cada tile tiene el alto completo de `imagen` y un ancho de
    `imagen.width // n`; el último tile se extiende hasta el borde derecho
    para cubrir el resto que deja la división entera. Juntos, los tiles
    cubren exactamente el cuadrante original.
    """
    raise NotImplementedError(
        "Completen dividir_en_tiles antes de ejecutar el programa."
    )


def extraer_embeddings(
    rutas: list[Path],
    modelo: Callable[[torch.Tensor], torch.Tensor],
    transformacion: Callable[[Image.Image], torch.Tensor],
    tamano_lote: int = 16,
) -> np.ndarray:
    """Extrae un embedding por imagen, en el mismo orden que `rutas`.

    `modelo` es cualquier invocable que recibe un tensor `(lote, canales,
    alto, ancho)` y devuelve `(lote, dimensión)` — en la pauta es un
    extractor de `timm` en modo evaluación (`model.eval()`), y en las
    pruebas puede ser un doble liviano. Cada imagen se abre, se le aplica
    `transformacion` (el preprocesamiento que declara el propio modelo) y
    se agrupa en lotes de `tamano_lote` antes de pasar por `modelo`, sin
    calcular gradientes. El resultado es un arreglo `(len(rutas),
    dimensión)`.
    """
    raise NotImplementedError(
        "Completen extraer_embeddings antes de ejecutar el programa."
    )
