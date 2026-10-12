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
    # Ancho de cada tile con división entera (el resto lo absorbe el último).
    ancho_tile = imagen.width // n

    tiles = []
    # Un `for` es válido aquí: se recorren tiles, no filas de una tabla.
    for i in range(n):
        # Borde izquierdo: cada tile parte donde terminó el anterior, así no
        # hay solape ni huecos entre ellos.
        izquierda = i * ancho_tile
        # Borde derecho: el último tile llega hasta el final de la imagen para
        # incluir los píxeles sobrantes si el ancho no es divisible por n.
        derecha = imagen.width if i == n - 1 else (i + 1) * ancho_tile
        # `crop` recibe (izquierda, arriba, derecha, abajo); usamos el alto
        # completo de la imagen en todos los tiles.
        tiles.append(imagen.crop((izquierda, 0, derecha, imagen.height)))
    return tiles


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
    # Sin imágenes no hay nada que concatenar: devolvemos un arreglo vacío.
    if not rutas:
        return np.empty((0, 0), dtype=np.float32)

    embeddings_por_lote = []

    # `no_grad` desactiva el cálculo de gradientes: solo hacemos inferencia,
    # así ahorramos memoria y tiempo (el extractor está congelado).
    with torch.no_grad():
        # Recorremos las rutas de a `tamano_lote` imágenes para no cargar las
        # 357 fotos en memoria a la vez.
        for inicio in range(0, len(rutas), tamano_lote):
            rutas_lote = rutas[inicio : inicio + tamano_lote]

            tensores = []
            for ruta in rutas_lote:
                # Se abre cada foto, se pasa a RGB (por si viniera en otro
                # modo) y se le aplica el preprocesamiento del extractor.
                with Image.open(ruta) as imagen:
                    tensores.append(transformacion(imagen.convert("RGB")))

            # Se apilan los tensores de las imágenes en un solo lote
            # `(lote, canales, alto, ancho)`.
            lote = torch.stack(tensores)
            # El extractor devuelve un embedding por imagen: `(lote, dim)`.
            salida = modelo(lote)
            # Pasamos a NumPy (en CPU) para poder concatenar al final.
            embeddings_por_lote.append(salida.cpu().numpy())

    # Se unen los lotes en orden: queda una fila por imagen, en el mismo orden
    # que `rutas`.
    return np.concatenate(embeddings_por_lote, axis=0)