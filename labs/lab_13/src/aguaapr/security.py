"""Verificación de la clave de API."""


def verificar_api_key(recibida: str | None, esperada: str) -> None:
    """Acepta la clave solo si coincide con `esperada`.

    Si `recibida` es `None` o no coincide, lanza `HTTPException` con estado
    401. La comparación debe tomar el mismo tiempo sin importar en qué
    carácter difieren las claves, para que una medición de tiempos no las
    delate.
    """
    raise NotImplementedError(
        "Completen verificar_api_key antes de ejecutar el programa."
    )
