"""Transformaciones y reglas críticas de las entidades Silver."""

from __future__ import annotations

import polars as pl

from src.pudulake.contracts import ContractViolation

# Columnas de orders.parquet que llegan como texto y deben tiparse como
# fecha/hora real antes de poder compararse u ordenarse.
COLUMNAS_FECHA = (
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
)
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"

# Únicos estados de order_status que el contrato de Silver acepta.
ESTADOS_VALIDOS = {
    "approved",
    "canceled",
    "created",
    "delivered",
    "invoiced",
    "processing",
    "shipped",
    "unavailable",
}


def build_orders(orders: pl.DataFrame) -> pl.DataFrame:
    """Tipa fechas de órdenes y comprueba su secuencia temporal."""
    # strict=False: si un valor no calza con el formato, en vez de
    # lanzar un error de Polars, devuelve null para esa celda — así
    # podemos distinguir nosotros mismos entre "nulo real" (ya venía
    # vacío) y "fecha no interpretable" (venía con texto raro).
    # cast(pl.String) primero: si una columna llega completamente vacía
    # (todos None), Polars la infiere como tipo Null, no String, y
    # .str.strptime(...) exige String — el cast la deja siempre en el
    # tipo correcto, sea cual sea su contenido real.
    resultado = orders.with_columns(
        [
            pl.col(columna)
            .cast(pl.String)
            .str.strptime(pl.Datetime, FORMATO_FECHA, strict=False)
            for columna in COLUMNAS_FECHA
        ]
    )

    # Si la columna original NO era nula pero el resultado parseado SÍ
    # lo es, significa que el texto no calzaba con el formato esperado
    # (una fecha "no interpretable"), y no una ausencia real de dato.
    for columna in COLUMNAS_FECHA:
        fallo_de_parseo = (
            orders[columna].is_not_null() & resultado[columna].is_null()
        )
        if fallo_de_parseo.any():
            raise ContractViolation(
                f"silver.orders.{columna} contiene una fecha no interpretable."
            )

    # order_status es un contrato cerrado: cualquier valor fuera de la
    # lista declarada rompe la garantía de silver.orders.
    estados_desconocidos = (
        set(resultado["order_status"].unique().to_list()) - ESTADOS_VALIDOS
    )
    if estados_desconocidos:
        raise ContractViolation(
            "silver.orders.order_status contiene estados no reconocidos: "
            f"{', '.join(sorted(estados_desconocidos))}."
        )

    # Una orden "delivered" sin fecha de entrega es una ausencia real de
    # dato (no un error de formato): se marca en una columna aparte para
    # que el resto del pipeline la pueda tratar explícitamente.
    resultado = resultado.with_columns(
        (
            (pl.col("order_status") == "delivered")
            & pl.col("order_delivered_customer_date").is_null()
        ).alias("delivery_timestamp_missing")
    )

    # Una orden entregada no puede tener fecha de entrega ANTERIOR a su
    # fecha de compra: violaría la secuencia temporal del negocio.
    entregas_antes_de_comprar = resultado.filter(
        (pl.col("order_status") == "delivered")
        & pl.col("order_delivered_customer_date").is_not_null()
        & (
            pl.col("order_delivered_customer_date")
            < pl.col("order_purchase_timestamp")
        )
    )
    if entregas_antes_de_comprar.height > 0:
        raise ContractViolation(
            "silver.orders tiene órdenes entregadas con fecha de entrega "
            "anterior a la fecha de compra."
        )

    return resultado


def build_customers(customers: pl.DataFrame) -> pl.DataFrame:
    """Conserva clientes y verifica la relación uno a uno con customer_id."""
    # customer_id debe identificar exactamente una fila: si aparece
    # repetido, la tabla no cumple su propio contrato de unicidad.
    if customers.select(pl.col("customer_id").n_unique()).item() != (
        customers.height
    ):
        raise ContractViolation(
            "silver.customers no respeta la relación uno a uno de customer_id."
        )
    return customers


def _rechazar_montos_no_finitos(
    frame: pl.DataFrame, columnas: tuple[str, ...], tabla: str
) -> None:
    """Revisa primero NaN/infinito, antes de revisar negativos."""
    for columna in columnas:
        if not frame[columna].is_finite().all():
            raise ContractViolation(
                f"{tabla}.{columna} tiene valores no finitos."
            )


def _rechazar_montos_negativos(
    frame: pl.DataFrame, columnas: tuple[str, ...], tabla: str
) -> None:
    for columna in columnas:
        if (frame[columna] < 0).any():
            raise ContractViolation(
                f"{tabla}.{columna} tiene valores negativos."
            )


def build_order_items(items: pl.DataFrame) -> pl.DataFrame:
    """Comprueba que los ítems no tengan precios ni fletes negativos."""
    # El orden importa: un NaN nunca es "< 0" (esa comparación siempre
    # da False), así que hay que descartar NaN/infinito ANTES de poder
    # confiar en el chequeo de negativos.
    _rechazar_montos_no_finitos(
        items, ("price", "freight_value"), "silver.order_items"
    )
    _rechazar_montos_negativos(
        items, ("price", "freight_value"), "silver.order_items"
    )
    return items


def build_payments(payments: pl.DataFrame) -> pl.DataFrame:
    """Comprueba que los pagos no tengan montos negativos."""
    _rechazar_montos_no_finitos(payments, ("payment_value",), "silver.payments")
    _rechazar_montos_negativos(payments, ("payment_value",), "silver.payments")
    return payments


def validate_relationships(
    orders: pl.DataFrame,
    customers: pl.DataFrame,
    items: pl.DataFrame,
    payments: pl.DataFrame,
) -> None:
    """Verifica las claves foráneas antes de construir productos Gold."""
    # anti-join: se queda solo con las filas de la izquierda que NO
    # encuentran pareja en la derecha — exactamente las filas "huérfanas".
    huerfanas_customers = orders.join(
        customers.select("customer_id"), on="customer_id", how="anti"
    )
    if huerfanas_customers.height > 0:
        raise ContractViolation(
            "silver.orders tiene una clave foránea huérfana hacia "
            f"silver.customers ({huerfanas_customers.height} filas)."
        )

    huerfanas_items = items.join(
        orders.select("order_id"), on="order_id", how="anti"
    )
    if huerfanas_items.height > 0:
        raise ContractViolation(
            "silver.order_items tiene una clave foránea huérfana hacia "
            f"silver.orders ({huerfanas_items.height} filas)."
        )

    huerfanas_payments = payments.join(
        orders.select("order_id"), on="order_id", how="anti"
    )
    if huerfanas_payments.height > 0:
        raise ContractViolation(
            "silver.payments tiene una clave foránea huérfana hacia "
            f"silver.orders ({huerfanas_payments.height} filas)."
        )
