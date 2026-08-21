"""Operaciones de procesamiento de imágenes para completar."""

from __future__ import annotations

import numpy as np
from scipy.signal import convolve2d

from src.pixellab.imagen import Imagen


class LibImagen:
    """Filtros y transformaciones que reciben y retornan ``Imagen``."""

    def to_negative(self, img_in: Imagen) -> Imagen:
        # Su código aquí
        """Invierte cada intensidad: resultado = 255 - imagen.
        La resta es elementwise sobre todo el arreglo (vectorizada, sin
        ciclos): cada intensidad queda reflejada respecto del punto medio.
        """

        resultado = 255 - img_in.imagen
        resultado = resultado.astype(int)
        resultado[resultado > 255] = 255
        resultado[resultado < 0] = 0
        return Imagen(np.copy(resultado))

    def to_gray(self, img_in: Imagen) -> Imagen:
        # Su código aquí
        """Convierte a escala de grises con la fórmula NTSC.
        ``gris = 0.299*R + 0.587*G + 0.114*B``, apilado en los 3 canales
        con ``np.stack`` para conservar la forma ``(alto, ancho, 3)``.
        """
        img = img_in.imagen
        r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
        gris = 0.299 * r + 0.587 * g + 0.114 * b
        resultado = np.stack([gris, gris, gris], axis=2)
        resultado = resultado.astype(int)
        resultado[resultado > 255] = 255
        resultado[resultado < 0] = 0
        return Imagen(np.copy(resultado))

    def get_channel(self, img_in: Imagen, channel: str) -> Imagen:
        # Su código aquí
        """Deja solo el canal pedido y en 0 los otros dos."""
        canales = {"r": 0, "g": 1, "b": 2}
        if channel not in canales:
            raise ValueError(
                f"Canal '{channel}' no válido. Valores posibles: 'r', "
                "'g' o 'b'."
            )
        indice = canales[channel]
        resultado = np.zeros_like(img_in.imagen)
        resultado[:, :, indice] = img_in.imagen[:, :, indice]
        return Imagen(np.copy(resultado.astype(int)))

    def flip(self, img_in: Imagen, axis: str) -> Imagen:
        # Su código aquí
        """Voltea la imagen horizontal (``'h'``) o vertical (``'v'``).
        Usa slicing con paso ``-1``, el mismo patrón para invertir un eje
        que se ejercita en ``Lab3_Teoria.ipynb``.
        """
        if axis == "h":
            resultado = img_in.imagen[:, ::-1, :]
        elif axis == "v":
            resultado = img_in.imagen[::-1, :, :]
        else:
            raise ValueError(
                f"Eje '{axis}' no válido. Valores posibles: 'h' "
                "(horizontal) o 'v' (vertical)."
            )
        return Imagen(np.copy(resultado.astype(int)))

    def set_saturation(self, img_in: Imagen, C: float) -> Imagen:
        # Su código aquí
        """Ajusta la saturación: ``R = gris + C * (img - gris)``."""
        gris = self.to_gray(img_in).imagen
        resultado = gris + C * (img_in.imagen - gris)
        resultado = resultado.astype(int)
        resultado[resultado > 255] = 255
        resultado[resultado < 0] = 0
        return Imagen(np.copy(resultado))

    def set_contrast(self, img_in: Imagen, C: float) -> Imagen:
        # Su código aquí
        """Ajusta el contraste.
        ``F = 259 * (C + 255) / (255 * (259 - C))`` y
        ``R = F * (img - 128) + 128``.
        """
        f = 259 * (C + 255) / (255 * (259 - C))
        resultado = f * (img_in.imagen - 128) + 128
        resultado = resultado.astype(int)
        resultado[resultado > 255] = 255
        resultado[resultado < 0] = 0
        return Imagen(np.copy(resultado))

    def conv_channel(self, img_in: Imagen, kernel: np.ndarray) -> Imagen:
        """Por documentar (esto es parte del trabajo de la Etapa 6)."""
        # El cuerpo de este método lo entrega el curso.
        img = img_in.imagen
        img_out = []
        for i in range(img.shape[-1]):
            img_channel = convolve2d(
                img[:, :, i], kernel, mode="same", boundary="symm"
            )
            img_out.append(img_channel)
        new_image = np.stack(img_out, axis=2)
        new_image[new_image > 255], new_image[new_image < 0] = 255, 0
        return Imagen(new_image.astype(int))
