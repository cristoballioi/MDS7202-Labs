"""Constantes y tipos compartidos del paquete `pasturecam`.

Este archivo se copia igual a la pauta y al enunciado: no es un stub, porque
no hay ninguna implementación que completar, solo un contrato que los demás
módulos comparten.
"""

from dataclasses import dataclass

OBJETIVOS = [
    "Dry_Green_g",
    "Dry_Dead_g",
    "Dry_Clover_g",
    "GDM_g",
    "Dry_Total_g",
]

AREA_CUADRANTE_M2 = 0.70 * 0.30

# Peso de cada objetivo en la métrica ponderada: 0,1 para verde, muerta y
# trébol, 0,2 para GDM y 0,5 para el total.
PESOS_OBJETIVOS = {
    "Dry_Green_g": 0.1,
    "Dry_Dead_g": 0.1,
    "Dry_Clover_g": 0.1,
    "GDM_g": 0.2,
    "Dry_Total_g": 0.5,
}

NOMBRE_EXPERIMENTO = "biomasa-rahue"

# `skops` (el serializador de mlflow.sklearn) rechaza por omisión los tipos
# internos de HistGradientBoostingRegressor, pensado para archivos de origen
# desconocido. Los pipelines que registra este laboratorio son siempre
# propios, nunca un archivo externo, así que confiar en este tipo es seguro.
TIPOS_CONFIABLES = [
    "sklearn.ensemble._hist_gradient_boosting.predictor.TreePredictor"
]


@dataclass
class ResultadoCV:
    """Resultado de evaluar un pipeline con validación cruzada.

    `puntajes` trae un valor por fold, en el orden en que `cv` los generó.
    `descripcion_validacion` nombra el esquema usado (por ejemplo,
    `"GroupKFold(5)"`), para que quede junto al número y no se pierda al
    comparar dos resultados.
    """

    puntajes: list[float]
    promedio: float
    desviacion: float
    descripcion_validacion: str
