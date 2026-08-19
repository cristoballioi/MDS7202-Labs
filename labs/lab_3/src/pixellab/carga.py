"""Carga de imágenes. Este módulo lo entrega el curso: no hay que modificarlo."""

from pathlib import Path

import numpy as np
from PIL import Image


def cargar_imagen(ruta) -> np.ndarray:
    """Lee una imagen y la devuelve como arreglo int (alto, ancho, 3)."""
    return np.array(Image.open(Path(ruta)).convert("RGB"), dtype="int")
