"""Flow Prefect que conecta Bronze, Silver y Gold."""

from __future__ import annotations

from pathlib import Path

import polars as pl
import yaml
from prefect import flow, task
from prefect.assets import Asset, materialize

from src.pudulake.bronze import read_sources
from src.pudulake.contracts import (
    ContractViolation,
    load_contract,
    validate_contract,
)
from src.pudulake.gold import (
    build_customer_rfm,
    build_rfm_exclusions,
    build_sales_daily,
)
from src.pudulake.silver import (
    build_customers,
    build_order_items,
    build_orders,
    build_payments,
    validate_relationships,
)
from src.pudulake.storage import (
    connect_lake,
    record_run_status,
    write_table,
    write_tables,
)

ASSETS = (
    {
        f"bronze.{name}": Asset(key=f"ducklake://mercado-pudu/bronze/{name}")
        for name in ("orders", "customers", "order_items", "payments")
    }
    | {
        f"silver.{name}": Asset(key=f"ducklake://mercado-pudu/silver/{name}")
        for name in ("orders", "customers", "order_items", "payments")
    }
    | {
        "gold.sales_daily": Asset(
            key="ducklake://mercado-pudu/gold/sales_daily"
        ),
        "gold.customer_rfm": Asset(
            key="ducklake://mercado-pudu/gold/customer_rfm"
        ),
        "gold.rfm_exclusions": Asset(
            key="ducklake://mercado-pudu/gold/rfm_exclusions"
        ),
    }
)


def _contract(contracts_dir: Path, table: str) -> dict:
    return load_contract(contracts_dir / f"{table.replace('.', '_')}.yaml")


def _persist(lake_dir: Path, table: str, frame: pl.DataFrame) -> None:
    connection = connect_lake(lake_dir)
    try:
        write_table(connection, table, frame)
    finally:
        connection.close()


@task
def _load(raw_dir: Path) -> dict[str, pl.DataFrame]:
    return read_sources(raw_dir)


@materialize(ASSETS["bronze.orders"])
def _bronze_orders(lake_dir: Path, frame: pl.DataFrame) -> pl.DataFrame:
    _persist(lake_dir, "bronze.orders", frame)
    return frame


@materialize(ASSETS["bronze.customers"])
def _bronze_customers(lake_dir: Path, frame: pl.DataFrame) -> pl.DataFrame:
    _persist(lake_dir, "bronze.customers", frame)
    return frame


@materialize(ASSETS["bronze.order_items"])
def _bronze_items(lake_dir: Path, frame: pl.DataFrame) -> pl.DataFrame:
    _persist(lake_dir, "bronze.order_items", frame)
    return frame


@materialize(ASSETS["bronze.payments"])
def _bronze_payments(lake_dir: Path, frame: pl.DataFrame) -> pl.DataFrame:
    _persist(lake_dir, "bronze.payments", frame)
    return frame


@task
def _silver_orders(
    lake_dir: Path, frame: pl.DataFrame, contract: dict
) -> pl.DataFrame:
    result = build_orders(frame)
    validate_contract(result, contract)
    return result


@task
def _silver_customers(
    lake_dir: Path, frame: pl.DataFrame, contract: dict
) -> pl.DataFrame:
    result = build_customers(frame)
    validate_contract(result, contract)
    return result


@task
def _silver_items(
    lake_dir: Path, frame: pl.DataFrame, contract: dict
) -> pl.DataFrame:
    result = build_order_items(frame)
    validate_contract(result, contract)
    return result


@task
def _silver_payments(
    lake_dir: Path, frame: pl.DataFrame, contract: dict
) -> pl.DataFrame:
    result = build_payments(frame)
    validate_contract(result, contract)
    return result


@task
def _publish_silver(
    lake_dir: Path,
    orders: pl.DataFrame,
    customers: pl.DataFrame,
    items: pl.DataFrame,
    payments: pl.DataFrame,
) -> None:
    """Publica Silver solo después de validar sus relaciones."""
    connection = connect_lake(lake_dir)
    try:
        write_tables(
            connection,
            {
                "silver.orders": orders,
                "silver.customers": customers,
                "silver.order_items": items,
                "silver.payments": payments,
            },
        )
    finally:
        connection.close()


@materialize(ASSETS["silver.orders"], asset_deps=[ASSETS["bronze.orders"]])
def _materialize_silver_orders(frame: pl.DataFrame) -> pl.DataFrame:
    """Registra la materialización ya publicada de silver.orders."""
    return frame


