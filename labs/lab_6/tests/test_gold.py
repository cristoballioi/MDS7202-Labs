from datetime import datetime
from pathlib import Path

import polars as pl
import pytest

from src.pudulake.contracts import load_contract
from src.pudulake.gold import (
    build_customer_rfm,
    build_rfm_exclusions,
    build_sales_daily,
)
from src.pudulake.silver import build_orders

pytestmark = pytest.mark.etapa3


def test_los_contratos_gold_declaran_su_gobernanza():
    contracts_dir = Path(__file__).parents[1] / "contracts"

    for path in contracts_dir.glob("gold_*.yaml"):
        contract = load_contract(path)
        assert contract["purpose"], path.name
        assert contract["grain"], path.name
        assert contract["primary_key"], path.name
        assert contract["owner"], path.name
        assert contract["lineage"], path.name
        assert contract["classification"], path.name
        assert contract["required_columns"], path.name
        assert contract["constraints"], path.name


def test_ventas_diarias_usa_solo_ordenes_entregadas(raw_dir):
    orders = build_orders(pl.read_parquet(raw_dir / "orders.parquet"))
    items = pl.read_parquet(raw_dir / "order_items.parquet")

    result = build_sales_daily(orders, items)

    assert result.height == 4
    assert result["items_sold_value"].sum() == 150.0
    assert result["delivered_orders"].sum() == 4


def test_rfm_agrupa_por_cliente_real(raw_dir, segments):
    orders = build_orders(pl.read_parquet(raw_dir / "orders.parquet"))
    customers = pl.read_parquet(raw_dir / "customers.parquet")
    payments = pl.read_parquet(raw_dir / "payments.parquet")

    result = build_customer_rfm(orders, customers, payments, segments)

    assert result.height == 2
    customer = result.filter(pl.col("customer_unique_id") == "u1")
    assert customer["frequency"].item() == 2
    assert customer["monetary"].item() == 80.0
    assert customer["recency_days"].item() == 1
    assert customer["segment"].item() == "Champions"


def test_rfm_registra_y_excluye_orden_entregada_sin_pago(raw_dir):
    orders = build_orders(pl.read_parquet(raw_dir / "orders.parquet"))
    payments = pl.read_parquet(raw_dir / "payments.parquet")

    exclusions = build_rfm_exclusions(orders, payments)

    assert exclusions.to_dicts() == [
        {
            "order_id": "o3",
            "customer_id": "c3",
            "order_purchase_timestamp": datetime(2018, 2, 2, 10, 0),
            "reason": "delivered_order_without_payment",
        }
    ]


def test_rfm_cuenta_dias_calendario(raw_dir, segments):
    orders = build_orders(pl.read_parquet(raw_dir / "orders.parquet"))
    customers = pl.read_parquet(raw_dir / "customers.parquet")
    payments = pl.read_parquet(raw_dir / "payments.parquet")

    result = build_customer_rfm(orders, customers, payments, segments)

    assert (
        result.filter(pl.col("customer_unique_id") == "u2")[
            "recency_days"
        ].item()
        == 3
    )
