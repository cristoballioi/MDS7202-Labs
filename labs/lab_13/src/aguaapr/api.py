"""Rutas de inferencia: información del modelo, vida y predicción."""

from fastapi import APIRouter

from src.aguaapr.contracts import Servicios


def crear_router_inferencia(servicios: Servicios) -> APIRouter:
    """Construye el router con tres rutas.

    - `GET /`: describe el modelo. Responde las métricas de validación de la
      metadata, la entrada (cada columna con su rango) y la
      salida.
    - `GET /health`: ruta de vida, pública. Responde
      `{"estado": "ok"}`.
    - `POST /predict`: recibe una `MedicionAgua` en el cuerpo y responde una
      `RespuestaPrediccion` con la predicción y su probabilidad. Exige la
      clave de API con `crear_dependencia_clave`.
    """
    raise NotImplementedError(
        "Completen crear_router_inferencia antes de ejecutar el programa."
    )