@materialize(
    ASSETS["silver.customers"], asset_deps=[ASSETS["bronze.customers"]]
)
def _materialize_silver_customers(frame: pl.DataFrame) -> pl.DataFrame:
    """Registra la materialización ya publicada de silver.customers."""
    return frame


@materialize(
    ASSETS["silver.order_items"], asset_deps=[ASSETS["bronze.order_items"]]
)
def _materialize_silver_items(frame: pl.DataFrame) -> pl.DataFrame:
    """Registra la materialización ya publicada de silver.order_items."""
    return frame


@materialize(ASSETS["silver.payments"], asset_deps=[ASSETS["bronze.payments"]])
def _materialize_silver_payments(frame: pl.DataFrame) -> pl.DataFrame:
    """Registra la materialización ya publicada de silver.payments."""
    return frame


@materialize(
    ASSETS["gold.sales_daily"],
    asset_deps=[ASSETS["silver.orders"], ASSETS["silver.order_items"]],
)
def _gold_sales(
    lake_dir: Path,
    orders: pl.DataFrame,
    items: pl.DataFrame,
    contract: dict,
) -> pl.DataFrame:
    result = build_sales_daily(orders, items)
    validate_contract(result, contract)
    _persist(lake_dir, "gold.sales_daily", result)
    return result


@materialize(
    ASSETS["gold.customer_rfm"],
    asset_deps=[
        ASSETS["silver.orders"],
        ASSETS["silver.customers"],
        ASSETS["silver.payments"],
    ],
)
def _gold_rfm(
    lake_dir: Path,
    orders: pl.DataFrame,
    customers: pl.DataFrame,
    payments: pl.DataFrame,
    contract: dict,
    segments: dict,
) -> pl.DataFrame:
    result = build_customer_rfm(orders, customers, payments, segments)
    validate_contract(result, contract)
    _persist(lake_dir, "gold.customer_rfm", result)
    return result


@materialize(
    ASSETS["gold.rfm_exclusions"],
    asset_deps=[ASSETS["silver.orders"], ASSETS["silver.payments"]],
)
def _gold_rfm_exclusions(
    lake_dir: Path,
    orders: pl.DataFrame,
    payments: pl.DataFrame,
    contract: dict,
) -> pl.DataFrame:
    result = build_rfm_exclusions(orders, payments)
    validate_contract(result, contract)
    _persist(lake_dir, "gold.rfm_exclusions", result)
    return result


@flow(name="mercado-del-pudu")
def run_pipeline(
    raw_dir: Path,
    lake_dir: Path,
    contracts_dir: Path,
    segments_path: Path,
) -> dict[str, int]:
    """Reconstruye el lakehouse completo desde las fuentes entregadas."""
    try:
        sources = _load(raw_dir)
        bronze_orders = _bronze_orders(lake_dir, sources["orders"])
        bronze_customers = _bronze_customers(lake_dir, sources["customers"])
        bronze_items = _bronze_items(lake_dir, sources["order_items"])
        bronze_payments = _bronze_payments(lake_dir, sources["payments"])
        orders = _silver_orders(
            lake_dir, bronze_orders, _contract(contracts_dir, "silver.orders")
        )
        customers = _silver_customers(
            lake_dir,
            bronze_customers,
            _contract(contracts_dir, "silver.customers"),
        )
        items = _silver_items(
            lake_dir,
            bronze_items,
            _contract(contracts_dir, "silver.order_items"),
        )
        payments = _silver_payments(
            lake_dir,
            bronze_payments,
            _contract(contracts_dir, "silver.payments"),
        )
        validate_relationships(orders, customers, items, payments)
        _publish_silver(lake_dir, orders, customers, items, payments)
        _materialize_silver_orders(orders)
        _materialize_silver_customers(customers)
        _materialize_silver_items(items)
        _materialize_silver_payments(payments)
        sales = _gold_sales(
            lake_dir,
            orders,
            items,
            _contract(contracts_dir, "gold.sales_daily"),
        )
        exclusions = _gold_rfm_exclusions(
            lake_dir,
            orders,
            payments,
            _contract(contracts_dir, "gold.rfm_exclusions"),
        )
        rfm = _gold_rfm(
            lake_dir,
            orders,
            customers,
            payments,
            _contract(contracts_dir, "gold.customer_rfm"),
            yaml.safe_load(segments_path.read_text()),
        )
    except ContractViolation as error:
        record_run_status(lake_dir, "failed", str(error))
        raise
    record_run_status(lake_dir, "succeeded")
    return {
        "sales_daily": sales.height,
        "customer_rfm": rfm.height,
        "rfm_exclusions": exclusions.height,
    }
