import numpy as np
import polars as pl
import pytest

from src.heroverse.clustering import (
    elegir_k,
    equivalentes,
    estabilidad,
    perfil_clusters,
)

pytestmark = pytest.mark.etapa5


@pytest.fixture
def tres_grupos() -> np.ndarray:
    """Tres nubes separadas de 20 puntos en dos dimensiones."""
    rng = np.random.default_rng(7)
    centros = np.array([[0.0, 0.0], [10.0, 0.0], [0.0, 10.0]])
    return np.vstack([c + rng.normal(scale=0.5, size=(20, 2)) for c in centros])


def test_elegir_k_reporta_inercia_y_silhouette(tres_grupos):
    tabla = elegir_k(tres_grupos, [2, 3, 4, 5])
    assert tabla.columns == ["k", "inercia", "silhouette"]
    inercias = tabla["inercia"].to_list()
    assert inercias == sorted(inercias, reverse=True)
    assert tabla["silhouette"].is_between(-1, 1).all()
    mejor = tabla.sort("silhouette", descending=True)["k"][0]
    assert mejor == 3


def test_estabilidad_alta_con_grupos_claros(tres_grupos):
    valor = estabilidad(tres_grupos, 3, semillas=[0, 1, 2, 3])
    assert 0.9 <= valor <= 1.0


def test_estabilidad_baja_sin_estructura():
    rng = np.random.default_rng(0)
    ruido = rng.uniform(size=(200, 2))
    valor = estabilidad(ruido, 8, semillas=[0, 1, 2, 3])
    assert valor < 0.9


def test_perfil_clusters_tamanio_y_promedios():
    features = pl.DataFrame({"fuerza": [10, 20, 90, 100]})
    perfil = perfil_clusters(features, np.array([0, 0, 1, 1]), ["fuerza"])
    assert perfil.rows() == [(0, 2, 15.0), (1, 2, 95.0)]


def test_equivalentes_fuera_de_marvel_y_ordenados():
    personajes = pl.DataFrame(
        {
            "name": ["Mercenario", "Gemelo", "Primo", "Lejano", "Anonimo"],
            "creator": [
                "Marvel Comics",
                "Marvel Comics",
                "DC Comics",
                "Image Comics",
                None,
            ],
        }
    )
    X = np.array([[1.0, 0.0], [0.99, 0.1], [0.9, 0.3], [0.0, 1.0], [0.7, 0.7]])
    resultado = equivalentes(X, personajes, "Mercenario", k=3)
    assert resultado.columns == ["name", "creator", "distancia"]
    assert "Marvel Comics" not in resultado["creator"].to_list()
    assert resultado["name"].to_list() == ["Primo", "Anonimo", "Lejano"]
    distancias = resultado["distancia"].to_list()
    assert distancias == sorted(distancias)
