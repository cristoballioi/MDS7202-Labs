import numpy as np
import pytest
from sklearn.exceptions import NotFittedError
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.utils.validation import check_is_fitted

from src.radio_fcfm.pipeline import construir_pipeline

pytestmark = pytest.mark.etapa2


def test_construir_pipeline_encadena_vectorizador_y_clasificador():
    pipeline = construir_pipeline()
    assert list(pipeline.named_steps) == ["tfidf", "clasificador"]
    assert isinstance(pipeline.named_steps["tfidf"], TfidfVectorizer)
    assert isinstance(pipeline.named_steps["clasificador"], LogisticRegression)


def test_construir_pipeline_usa_los_parametros_del_contrato():
    pipeline = construir_pipeline()
    assert pipeline.named_steps["tfidf"].stop_words == "english"
    assert pipeline.named_steps["tfidf"].min_df == 2
    assert pipeline.named_steps["clasificador"].max_iter == 1000


def test_construir_pipeline_devuelve_un_pipeline_sin_ajustar():
    # Si el vectorizador llegara ajustado, ya habría visto las letras de
    # validación: justo la fuga que el pipeline debe evitar.
    with pytest.raises(NotFittedError):
        check_is_fitted(construir_pipeline().named_steps["tfidf"])


def test_construir_pipeline_entrega_probabilidades(corpus_sintetico):
    letras, estados = corpus_sintetico
    pipeline = construir_pipeline().fit(letras, estados)

    probabilidades = pipeline.predict_proba(letras)

    assert probabilidades.shape == (len(letras), 4)
    assert np.allclose(probabilidades.sum(axis=1), 1.0)
    assert sorted(pipeline.classes_) == sorted(set(estados))


def test_cada_fold_ajusta_su_propio_vocabulario(corpus_sintetico):
    letras, estados = corpus_sintetico
    # Cada palabra `par<k>` aparece en exactamente dos letras. Con `min_df=2`
    # solo entra al vocabulario de un fold si sus dos letras quedaron en el
    # entrenamiento: si el vocabulario se ajustara con todo el corpus, sería
    # el mismo en los cuatro folds.
    letras = [f"{letra} par{i % 20}" for i, letra in enumerate(letras)]
    cv = StratifiedKFold(4, shuffle=True, random_state=0)

    resultado = cross_validate(
        construir_pipeline(),
        letras,
        estados,
        cv=cv,
        return_estimator=True,
    )

    vocabularios = [
        frozenset(e.named_steps["tfidf"].vocabulary_)
        for e in resultado["estimator"]
    ]
    assert len(set(vocabularios)) > 1


def test_k_palabras_agrega_la_seleccion_dentro_del_pipeline(corpus_sintetico):
    letras, estados = corpus_sintetico
    pipeline = construir_pipeline(k_palabras=5)
    assert list(pipeline.named_steps) == [
        "tfidf",
        "seleccion",
        "clasificador",
    ]

    pipeline.fit(letras, estados)

    assert pipeline.named_steps["seleccion"].get_support().sum() == 5
