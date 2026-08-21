"""Clase ``Imagen``: contenedor de imágenes sobre el que se opera con NumPy."""

from __future__ import annotations

import numpy as np


class Imagen:
    """Contenedor de imágenes RGB.

    Completen el constructor y los operadores de esta clase siguiendo el
    contrato del enunciado y los tests de ``tests/test_imagen.py``.
    """

    def __init__(self, img: np.ndarray) -> None:
        if not isinstance(img, np.ndarray):
            raise TypeError(
                "Debes entregar un arreglo de numpy como argumento del "
                "constructor de Imagen"
            )
        if img.ndim != 3:
            raise ValueError(
                "La imagen debe tener 3 dimensiones (alto, ancho, "
                f"canales); se recibió un arreglo de {img.ndim} "
                "dimensiones."
            )
        if img.shape[-1] != 3:
            raise ValueError(
                "La imagen debe tener 3 canales (RGB); se recibió un "
                f"arreglo con {img.shape[-1]} canales."
            )
        self.imagen = img

    def _operando(self, other: int | float | np.ndarray | Imagen) -> object:
        """Extrae el arreglo con el que operar, validando dimensiones."""
        if isinstance(other, Imagen):
            if other.imagen.shape != self.imagen.shape:
                alto, ancho, canales = self.imagen.shape
                oalto, oancho, ocanales = other.imagen.shape
                raise ValueError(
                    "Las dimensiones de la imagen a operar "
                    f"({oalto}x{oancho}x{ocanales}) no calzan con las de "
                    f"la imagen original ({alto}x{ancho}x{canales})"
                )
            return other.imagen
        return other

    def _saturar(self, resultado: np.ndarray) -> Imagen:
        """Convierte a entero y satura al rango [0, 255] con indexado
        condicional, retornando una `Imagen` nueva a partir de una copia.
        """
        resultado = resultado.astype(int)
        resultado[resultado > 255] = 255
        resultado[resultado < 0] = 0
        return Imagen(np.copy(resultado))

    def __add__(self, other: int | float | np.ndarray | Imagen) -> Imagen:
        # Su código aquí
        operando = self._operando(other)
        return self._saturar(self.imagen + operando)

    def __radd__(self, other: int | float | np.ndarray | Imagen) -> Imagen:
        # Su código aquí
        return self.__add__(other)

    def __sub__(self, other: int | float | np.ndarray | Imagen) -> Imagen:
        # Su código aquí
        operando = self._operando(other)
        return self._saturar(self.imagen - operando)

    def __rsub__(self, other: int | float | np.ndarray | Imagen) -> Imagen:
        # Su código aquí
        operando = self._operando(other)
        return self._saturar(operando - self.imagen)

    def __mul__(self, other: int | float | np.ndarray | Imagen) -> Imagen:
        # Su código aquí
        operando = self._operando(other)
        return self._saturar(self.imagen * operando)

    def __rmul__(self, other: int | float | np.ndarray | Imagen) -> Imagen:
        # Su código aquí
        return self.__mul__(other)
