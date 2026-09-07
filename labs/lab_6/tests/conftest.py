from pathlib import Path

import polars as pl
import pytest


@pytest.fixture
def raw_dir(tmp_path: Path) -> Path:
    orders = pl.DataFrame(
        {
            "order_id": ["o1", "o2", "o3", "o4", "o5"],
            "customer_id": ["c1", "c2", "c3", "c2", "c3"],
            "order_status": [
                "delivered",
                "delivered",
                "delivered",
                "canceled",
                "delivered",
            ],
            "order_purchase_timestamp": [
                "2018-01-01 10:00:00",
                "2018-02-01 10:00:00",
                "2018-02-02 10:00:00",
                "2018-03-01 10:00:00",
                "2018-02-03 10:00:00",
            ],
            "order_approved_at": [None, None, None, None, None],
            "order_delivered_carrier_date": [None, None, None, None, None],
            "order_delivered_customer_date": [
                "2018-01-04 10:00:00",
                "2018-02-04 10:00:00",
                "2018-02-05 10:00:00",
                None,
                None,
            ],
            "order_estimated_delivery_date": [None, None, None, None, None],
        }
    )
    customers = pl.DataFrame(
        {
            "customer_id": ["c1", "c2", "c3"],
            "customer_unique_id": ["u1", "u2", "u1"],
        }
    )
    items = pl.DataFrame(
        {
            "order_id": ["o1", "o1", "o2", "o3", "o4", "o5"],
            "order_item_id": [1, 2, 1, 1, 1, 1],
            "price": [10.0, 20.0, 30.0, 40.0, 80.0, 50.0],
            "freight_value": [1.0, 2.0, 3.0, 4.0, 8.0, 5.0],
        }
    )
    payments = pl.DataFrame(
        {
            "order_id": ["o1", "o1", "o2", "o4", "o5"],
            "payment_sequential": [1, 2, 1, 1, 1],
            "payment_value": [10.0, 20.0, 30.0, 80.0, 50.0],
        }
    )
    for name, frame in {
        "orders": orders,
        "customers": customers,
        "order_items": items,
        "payments": payments,
    }.items():
        frame.write_parquet(tmp_path / f"{name}.parquet")
    return tmp_path


@pytest.fixture
def segments() -> dict:
    return {
        "segments": {
            "champions": {
                "max_recency_days": 40,
                "min_frequency": 2,
                "min_monetary": 50.0,
            },
            "loyal": {"min_frequency": 2},
            "new": {"max_recency_days": 40},
            "lost": {"min_recency_days": 90},
        }
    }
