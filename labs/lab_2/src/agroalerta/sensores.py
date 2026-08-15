"""Clases de sensores para AgroAlerta.

Define la clase base abstracta `Sensor` y tres sensores concretos:
`SensorTemperatura`, `SensorViento` y `SensorHumedad`.
"""

from abc import ABC, abstractmethod


class Sensor(ABC):
    """Clase base para todos los sensores de la estación."""

    def __init__(self, nombre: str, unidad: str) -> None:
        self.nombre = nombre
        self.unidad = unidad

    @abstractmethod
    def es_riesgo(self, valor: float) -> bool:
        """Indica si `valor` corresponde a una situación de riesgo."""
        ...


class SensorTemperatura(Sensor):
    """Sensor de temperatura. Es riesgo bajo `_minimo` o sobre `_maximo`."""

    def __init__(self, minimo: float, maximo: float) -> None:
        super().__init__("temperatura", "°C")
        self._minimo = minimo
        self._maximo = maximo

    def es_riesgo(self, valor: float) -> bool:
        return valor < self._minimo or valor > self._maximo


class SensorViento(Sensor):
    """Sensor de viento. Es riesgo sobre `_maximo`."""

    def __init__(self, maximo: float) -> None:
        super().__init__("viento", "km/h")
        self._maximo = maximo

    def es_riesgo(self, valor: float) -> bool:
        return valor > self._maximo


class SensorHumedad(Sensor):
    """Sensor de humedad. Es riesgo sobre `_maximo`."""

    def __init__(self, maximo: float) -> None:
        super().__init__("humedad", "%")
        self._maximo = maximo

    def es_riesgo(self, valor: float) -> bool:
        return valor > self._maximo
