"""Ingesta reproducible de las fuentes Parquet hacia Bronze."""

from __future__ import annotations

from pathlib import Path

import polars as pl


def read_sources(raw_dir: Path) -> dict[str, pl.DataFrame]:
    """Lee las cuatro fuentes crudas y conserva exactamente su esquema."""

    # Mapeo de las llaves del diccionario con sus respectivos archivos Parquet
    archivos_esperados = {
        "orders": "orders.parquet",
        "customers": "customers.parquet",
        "order_items": "order_items.parquet",
        "payments": "payments.parquet",
    }

    fuentes = {}

    for llave, nombre_archivo in archivos_esperados.items():
        ruta_archivo = raw_dir / nombre_archivo

        # Validar la existencia del archivo para levantar el error solicitado
        if not ruta_archivo.exists():
            raise FileNotFoundError(
                f"No se encontró la fuente ausente: {nombre_archivo} en el directorio {raw_dir}"
            )

        # Leer la fuente sin alterar el esquema (regla Bronze)
        fuentes[llave] = pl.read_parquet(ruta_archivo)

    return fuentes
