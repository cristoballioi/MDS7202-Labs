"""Registro y consulta de experimentos en MLflow local.

Material provisto: este módulo viene implementado y no hay que completarlo.
"""

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.base import BaseEstimator

from src.pasturecam.contratos import (
    NOMBRE_EXPERIMENTO,
    TIPOS_CONFIABLES,
    ResultadoCV,
)


def registrar_run(
    nombre: str,
    resultado: ResultadoCV,
    params: dict,
    modelo: BaseEstimator | None = None,
    etiquetas: dict | None = None,
    nombre_experimento: str = NOMBRE_EXPERIMENTO,
) -> str:
    """Registra en MLflow un run con el resultado de una evaluación.

    Requiere un tracking URI ya configurado. El run se llama `nombre`, que
    conviene que sea estable (el mismo cada vez que se repite la misma
    evaluación) para que `tabla_runs` pueda quedarse con el más reciente.
    Guarda `params` como parámetros; las métricas `puntaje_fold_<i>` de cada
    fold, más `promedio` y `desviacion`; la descripción de la validación y
    las `etiquetas` como tags; y, si se entrega, `modelo` como artefacto
    llamado `"modelo"`. `TIPOS_CONFIABLES` evita que `log_model` rechace
    modelos con tipos internos poco comunes, como los de
    `HistGradientBoostingRegressor`. Devuelve el `run_id`.
    """
    mlflow.set_experiment(nombre_experimento)
    with mlflow.start_run(run_name=nombre) as run:
        mlflow.log_params(params)
        mlflow.set_tags(
            {
                "validacion": resultado.descripcion_validacion,
                **(etiquetas or {}),
            }
        )
        metricas = {
            f"puntaje_fold_{i}": puntaje
            for i, puntaje in enumerate(resultado.puntajes)
        }
        metricas["promedio"] = resultado.promedio
        metricas["desviacion"] = resultado.desviacion
        mlflow.log_metrics(metricas)
        if modelo is not None:
            mlflow.sklearn.log_model(
                modelo, name="modelo", skops_trusted_types=TIPOS_CONFIABLES
            )
        return run.info.run_id


def tabla_runs(nombre_experimento: str = NOMBRE_EXPERIMENTO) -> pd.DataFrame:
    """Devuelve los runs del experimento, uno por nombre: el más reciente.

    Si el notebook se ejecuta varias veces, cada evaluación queda registrada
    otra vez con el mismo nombre. Esta tabla conserva solo la última, así
    que trae una fila por evaluación distinta.
    """
    runs = mlflow.search_runs(
        experiment_names=[nombre_experimento],
        order_by=["attributes.start_time DESC"],
    )
    return runs.drop_duplicates(subset="tags.mlflow.runName").reset_index(
        drop=True
    )
