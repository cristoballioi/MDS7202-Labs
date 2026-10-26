"""Evaluación de las predicciones por franja de programación."""

from collections.abc import Sequence

import polars as pl

from src.radio_fcfm.contratos import FRANJAS


def a_franja(estado: str) -> str:
    """Devuelve la franja de programación en que suena un estado de ánimo.

    Radio fcFM programa `happy` por la mañana, `angry` en la hora del taco
    y `sad` o `relaxed` de noche; el nombre de cada franja está en `FRANJAS`.
    Si `estado` no es uno de los cuatro estados de MoodyLyrics4Q, levanta un
    `ValueError` que nombra el estado desconocido.
    """
    # Un ánimo fuera de los cuatro no tiene franja: se avisa con un error que
    # lo nombra, en vez de devolver algo inventado.
    if estado not in FRANJAS:
        raise ValueError(
            f"Estado de ánimo desconocido: {estado!r}. "
            f"Los válidos son {sorted(FRANJAS)}."
        )
    return FRANJAS[estado]


def acierto_por_franja(y_real: Sequence[str], y_pred: Sequence[str]) -> float:
    """Calcula la fracción de canciones cuya franja predicha es la correcta.

    Compara la franja del estado real con la del estado predicho, no los
    estados: confundir `sad` con `relaxed` cuenta como acierto, porque las dos
    suenan de noche. Si `y_real` e `y_pred` tienen largo distinto, levanta un
    `ValueError`. El resultado va entre 0 y 1 y, como fusionar estados solo
    elimina errores, nunca es menor que el accuracy de los cuatro estados.
    """
    # Las dos listas deben describir las mismas canciones, una a una.
    if len(y_real) != len(y_pred):
        raise ValueError(
            "y_real e y_pred deben tener el mismo largo: "
            f"{len(y_real)} != {len(y_pred)}."
        )

    # Antes de mapear, se revisa que todos los ánimos existan; si alguno no,
    # `a_franja` levanta el ValueError que lo nombra.
    desconocidos = sorted({*map(str, y_real), *map(str, y_pred)} - set(FRANJAS))
    if desconocidos:
        a_franja(desconocidos[0])

    # Se pasa cada ánimo a su franja con una expresión de Polars (sin `for`
    # sobre las canciones) y se calcula la fracción de franjas iguales.
    tabla = pl.DataFrame(
        {
            "real": [str(e) for e in y_real],
            "predicho": [str(e) for e in y_pred],
        },
        schema={"real": pl.String, "predicho": pl.String},
    )
    iguales = tabla.select(
        (
            pl.col("real").replace_strict(FRANJAS)
            == pl.col("predicho").replace_strict(FRANJAS)
        ).mean()
    ).item()
    # Con cero canciones no hay nada que acertar: se devuelve 0,0.
    return float(iguales) if iguales is not None else 0.0
