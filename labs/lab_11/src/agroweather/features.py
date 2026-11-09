"""Variables de pronóstico para la temperatura y la noche en Curicó."""

from __future__ import annotations

import math

import polars as pl


def add_dew_point(datos: pl.DataFrame) -> pl.DataFrame:
    """Agrega el punto de rocío y su depresión con la fórmula de Magnus.

    Se usan `a = 17,62` y `b = 243,12` °C sobre la temperatura `T` en °C y
    la humedad relativa `RH` en porcentaje. Con
    `gamma = ln(RH/100) + a*T/(b+T)`, el punto de rocío es
    `T_d = b*gamma/(a-gamma)`. Para 20 °C y 50 % de humedad, `T_d` es
    9,26 °C. La depresión es `temp - punto_rocio`: una diferencia pequeña
    indica aire próximo a saturarse. La condensación puede moderar el
    enfriamiento, pero el punto de rocío del origen no fija la mínima nocturna.
    """
    if not {"temp", "rhum"} <= set(datos.columns):
        raise ValueError("datos debe incluir temp y rhum")

    a, b = 17.62, 243.12
    humedad = pl.when(pl.col("rhum") > 0).then(pl.col("rhum"))
    gamma = (humedad / 100).log() + a * pl.col("temp") / (b + pl.col("temp"))
    return datos.with_columns(
        (b * gamma / (a - gamma)).alias("punto_rocio")
    ).with_columns(
        (pl.col("temp") - pl.col("punto_rocio")).alias("depresion_rocio")
    )


def add_wind_components(datos: pl.DataFrame) -> pl.DataFrame:
    """Convierte velocidad y dirección en componentes `viento_u` y `viento_v`.

    La dirección meteorológica indica de dónde viene el viento. Con `theta` en
    grados desde el norte y `wspd` en km/h, `u = -wspd * sin(theta)` y
    `v = -wspd * cos(theta)`. Trabajar con componentes evita el salto
    artificial entre 359° y 1°, que están a 2° de distancia y no a 358°.
    """
    if not {"wspd", "wdir"} <= set(datos.columns):
        raise ValueError("datos debe incluir wspd y wdir")

    theta = pl.col("wdir").radians()
    return datos.with_columns(
        (-pl.col("wspd") * theta.sin()).alias("viento_u"),
        (-pl.col("wspd") * theta.cos()).alias("viento_v"),
    )


def add_wet_bulb(datos: pl.DataFrame) -> pl.DataFrame:
    """Agrega la temperatura de bulbo húmedo con la aproximación de Stull.

    La fórmula es válida para humedad relativa entre 5 % y 99 %. Para 20 °C y
    50 %, entrega 13,7 °C. Aproxima la temperatura de un termómetro con el
    bulbo humedecido y ventilado, enfriado por evaporación; combina
    información de temperatura y humedad.
    """
    if not {"temp", "rhum"} <= set(datos.columns):
        raise ValueError("datos debe incluir temp y rhum")

    temp = pl.col("temp")
    humedad = pl.col("rhum")
    return datos.with_columns(
        (
            temp * (0.151977 * (humedad + 8.313659).sqrt()).arctan()
            + (temp + humedad).arctan()
            - (humedad - 1.676331).arctan()
            + 0.00391838 * humedad**1.5 * (0.023101 * humedad).arctan()
            - 4.686035
        ).alias("bulbo_humedo")
    )


def add_calendar_cycles(datos: pl.DataFrame) -> pl.DataFrame:
    """Agrega la hora y el día del año como pares seno-coseno.

    El par seno-coseno deja cerca las 23:00 y las 00:00 en el plano y
    representa la continuidad del ciclo. Puede ayudar al modelo, aunque los
    árboles también pueden trabajar con las variables originales. Con `h = hora + minuto/60` y
    `d = día del año`, agrega `hora_seno = sin(2*pi*h/24)`,
    `hora_coseno = cos(2*pi*h/24)`, `dia_anio_seno = sin(2*pi*(d-1)/365.25)`
    y `dia_anio_coseno = cos(2*pi*(d-1)/365.25)`. La hora y el día son los de
    la columna `hora`, en hora local.
    """
    if "hora" not in datos.columns:
        raise ValueError("datos debe incluir la columna hora")

    hora = pl.col("hora").dt.hour() + pl.col("hora").dt.minute() / 60
    dia = pl.col("hora").dt.ordinal_day()
    angulo_hora = 2 * math.pi * hora / 24
    angulo_dia = 2 * math.pi * (dia - 1) / 365.25
    return datos.with_columns(
        angulo_hora.sin().alias("hora_seno"),
        angulo_hora.cos().alias("hora_coseno"),
        angulo_dia.sin().alias("dia_anio_seno"),
        angulo_dia.cos().alias("dia_anio_coseno"),
    )


