"""Pipeline de clasificación sobre las letras."""

from sklearn.pipeline import Pipeline


def construir_pipeline(k_palabras: int | None = None) -> Pipeline:
    """Arma el pipeline de texto: TF-IDF y regresión logística, sin ajustar.

    El pipeline tiene dos pasos, `"tfidf"` y `"clasificador"`. `"tfidf"` es un
    `TfidfVectorizer` que descarta las palabras vacías del inglés
    (`stop_words="english"`) y las que aparecen en menos de dos canciones
    (`min_df=2`). `"clasificador"` es una `LogisticRegression` con
    `max_iter=1000`. Si `k_palabras` no es `None`, se inserta entre ambos un
    paso `"seleccion"`: un `SelectKBest` con la prueba `chi2` que se queda con
    las `k_palabras` palabras más asociadas a la etiqueta. Como la selección
    vive dentro del pipeline, cada fold la calcula solo con sus letras de
    entrenamiento.
    """
    raise NotImplementedError(
        "Completen construir_pipeline antes de ejecutar el programa."
    )
