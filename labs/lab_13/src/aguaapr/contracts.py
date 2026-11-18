"""Contratos del servicio: la respuesta y lo que las rutas necesitan."""

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from src.aguaapr.config import Settings


class RespuestaPrediccion(BaseModel):
    prediccion: int
    probabilidad: float


@dataclass
class Servicios:
    """Lo que las rutas necesitan: configuración y modelo."""

    settings: Settings
    modelo: Any
    metadata: dict[str, Any]
