"""Generación de features desde el scrape de superherodb."""

import polars as pl
from sklearn.preprocessing import MultiLabelBinarizer

from src.heroverse.columns import CATEGORICAS, PUNTAJES


def altura_en_cm(columna: str = "height") -> pl.Expr:
    """Expresión con la altura en centímetros, llamada `altura_cm`.

    Lee la parte métrica de valores como "6'2 • 188 cm" (188,0) o
    "49'2 • 15.0 meters" (1 500,0). Es nula si el valor es "-" o
    "0'0 • 0 cm": nadie mide 0 cm, así que ese cero es la forma en que el
    scrape marca un dato ausente.
    """
    # Extraemos el número que sigue al "•" y su unidad (cm o meters).
    # "-" no calza con el patrón, así que numero/unidad quedan nulos.
    numero = pl.col(columna).str.extract(r"•\s*([\d,.]+)\s*(?:cm|meters)", 1)
    unidad = pl.col(columna).str.extract(r"•\s*[\d,.]+\s*(cm|meters)", 1)
    # La coma de miles no aplica acá, pero la sacamos por si el scrape la usa.
    valor = numero.str.replace_all(",", "").cast(pl.Float64)
    # "meters" se convierte a centímetros multiplicando por 100.
    cm = pl.when(unidad == "meters").then(valor * 100).otherwise(valor)
    # Un valor métrico de 0 cm es un dato ausente, no una altura real.
    return pl.when(cm == 0).then(None).otherwise(cm).alias("altura_cm")


def peso_en_kg(columna: str = "weight") -> pl.Expr:
    """Expresión con el peso en kilogramos, llamada `peso_kg`.

    Lee la parte métrica de valores como "198 lb • 89 kg" (89,0) o
    "6,600 lb • 3.0 tons" (3 000,0; una tonelada son 1 000 kg). La coma de
    "6,600" separa miles. Es nula si el valor es "-".
    """
    # Extraemos el número métrico (kg o tons) y su unidad.
    numero = pl.col(columna).str.extract(r"•\s*([\d,.]+)\s*(?:kg|tons)", 1)
    unidad = pl.col(columna).str.extract(r"•\s*[\d,.]+\s*(kg|tons)", 1)
    # Quitamos la coma de miles (ej. "6,600") antes de castear a float.
    valor = numero.str.replace_all(",", "").cast(pl.Float64)
    # "tons" se convierte a kilogramos multiplicando por 1000.
    kg = pl.when(unidad == "tons").then(valor * 1000).otherwise(valor)
    return kg.alias("peso_kg")


def anio_aparicion(columna: str = "first_appearance") -> pl.Expr:
    """Expresión `anio_aparicion` (Int64) con el año de primera aparición.

    Lee "(April, 2008)", "(1979)" o "(november 1986)". Solo acepta años entre
    1900 y 2029, para no leer "(2099)", que es parte de un título.
    """
    patron = "\\((?:[A-Za-z]+,?\\s+)?(19\\d{2}|20[0-2]\\d)\\)"
    return (
        pl.col(columna)
        .str.extract(patron, 1)
        .cast(pl.Int64)
        .alias("anio_aparicion")
    )


def lista_poderes(columna: str = "superpowers") -> pl.Expr:
    """Expresión `poderes`: "['Flight', 'Super Speed']" como lista de strings.

    "[]" produce una lista vacía. Se eliminan etiquetas repetidas
    conservando el orden de primera aparición.
    """
    # extract_all captura cada substring entre comillas simples, incluidas
    # las comillas ("'Flight'"); list.eval + strip_chars se las quita a cada
    # elemento de la lista resultante. "[]" no tiene comillas, así que
    # extract_all devuelve una lista vacía.
    return (
        pl.col(columna)
        .str.extract_all(r"'[^']+'")
        .list.eval(pl.element().str.strip_chars("'"))
        # maintain_order=True deduplica conservando la primera aparición:
        # un poder repetido dos veces en el texto cuenta una sola vez.
        .list.unique(maintain_order=True)
        .alias("poderes")
    )


def puntajes_con_ficha() -> list[pl.Expr]:
    """Los seis `PUNTAJES` como enteros, nulos si todos valen 0.

    Seis ceros no describen a un personaje sin habilidades: en el catálogo
    coinciden siempre con `overall_score == "-"`, es decir, sin ficha.
    """
    # "Sin ficha" se detecta comparando los seis puntajes contra 0 a la vez.
    sin_ficha = pl.all_horizontal([pl.col(c) == 0 for c in PUNTAJES])
    return [
        pl.when(sin_ficha)
        .then(None)
        .otherwise(pl.col(c))
        .cast(pl.Int64)
        .alias(c)
        for c in PUNTAJES
    ]


