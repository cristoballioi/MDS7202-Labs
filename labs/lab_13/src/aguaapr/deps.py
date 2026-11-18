"""Dependencia de FastAPI que exige la clave de API (material provisto)."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Header

from src.aguaapr.contracts import Servicios
from src.aguaapr.security import verificar_api_key


def crear_dependencia_clave(servicios: Servicios) -> Callable[..., None]:
    """Devuelve la dependencia que llama a `verificar_api_key` del equipo."""

    def dependencia(
        x_api_key: Annotated[str | None, Header()] = None,
    ) -> None:
        verificar_api_key(
            x_api_key, servicios.settings.api_key.get_secret_value()
        )

    return dependencia
