"""Punto de entrada de la API: `uvicorn src.aguaapr.main:app`."""

from src.aguaapr.app import crear_app
from src.aguaapr.bootstrap import construir_servicios
from src.aguaapr.config import get_settings

app = crear_app(construir_servicios(get_settings()))