def construir_features(personajes: pl.DataFrame) -> pl.DataFrame:
    """Devuelve una fila por personaje con sus features tipadas.

    Columnas, en este orden: `name`; las de `CATEGORICAS` sin cambios; los
    seis `PUNTAJES` según `puntajes_con_ficha` (ambas listas están en
    `src/heroverse/columns.py`); `altura_cm`, `peso_kg`,
    `anio_aparicion` y `poderes`; `n_poderes`, el largo de `poderes`; y
    `powers_text` sin cambios. La codificación binaria se ajusta después
    con `ajustar_poderes`, a partir de la lista `poderes`.

    Precondición: `name` no tiene nulos ni duplicados. Si los tiene, levanta
    `ValueError` con un mensaje que menciona `name`, porque cada fila debe
    representar a un solo personaje.
    """
    # Validamos el grano antes de transformar nada: cada fila es un
    # personaje único, así que "name" no puede tener nulos ni repetirse.
    if personajes["name"].null_count() > 0:
        raise ValueError("La columna 'name' no debe tener valores nulos.")
    if personajes["name"].n_unique() != personajes.height:
        raise ValueError("La columna 'name' no debe tener duplicados.")

    # Seleccionamos y tipamos todas las columnas en el orden pedido,
    # dejando "poderes" listo para calcular "n_poderes" después.
    resultado = personajes.select(
        "name",
        *CATEGORICAS,
        *puntajes_con_ficha(),
        altura_en_cm(),
        peso_en_kg(),
        anio_aparicion(),
        lista_poderes(),
        "powers_text",
    ).with_columns(pl.col("poderes").list.len().alias("n_poderes"))

    # Reordenamos para que "n_poderes" quede junto a "poderes" y antes de
    # "powers_text", tal como pide el contrato.
    orden = [
        "name",
        *CATEGORICAS,
        *PUNTAJES,
        "altura_cm",
        "peso_kg",
        "anio_aparicion",
        "poderes",
        "n_poderes",
        "powers_text",
    ]
    return resultado.select(orden)


def ajustar_poderes(
    features: pl.DataFrame,
) -> tuple[MultiLabelBinarizer, pl.DataFrame]:
    """Aprende los poderes del catálogo y devuelve encoder y tabla codificada.

    `features` tiene una columna `poderes` con listas de strings sin nulos.
    Se conservan todas las columnas, el número y el orden de las filas.
    Se agrega una columna Int8 `poder_<etiqueta>` por cada etiqueta aprendida,
    en el orden de `classes_`, sin modificar espacios ni mayúsculas.
    Una lista vacía produce una fila de ceros en el bloque de poderes.
    """
    binarizador = MultiLabelBinarizer()
    # fit_transform aprende el vocabulario (classes_, orden alfabético) y
    # codifica en un solo paso.
    matriz = binarizador.fit_transform(features["poderes"].to_list())
    columnas_poder = [f"poder_{etiqueta}" for etiqueta in binarizador.classes_]
    bloque_poderes = pl.DataFrame(
        {
            columna: matriz[:, i].astype("int8")
            for i, columna in enumerate(columnas_poder)
        }
    )
    # Concatenamos horizontalmente: mismas filas y orden, columnas nuevas al final.
    salida = pl.concat([features, bloque_poderes], how="horizontal_extend")
    return binarizador, salida


def transformar_poderes(
    features: pl.DataFrame, binarizador: MultiLabelBinarizer
) -> pl.DataFrame:
    """Codifica poderes con un encoder ajustado, sin aprender nuevas etiquetas.

    Conserva filas y columnas de `features`; agrega el mismo bloque Int8 y
    en el mismo orden que `ajustar_poderes`. Una lista vacía da ceros.
    Un poder fuera de `classes_` no tiene columna: se ignora, y
    `MultiLabelBinarizer` emite un `UserWarning` que lo nombra. No se
    reajusta, porque eso cambiaría las columnas del catálogo.
    """
    # transform (no fit_transform) reutiliza classes_ ya aprendidas y avisa
    # con UserWarning si aparece una etiqueta desconocida, sin agregarla.
    matriz = binarizador.transform(features["poderes"].to_list())
    columnas_poder = [f"poder_{etiqueta}" for etiqueta in binarizador.classes_]
    bloque_poderes = pl.DataFrame(
        {
            columna: matriz[:, i].astype("int8")
            for i, columna in enumerate(columnas_poder)
        }
    )
    return pl.concat([features, bloque_poderes], how="horizontal_extend")
