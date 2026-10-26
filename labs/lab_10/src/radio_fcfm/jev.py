"""Apoyo para clasificar letras con Jev, el modelo de TypeSafe, desde el notebook.

Material provisto: este módulo viene implementado y no hay que completarlo. Deja
fijas las instrucciones y los criterios de la pregunta que se le hace a Jev,
para que nadie los ajuste mirando el resultado en el test, y se ocupa de lo
pesado: llamar a la API con varios hilos, no detenerse si una llamada falla y
guardar las respuestas en un archivo para no repetir las llamadas.

Lo que sí escriben los estudiantes es `preguntar_a_jev(letra)`, la llamada a la
API para una sola letra, que este módulo recibe como argumento.
"""

import csv
import hashlib
import json
import threading
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MODELO = "jev-latest"
URL_OPENROUTER = "https://openrouter.ai/api"
MAX_CARACTERES = 3000

INSTRUCCIONES = (
    "What mood do the lyrics of this song convey? Choose the quadrant of "
    "Russell's circumplex model of affect (valence and arousal) that fits best."
)
CRITERIOS = {
    "happy": "Pleasant and energetic: joyful, excited, celebratory, upbeat",
    "angry": "Unpleasant and energetic: anger, aggression, rage, tension",
    "sad": "Unpleasant and calm: sorrow, loss, depression, melancholy",
    "relaxed": "Pleasant and calm: serene, peaceful, tender, soothing",
}


def _huella(letra: str) -> str:
    """Identifica una respuesta: cambia si cambia el modelo, la pregunta o la letra."""
    contenido = "\n".join(
        [MODELO, INSTRUCCIONES, json.dumps(CRITERIOS, sort_keys=True), letra]
    )
    return hashlib.sha1(contenido.encode()).hexdigest()


def _leer_cache(ruta: Path) -> list[dict[str, str]]:
    with ruta.open(newline="") as archivo:
        return list(csv.DictReader(archivo))


def _guardar_cache(ruta: Path, filas: list[dict[str, str | float]]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="") as archivo:
        escritor = csv.DictWriter(
            archivo, fieldnames=["huella", "animo", "confianza"]
        )
        escritor.writeheader()
        escritor.writerows(filas)


def clasificar_con_jev(
    letras: Sequence[str],
    preguntar: Callable[[str], tuple[str, float]],
    hilos: int = 8,
    ruta_cache: Path | str | None = None,
) -> tuple[list[str | None], list[float | None]]:
    """Clasifica cada letra con `preguntar` y devuelve `(animos, confianzas)`.

    `preguntar(letra)` hace la llamada a Jev para una letra y devuelve
    `(animo, confianza)`. Las letras se procesan con `hilos` hilos y las listas
    resultantes quedan en el mismo orden que `letras`. Si una llamada falla, la
    función no se detiene: deja `None` en esa posición y avisa cuántas fallaron.

    Si se entrega `ruta_cache` y el archivo existe con las respuestas de las
    mismas letras, el mismo modelo y la misma pregunta, las lee y no llama a la
    API. Las respuestas se guardan en ese archivo solo si todas las llamadas
    salieron bien, de modo que una ejecución con fallas se puede repetir.
    """
    huellas = [_huella(letra) for letra in letras]
    cache = Path(ruta_cache) if ruta_cache is not None else None
    if cache is not None and cache.exists():
        filas = _leer_cache(cache)
        if [fila["huella"] for fila in filas] == huellas:
            print(
                f"Respuestas de Jev leídas de {cache.name}: no se llamó a la API"
            )
            return (
                [fila["animo"] for fila in filas],
                [float(fila["confianza"]) for fila in filas],
            )

    contador = {"hechas": 0, "fallas": 0}
    cerrojo = threading.Lock()

    def una(letra: str) -> tuple[str | None, float | None]:
        try:
            resultado = preguntar(letra)
        except Exception as error:
            with cerrojo:
                contador["fallas"] += 1
                if contador["fallas"] == 1:
                    print(f"Falló una llamada: {type(error).__name__}: {error}")
            resultado = (None, None)
        with cerrojo:
            contador["hechas"] += 1
            if contador["hechas"] % 50 == 0:
                print(
                    f"  {contador['hechas']}/{len(letras)} letras clasificadas"
                )
        return resultado

    with ThreadPoolExecutor(max_workers=hilos) as pool:
        resultados = list(pool.map(una, letras))
    animos = [animo for animo, _ in resultados]
    confianzas = [confianza for _, confianza in resultados]
    print(
        f"Respuestas válidas: {len(letras) - contador['fallas']} de {len(letras)}"
    )

    if cache is not None and contador["fallas"] == 0:
        _guardar_cache(
            cache,
            [
                {"huella": h, "animo": a, "confianza": c}
                for h, a, c in zip(huellas, animos, confianzas, strict=True)
            ],
        )
    return animos, confianzas
