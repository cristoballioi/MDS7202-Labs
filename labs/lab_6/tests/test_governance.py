import shutil
from pathlib import Path

import polars as pl
import pytest

from src.pudulake.contracts import ContractViolation
from src.pudulake.flows import ASSETS, run_pipeline
from src.pudulake.storage import (
    connect_lake,
    read_table,
    run_status,
    table_status,
)

pytestmark = pytest.mark.etapa4


def test_assets_declaran_las_capas_del_lakehouse():
    assert set(ASSETS) == {
        "bronze.orders",
        "bronze.customers",
        "bronze.order_items",
        "bronze.payments",
        "silver.orders",
        "silver.customers",
        "silver.order_items",
        "silver.payments",
        "gold.sales_daily",
        "gold.customer_rfm",
        "gold.rfm_exclusions",
    }
    assert all(
        asset.key.startswith("ducklake://mercado-pudu/")
        for asset in ASSETS.values()
    )


def test_flow_publica_silver_despues_de_validar_y_conserva_gold_valido(
    raw_dir, tmp_path
):
    root = Path(__file__).parents[1]

    result = run_pipeline(
        raw_dir=raw_dir,
        lake_dir=tmp_path / "lake",
        contracts_dir=root / "contracts",
        segments_path=root / "config/rfm_segments.yaml",
    )

    assert result == {
        "sales_daily": 4,
        "customer_rfm": 2,
        "rfm_exclusions": 1,
    }
    lake_dir = tmp_path / "lake"
    connection = connect_lake(lake_dir)
    try:
        assert {name for name, _ in table_status(connection)} == {
            "bronze.orders",
            "bronze.customers",
            "bronze.order_items",
            "bronze.payments",
            "silver.orders",
            "silver.customers",
            "silver.order_items",
            "silver.payments",
            "gold.sales_daily",
            "gold.customer_rfm",
            "gold.rfm_exclusions",
        }
        payments_before = read_table(connection, "silver.payments")
        rfm_before = read_table(connection, "gold.customer_rfm")
    finally:
        connection.close()

    invalid_dir = tmp_path / "raw_invalid"
    shutil.copytree(raw_dir, invalid_dir)
    payments = pl.read_parquet(invalid_dir / "payments.parquet").with_columns(
        pl.when(pl.col("order_id") == "o5")
        .then(pl.lit("orphan"))
        .otherwise(pl.col("order_id"))
        .alias("order_id")
    )
    payments.write_parquet(invalid_dir / "payments.parquet")

    with pytest.raises(ContractViolation, match="huérfana"):
        run_pipeline(
            raw_dir=invalid_dir,
            lake_dir=lake_dir,
            contracts_dir=root / "contracts",
            segments_path=root / "config/rfm_segments.yaml",
        )

    connection = connect_lake(lake_dir)
    try:
        assert read_table(connection, "silver.payments").equals(payments_before)
        assert read_table(connection, "gold.customer_rfm").equals(rfm_before)
    finally:
        connection.close()
    status = run_status(lake_dir)
    assert status["last_run"]["status"] == "failed"
    assert status["last_successful_gold"]