def add_hours_since_sunset(
    datos: pl.DataFrame,
    latitud: float = -34.97,
    longitud: float = -71.23,
) -> pl.DataFrame:
    """Agrega las horas transcurridas desde el último atardecer.

    Usa la declinación solar de Cooper y el ángulo horario del atardecer. La
    corrección por longitud y zona horaria convierte la hora solar a la hora
    local, incluido el cambio de horario. Es una función astronómica: no usa
    mediciones y mide cuánto lleva enfriándose el aire en una noche despejada.
    """
    if "hora" not in datos.columns:
        raise ValueError("datos debe incluir la columna hora")

    dia = pl.col("hora").dt.ordinal_day()
    declinacion = math.radians(23.44) * (2 * math.pi * (284 + dia) / 365).sin()
    tan_latitud = math.tan(math.radians(latitud))
    angulo = (-tan_latitud * declinacion.tan()).clip(-1.0, 1.0).arccos()
    atardecer_solar = 12 + 12 * angulo / math.pi

    desfase_horas = (
        pl.col("hora").dt.base_utc_offset() + pl.col("hora").dt.dst_offset()
    ).dt.total_seconds() / 3600
    correccion = (desfase_horas * 15 - longitud) / 15
    hora_local = pl.col("hora").dt.hour() + pl.col("hora").dt.minute() / 60
    horas = (hora_local - (atardecer_solar + correccion)) % 24
    return datos.with_columns(horas.alias("horas_desde_atardecer"))


def add_lags(
    datos: pl.DataFrame, lags: list[int] | tuple[int, ...]
) -> pl.DataFrame:
    """Agrega `temp_lag_k` con la temperatura de `t - k` para cada orden.

    El orden 0 es la temperatura de la hora actual y es una variable legítima:
    está medida antes de emitir el pronóstico. Un orden negativo usaría el
    futuro y se rechaza. Las filas deben ser horas consecutivas, como las que
    entrega `load_station`.
    """
    if "temp" not in datos.columns:
        raise ValueError("datos debe incluir la columna temp")
    if not lags:
        raise ValueError("lags no puede estar vacío")
    if len(set(lags)) != len(lags):
        raise ValueError("lags no puede tener valores repetidos")
    if any(lag < 0 for lag in lags):
        raise ValueError("Cada lag debe ser al menos 0")

    return datos.with_columns(
        [pl.col("temp").shift(lag).alias(f"temp_lag_{lag}") for lag in lags]
    )


