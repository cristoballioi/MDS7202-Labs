"""Productos analíticos Gold de Pudubella."""

from __future__ import annotations

from typing import Any

import polars as pl


def build_rfm_exclusions(
    orders: pl.DataFrame, payments: pl.DataFrame
) -> pl.DataFrame:
    """Registra órdenes entregadas sin pago para excluirlas de RFM."""
    raise NotImplementedError(
        "Completen build_rfm_exclusions antes de ejecutar el programa."
    )


def build_sales_daily(
    orders: pl.DataFrame, items: pl.DataFrame
) -> pl.DataFrame:
    """Construye ventas de ítems por fecha de compra y órdenes entregadas."""
    raise NotImplementedError(
        "Completen build_sales_daily antes de ejecutar el programa."
    )


def build_customer_rfm(
    orders: pl.DataFrame,
    customers: pl.DataFrame,
    payments: pl.DataFrame,
    segments: dict[str, Any],
) -> pl.DataFrame:
    """Calcula RFM de compras entregadas y aplica reglas congeladas."""
    raise NotImplementedError(
        "Completen build_customer_rfm antes de ejecutar el programa."
    )
