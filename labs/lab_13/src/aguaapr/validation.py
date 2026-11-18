"""Contrato de entrada: las nueve mediciones de una muestra de agua."""

from pydantic import BaseModel


class MedicionAgua(BaseModel):
    """Una muestra de agua: nueve mediciones químicas, cada una con su rango.

    Los rangos son los de la tabla del enunciado, con los límites incluidos.
    `ph`, `Sulfate` y `Trihalomethanes` pueden faltar (`None`) y su valor por
    defecto es `None`; las otras seis son obligatorias. Un valor fuera de su
    rango, o `nan`, se rechaza con un `ValidationError` que nombra el campo.
    """

    # Su código aquí: declaren las nueve mediciones con su tipo y su rango.
