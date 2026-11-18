"""Cliente HTTP de la API para la interfaz gráfica (material provisto)."""

import httpx


class ErrorApi(Exception):
    """La API no pudo atender la solicitud; el mensaje es apto para mostrarlo."""


def _detalle_422(respuesta: httpx.Response) -> str:
    """Resume el 422 de FastAPI: qué campo falló y por qué."""
    try:
        errores = respuesta.json()["detail"]
        return "; ".join(
            f"{'.'.join(str(parte) for parte in error['loc'][1:])}: "
            f"{error['msg']}"
            for error in errores
        )
    except (ValueError, KeyError, TypeError):
        return respuesta.text


def consultar_api(
    url: str, clave: str, medicion: dict[str, float | None]
) -> dict:
    """Envía una medición a `POST /predict` y devuelve su respuesta."""
    try:
        respuesta = httpx.post(
            f"{url.rstrip('/')}/predict",
            json=medicion,
            headers={"X-API-Key": clave},
            timeout=15,
        )
    except httpx.HTTPError as error:
        raise ErrorApi(
            f"No se pudo comunicar con la API en {url}. "
            f"¿Está en ejecución? ({type(error).__name__})"
        ) from error

    if respuesta.status_code == 200:
        return respuesta.json()
    if respuesta.status_code == 401:
        raise ErrorApi(
            "La API rechazó la clave (401). Revisen que `APR_API_KEY` sea "
            "la misma en la interfaz y en la API."
        )
    if respuesta.status_code == 422:
        raise ErrorApi(
            f"La API rechazó la medición (422). {_detalle_422(respuesta)}"
        )
    raise ErrorApi(f"La API respondió {respuesta.status_code}.")
