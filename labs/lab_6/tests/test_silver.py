from pathlib import Path

import polars as pl
import pytest

from src.pudulake.contracts import (
    ContractViolation,
    load_contract,
    validate_contract,
)
from src.pudulake.silver import (
    build_order_items,
    build_orders,
    build_payments,
    validate_relationships,
)

pytestmark = pytest.mark.etapa2


def test_orders_tipa_las_fechas(raw_dir):
    orders = pl.read_parquet(raw_dir / "orders.parquet")
    result = build_orders(orders)

    assert result.schema["order_purchase_timestamp"] == pl.Datetime


def test_rechaza_un_pago_negativo(raw_dir):
    payments = pl.read_parquet(raw_dir / "payments.parquet").with_columns(
        pl.lit(-1.0).alias("payment_value")
    )

    with pytest.raises(ContractViolation, match="negativos"):
        build_payments(payments)


def test_rechaza_un_pago_no_finito(raw_dir):
    payments = pl.read_parquet(raw_dir / "payments.parquet").with_columns(
        pl.lit(float("nan")).alias("payment_value")
    )

    with pytest.raises(ContractViolation, match="no finitos"):
        build_payments(payments)


def test_rechaza_item_con_precio_negativo(raw_dir):
    items = pl.read_parquet(raw_dir / "order_items.parquet").with_columns(
        pl.lit(-1.0).alias("price")
    )

    with pytest.raises(ContractViolation, match="negativos"):
        build_order_items(items)


def test_rechaza_una_clave_foranea_huerfana(raw_dir):
    orders = build_orders(pl.read_parquet(raw_dir / "orders.parquet"))
    customers = pl.read_parquet(raw_dir / "customers.parquet")
    items = pl.read_parquet(raw_dir / "order_items.parquet")
    payments = pl.read_parquet(raw_dir / "payments.parquet").with_columns(
        pl.lit("otra_orden").alias("order_id")
    )

    with pytest.raises(ContractViolation, match="huérfana"):
        validate_relationships(orders, customers, items, payments)


def test_distingue_fecha_invalida_de_ausencia_real(raw_dir):
    orders = pl.read_parquet(raw_dir / "orders.parquet")
    invalid = orders.with_columns(
        pl.when(pl.col("order_id") == "o1")
        .then(pl.lit("fecha_invalida"))
        .otherwise(pl.col("order_delivered_customer_date"))
        .alias("order_delivered_customer_date")
    )

    with pytest.raises(ContractViolation, match="no interpretable"):
        build_orders(invalid)

    result = build_orders(orders)
    assert result.filter(pl.col("order_id") == "o5")[
        "delivery_timestamp_missing"
    ].item()


def test_los_contratos_silver_declaran_su_gobernanza():
    contracts_dir = Path(__file__).parents[1] / "contracts"

    for path in contracts_dir.glob("silver_*.yaml"):
        contract = load_contract(path)
        assert contract["purpose"], path.name
        assert contract["grain"], path.name
        assert contract["primary_key"], path.name
        assert contract["owner"], path.name
        assert contract["lineage"], path.name
        assert contract["classification"], path.name
        assert contract["required_columns"], path.name
        assert contract["constraints"], path.name


def test_rechaza_contrato_vacio_o_regla_desconocida(raw_dir, tmp_path):
    empty = tmp_path / "empty.yaml"
    empty.write_text("table: silver.payments\n")
    with pytest.raises(ContractViolation, match="no declara"):
        load_contract(empty)

    malformed = tmp_path / "malformed.yaml"
    malformed.write_text(
        (Path(__file__).parents[1] / "contracts/silver_payments.yaml")
        .read_text()
        .replace("minimum:", "minimun:")
    )
    with pytest.raises(ContractViolation, match="desconocidas"):
        load_contract(malformed)

    contract = load_contract(
        Path(__file__).parents[1] / "contracts/silver_payments.yaml"
    )
    with pytest.raises(ContractViolation, match="tablas vacías"):
        validate_contract(
            pl.DataFrame(
                schema={
                    "order_id": pl.String,
                    "payment_sequential": pl.Int64,
                    "payment_value": pl.Float64,
                }
            ),
            contract,
        )
