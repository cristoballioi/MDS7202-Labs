import numpy as np
import pytest
from sklearn.preprocessing import StandardScaler

from src.heroverse.neighbors import vecinos_mas_cercanos

pytestmark = pytest.mark.etapa2

NOMBRES = ["consulta", "mismo_puntaje", "mismo_peso"]
# Columnas: puntaje (0-100) y peso en kg. "mismo_puntaje" coincide en el
# puntaje y difiere en 50 kg; "mismo_peso" coincide en el peso y difiere en
# 60 puntos. Las pruebas expresan el peso en gramos para que su rango domine
# la distancia euclidiana hasta que se escala.
X = np.array(
    [
        [50.0, 100.0],
        [50.0, 150.0],
        [110.0, 100.0],
        [20.0, 900.0],
        [80.0, 60.0],
    ]
)
NOMBRES_X = [*NOMBRES, "coloso", "ligero"]


def test_sin_escalar_domina_la_columna_de_mayor_rango():
    X_sin_peso = X.copy()
    X_sin_peso[:, 1] = X[:, 1] * 1000  # el peso en gramos agranda su rango
    vecinos = vecinos_mas_cercanos(X_sin_peso, NOMBRES_X, "consulta", k=1)
    assert vecinos["name"].to_list() == ["mismo_peso"]


def test_escalar_cambia_el_vecino():
    X_gramos = X.copy()
    X_gramos[:, 1] = X[:, 1] * 1000
    escalado = StandardScaler().fit_transform(X_gramos)
    sin_escalar = vecinos_mas_cercanos(X_gramos, NOMBRES_X, "consulta", k=1)
    con_escala = vecinos_mas_cercanos(escalado, NOMBRES_X, "consulta", k=1)
    assert sin_escalar["name"].to_list() != con_escala["name"].to_list()


def test_resultado_ordenado_y_sin_la_consulta():
    vecinos = vecinos_mas_cercanos(X, NOMBRES_X, "consulta", k=3)
    assert vecinos.columns == ["name", "distancia"]
    assert vecinos.height == 3
    assert "consulta" not in vecinos["name"].to_list()
    distancias = vecinos["distancia"].to_list()
    assert distancias == sorted(distancias)


def test_acepta_otras_metricas():
    binarias = np.array([[1, 1, 0, 0], [1, 1, 0, 1], [0, 0, 1, 1]], dtype=bool)
    vecinos = vecinos_mas_cercanos(
        binarias, NOMBRES, "consulta", k=2, metrica="jaccard"
    )
    assert vecinos["name"].to_list() == ["mismo_puntaje", "mismo_peso"]
    assert vecinos["distancia"].to_list() == pytest.approx([1 / 3, 1.0])


def test_consulta_desconocida_levanta_key_error():
    with pytest.raises(KeyError):
        vecinos_mas_cercanos(X, NOMBRES_X, "nadie")
