import numpy as np
import pytest
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.model_selection import GroupKFold, KFold
from sklearn.neighbors import KNeighborsRegressor

from src.pasturecam.evaluation import construir_pipeline, evaluar

pytestmark = pytest.mark.etapa3


def _datos_con_grupos_duplicados(
    n_grupos: int = 10, repeticiones: int = 2, semilla: int = 0
):
    """Cada grupo tiene `repeticiones` filas casi idénticas entre sí.

    Si una fila de un grupo cae en entrenamiento y su casi-duplicado cae en
    validación (posible con `KFold`, imposible con `GroupKFold`), predecirla
    es trivial: el vecino más cercano es su propio duplicado.
    """
    rng = np.random.default_rng(semilla)
    X, y, grupos = [], [], []
    for grupo in range(n_grupos):
        x_base = rng.normal(size=4)
        y_base = rng.normal() * 10
        for _ in range(repeticiones):
            X.append(x_base + rng.normal(scale=0.01, size=4))
            y.append(y_base + rng.normal(scale=0.01))
            grupos.append(grupo)
    return np.array(X), np.array(y), np.array(grupos)


def test_groupkfold_nunca_mezcla_un_grupo_entre_train_y_test():
    X, y, grupos = _datos_con_grupos_duplicados()
    for indices_train, indices_test in GroupKFold(n_splits=5).split(
        X, y, grupos
    ):
        assert set(grupos[indices_train]).isdisjoint(set(grupos[indices_test]))


def test_kfold_sobreestima_frente_a_groupkfold_con_grupos_duplicados():
    X, y, grupos = _datos_con_grupos_duplicados()
    regresor = KNeighborsRegressor(n_neighbors=1)

    resultado_kfold = evaluar(
        regresor, X, y, grupos, KFold(n_splits=5, shuffle=True, random_state=0)
    )
    resultado_grupal = evaluar(regresor, X, y, grupos, GroupKFold(n_splits=5))

    # KFold puede dejar el casi-duplicado de una fila de test en train:
    # predecirla es casi perfecto. GroupKFold nunca permite eso.
    assert resultado_kfold.promedio > resultado_grupal.promedio
    assert resultado_kfold.descripcion_validacion == "KFold(5)"
    assert resultado_grupal.descripcion_validacion == "GroupKFold(5)"


_medias_de_entrenamiento_vistas: list[float] = []


class _RegresorEspia(BaseEstimator, RegressorMixin):
    """Regresor trivial que registra la media de los datos con que se ajustó.

    Registra en una lista externa (no en `self`) porque `evaluar` clona el
    estimador en cada fold con `sklearn.base.clone`, y clonar construye una
    instancia nueva: cualquier estado en `self` se perdería entre folds.
    """

    def fit(self, X, y):
        _medias_de_entrenamiento_vistas.append(float(np.mean(X)))
        self.media_y_ = float(np.mean(y))
        return self

    def predict(self, X):
        return np.full(len(X), self.media_y_)


def test_evaluar_ajusta_cada_fold_solo_con_su_entrenamiento():
    _medias_de_entrenamiento_vistas.clear()
    rng = np.random.default_rng(0)
    # Dos grupos con escalas muy distintas: si `evaluar` ajustara con los
    # datos completos antes de dividir, ambas medias vistas por el espía
    # mezclarían las dos escalas y saldrían parecidas entre sí.
    X = np.concatenate(
        [rng.normal(0, 1, size=(20, 3)), rng.normal(100, 1, size=(20, 3))]
    )
    y = rng.normal(size=40)
    grupos = np.array([0] * 20 + [1] * 20)

    # Sin escalador: el espía recibe el `X` del fold tal cual, para
    # que su media refleje directamente qué datos vio ese fold.
    evaluar(_RegresorEspia(), X, y, grupos, GroupKFold(n_splits=2))

    assert len(_medias_de_entrenamiento_vistas) == 2
    # Un fold de entrenamiento es puro grupo 0 (media ~0), el otro puro
    # grupo 1 (media ~100): deben quedar lejos entre sí, no mezclados.
    assert (
        abs(
            _medias_de_entrenamiento_vistas[0]
            - _medias_de_entrenamiento_vistas[1]
        )
        > 50
    )


def test_construir_pipeline_tiene_escalador_y_regresor():
    pipeline = construir_pipeline(KNeighborsRegressor())
    nombres = [nombre for nombre, _ in pipeline.steps]
    assert nombres == ["escalador", "regresor"]
