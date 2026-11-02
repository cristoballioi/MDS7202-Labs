"""Conexión con MLflow y consulta de los runs del laboratorio.

Material provisto: este módulo viene implementado y no hay que completarlo.
El registro de cada experimento lo escriben ustedes en el notebook.
"""

from __future__ import annotations

import logging
import os
import warnings
from pathlib import Path

# Al importarse, MLflow imprime un aviso para asistentes de código que tapa
# las salidas del notebook. Se desactiva antes del import.
os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")

import mlflow
import polars as pl

NOMBRE_EXPERIMENTO = "heladas-curico"
RAIZ_LAB = Path(__file__).resolve().parents[2]


def configurar_mlflow(
    nombre_experimento: str = NOMBRE_EXPERIMENTO,
    raiz: str | Path | None = None,
) -> str:
    """Deja MLflow listo para registrar runs en una base local.

    La base `mlflow.db` y los artefactos (`mlruns/`) quedan en `raiz`, que por
    omisión es la carpeta del laboratorio. Activa el experimento
    `nombre_experimento`, creándolo si no existe, y baja el volumen de los
    mensajes de MLflow para que no tapen las salidas. Devuelve el id del
    experimento.
    """
    for nombre in ("mlflow", "alembic"):
        logging.getLogger(nombre).setLevel(logging.WARNING)
    # Aviso interno de SQLAlchemy dentro de MLflow; no depende del notebook.
    warnings.filterwarnings("ignore", message=".*noload.*")

    raiz = Path(raiz).resolve() if raiz is not None else RAIZ_LAB
    raiz.mkdir(parents=True, exist_ok=True)
    # as_posix() deja la URI válida también en Windows.
    mlflow.set_tracking_uri(f"sqlite:///{raiz.as_posix()}/mlflow.db")

    experimento = mlflow.get_experiment_by_name(nombre_experimento)
    if experimento is None:
        id_experimento = mlflow.create_experiment(
            nombre_experimento,
            artifact_location=(raiz / "mlruns").as_uri(),
        )
    else:
        id_experimento = experimento.experiment_id
    mlflow.set_experiment(experiment_id=id_experimento)
    return id_experimento


def tabla_runs(
    prefijo: str | None = None,
    nombre_experimento: str = NOMBRE_EXPERIMENTO,
) -> pl.DataFrame:
    """Devuelve los runs del experimento, uno por nombre: el más reciente.

    Si el notebook se ejecuta varias veces, cada registro se repite con el
    mismo nombre; la tabla conserva solo el último, así que trae una fila
    por run distinto, ordenadas del primero al último registrado. Con
    `prefijo`, solo quedan los runs cuyo nombre empieza así. Las columnas
    son `run`, `padre` (el nombre del run que lo contiene, o `null` si no
    está anidado) y, en orden alfabético, las de `params.*`, `metrics.*` y
    `tags.*` que tengan algún valor en esos runs. Las métricas con varios
    pasos muestran el último paso registrado.

    Solo considera runs terminados: un run que falló a mitad de una celda no
    reemplaza al registro anterior. El padre se resuelve por nombre, así que
    si una búsqueda se interrumpe, sus trials de una ejecución anterior siguen
    apareciendo bajo el mismo padre hasta que la búsqueda se repita completa.
    """
    runs = mlflow.search_runs(
        experiment_names=[nombre_experimento],
        filter_string="attributes.status = 'FINISHED'",
        order_by=["attributes.start_time DESC"],
    )
    if runs.empty:
        return pl.DataFrame(schema={"run": pl.String, "padre": pl.String})

    nombres = dict(
        zip(runs["run_id"], runs["tags.mlflow.runName"], strict=True)
    )
    ids_padre = runs.get("tags.mlflow.parentRunId", [None] * len(runs))
    padres = [
        nombres.get(id_padre) if isinstance(id_padre, str) else None
        for id_padre in ids_padre
    ]

    columnas = sorted(
        columna
        for columna in runs.columns
        if columna.startswith(("params.", "metrics.", "tags."))
        and not columna.startswith("tags.mlflow.")
    )
    tabla = pl.from_pandas(runs[columnas]).select(
        pl.Series("run", runs["tags.mlflow.runName"].tolist(), pl.String),
        pl.Series("padre", padres, pl.String),
        pl.all(),
    )
    # search_runs entrega del más reciente al más antiguo: se conserva la
    # primera aparición de cada nombre y después se invierte el orden.
    tabla = tabla.unique(subset="run", keep="first", maintain_order=True)
    tabla = tabla.reverse()
    if prefijo is not None:
        tabla = tabla.filter(pl.col("run").str.starts_with(prefijo))
    # search_runs trae columnas de todos los runs guardados, incluidas las de
    # registros antiguos; solo quedan las que tienen datos en esta tabla.
    vacias = [
        columna
        for columna in columnas
        if tabla[columna].null_count() == tabla.height
    ]
    return tabla.drop(vacias)
