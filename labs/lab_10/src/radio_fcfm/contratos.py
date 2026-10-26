"""Constantes y tipos compartidos del paquete `fcfm`.

Este archivo se copia igual a la pauta y al enunciado: no es un stub, porque
no hay ninguna implementación que completar, solo un contrato que los demás
módulos comparten.
"""

from dataclasses import dataclass

# Los cuatro cuadrantes del modelo de Russell en MoodyLyrics4Q, en el orden en
# que se leen las filas y columnas de una matriz de confusión: arriba los dos
# de valencia positiva (`happy`, `relaxed`) y abajo los de valencia negativa
# (`sad`, `angry`).
ESTADOS = ["happy", "relaxed", "sad", "angry"]

# Franja de programación de Radio fcFM en que suena cada estado de ánimo.
FRANJAS = {
    "happy": "mañana",
    "angry": "hora del taco",
    "sad": "noche",
    "relaxed": "noche",
}

# Los dos ejes del modelo de Russell: la valencia dice qué tan agradable es el
# ánimo y la activación, cuánta energía tiene. Cada estado ocupa un cuadrante.
VALENCIA = {
    "happy": "positiva",
    "relaxed": "positiva",
    "sad": "negativa",
    "angry": "negativa",
}
ACTIVACION = {
    "happy": "alta",
    "angry": "alta",
    "relaxed": "baja",
    "sad": "baja",
}

NOMBRE_EXPERIMENTO = "radio-fcfm"

# `skops` (el serializador de mlflow.sklearn) rechaza por omisión los tipos que
# no reconoce, pensado para archivos de origen desconocido. Los pipelines que
# registra este laboratorio son siempre propios, nunca un archivo externo, así
# que confiar en los tipos que declare esta lista es seguro. Un árbol guarda su
# estructura en `Tree`, que es el tipo que un bosque necesita.
TIPOS_CONFIABLES: list[str] = ["sklearn.tree._tree.Tree"]


@dataclass
class ResultadoCV:
    """Resultado de evaluar un pipeline con validación cruzada.

    `puntajes` trae un valor por fold, en el orden en que `cv` los generó.
    `descripcion_validacion` nombra el esquema usado (por ejemplo,
    `"StratifiedGroupKFold(5)"`), para que quede junto al número y no se
    pierda al comparar dos resultados. `promedio_entrenamiento` es el puntaje
    promedio sobre las canciones con que se ajustó cada fold; queda en `None`
    cuando la evaluación no lo calculó.
    """

    puntajes: list[float]
    promedio: float
    desviacion: float
    descripcion_validacion: str
    promedio_entrenamiento: float | None = None
