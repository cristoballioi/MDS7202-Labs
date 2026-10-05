"""Codificación de texto: bag of words y TF-IDF, ambos dispersos."""

from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


def vectorizar_tfidf(
    textos: list[str], min_df: int = 2, max_features: int | None = 5000
) -> tuple[TfidfVectorizer, csr_matrix]:
    """Ajusta TF-IDF sobre `textos` y devuelve el vectorizador y la matriz.

    Usa `stop_words="english"`, porque los textos de superherodb están en
    inglés, junto con `min_df` y `max_features`. La matriz es dispersa, tiene
    una fila por texto. Las filas con tokens retenidos tienen norma 1;
    las que quedan sin tokens son vectores cero y conservan su posición.
    """
    # TfidfVectorizer normaliza cada fila a norma L2 = 1 por defecto (norm="l2"),
    # salvo las filas sin ningún token del vocabulario, que quedan en cero.
    vectorizador = TfidfVectorizer(
        stop_words="english", min_df=min_df, max_features=max_features
    )
    matriz = vectorizador.fit_transform(textos)
    return vectorizador, matriz


def vectorizar_bolsa(
    textos: list[str], min_df: int = 2, max_features: int | None = 5000
) -> tuple[CountVectorizer, csr_matrix]:
    """Cuenta las palabras de `textos` y devuelve el vectorizador y la matriz.

    Usa los mismos parámetros que `vectorizar_tfidf`: `stop_words="english"`,
    `min_df` y `max_features`. La matriz es dispersa, tiene una fila por texto
    y cada celda cuenta cuántas veces aparece la palabra en ese texto.
    """
    vectorizador = CountVectorizer(
        stop_words="english", min_df=min_df, max_features=max_features
    )
    matriz = vectorizador.fit_transform(textos)
    return vectorizador, matriz
