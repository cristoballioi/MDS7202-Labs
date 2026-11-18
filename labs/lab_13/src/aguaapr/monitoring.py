"""Registros JSON de cada solicitud (material provisto)."""

import json
import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime

from fastapi import FastAPI, Request, Response

REGISTRO = logging.getLogger("aguaapr")


class JsonFormatter(logging.Formatter):
    """Una línea JSON por registro, apta para que una plataforma la recoja."""

    def format(self, record: logging.LogRecord) -> str:
        datos = {
            "t": datetime.now(UTC).isoformat(timespec="milliseconds"),
            "nivel": record.levelname,
            "mensaje": record.getMessage(),
        }
        datos.update(getattr(record, "campos", {}))
        if record.exc_info:
            datos["traza"] = self.formatException(record.exc_info)
        return json.dumps(datos, ensure_ascii=False)


def configurar_logging(nivel: str) -> None:
    manejador = logging.StreamHandler()
    manejador.setFormatter(JsonFormatter())
    REGISTRO.handlers = [manejador]
    REGISTRO.setLevel(nivel.upper())
    REGISTRO.propagate = False


def registrar_middleware(app: FastAPI) -> None:
    """Escribe, por cada solicitud, una línea JSON con su identificador."""

    @app.middleware("http")
    async def medir(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        id_solicitud = request.headers.get("x-request-id") or uuid.uuid4().hex
        inicio = time.perf_counter()
        estado = 500
        try:
            respuesta = await call_next(request)
            estado = respuesta.status_code
            respuesta.headers["X-Request-ID"] = id_solicitud
            return respuesta
        finally:
            latencia = (time.perf_counter() - inicio) * 1000
            REGISTRO.info(
                "solicitud",
                extra={
                    "campos": {
                        "id_solicitud": id_solicitud,
                        "metodo": request.method,
                        "ruta": request.url.path,
                        "estado": estado,
                        "latencia_ms": round(latencia, 2),
                    }
                },
            )
