"""Evaluación de las predicciones por franja de programación."""

from collections.abc import Sequence


def a_franja(estado: str) -> str:
    """Devuelve la franja de programación en que suena un estado de ánimo.

    Radio fcFM programa `happy` por la mañana, `angry` en la hora del taco
    y `sad` o `relaxed` de noche; el nombre de cada franja está en `FRANJAS`.
    Si `estado` no es uno de los cuatro estados de MoodyLyrics4Q, levanta un
    `ValueError` que nombra el estado desconocido.
    """
    raise NotImplementedError(
        "Completen a_franja antes de ejecutar el programa."
    )


def acierto_por_franja(y_real: Sequence[str], y_pred: Sequence[str]) -> float:
    """Calcula la fracción de canciones cuya franja predicha es la correcta.

    Compara la franja del estado real con la del estado predicho, no los
    estados: confundir `sad` con `relaxed` cuenta como acierto, porque las dos
    suenan de noche. Si `y_real` e `y_pred` tienen largo distinto, levanta un
    `ValueError`. El resultado va entre 0 y 1 y, como fusionar estados solo
    elimina errores, nunca es menor que el accuracy de los cuatro estados.
    """
    raise NotImplementedError(
        "Completen acierto_por_franja antes de ejecutar el programa."
    )
