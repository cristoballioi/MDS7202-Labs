"""Limpieza y partición de las letras de MoodyLyrics4Q."""

from collections.abc import Sequence

import numpy as np


def limpiar_letra(texto: str) -> str:
    """Quita las marcas de estructura de una letra y normaliza los espacios.

    Las letras de lrclib traen marcas entre corchetes que no son parte de lo
    que se canta, como `[Verse 1]` o `[Chorus]`, y algunas marcas de sección
    entre paréntesis, como `(Chorus)` o `(Instrumental break)`. Esta función
    elimina ambas: las de paréntesis son las que empiezan con `Chorus`,
    `Verse`, `Bridge`, `Intro`, `Outro` o `Instrumental`, sin importar las
    mayúsculas. Deja intactos los demás paréntesis, que suelen ser coros
    (`(oh oh)`), y reemplaza cualquier secuencia de espacios, tabulaciones o
    saltos de línea por un solo espacio. El resultado no tiene espacios al
    inicio ni al final, y aplicar la función dos veces da lo mismo que
    aplicarla una.
    """
    raise NotImplementedError(
        "Completen limpiar_letra antes de ejecutar el programa."
    )


def separar_test(
    artistas: Sequence[str], estados: Sequence[str]
) -> tuple[np.ndarray, np.ndarray]:
    """Aparta el 20 % de los artistas como conjunto de test.

    Devuelve `(train_val, test)`: las posiciones de las canciones que se
    usan para entrenar y validar, y las de las que se guardan para el test. Ningún artista aparece en ambos
    conjuntos, porque las canciones de un mismo artista se parecen entre sí.
    Estratifica por estado para que los cuatro estén en los dos conjuntos
    tanto como lo permitan los grupos. La partición es reproducible: usa
    `StratifiedGroupKFold` con cinco particiones, `shuffle=True` y
    `random_state=0`, y el test es la primera de ellas.
    """
    raise NotImplementedError(
        "Completen separar_test antes de ejecutar el programa."
    )
