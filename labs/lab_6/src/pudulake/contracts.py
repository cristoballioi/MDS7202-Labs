"""Contratos YAML y validaciones genéricas de las tablas del lakehouse."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl
import yaml


class ContractViolation(ValueError):
    """Una tabla no cumple la garantía declarada en su contrato."""


REQUIRED_FIELDS = {
    "table",
    "purpose",
    "grain",
    "primary_key",
    "owner",
    "lineage",
    "classification",
    "required_columns",
    "column_types",
    "allow_empty",
    "constraints",
}
ALLOWED_RULES = {
    "nullable",
    "unique",
    "minimum",
    "allowed_values",
    "finite",
}
ALLOWED_TYPES = {"string", "integer", "float", "datetime", "date"}


def load_contract(path: Path) -> dict[str, Any]:
    """Lee un contrato YAML y verifica sus campos de gobernanza mínimos."""
    contract = yaml.safe_load(path.read_text())
    if not isinstance(contract, dict):
        raise ContractViolation(f"{path.name} debe contener un mapa YAML.")
    missing = REQUIRED_FIELDS - set(contract)
    if missing:
        raise ContractViolation(
            f"{path.name} no declara: {', '.join(sorted(missing))}."
        )
    unknown = set(contract) - REQUIRED_FIELDS
    if unknown:
        raise ContractViolation(
            f"{path.name} declara campos desconocidos: "
            f"{', '.join(sorted(unknown))}."
        )
    required_columns = contract["required_columns"]
    if not isinstance(required_columns, list) or not required_columns:
        raise ContractViolation(
            f"{path.name} debe declarar columnas requeridas."
        )
    if not all(
        isinstance(column, str) and column for column in required_columns
    ):
        raise ContractViolation(
            f"{path.name} tiene columnas requeridas inválidas."
        )
    if len(set(required_columns)) != len(required_columns):
        raise ContractViolation(f"{path.name} repite columnas requeridas.")
    if (
        not isinstance(contract["primary_key"], list)
        or not contract["primary_key"]
    ):
        raise ContractViolation(
            f"{path.name} debe declarar una clave primaria."
        )
    if not set(contract["primary_key"]) <= set(required_columns):
        raise ContractViolation(
            f"{path.name} declara una clave fuera de sus columnas requeridas."
        )
    for field in ("table", "purpose", "grain", "owner", "classification"):
        if not isinstance(contract[field], str) or not contract[field].strip():
            raise ContractViolation(f"{path.name} no declara {field}.")
    if not isinstance(contract["lineage"], list):
        raise ContractViolation(
            f"{path.name} debe declarar lineage como lista."
        )
    if not isinstance(contract["allow_empty"], bool):
        raise ContractViolation(
            f"{path.name} debe declarar allow_empty como booleano."
        )
    column_types = contract["column_types"]
    if not isinstance(column_types, dict) or not column_types:
        raise ContractViolation(f"{path.name} debe declarar tipos críticos.")
    if not set(column_types) <= set(required_columns):
        raise ContractViolation(
            f"{path.name} declara tipos para columnas no requeridas."
        )
    invalid_types = {
        column
        for column, dtype in column_types.items()
        if dtype not in ALLOWED_TYPES
    }
    if invalid_types:
        raise ContractViolation(
            f"{path.name} declara tipos no reconocidos: "
            f"{', '.join(sorted(invalid_types))}."
        )
    constraints = contract["constraints"]
    if not isinstance(constraints, dict) or not constraints:
        raise ContractViolation(f"{path.name} debe declarar restricciones.")
    if not set(constraints) <= set(required_columns):
        raise ContractViolation(
            f"{path.name} restringe columnas no requeridas."
        )
    for column, rules in constraints.items():
        if not isinstance(rules, dict):
            raise ContractViolation(f"{path.name}.{column} debe ser un mapa.")
        unknown_rules = set(rules) - ALLOWED_RULES
        if unknown_rules:
            raise ContractViolation(
                f"{path.name}.{column} declara reglas desconocidas: "
                f"{', '.join(sorted(unknown_rules))}."
            )
    return contract


def validate_contract(frame: pl.DataFrame, contract: dict[str, Any]) -> None:
    """Levanta ``ContractViolation`` si ``frame`` rompe su contrato."""
    required_columns = set(contract["required_columns"])
    missing = required_columns - set(frame.columns)
    if missing:
        raise ContractViolation(
            f"{contract['table']} no tiene: {', '.join(sorted(missing))}."
        )

    if frame.is_empty() and not contract["allow_empty"]:
        raise ContractViolation(f"{contract['table']} no admite tablas vacías.")

    for column, expected in contract["column_types"].items():
        dtype = frame.schema[column]
        matches = {
            "string": dtype == pl.String,
            "integer": dtype.is_integer(),
            "float": dtype.is_float(),
            "datetime": dtype.base_type() == pl.Datetime,
            "date": dtype == pl.Date,
        }[expected]
        if not matches:
            raise ContractViolation(
                f"{contract['table']}.{column} debe tener tipo {expected}; "
                f"recibió {dtype}."
            )

    keys = contract["primary_key"]
    if keys:
        null_keys = (
            frame.select(
                pl.any_horizontal([pl.col(key).is_null() for key in keys])
            )
            .to_series()
            .any()
        )
        if null_keys or frame.select(keys).n_unique() != frame.height:
            raise ContractViolation(
                f"{contract['table']} no respeta su clave primaria {keys}."
            )

    for column, rules in contract["constraints"].items():
        if column not in frame.columns:
            raise ContractViolation(
                f"{contract['table']} no tiene la columna restringida {column}."
            )
        series = frame[column]
        if rules.get("nullable") is False and series.null_count() > 0:
            raise ContractViolation(
                f"{contract['table']}.{column} no admite nulos."
            )
        if rules.get("unique") is True and series.n_unique() != frame.height:
            raise ContractViolation(
                f"{contract['table']}.{column} debe ser única."
            )
        if "minimum" in rules and series.drop_nulls().min() < rules["minimum"]:
            raise ContractViolation(
                f"{contract['table']}.{column} no puede ser menor que "
                f"{rules['minimum']}."
            )
        if rules.get("finite") is True:
            non_finite = series.drop_nulls().filter(
                ~series.drop_nulls().is_finite()
            )
            if non_finite.len() > 0:
                raise ContractViolation(
                    f"{contract['table']}.{column} debe contener valores finitos."
                )
        if "allowed_values" in rules:
            values = set(series.drop_nulls().unique().to_list())
            allowed = set(rules["allowed_values"])
            if not values <= allowed:
                raise ContractViolation(
                    f"{contract['table']}.{column} contiene valores fuera del "
                    "contrato."
                )
