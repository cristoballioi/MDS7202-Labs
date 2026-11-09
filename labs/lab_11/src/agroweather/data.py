"""Carga y limpieza de las observaciones horarias de la estación de Curicó."""

from __future__ import annotations

from pathlib import Path

import polars as pl


def load_station(ruta: str | Path) -> pl.DataFrame:
    """Lee el Parquet de la estación y lo lleva a una grilla horaria completa.

    El archivo trae la hora en la columna `time`; la tabla resultante la
    renombra `hora`, la deja primera, ordenada, sin repetidos y con la zona
    horaria de Curicó. La grilla va desde la primera hasta la última
    observación, sin saltos: una hora que el archivo no trae queda como fila
    con valores faltantes (`null`). Las mediciones son `temp` (°C), `rhum` (%),
    `pres` (hPa), `wspd` (km/h), `wdir` (grados), `cldc` (oktas) y `coco`
    (código de fenómeno). Se conservan las columnas `<variable>_source`, que
    indican si el dato provino de `isd_lite` o de `metar`.

    Levanta `ValueError` si falta una columna, si `time` no es una fecha con
    zona horaria o si hay horas duplicadas.
    """
    datos = pl.read_parquet(ruta)

    mediciones = ["temp", "rhum", "pres", "wspd", "wdir", "cldc", "coco"]
    fuentes = [f"{medicion}_source" for medicion in mediciones]
    requeridas = ["time", *mediciones, *fuentes]
    faltantes = [columna for columna in requeridas if columna not in datos]
    if faltantes:
        raise ValueError(f"Faltan columnas en el Parquet: {faltantes}")
    tipo = datos.schema["time"]
    if not isinstance(tipo, pl.Datetime):
        raise ValueError("La columna time debe ser de fechas")
    if datos["time"].is_duplicated().any():
        raise ValueError("Hay horas duplicadas en el Parquet")
    if tipo.time_zone is None:
        raise ValueError("La columna time debe declarar su zona horaria")

    datos = datos.select(requeridas).rename({"time": "hora"}).sort("hora")
    grilla = pl.datetime_range(
        datos["hora"].min(),
        datos["hora"].max(),
        interval="1h",
        time_zone=tipo.time_zone,
        eager=True,
    ).alias("hora")
    return grilla.to_frame().join(datos, on="hora", how="left")


def clean_station(estacion: pl.DataFrame) -> pl.DataFrame:
    """Descarta los valores que el registro no pudo haber medido.

    El 13 de marzo de 2018 a las 09:00 el anemómetro marca 176 km/h, más del
    doble del siguiente valor más alto de la serie (74,2 km/h): es un error
    del sensor y se reemplaza por `null`, no por cero. El código `coco` 0 no pertenece a la
    tabla de Meteostat y también se invalida. El resto de la tabla no cambia.
    """
    if "wspd" not in estacion.columns or "coco" not in estacion.columns:
        raise ValueError("La estación debe incluir wspd y coco")

    return estacion.with_columns(
        pl.when(pl.col("wspd") > 100.0)
        .then(None)
        .otherwise(pl.col("wspd"))
        .alias("wspd"),
        pl.when(pl.col("coco") == 0)
        .then(None)
        .otherwise(pl.col("coco"))
        .alias("coco"),
    )
