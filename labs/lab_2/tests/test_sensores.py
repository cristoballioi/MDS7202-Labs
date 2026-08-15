"""Pruebas unitarias para los sensores y el reporte de AgroAlerta."""

from agroalerta.reporte import contar_riesgos
from agroalerta.sensores import SensorHumedad, SensorTemperatura, SensorViento


def test_temperatura_bajo_cero_es_riesgo():
    sensor = SensorTemperatura(0, 40)

    assert sensor.es_riesgo(-2) is True


def test_temperatura_templada_no_es_riesgo():
    sensor = SensorTemperatura(0, 40)

    assert sensor.es_riesgo(18) is False


def test_viento_normal_no_es_riesgo():
    sensor = SensorViento(25)

    assert sensor.es_riesgo(10) is False


def test_viento_sobre_el_maximo_es_riesgo():
    sensor = SensorViento(25)

    assert sensor.es_riesgo(30) is True


def test_humedad_sobre_el_maximo_es_riesgo():
    sensor = SensorHumedad(85)

    assert sensor.es_riesgo(90) is True


def test_contar_riesgos_devuelve_conteo_esperado():
    sensores = [
        SensorTemperatura(0, 40),
        SensorViento(25),
        SensorHumedad(85),
    ]
    lecturas = {
        "temperatura": [-2, 18, 42],
        "viento": [10, 30],
        "humedad": [90, 70, 95],
    }

    conteo = contar_riesgos(sensores, lecturas)

    assert conteo == {"temperatura": 2, "viento": 1, "humedad": 2}


def test_contar_riesgos_sensor_sin_lecturas_da_cero():
    sensores = [SensorTemperatura(0, 40)]
    lecturas: dict[str, list[float]] = {}

    conteo = contar_riesgos(sensores, lecturas)

    assert conteo == {"temperatura": 0}