def build_moving_windows(
    datos: pl.DataFrame,
    ventanas: list[int] | tuple[int, ...],
    estadisticas: list[str] | tuple[str, ...],
) -> pl.DataFrame:
    """Resume la temperatura en ventanas móviles que terminan en `t`.

    Cada ventana se mide en horas y no en filas, para que un hueco no desplace
    el período. Exige al menos la mitad de las horas de la ventana; si no,
    deja `null`. Devuelve solo las columnas nuevas, con las mismas filas y el
    mismo orden que `datos`: una columna `temp_{estadistica}_{ventana}h` por
    combinación.
    """
    if "temp" not in datos.columns or "hora" not in datos.columns:
        raise ValueError("datos debe incluir las columnas hora y temp")
    if not ventanas:
        raise ValueError("ventanas no puede estar vacía")
    if not estadisticas:
        raise ValueError("estadisticas no puede estar vacía")
    if len(set(ventanas)) != len(ventanas):
        raise ValueError("ventanas no puede tener valores repetidos")
    if len(set(estadisticas)) != len(estadisticas):
        raise ValueError("estadisticas no puede tener valores repetidos")
    if any(ventana < 2 for ventana in ventanas):
        raise ValueError("Cada ventana debe ser al menos 2")
    desconocidas = [
        nombre
        for nombre in estadisticas
        if nombre not in {"mean", "std", "median", "min", "max"}
    ]
    if desconocidas:
        raise ValueError(f"Estadística desconocida: {desconocidas}")

    columnas = []
    for ventana in ventanas:
        minimo = max(2, ventana // 2)
        for estadistica in estadisticas:
            rolling = getattr(pl.col("temp"), f"rolling_{estadistica}_by")
            columnas.append(
                rolling(
                    "hora",
                    window_size=f"{ventana}h",
                    min_samples=minimo,
                ).alias(f"temp_{estadistica}_{ventana}h")
            )
    return datos.select(columnas)


def build_features(
    datos: pl.DataFrame,
    lags: list[int] | tuple[int, ...] = (0, 1, 2, 3, 6, 12, 24),
    ventanas: list[int] | tuple[int, ...] = (3, 6, 12, 24),
) -> pl.DataFrame:
    """Construye las variables disponibles en el origen del pronóstico.

    Conserva `hora` y `temp` en el origen (esta última para construir el
    objetivo) y agrega:

    - las mediciones de la hora actual;
    - punto de rocío, su depresión, bulbo húmedo y componentes del viento;
    - hora y día del año como ciclos;
    - horas desde el atardecer;
    - lags de temperatura;
    - media, mínimo, máximo y desviación de ventanas de 3, 6, 12 y 24 horas.

    Ninguna columna usa información posterior al origen `t`.
    """
    requeridas = {"hora", "temp", "rhum", "pres", "wspd", "wdir", "cldc"}
    faltantes = requeridas - set(datos.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas: {sorted(faltantes)}")

    base = datos.select("hora", "temp", "rhum", "pres", "wspd", "wdir", "cldc")
    base = add_dew_point(base)
    base = add_wind_components(base)
    base = add_wet_bulb(base)
    base = add_calendar_cycles(base)
    base = add_hours_since_sunset(base)
    base = base.drop("wdir")
    base = add_lags(base, lags)

    moviles = build_moving_windows(
        datos,
        ventanas=ventanas,
        estadisticas=["mean", "min", "max", "std"],
    )
    return pl.concat([base, moviles], how="horizontal")


def build_supervised(
    features: pl.DataFrame,
    horizonte: int = 12,
    columnas_features: list[str] | None = None,
) -> tuple[pl.DataFrame, pl.Series]:
    """Alinea cada origen `t` con la temperatura de `t + horizonte`.

    Devuelve `(X, y)` sin filas cuyo origen o cuyo objetivo falten. `X` conserva
    la columna `hora` (el origen) y las variables; `y` es la serie
    `temp_objetivo`, en las mismas filas y el mismo orden. Las variables pueden
    conservar valores faltantes (por ejemplo, la cobertura de nubes no se
    informa siempre) porque LightGBM los acepta. Por defecto, `X` usa todas las
    columnas salvo `temp`, que es la materia prima del objetivo.
    """
    if horizonte < 1:
        raise ValueError("horizonte debe ser al menos 1")
    if "temp" not in features.columns or "hora" not in features.columns:
        raise ValueError("features debe incluir las columnas hora y temp")

    if columnas_features is None:
        columnas_features = [
            columna
            for columna in features.columns
            if columna not in ("hora", "temp")
        ]

    faltantes = [
        columna
        for columna in columnas_features
        if columna not in features.columns
    ]
    if faltantes:
        raise ValueError(f"Faltan features: {faltantes}")

    tabla = features.with_columns(
        pl.col("temp").shift(-horizonte).alias("temp_objetivo")
    ).filter(
        pl.col("temp").is_not_null() & pl.col("temp_objetivo").is_not_null()
    )
    if tabla.is_empty():
        raise ValueError("No quedan filas completas después de alinear")

    return tabla.select("hora", *columnas_features), tabla["temp_objetivo"]


def build_nightly_target(
    estacion: pl.DataFrame,
    meses: tuple[int, ...] = (5, 6, 7, 8, 9),
    hora_origen: int = 18,
    minimo_horas: int = 8,
) -> pl.DataFrame:
    """Calcula la temperatura mínima de cada noche, indexada por su origen.

    Una noche se observa desde las 21:00 del día del origen hasta las 08:00
    del día siguiente. Si hay menos de `minimo_horas` observaciones, la noche
    no entrega objetivo. Devuelve una tabla con dos columnas, `hora` (el
    origen, a las 18:00 por defecto, que es el instante en que se emite el
    pronóstico) y `temp_minima`, ordenada por `hora`.
    """
    if "temp" not in estacion.columns or "hora" not in estacion.columns:
        raise ValueError("estacion debe incluir las columnas hora y temp")
    if minimo_horas < 1:
        raise ValueError("minimo_horas debe ser al menos 1")

    # La ventana de las 12 horas de la noche termina 14 horas después del
    # origen; se calcula ahí y se trae de vuelta al origen.
    minimo_noche = (
        pl.col("temp")
        .rolling_min_by("hora", window_size="12h", min_samples=minimo_horas)
        .shift(-14)
    )
    return (
        estacion.with_columns(minimo_noche.alias("temp_minima"))
        .filter(
            (pl.col("hora").dt.hour() == hora_origen)
            & pl.col("hora").dt.month().is_in(meses)
            & pl.col("temp_minima").is_not_null()
        )
        .select("hora", "temp_minima")
        .sort("hora")
    )
