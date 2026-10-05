import numpy as np
import pytest

from src.pasturecam.metrics import gramos_a_kg_ha, r2_log_ponderado

pytestmark = pytest.mark.etapa4

OBJETIVOS = [
    "Dry_Green_g",
    "Dry_Dead_g",
    "Dry_Clover_g",
    "GDM_g",
    "Dry_Total_g",
]


def _diccionario(valores: list[float]) -> dict[str, np.ndarray]:
    return {nombre: np.array(valores) for nombre in OBJETIVOS}


def test_r2_log_ponderado_prediccion_perfecta():
    reales = _diccionario([10.0, 5.0, 2.0, 0.0, 30.0])
    assert r2_log_ponderado(reales, reales) == pytest.approx(1.0)


def test_r2_log_ponderado_respeta_los_pesos():
    # Si solo el objetivo con mayor peso (Dry_Total_g, 0,5) está mal
    # predicho y el resto es perfecto, el puntaje baja pero no se derrumba.
    reales = {
        "Dry_Green_g": np.array([10.0, 20.0, 30.0]),
        "Dry_Dead_g": np.array([5.0, 5.0, 5.0]),
        "Dry_Clover_g": np.array([2.0, 2.0, 2.0]),
        "GDM_g": np.array([12.0, 22.0, 32.0]),
        "Dry_Total_g": np.array([17.0, 27.0, 37.0]),
    }
    predichos = dict(reales)
    predichos["Dry_Total_g"] = np.array([5.0, 5.0, 5.0])
    puntaje = r2_log_ponderado(reales, predichos)
    assert puntaje < 1.0
    # Los cuatro objetivos perfectos, con peso 0,1+0,1+0,1+0,2 = 0,5, deben
    # seguir aportando su 0,5 completo al puntaje total.
    solo_imperfectos = {k: v for k, v in reales.items() if k != "Dry_Total_g"}
    solo_predichos = {k: v for k, v in predichos.items() if k != "Dry_Total_g"}
    pesos_sin_total = {
        "Dry_Green_g": 0.1,
        "Dry_Dead_g": 0.1,
        "Dry_Clover_g": 0.1,
        "GDM_g": 0.2,
    }
    aporte_perfecto = r2_log_ponderado(
        solo_imperfectos, solo_predichos, pesos_sin_total
    )
    assert aporte_perfecto == pytest.approx(0.5)


def test_r2_log_ponderado_clava_predicciones_negativas_en_cero():
    reales = _diccionario([0.0, 0.0, 0.0, 0.0, 0.0])
    predichos = _diccionario([-5.0, -5.0, -5.0, -5.0, -5.0])
    # log1p(clip(-5, 0)) = log1p(0) = 0 para ambos: el puntaje es perfecto,
    # porque clavar en 0 es la mejor predicción posible para un real de 0.
    assert r2_log_ponderado(reales, predichos) == pytest.approx(1.0)


def test_gramos_a_kg_ha_un_gramo():
    assert gramos_a_kg_ha(1.0) == pytest.approx(47.619, rel=1e-3)


def test_gramos_a_kg_ha_es_lineal():
    assert gramos_a_kg_ha(10.0) == pytest.approx(10 * gramos_a_kg_ha(1.0))
