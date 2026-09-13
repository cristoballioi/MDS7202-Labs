"""Productos analíticos Gold de Pudubella."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import polars as pl

# Prioridad de segmentación RFM: se evalúa de arriba hacia abajo y se
# asigna el PRIMER segmento cuyas reglas se cumplan todas.
PRIORIDAD_SEGMENTOS = ("champions", "loyal", "new", "lost")


def build_rfm_exclusions(
    orders: pl.DataFrame, payments: pl.DataFrame
) -> pl.DataFrame:
    """Registra órdenes entregadas sin pago para excluirlas de RFM."""
    entregadas = orders.filter(pl.col("order_status") == "delivered")
    # Los order_id que sí tienen al menos un pago registrado.
    ordenes_con_pago = payments.select("order_id").unique()
    # anti-join: entregadas que NO aparecen en ordenes_con_pago.
    sin_pago = entregadas.join(ordenes_con_pago, on="order_id", how="anti")
    return sin_pago.select(
        "order_id", "customer_id", "order_purchase_timestamp"
    ).with_columns(pl.lit("delivered_order_without_payment").alias("reason"))


def build_sales_daily(
    orders: pl.DataFrame, items: pl.DataFrame
) -> pl.DataFrame:
    """Construye ventas de ítems por fecha de compra y órdenes entregadas."""
    entregadas = orders.filter(pl.col("order_status") == "delivered")
    # inner join: cada ítem se junta con SU orden entregada; los ítems
    # de órdenes no entregadas quedan fuera automáticamente.
    unido = entregadas.join(items, on="order_id", how="inner")
    return (
        unido.with_columns(
            pl.col("order_purchase_timestamp").dt.date().alias("sale_date")
        )
        .group_by("sale_date")
        .agg(
            pl.col("price").sum().alias("items_sold_value"),
            # order_id distintos: si una orden tiene varios ítems, cuenta
            # como UNA sola orden entregada, no una por ítem.
            pl.col("order_id").n_unique().alias("delivered_orders"),
        )
        .sort("sale_date")
    )


def _regla_se_cumple(reglas: dict[str, Any]) -> pl.Expr:
    """Combina con AND todas las condiciones declaradas para un segmento."""
    condicion = pl.lit(value=True)
    if "max_recency_days" in reglas:
        condicion = condicion & (
            pl.col("recency_days") <= reglas["max_recency_days"]
        )
    if "min_recency_days" in reglas:
        condicion = condicion & (
            pl.col("recency_days") >= reglas["min_recency_days"]
        )
    if "min_frequency" in reglas:
        condicion = condicion & (pl.col("frequency") >= reglas["min_frequency"])
    if "min_monetary" in reglas:
        condicion = condicion & (pl.col("monetary") >= reglas["min_monetary"])
    return condicion


def _segmento_expr(segmentos: dict[str, dict[str, Any]]) -> pl.Expr:
    """Arma un when/otherwise anidado que respeta PRIORIDAD_SEGMENTOS.

    Se construye de atrás hacia adelante (empezando por el segmento de
    menor prioridad) para que el segmento de mayor prioridad quede como
    el `.when(...)` más externo, y por lo tanto sea el primero en
    evaluarse.
    """
    expresion = pl.lit("Other")
    for nombre in reversed(PRIORIDAD_SEGMENTOS):
        reglas = segmentos.get(nombre)
        if not reglas:
            continue
        expresion = (
            pl.when(_regla_se_cumple(reglas))
            .then(pl.lit(nombre.capitalize()))
            .otherwise(expresion)
        )
    return expresion


def build_customer_rfm(
    orders: pl.DataFrame,
    customers: pl.DataFrame,
    payments: pl.DataFrame,
    segments: dict[str, Any],
) -> pl.DataFrame:
    """Calcula RFM de compras entregadas y aplica reglas congeladas."""
    # Monto total pagado por orden (una orden puede tener varias filas
    # de pago, ej. cuotas): se suma antes de unir con las órdenes.
    pagos_por_orden = payments.group_by("order_id").agg(
        pl.col("payment_value").sum().alias("order_payment_total")
    )
    # Una orden es "elegible" para RFM si está entregada Y tiene pago:
    # el join inner con pagos_por_orden descarta automáticamente las
    # entregadas sin pago (esas van a build_rfm_exclusions, no aquí).
    elegibles = (
        orders.filter(pl.col("order_status") == "delivered")
        .join(pagos_por_orden, on="order_id", how="inner")
        .join(
            customers.select("customer_id", "customer_unique_id"),
            on="customer_id",
            how="inner",
        )
    )

    # La fecha de referencia es GLOBAL (un solo día para todo el
    # dataset): el día siguiente a la última compra elegible de
    # cualquier cliente, no una fecha distinta por cliente.
    ultima_compra_global = elegibles.select(
        pl.col("order_purchase_timestamp").max()
    ).item()
    fecha_referencia = ultima_compra_global + timedelta(days=1)

    resultado = (
        elegibles.group_by("customer_unique_id")
        .agg(
            pl.col("order_purchase_timestamp").max().alias("last_purchase"),
            # order_id único: si customer_unique_id agrupa a más de un
            # customer_id (mismo cliente con más de un perfil), cada
            # orden sigue contando una sola vez.
            pl.col("order_id").n_unique().alias("frequency"),
            pl.col("order_payment_total").sum().alias("monetary"),
        )
        .with_columns(
            (pl.lit(fecha_referencia) - pl.col("last_purchase"))
            .dt.total_days()
            .alias("recency_days")
        )
    )
    return resultado.with_columns(
        _segmento_expr(segments["segments"]).alias("segment")
    ).sort("customer_unique_id")
