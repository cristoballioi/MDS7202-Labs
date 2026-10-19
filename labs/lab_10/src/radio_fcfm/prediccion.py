"""Predicción del ánimo de canciones nuevas."""

from collections.abc import Sequence

import pandas as pd
from sklearn.pipeline import Pipeline


def predecir_animo(modelo: Pipeline, letras: Sequence[str]) -> pd.DataFrame:
    """Predice el ánimo, la franja y la confianza de cada letra.

    `modelo` es un `Pipeline` ya ajustado que entrega `predict_proba`. Cada
    letra se limpia con `limpiar_letra`, igual que las del entrenamiento. El
    resultado tiene una fila por letra, en el mismo orden, con tres columnas:
    `animo` (la clase de mayor probabilidad), `franja` (la franja de
    programación de ese ánimo, según `a_franja`) y `confianza` (la
    probabilidad de la clase elegida, entre 0 y 1). La confianza no está
    calibrada: no es la probabilidad real de acertar.
    """
    raise NotImplementedError(
        "Completen predecir_animo antes de ejecutar el programa."
    )
