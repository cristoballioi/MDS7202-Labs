"""Etapa 1: el contrato de entrada valida tipo, rango y valores ausentes."""

import csv

import pytest
from pydantic import ValidationError

from src.aguaapr.constants import FEATURES, OPCIONALES, RANGOS
from src.aguaapr.validation import MedicionAgua

from .conftest import CSV_REAL

pytestmark = pytest.mark.etapa1


def test_una_medicion_valida_se_acepta(medicion_valida: dict):
    medicion = MedicionAgua(**medicion_valida)
    assert medicion.ph == 7.1
    assert medicion.Hardness == 190.0


@pytest.mark.parametrize("nombre", FEATURES)
def test_los_limites_del_rango_se_aceptan(nombre: str, medicion_valida: dict):
    minimo, maximo = RANGOS[nombre]
    for limite in (minimo, maximo):
        medicion = MedicionAgua(**{**medicion_valida, nombre: limite})
        assert getattr(medicion, nombre) == limite


@pytest.mark.parametrize("nombre", FEATURES)
def test_un_valor_fuera_de_rango_nombra_el_campo(
    nombre: str, medicion_valida: dict
):
    minimo, maximo = RANGOS[nombre]
    for fuera in (minimo - 0.1, maximo + 0.1):
        with pytest.raises(ValidationError) as error:
            MedicionAgua(**{**medicion_valida, nombre: fuera})
        assert nombre in str(error.value)


def test_un_nan_se_rechaza(medicion_valida: dict):
    with pytest.raises(ValidationError, match="ph"):
        MedicionAgua(**{**medicion_valida, "ph": float("nan")})


@pytest.mark.parametrize("nombre", OPCIONALES)
def test_las_columnas_opcionales_aceptan_valores_ausentes(
    nombre: str, medicion_valida: dict
):
    medicion = MedicionAgua(**{**medicion_valida, nombre: None})
    assert getattr(medicion, nombre) is None


def test_las_columnas_opcionales_pueden_omitirse(medicion_valida: dict):
    sin_opcionales = {
        k: v for k, v in medicion_valida.items() if k not in OPCIONALES
    }
    assert MedicionAgua(**sin_opcionales).ph is None


@pytest.mark.parametrize("nombre", [n for n in FEATURES if n not in OPCIONALES])
def test_una_columna_obligatoria_no_puede_faltar(
    nombre: str, medicion_valida: dict
):
    sin_columna = {k: v for k, v in medicion_valida.items() if k != nombre}
    with pytest.raises(ValidationError, match=nombre):
        MedicionAgua(**sin_columna)
    with pytest.raises(ValidationError, match=nombre):
        MedicionAgua(**{**medicion_valida, nombre: None})


def test_el_esquema_acepta_cada_fila_del_csv_real():
    with CSV_REAL.open(newline="") as archivo:
        for numero, fila in enumerate(csv.DictReader(archivo), start=2):
            datos = {c: float(fila[c]) if fila[c] else None for c in FEATURES}
            try:
                MedicionAgua.model_validate(datos)
            except ValidationError as error:  # pragma: no cover
                pytest.fail(
                    f"La línea {numero} del CSV real se rechazó: {error}"
                )
