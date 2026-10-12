"""Pipelines y validación cruzada honesta para los modelos de biomasa."""

from collections.abc import Callable

import numpy as np
from sklearn.base import BaseEstimator, clone
from sklearn.metrics import r2_score
from sklearn.model_selection import BaseCrossValidator
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.pasturecam.contratos import ResultadoCV


def construir_pipeline(regresor: BaseEstimator) -> Pipeline:
    """Arma `StandardScaler → regresor`, sin ajustarlo.

    El escalador deja cada componente del embedding con media 0 y desviación
    1. Así la penalización de un regresor regularizado, como `Ridge`, trata a
    todas las componentes por igual: sin escalar, las de mayor escala
    quedarían menos penalizadas.
    """
    # Dos pasos con nombre fijo ("escalador" y "regresor"): las pruebas y el
    # resto del notebook dependen de esos nombres. No se ajusta nada todavía.
    return Pipeline(
        steps=[
            ("escalador", StandardScaler()),
            ("regresor", regresor),
        ]
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
    puntajes = []

    # Un `for` es válido aquí: se repite el experimento por cada partición.
    # `grupos` se entrega siempre; `GroupKFold` lo usa para no separar un
    # grupo entre entrenamiento y validación y `KFold` lo ignora.
    for indices_train, indices_val in cv.split(X, y, grupos):
        # `clone` crea una copia sin ajustar: cada fold parte desde cero y no
        # arrastra lo aprendido (escalador, pesos) del fold anterior.
        modelo = clone(pipeline)
        # El ajuste usa SOLO el entrenamiento del fold: el escalador calcula
        # media y desviación sin ver los datos de validación (evita leakage).
        modelo.fit(X[indices_train], y[indices_train])
        # Se predice sobre la validación y se mide con la métrica pedida.
        predicciones = modelo.predict(X[indices_val])
        puntajes.append(float(metrica(y[indices_val], predicciones)))

    # Descripción con el formato "<Clase>(<n>)", p. ej. "GroupKFold(5)": la
    # tabla de MLflow y las pruebas dependen de este texto.
    descripcion = f"{type(cv).__name__}({cv.get_n_splits(X, y, grupos)})"

    return ResultadoCV(
        puntajes=puntajes,
        promedio=float(np.mean(puntajes)),
        # `np.std` (desviación poblacional, ddof=0), como pide el enunciado.
        desviacion=float(np.std(puntajes)),
        descripcion_validacion=descripcion,
    )