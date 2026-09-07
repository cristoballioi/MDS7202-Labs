"""Persistencia local en DuckLake."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import duckdb
import polars as pl


def connect_lake(lake_dir: Path) -> duckdb.DuckDBPyConnection:
    """Abre el catálogo DuckLake local y prepara sus capas."""
    lake_dir.mkdir(parents=True, exist_ok=True)
    catalog = lake_dir / "olist.ducklake"
    files = lake_dir / "olist.ducklake.files"
    files.mkdir(exist_ok=True)
    connection = duckdb.connect()
    try:
        connection.execute("LOAD ducklake")
    except duckdb.Error as error:
        connection.close()
        raise RuntimeError(
            "No se pudo cargar DuckLake. Ejecuten la preparación del "
            "ambiente antes de iniciar el flow."
        ) from error
    catalog_uri = f"ducklake:{catalog}".replace("'", "''")
    data_path = str(files).replace("'", "''")
    connection.execute(
        f"ATTACH '{catalog_uri}' AS olist (DATA_PATH '{data_path}')"
    )
    connection.execute("USE olist")
    for layer in ("bronze", "silver", "gold"):
        connection.execute(f"CREATE SCHEMA IF NOT EXISTS {layer}")
    return connection


def write_table(
    connection: duckdb.DuckDBPyConnection, table: str, frame: pl.DataFrame
) -> None:
    """Materializa un DataFrame de Polars en una tabla de DuckLake."""
    connection.register("frame_to_write", frame.to_arrow())
    connection.execute(
        f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM frame_to_write"
    )
    connection.unregister("frame_to_write")


def write_tables(
    connection: duckdb.DuckDBPyConnection,
    tables: dict[str, pl.DataFrame],
) -> None:
    """Publica varias tablas como una única transacción del catálogo."""
    connection.execute("BEGIN TRANSACTION")
    try:
        for table, frame in tables.items():
            write_table(connection, table, frame)
    except Exception:
        connection.execute("ROLLBACK")
        raise
    else:
        connection.execute("COMMIT")


def read_table(
    connection: duckdb.DuckDBPyConnection, table: str
) -> pl.DataFrame:
    """Lee una tabla del lakehouse como DataFrame de Polars."""
    return pl.from_arrow(connection.execute(f"SELECT * FROM {table}").arrow())


def table_status(
    connection: duckdb.DuckDBPyConnection,
) -> list[tuple[str, int]]:
    """Devuelve las tablas de las capas y su número de filas."""
    tables = connection.execute(
        """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema IN ('bronze', 'silver', 'gold')
        ORDER BY table_schema, table_name
        """
    ).fetchall()
    return [
        (
            f"{schema}.{name}",
            connection.execute(
                f"SELECT count(*) FROM {schema}.{name}"
            ).fetchone()[0],
        )
        for schema, name in tables
    ]


def snapshots(connection: duckdb.DuckDBPyConnection) -> pl.DataFrame:
    """Consulta los snapshots que DuckLake registró en el catálogo."""
    return pl.from_arrow(
        connection.execute("FROM ducklake_snapshots('olist')").arrow()
    )


def record_run_status(
    lake_dir: Path,
    status: str,
    detail: str | None = None,
) -> None:
    """Registra la última corrida y conserva la referencia al último Gold válido."""
    lake_dir.mkdir(parents=True, exist_ok=True)
    path = lake_dir / "pipeline_status.json"
    previous = json.loads(path.read_text()) if path.exists() else {}
    timestamp = datetime.now(UTC).isoformat()
    previous["last_run"] = {"status": status, "at": timestamp, "detail": detail}
    if status == "succeeded":
        previous["last_successful_gold"] = timestamp
    path.write_text(json.dumps(previous, indent=2) + "\n")


def run_status(lake_dir: Path) -> dict[str, object]:
    """Lee el estado persistido de las corridas, si existe."""
    path = lake_dir / "pipeline_status.json"
    return json.loads(path.read_text()) if path.exists() else {}
