import mlflow
import mlflow.sklearn
import numpy as np
import pytest
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge

from src.pasturecam.evaluation import ResultadoCV
from src.pasturecam.tracking import registrar_run, tabla_runs


@pytest.fixture(autouse=True)
def mlflow_en_tmp_path(tmp_path, monkeypatch):
    """Aísla MLflow dentro de `tmp_path`: ni la base ni los artefactos tocan
    el proyecto real.

    El tracking URI por sí solo no basta: con un backend SQLite, MLflow
    guarda los artefactos de cada modelo (``mlruns/<experimento>/...``) en
    una ruta relativa al directorio de trabajo, no relativa al tracking
    URI. Sin el `chdir`, las pruebas escriben esos artefactos en la carpeta
    real del laboratorio.
    """
    monkeypatch.chdir(tmp_path)
    mlflow.set_tracking_uri(f"sqlite:///{tmp_path}/mlflow.db")


def test_registrar_run_guarda_parametros_metricas_y_tag():
    resultado = ResultadoCV(
        puntajes=[0.1, 0.2, 0.3],
        promedio=0.2,
        desviacion=0.0816,
        descripcion_validacion="GroupKFold(3)",
    )
    pipeline = Ridge().fit([[1], [2], [3]], [1, 2, 3])

    run_id = registrar_run(
        "ridge-prueba",
        resultado,
        params={"modelo": "Ridge", "alpha": 1.0},
        modelo=pipeline,
        etiquetas={"tipo": "modelo"},
        nombre_experimento="prueba-metadatos",
    )

    run = mlflow.get_run(run_id)
    assert run.data.params["modelo"] == "Ridge"
    assert run.data.params["alpha"] == "1.0"
    assert run.data.metrics["promedio"] == pytest.approx(0.2)
    assert run.data.metrics["puntaje_fold_0"] == pytest.approx(0.1)
    assert run.data.metrics["puntaje_fold_2"] == pytest.approx(0.3)
    assert run.data.tags["validacion"] == "GroupKFold(3)"
    assert run.data.tags["tipo"] == "modelo"
    assert run.data.tags["mlflow.runName"] == "ridge-prueba"


def test_search_runs_devuelve_el_run_registrado():
    resultado = ResultadoCV([0.5], 0.5, 0.0, "KFold(1)")
    pipeline = Ridge().fit([[1], [2]], [1, 2])

    run_id = registrar_run(
        "prueba",
        resultado,
        params={},
        modelo=pipeline,
        nombre_experimento="prueba-busqueda",
    )

    runs = mlflow.search_runs(experiment_names=["prueba-busqueda"])
    assert run_id in runs["run_id"].tolist()


def test_pipeline_recargado_predice_lo_mismo():
    X = np.array([[1.0], [2.0], [3.0], [4.0]])
    y = np.array([2.0, 4.0, 6.0, 8.0])
    pipeline = Ridge().fit(X, y)
    resultado = ResultadoCV([1.0], 1.0, 0.0, "KFold(1)")

    run_id = registrar_run(
        "prueba",
        resultado,
        params={},
        modelo=pipeline,
        nombre_experimento="prueba-recarga",
    )

    recargado = mlflow.sklearn.load_model(f"runs:/{run_id}/modelo")
    assert np.allclose(recargado.predict(X), pipeline.predict(X))


def test_registrar_run_acepta_hist_gradient_boosting():
    # HistGradientBoostingRegressor guarda un tipo interno (TreePredictor)
    # que el serializador por omisión de mlflow.sklearn rechaza sin que se
    # declare explícitamente como confiable; esta prueba cubre justo eso.
    X = np.array([[1.0], [2.0], [3.0], [4.0], [5.0]])
    y = np.array([2.0, 4.0, 6.0, 8.0, 10.0])
    pipeline = HistGradientBoostingRegressor(random_state=0).fit(X, y)
    resultado = ResultadoCV([1.0], 1.0, 0.0, "KFold(1)")

    run_id = registrar_run(
        "prueba",
        resultado,
        params={},
        modelo=pipeline,
        nombre_experimento="prueba-boosting",
    )

    recargado = mlflow.sklearn.load_model(f"runs:/{run_id}/modelo")
    assert np.allclose(recargado.predict(X), pipeline.predict(X))


def test_tabla_runs_conserva_el_run_mas_reciente_de_cada_nombre():
    registrar_run(
        "baseline",
        ResultadoCV([0.1], 0.1, 0.0, "KFold(1)"),
        {},
        nombre_experimento="prueba-tabla",
    )
    registrar_run(
        "baseline",
        ResultadoCV([0.2], 0.2, 0.0, "KFold(1)"),
        {},
        nombre_experimento="prueba-tabla",
    )
    registrar_run(
        "otro",
        ResultadoCV([0.3], 0.3, 0.0, "KFold(1)"),
        {},
        nombre_experimento="prueba-tabla",
    )

    tabla = tabla_runs("prueba-tabla")
    assert len(tabla) == 2
    fila = tabla[tabla["tags.mlflow.runName"] == "baseline"]
    assert fila["metrics.promedio"].item() == pytest.approx(0.2)
