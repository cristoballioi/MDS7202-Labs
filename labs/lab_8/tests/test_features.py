import polars as pl
import pytest

from src.heroverse.columns import PUNTAJES
from src.heroverse.features import (
    altura_en_cm,
    construir_features,
    lista_poderes,
    peso_en_kg,
    puntajes_con_ficha,
)

pytestmark = pytest.mark.etapa1


def test_altura_convierte_centimetros_y_metros():
    df = pl.DataFrame({"height": ["6'2 • 188 cm", "49'2 • 15.0 meters"]})
    assert df.select(altura_en_cm())["altura_cm"].to_list() == [188.0, 1500.0]


def test_peso_convierte_kilos_y_toneladas():
    df = pl.DataFrame({"weight": ["198 lb • 89 kg", "6,600 lb • 3.0 tons"]})
    assert df.select(peso_en_kg())["peso_kg"].to_list() == [89.0, 3000.0]


def test_guion_es_faltante_y_no_cero():
    df = pl.DataFrame({"height": ["-"], "weight": ["-"]})
    resultado = df.select(altura_en_cm(), peso_en_kg())
    assert resultado.row(0) == (None, None)


def test_altura_cero_es_faltante():
    df = pl.DataFrame({"height": ["0'0 • 0 cm", "0'1 • 3 cm"]})
    assert df.select(altura_en_cm())["altura_cm"].to_list() == [None, 3.0]


def test_seis_puntajes_en_cero_son_una_ficha_faltante():
    df = pl.DataFrame(
        {c: [0, 40 if c == "combat_score" else 0] for c in PUNTAJES}
    )
    resultado = df.select(puntajes_con_ficha())
    assert resultado.row(0) == (None,) * 6
    assert resultado.row(1) == (0, 0, 0, 0, 0, 40)


def test_lista_poderes_desde_texto():
    df = pl.DataFrame({"superpowers": ["['Flight', 'Super Strength']", "[]"]})
    poderes = df.select(lista_poderes())["poderes"].to_list()
    assert poderes == [["Flight", "Super Strength"], []]


def test_construir_features_conserva_el_grano(personajes_crudos):
    features = construir_features(personajes_crudos)
    assert features.height == personajes_crudos.height
    assert features["name"].to_list() == personajes_crudos["name"].to_list()


def test_construir_features_tipa_las_columnas(personajes_crudos):
    features = construir_features(personajes_crudos)
    assert features.schema["strength_score"] == pl.Int64
    assert features.schema["poderes"] == pl.List(pl.String)
    assert features["n_poderes"].to_list() == [2, 0, 1]
    assert features["poderes"].to_list()[1] == []
    assert features["altura_cm"].to_list() == [188.0, None, 1500.0]


def test_construir_features_rechaza_nombres_repetidos(personajes_crudos):
    repetidos = pl.concat([personajes_crudos, personajes_crudos.head(1)])
    with pytest.raises(ValueError, match="name"):
        construir_features(repetidos)


def test_construir_features_rechaza_nombres_nulos(personajes_crudos):
    sin_nombre = personajes_crudos.with_columns(
        pl.when(pl.col("name") == "Brisa")
        .then(None)
        .otherwise(pl.col("name"))
        .alias("name")
    )
    with pytest.raises(ValueError, match="name"):
        construir_features(sin_nombre)


# El contrato debe detectar columnas desalineadas, pérdida de poderes o un
# reajuste del vocabulario al recibir personajes nuevos.
def test_codificar_poderes_conserva_filas_y_cubre_todas_las_etiquetas():
    from src.heroverse import features as modulo

    features = pl.DataFrame(
        {
            "name": ["Brisa", "Atlas", "Coloso"],
            "poderes": [["Flight", "Super Speed"], [], ["Super Speed"]],
        }
    )
    binarizador, salida = modulo.ajustar_poderes(features)
    assert salida["name"].to_list() == ["Brisa", "Atlas", "Coloso"]
    assert salida.select("poder_Flight", "poder_Super Speed").rows() == [
        (1, 1),
        (0, 0),
        (0, 1),
    ]
    assert binarizador.classes_.tolist() == ["Flight", "Super Speed"]
    assert salida.select(features.columns).equals(features)
    assert salida.columns == [
        *features.columns,
        "poder_Flight",
        "poder_Super Speed",
    ]
    assert salida.select("poder_Flight", "poder_Super Speed").dtypes == [
        pl.Int8,
        pl.Int8,
    ]


def test_transformar_poderes_reutiliza_columnas_sin_reajustar():
    from src.heroverse import features as modulo

    catalogo = pl.DataFrame(
        {
            "name": ["Atlas", "Brisa"],
            "poderes": [["Flight"], ["Magic"]],
        }
    )
    binarizador, original = modulo.ajustar_poderes(catalogo)
    nuevos = pl.DataFrame(
        {
            "name": ["Coloso", "Vacio"],
            "poderes": [["Magic"], []],
        }
    )
    salida = modulo.transformar_poderes(nuevos, binarizador)
    assert salida.columns == original.columns
    assert salida.select(nuevos.columns).equals(nuevos)
    assert salida.select("poder_Flight", "poder_Magic").dtypes == [
        pl.Int8,
        pl.Int8,
    ]
    assert salida.select("poder_Flight", "poder_Magic").rows() == [
        (0, 1),
        (0, 0),
    ]
    assert binarizador.classes_.tolist() == ["Flight", "Magic"]


def test_transformar_poderes_ignora_etiquetas_desconocidas():
    from src.heroverse import features as modulo

    catalogo = pl.DataFrame({"poderes": [["Flight"]]})
    binarizador, _ = modulo.ajustar_poderes(catalogo)
    nuevos = pl.DataFrame({"poderes": [["Magic", "Flight"]]})
    with pytest.warns(UserWarning, match="Magic"):
        salida = modulo.transformar_poderes(nuevos, binarizador)
    assert salida.columns == ["poderes", "poder_Flight"]
    assert salida["poder_Flight"].to_list() == [1]
    assert binarizador.classes_.tolist() == ["Flight"]


def test_poderes_repetidos_se_cuentan_una_sola_vez(personajes_crudos):
    crudos = personajes_crudos.with_columns(
        pl.lit("['Flight', 'Magic', 'Flight']").alias("superpowers")
    )
    salida = construir_features(crudos)
    assert salida["poderes"].to_list() == [["Flight", "Magic"]] * 3
    assert salida["n_poderes"].to_list() == [2, 2, 2]
