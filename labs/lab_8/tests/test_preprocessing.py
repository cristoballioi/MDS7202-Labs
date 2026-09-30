import polars as pl
import pytest

from src.heroverse.preprocessing import construir_preprocesador

pytestmark = pytest.mark.etapa1


@pytest.fixture
def catalogo() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "strength_score": [10, 50, 90, 70, 30, None],
            "peso_kg": [60.0, 80.0, 90_000_000.0, None, 75.0, 70.0],
            "creator": [
                "Marvel Comics",
                "Marvel Comics",
                "DC Comics",
                "DC Comics",
                "Lego",
                None,
            ],
            "poder_Flight": [1, 0, 1, 0, 0, 1],
            "poder_Magic": [0, 1, 0, 1, 0, 0],
        }
    )


@pytest.fixture
def preprocesador():
    return construir_preprocesador(
        puntajes=["strength_score"],
        medidas=["peso_kg"],
        categoricas=["creator"],
        binarias=["poder_Flight", "poder_Magic"],
        min_frequency=2,
    )


def test_salida_polars_sin_nulos(catalogo, preprocesador):
    salida = preprocesador.fit_transform(catalogo)
    assert isinstance(salida, pl.DataFrame)
    assert salida.height == catalogo.height
    assert salida.null_count().sum_horizontal().item() == 0


def test_categorias_raras_comparten_una_columna(catalogo, preprocesador):
    columnas = preprocesador.fit_transform(catalogo).columns
    # Lego y "desconocido" aparecen una vez: quedan juntas como infrecuentes.
    creator = [c for c in columnas if c.startswith("creator_")]
    assert sorted(creator) == [
        "creator_DC Comics",
        "creator_Marvel Comics",
        "creator_infrequent_sklearn",
    ]


def test_nuevos_sin_reajuste_y_con_categoria_desconocida(
    catalogo, preprocesador
):
    preprocesador.fit(catalogo)
    nuevos = pl.DataFrame(
        {
            "strength_score": [40],
            "peso_kg": [85.0],
            "creator": ["Shueisha"],
            "poder_Flight": [0],
            "poder_Magic": [1],
        }
    )
    salida = preprocesador.transform(nuevos)
    assert salida.columns == preprocesador.transform(catalogo).columns
    assert salida["creator_infrequent_sklearn"].to_list() == [1.0]


def test_transform_usa_lo_aprendido_en_el_catalogo(catalogo, preprocesador):
    preprocesador.fit(catalogo)
    uno = catalogo.head(1)
    # Transformar una sola fila no reajusta: el resultado coincide con la
    # misma fila transformada junto al catálogo completo.
    solo = preprocesador.transform(uno)
    junto = preprocesador.transform(catalogo).head(1)
    assert solo.equals(junto)


def test_log_reduce_el_efecto_del_peso_extremo(catalogo, preprocesador):
    salida = preprocesador.fit_transform(catalogo)
    peso = salida["peso_kg"]
    # Sin log, el escalamiento robusto deja los 90 millones de kg a más de
    # un millón de unidades del resto; con log, a unos cientos.
    assert peso.max() < 1_000


def test_binarias_se_conservan_al_ajustar_y_transformar(
    catalogo, preprocesador
):
    columnas = ["poder_Flight", "poder_Magic"]
    ajustado = preprocesador.fit_transform(catalogo)
    assert ajustado.select(columnas).rows() == [
        (1, 0),
        (0, 1),
        (1, 0),
        (0, 1),
        (0, 0),
        (1, 0),
    ]
    nuevos = catalogo.reverse().head(2)
    transformado = preprocesador.transform(nuevos)
    assert transformado.select(columnas).rows() == [(1, 0), (0, 0)]


def test_features_encoder_y_preprocesador_comparten_columnas(personajes_crudos):
    from src.heroverse.features import (
        ajustar_poderes,
        construir_features,
        transformar_poderes,
    )

    features = construir_features(personajes_crudos)
    encoder, codificadas = ajustar_poderes(features)
    binarias = ["poder_Flight", "poder_Magic", "poder_Super Strength"]
    pipeline = construir_preprocesador(
        puntajes=["strength_score"],
        medidas=["peso_kg"],
        categoricas=["gender"],
        binarias=binarias,
        min_frequency=1,
    )
    original = pipeline.fit_transform(codificadas)
    nuevos = personajes_crudos.head(1).with_columns(
        pl.lit("Nuevo").alias("name"),
        pl.lit("['Magic', 'Magic']").alias("superpowers"),
    )
    nuevos_features = construir_features(nuevos)
    nuevos_codificados = transformar_poderes(nuevos_features, encoder)
    salida = pipeline.transform(nuevos_codificados)
    assert salida.columns == original.columns
    assert salida.select(binarias).rows() == [(0, 1, 0)]
    assert salida.null_count().sum_horizontal().item() == 0
    assert nuevos_features["n_poderes"].to_list() == [1]
