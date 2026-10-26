"""Limpieza y partición de las letras de MoodyLyrics4Q."""

import re
from collections.abc import Sequence

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

# Marca entre corchetes, como `[Verse 1]`, `[x2]` o una parte hablada que
# ocupa varias líneas. `[^\[\]]*` impide que la marca cruce otro corchete: así
# un corchete suelto de un error de tipeo (`p[lace`) no se "come" el texto
# hasta el `]` de la marca siguiente.
_MARCA_CORCHETES = re.compile(r"\[[^\[\]]*\]")

# Marca de sección entre paréntesis, como `(Chorus)` o `(Instrumental break)`.
# `(?i)` ignora mayúsculas y `\b` exige que la palabra termine ahí, para no
# confundir `(Introducing love)` con una marca `(Intro)`.
_MARCA_PARENTESIS = re.compile(
    r"(?i)\((?:chorus|verse|bridge|intro|outro|instrumental)\b[^()\n]*\)"
)

# Cualquier secuencia de espacios, tabulaciones o saltos de línea.
_ESPACIOS = re.compile(r"\s+")


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
    # Cada marca se reemplaza por un espacio (no por nada) para no pegar las
    # palabras que estaban a ambos lados: "Hola[x2]mundo" -> "Hola mundo".
    sin_corchetes = _MARCA_CORCHETES.sub(" ", texto)
    sin_marcas = _MARCA_PARENTESIS.sub(" ", sin_corchetes)
    # Se colapsan todos los espacios en uno solo y se quitan los de los
    # extremos. Como el resultado ya no tiene marcas ni espacios repetidos,
    # volver a limpiarlo no cambia nada (es idempotente).
    return _ESPACIOS.sub(" ", sin_marcas).strip()


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
    # Cinco particiones agrupadas por artista y estratificadas por ánimo; la
    # semilla fija hace que la partición sea siempre la misma.
    particion = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=0)
    # `split` solo usa la cantidad de filas de X, no sus valores: basta un
    # arreglo de ceros del largo correcto.
    filas = np.zeros(len(estados))
    # La primera partición: su parte de validación (un 20 % de los artistas)
    # es el test, y el resto queda para entrenar y validar.
    train_val, test = next(particion.split(filas, estados, groups=artistas))
    return train_val, test
