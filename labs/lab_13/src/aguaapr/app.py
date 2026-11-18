"""Arma la aplicación con sus rutas (material provisto)."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.aguaapr.api import crear_router_inferencia
from src.aguaapr.contracts import Servicios
from src.aguaapr.monitoring import REGISTRO, registrar_middleware


def crear_app(servicios: Servicios) -> FastAPI:
    app = FastAPI(title="Servicio de potabilidad de la sanitaria de Maipú")
    registrar_middleware(app)

    @app.exception_handler(Exception)
    async def error_interno(request, error):
        # El detalle va al registro del servidor, no al cliente.
        REGISTRO.error("error interno", exc_info=error)
        return JSONResponse({"detail": "Error interno"}, status_code=500)

    app.include_router(crear_router_inferencia(servicios))
    return app
