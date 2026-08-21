"""Kernels de convolución que deben definir para la Etapa 6."""

import numpy as np

# Su código aquí: agreguen al menos cinco tuplas (nombre, kernel).
KERNELS: list[tuple[str, np.ndarray]] = [
    (
        "identidad",
        # Deja la imagen intacta: el único peso no nulo es el del centro.
        np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]]),
    ),
    (
        "laplaciano",
        # Aproxima la segunda derivada espacial: resalta bordes en todas
        # direcciones y deja planas las zonas de color uniforme.
        np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]]),
    ),
    (
        "enfoque",
        # Sharpen: amplifica el píxel central y resta sus vecinos,
        # aumentando el contraste local en los bordes.
        np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]),
    ),
    (
        "desenfoque",
        # Box blur: promedia cada píxel con sus 8 vecinos, suavizando la
        # imagen y atenuando el ruido.
        np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]]) / 9,
    ),
    (
        "relieve",
        # Emboss: resalta los cambios de intensidad en la diagonal,
        # dando un efecto de relieve grabado sobre un fondo gris.
        np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]]),
    ),
]
