import numpy as np
import pytest

from src.heroverse.text import vectorizar_bolsa, vectorizar_tfidf

pytestmark = pytest.mark.etapa3

TEXTOS = [
    "He can fly and has super strength.",
    "She can fly faster than sound.",
    "A master of magic and ancient spells.",
]


def test_tfidf_una_fila_por_texto_y_norma_unitaria():
    vectorizador, matriz = vectorizar_tfidf(TEXTOS, min_df=1)
    assert matriz.shape[0] == len(TEXTOS)
    normas = np.sqrt(np.asarray(matriz.multiply(matriz).sum(axis=1))).ravel()
    assert normas == pytest.approx(np.ones(len(TEXTOS)))
    vocabulario = set(vectorizador.get_feature_names_out())
    assert "fly" in vocabulario
    assert "and" not in vocabulario  # stop word del inglés


def test_tfidf_min_df_descarta_palabras_de_un_solo_texto():
    vectorizador, _ = vectorizar_tfidf(TEXTOS, min_df=2)
    assert list(vectorizador.get_feature_names_out()) == ["fly"]


def test_bolsa_cuenta_apariciones():
    vectorizador, matriz = vectorizar_bolsa(TEXTOS, min_df=1)
    assert matriz.shape[0] == len(TEXTOS)
    columna_fly = list(vectorizador.get_feature_names_out()).index("fly")
    assert matriz[:, columna_fly].toarray().ravel().tolist() == [1, 1, 0]
    assert "and" not in set(vectorizador.get_feature_names_out())


def test_bolsa_usa_el_mismo_vocabulario_que_tfidf():
    vocabulario_bolsa, _ = vectorizar_bolsa(TEXTOS, min_df=1)
    vocabulario_tfidf, _ = vectorizar_tfidf(TEXTOS, min_df=1)
    assert list(vocabulario_bolsa.get_feature_names_out()) == list(
        vocabulario_tfidf.get_feature_names_out()
    )


def test_bolsa_min_df_descarta_palabras_de_un_solo_texto():
    vectorizador, matriz = vectorizar_bolsa(TEXTOS, min_df=2)
    assert list(vectorizador.get_feature_names_out()) == ["fly"]
    assert np.asarray(matriz.sum(axis=0)).ravel().tolist() == [2]


def test_tfidf_conserva_filas_sin_tokens_como_vectores_cero():
    textos = ["flight magic", "flight strength", "the and", "rareword"]
    _, matriz = vectorizar_tfidf(textos, min_df=2)
    assert matriz.shape == (4, 1)
    assert matriz.toarray().ravel().tolist() == [1.0, 1.0, 0.0, 0.0]
