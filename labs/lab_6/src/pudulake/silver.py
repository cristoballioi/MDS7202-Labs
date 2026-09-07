"""Transformaciones y reglas críticas de las entidades Silver."""

from __future__ import annotations

import polars as pl


def build_orders(orders: pl.DataFrame) -> pl.DataFrame:
    """Tipa fechas de órdenes y comprueba su secuencia temporal."""
    raise NotImplementedError(
        "Completen build_orders antes de ejecutar el programa."
    )


def build_customers(customers: pl.DataFrame) -> pl.DataFrame:
    """Conserva clientes y verifica la relación uno a uno con customer_id."""
    raise NotImplementedError(
        "Completen build_customers antes de ejecutar el programa."
    )


def build_order_items(items: pl.DataFrame) -> pl.DataFrame:
    """Comprueba que los ítems no tengan precios ni fletes negativos."""
    raise NotImplementedError(
        "Completen build_order_items antes de ejecutar el programa."
    )


def build_payments(payments: pl.DataFrame) -> pl.DataFrame:
    """Comprueba que los pagos no tengan montos negativos."""
    raise NotImplementedError(
        "Completen build_payments antes de ejecutar el programa."
    )


def validate_relationships(
    orders: pl.DataFrame,
    customers: pl.DataFrame,
    items: pl.DataFrame,
    payments: pl.DataFrame,
) -> None:
    """Verifica las claves foráneas antes de construir productos Gold."""
    raise NotImplementedError(
        "Completen validate_relationships antes de ejecutar el programa."
    )
