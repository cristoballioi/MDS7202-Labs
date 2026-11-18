"""Carga del modelo desde su artefacto."""

from pathlib import Path
from typing import Any

from sklearn.pipeline import Pipeline


def cargar_modelo(directorio: Path) -> tuple[Pipeline, dict[str, Any]]:
    """Carga el artefacto de `directorio` y devuelve (modelo, metadata).

    Antes de cargar el modelo comprueba que las variables de la metadata sean
    exactamente `FEATURES`, en ese orden, y que `sklearn_version` coincida con
    la versión de scikit-learn instalada. Si algo no calza lanza
    `ErrorArtefacto` con un mensaje que nombra la diferencia.
    """
    raise NotImplementedError(
        "Completen cargar_modelo antes de ejecutar el programa."
    )
