import mlflow
import mlflow.sklearn
import numpy as np
import pytest
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src.radio_fcfm.contratos import ResultadoCV
from src.radio_fcfm.tracking import registrar_run, tabla_runs

pytestmark = pytest.mark.etapa1


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


def _resultado(promedio: float) -> ResultadoCV:
    return ResultadoCV([promedio], promedio, 0.0, "StratifiedKFold(1)")


def test_registrar_run_guarda_parametros_metricas_y_tags():
    resultado = ResultadoCV(
        puntajes=[0.1, 0.2, 0.3],
        promedio=0.2,
        desviacion=0.0816,
        descripcion_validacion="StratifiedGroupKFold(3)",
    )
    modelo = DummyClassifier().fit([[1], [2], [3]], ["a", "b", "a"])

    run_id = registrar_run(
        "dummy-prueba",
        resultado,
        params={"modelo": "DummyClassifier", "estrategia": "prior"},
        modelo=modelo,
        etiquetas={"tipo": "baseline"},
        nombre_experimento="prueba-metadatos",
    )

    run = mlflow.get_run(run_id)
    assert run.data.params["modelo"] == "DummyClassifier"
    assert run.data.metrics["promedio"] == pytest.approx(0.2)
    assert run.data.metrics["puntaje_fold_0"] == pytest.approx(0.1)
    assert run.data.metrics["puntaje_fold_2"] == pytest.approx(0.3)
    assert run.data.tags["validacion"] == "StratifiedGroupKFold(3)"
    assert run.data.tags["tipo"] == "baseline"
    assert run.data.tags["mlflow.runName"] == "dummy-prueba"


def test_registrar_run_acepta_un_pipeline_con_tfidf():
    # El serializador de mlflow.sklearn (skops) rechaza los tipos que no
    # conoce; un Pipeline con TfidfVectorizer los usa, y esta prueba cubre
    # que se pueda guardar y recargar.
    letras = ["amor y flores", "odio y guerra", "amor total", "guerra total"]
    estados = ["happy", "angry", "happy", "angry"]
    pipeline = Pipeline(
        [("tfidf", TfidfVectorizer()), ("clf", LogisticRegression())]
    ).fit(letras, estados)

    run_id = registrar_run(
        "tfidf-prueba",
        _resultado(0.5),
        params={},
        modelo=pipeline,
        nombre_experimento="prueba-tfidf",
    )

    recargado = mlflow.sklearn.load_model(f"runs:/{run_id}/modelo")
    assert np.allclose(
        recargado.predict_proba(letras), pipeline.predict_proba(letras)
    )


def test_registrar_run_guarda_el_puntaje_de_entrenamiento_si_existe():
    resultado = ResultadoCV(
        puntajes=[0.4, 0.5],
        promedio=0.45,
        desviacion=0.05,
        descripcion_validacion="StratifiedKFold(2)",
        promedio_entrenamiento=0.9,
    )

    run_id = registrar_run(
        "con-entrenamiento", resultado, {}, nombre_experimento="prueba-train"
    )

    metricas = mlflow.get_run(run_id).data.metrics
    assert metricas["promedio_entrenamiento"] == pytest.approx(0.9)


def test_registrar_run_sin_puntaje_de_entrenamiento_no_lo_inventa():
    run_id = registrar_run(
        "sin-entrenamiento",
        _resultado(0.5),
        {},
        nombre_experimento="prueba-sin-train",
    )

    assert "promedio_entrenamiento" not in mlflow.get_run(run_id).data.metrics


def test_registrar_run_acepta_un_bosque_dentro_de_un_pipeline():
    # Un árbol guarda su estructura en `sklearn.tree._tree.Tree`, un tipo que
    # skops no confía por omisión: TIPOS_CONFIABLES debe declararlo.
    letras = ["amor y flores", "odio y guerra", "amor total", "guerra total"]
    estados = ["happy", "angry", "happy", "angry"]
    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("clf", RandomForestClassifier(5, random_state=0)),
        ]
    ).fit(letras, estados)

    run_id = registrar_run(
        "bosque-prueba",
        _resultado(0.5),
        params={},
        modelo=pipeline,
        nombre_experimento="prueba-bosque",
    )

    recargado = mlflow.sklearn.load_model(f"runs:/{run_id}/modelo")
    assert (recargado.predict(letras) == pipeline.predict(letras)).all()


def test_el_pipeline_recargado_predice_lo_mismo():
    X = np.array([[1.0], [2.0], [3.0], [4.0]])
    y = np.array(["a", "a", "b", "b"])
    modelo = LogisticRegression().fit(X, y)

    run_id = registrar_run(
        "prueba",
        _resultado(1.0),
        params={},
        modelo=modelo,
        nombre_experimento="prueba-recarga",
    )

    recargado = mlflow.sklearn.load_model(f"runs:/{run_id}/modelo")
    assert (recargado.predict(X) == modelo.predict(X)).all()


def test_tabla_runs_conserva_el_run_mas_reciente_de_cada_nombre():
    registrar_run("baseline", _resultado(0.1), {}, nombre_experimento="tabla")
    registrar_run("baseline", _resultado(0.2), {}, nombre_experimento="tabla")
    registrar_run("otro", _resultado(0.3), {}, nombre_experimento="tabla")

    tabla = tabla_runs("tabla")
    assert len(tabla) == 2
    fila = tabla[tabla["tags.mlflow.runName"] == "baseline"]
    assert fila["metrics.promedio"].item() == pytest.approx(0.2)
