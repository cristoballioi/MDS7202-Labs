import numpy as np
import pytest

PALABRAS_POR_ESTADO = {
    "happy": ["sol", "baile", "risa", "fiesta", "verano"],
    "relaxed": ["rio", "calma", "brisa", "sueño", "luna"],
    "sad": ["lluvia", "adios", "lagrimas", "frio", "soledad"],
    "angry": ["fuego", "guerra", "odio", "grito", "furia"],
}


@pytest.fixture
def corpus_sintetico() -> tuple[list[str], list[str]]:
    """Cuarenta letras inventadas, diez por estado de ánimo.

    Cada letra mezcla palabras de su estado con dos palabras comunes a todos,
    para que haya vocabulario compartido y vocabulario que discrimina. Se
    devuelve `(letras, estados)` en el mismo orden.
    """
    rng = np.random.default_rng(0)
    letras, estados = [], []
    for estado, palabras in PALABRAS_POR_ESTADO.items():
        for _ in range(10):
            propias = rng.choice(palabras, size=6).tolist()
            comunes = rng.choice(["yo", "tu", "ayer", "hoy"], size=2).tolist()
            letras.append(" ".join(propias + comunes))
            estados.append(estado)
    return letras, estados
