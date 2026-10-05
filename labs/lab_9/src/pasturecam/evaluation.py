"""Pipelines y validación cruzada honesta para los modelos de biomasa."""

from collections.abc import Callable

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.metrics import r2_score
from sklearn.model_selection import BaseCrossValidator
from sklearn.pipeline import Pipeline

from src.pasturecam.contratos import ResultadoCV


def construir_pipeline(regresor: BaseEstimator) -> Pipeline:
    """Arma `StandardScaler → regresor`, sin ajustarlo.

    El escalador deja cada componente del embedding con media 0 y desviación
    1. Así la penalización de un regresor regularizado, como `Ridge`, trata a
    todas las componentes por igual: sin escalar, las de mayor escala
    quedarían menos penalizadas.
    """
    raise NotImplementedError(
        "Completen construir_pipeline antes de ejecutar el programa."
    )


def evaluar(
    pipeline: BaseEstimator,
    X: np.ndarray,
    y: np.ndarray,
    grupos: np.ndarray,
    cv: BaseCrossValidator,
    metrica: Callable[[np.ndarray, np.ndarray], float] = r2_score,
) -> ResultadoCV:
    """Evalúa `pipeline` con la validación cruzada `cv`, fold por fold.

    En cada fold se clona `pipeline` (para no heredar estado del fold
    anterior) y se ajusta **solo** con `X[entrenamiento]`, `y[entrenamiento]`
    — así el escalamiento y la reducción de dimensionalidad nunca ven los
    datos de validación de ese fold. `grupos` se pasa siempre a `cv.split`;
    con un `KFold` corriente se ignora, y con un `GroupKFold` es lo que
    garantiza que ningún grupo quede a la vez en entrenamiento y
    validación. `metrica` recibe `(y_real, y_predicho)` del fold de
    validación; por omisión es el R² de `scikit-learn`.
    """
    raise NotImplementedError("Completen evaluar antes de ejecutar el programa.")
