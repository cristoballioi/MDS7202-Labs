"""Construye los servicios a partir de la configuración (material provisto)."""

from src.aguaapr.config import Settings
from src.aguaapr.contracts import Servicios
from src.aguaapr.monitoring import configurar_logging
from src.aguaapr.registry import cargar_modelo


def construir_servicios(settings: Settings) -> Servicios:
    configurar_logging(settings.log_level)
    modelo, metadata = cargar_modelo(settings.model_dir)
    return Servicios(settings=settings, modelo=modelo, metadata=metadata)
