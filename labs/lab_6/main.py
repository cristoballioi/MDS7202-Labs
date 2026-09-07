"""CLI provista para ejecutar y observar el lakehouse local."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

os.environ.setdefault("PREFECT_API_URL", "http://127.0.0.1:4200/api")

from src.pudulake.contracts import ContractViolation
from src.pudulake.flows import run_pipeline
from src.pudulake.storage import connect_lake, run_status, table_status
from src.pudulake.storage import snapshots as lake_snapshots

PREFECT_API_URL = os.environ["PREFECT_API_URL"]

app = typer.Typer(no_args_is_help=True, help="Pipeline local de Pudubella.")
console = Console()
error_console = Console(stderr=True)
ROOT = Path(__file__).parent


@app.command()
def run(
    raw_dir: Annotated[Path, typer.Option(exists=True)] = ROOT / "data/raw",
) -> None:
    """Reconstruye Bronze, Silver y Gold desde las fuentes Parquet."""
    console.print(f"Endpoint de Prefect: {PREFECT_API_URL}")
    with console.status("[bold green]Materializando el lakehouse..."):
        try:
            result = run_pipeline(
                raw_dir=raw_dir,
                lake_dir=ROOT / "data/lake",
                contracts_dir=ROOT / "contracts",
                segments_path=ROOT / "config/rfm_segments.yaml",
            )
        except ContractViolation as error:
            error_console.print(f"[bold red]Contrato incumplido:[/] {error}")
            raise typer.Exit(code=2) from error
        except RuntimeError as error:
            error_console.print(f"[bold red]Ambiente local:[/] {error}")
            raise typer.Exit(code=3) from error
    console.print(
        "[bold green]Flow terminado.[/] "
        f"Ventas diarias: {result['sales_daily']}; RFM: {result['customer_rfm']}; "
        f"exclusiones RFM: {result['rfm_exclusions']}."
    )


@app.command()
def status() -> None:
    """Muestra tablas materializadas y sus filas."""
    try:
        connection = connect_lake(ROOT / "data/lake")
        try:
            rows = table_status(connection)
        finally:
            connection.close()
    except RuntimeError as error:
        error_console.print(f"[bold red]Ambiente local:[/] {error}")
        raise typer.Exit(code=3) from error
    table = Table(title="Estado del lakehouse")
    table.add_column("Tabla")
    table.add_column("Filas", justify="right")
    for name, count in rows:
        table.add_row(name, str(count))
    console.print(table)
    status = run_status(ROOT / "data/lake")
    if status:
        console.print(status)


@app.command()
def snapshots() -> None:
    """Muestra los snapshots almacenados por DuckLake."""
    try:
        connection = connect_lake(ROOT / "data/lake")
        try:
            result = lake_snapshots(connection)
        finally:
            connection.close()
    except RuntimeError as error:
        error_console.print(f"[bold red]Ambiente local:[/] {error}")
        raise typer.Exit(code=3) from error
    console.print(result)


if __name__ == "__main__":
    app()
