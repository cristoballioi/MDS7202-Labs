"""Entrena una versión del modelo y la guarda como artefacto.

Uso, desde la raíz del laboratorio:

    uv run python -m src.aguaapr.training

Los hiperparámetros son fijos: no se busca ninguno. El laboratorio entrega el
modelo ya entrenado en `models/`; este script solo permite reproducirlo.
"""

import argparse
import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import polars as pl
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, make_pipeline

from src.aguaapr.artifacts import guardar_artefacto
from src.aguaapr.constants import FEATURES

SEMILLA = 42
HIPERPARAMETROS = {"n_estimators": 400, "max_depth": 14}


def entrenar(csv: Path, directorio: Path) -> tuple[Pipeline, dict[str, Any]]:
    """Entrena el modelo, lo guarda en `directorio` y devuelve su metadata."""
    tabla = pl.read_csv(csv)
    # Una tabla con columnas nombradas: el pipeline recuerda sus nombres y su
    # orden, y scikit-learn rechaza después una tabla con otras columnas.
    X = tabla.select(FEATURES)
    y = tabla["Potability"].to_numpy()
    X_tr, X_va, y_tr, y_va = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEMILLA
    )

    # La imputación vive dentro del pipeline: el servicio puede recibir `null`
    # en las columnas opcionales y el modelo las completa como en el entrenamiento.
    modelo = make_pipeline(
        SimpleImputer(strategy="median"),
        RandomForestClassifier(
            n_estimators=HIPERPARAMETROS["n_estimators"],
            max_depth=HIPERPARAMETROS["max_depth"],
            random_state=SEMILLA,
            n_jobs=1,
        ),
    )
    modelo.fit(X_tr, y_tr)
    predicciones = modelo.predict(X_va)

    metadata = {
        "entrenado_en": datetime.now(UTC).isoformat(timespec="seconds"),
        "sklearn_version": sklearn.__version__,
        "features": FEATURES,
        "hiperparametros": HIPERPARAMETROS,
        "semilla": SEMILLA,
        "metricas_validacion": {
            "exactitud": round(float(accuracy_score(y_va, predicciones)), 4),
            "f1": round(float(f1_score(y_va, predicciones)), 4),
        },
        "filas_entrenamiento": len(y_tr),
        "huella_datos": hashlib.sha256(csv.read_bytes()).hexdigest()[:16],
    }
    guardar_artefacto(modelo, metadata, directorio)
    return modelo, metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", default="data/raw/water_potability.csv")
    parser.add_argument("--salida", default="models")
    args = parser.parse_args()
    _, metadata = entrenar(Path(args.datos), Path(args.salida))
    metricas = metadata["metricas_validacion"]
    print(f"Modelo guardado en {args.salida}")
    print(f"exactitud={metricas['exactitud']}  f1={metricas['f1']}")


if __name__ == "__main__":
    main()
