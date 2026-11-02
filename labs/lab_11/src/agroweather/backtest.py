"""Particiones temporales, baselines, métricas y backtesting."""

from __future__ import annotations

from datetime import datetime

import lightgbm
import numpy as np
import polars as pl


def make_model(**params) -> lightgbm.LGBMRegressor:
    """Devuelve un LightGBM sin ajustar con los parámetros recibidos.

    Los valores default sirven para una serie horaria: árboles poco
    profundos, aprendizaje lento y `n_jobs=1` para que el resultado no dependa
    del número de núcleos. `verbose=-1` evita que cada ajuste escriba en la
    salida del notebook.
    """
    return lightgbm.LGBMRegressor(
        n_estimators=params.get("n_estimators", 300),
        num_leaves=params.get("num_leaves", 31),
        learning_rate=params.get("learning_rate", 0.05),
        min_child_samples=params.get("min_child_samples", 20),
        subsample=params.get("subsample", 0.8),
        subsample_freq=1,
        colsample_bytree=params.get("colsample_bytree", 0.8),
        reg_lambda=params.get("reg_lambda", 1.0),
        random_state=params.get("random_state", 42),
        n_jobs=1,
        verbose=-1,
    )


def temporal_split(
    X: pl.DataFrame,
    y: pl.Series,
    inicio_validation: str | datetime,
    inicio_test: str | datetime,
    horizonte: int = 12,
) -> dict[str, tuple[pl.DataFrame, pl.Series]]:
    """Divide `(X, y)` por la hora del target y purga ambas fronteras.

    `X` trae la hora del origen en `hora`; `y` tiene las mismas filas y orden.
    Los cortes se aplican a `hora + horizonte`. Además, train solo conserva
    targets anteriores a `inicio_validation - horizonte`, y validation,
    targets desde `inicio_validation` hasta antes de `inicio_test - horizonte`.
    Test conserva targets desde `inicio_test`. Las filas purgadas se excluyen,
    sin trasladarlas a otra parte. Así el ajuste y la climatología no usan
    targets posteriores al primer origen nominal del bloque siguiente.

    Rechaza largos distintos, ausencia de `hora` de tipo fecha, entradas
    vacías, horizonte menor que 1, cortes invertidos y particiones vacías.
    """
    raise NotImplementedError(
        "Completen temporal_split antes de ejecutar esta celda."
    )


def rmse(y_real: pl.Series, y_pred: pl.Series) -> float:
    """Raíz del error cuadrático medio entre dos series alineadas."""
    real = np.asarray(y_real, dtype=float)
    pred = np.asarray(y_pred, dtype=float)
    if real.shape != pred.shape:
        raise ValueError("y_real e y_pred deben tener el mismo largo")
    if real.size == 0:
        raise ValueError("No hay valores para calcular el RMSE")
    return float(np.sqrt(np.mean((real - pred) ** 2)))


def mae(y_real: pl.Series, y_pred: pl.Series) -> float:
    """Error absoluto medio entre dos series alineadas, en °C."""
    real = np.asarray(y_real, dtype=float)
    pred = np.asarray(y_pred, dtype=float)
    if real.shape != pred.shape:
        raise ValueError("y_real e y_pred deben tener el mismo largo")
    if real.size == 0:
        raise ValueError("No hay valores para calcular el MAE")
    return float(np.mean(np.abs(real - pred)))


def reporte_reglas(
    pronosticos: pl.DataFrame,
    reales: pl.Series,
    descartados: pl.Series,
) -> pl.DataFrame:
    """Reporta MAE y RMSE por regla sobre las mismas filas disponibles.

    `pronosticos` tiene una columna por regla y las mismas filas, en el mismo
    orden, que `reales`. `descartados` marca las filas sin pronóstico de
    persistencia diaria: se excluyen de todas las reglas y de `reales`.
    Devuelve una tabla con `regla`, `n`, `MAE` y `RMSE`.
    """
    if pronosticos.height != reales.len():
        raise ValueError("pronosticos y reales deben tener el mismo largo")
    if "diaria" not in pronosticos.columns:
        raise ValueError("pronosticos debe incluir la columna diaria")
    if pronosticos.height == 0:
        raise ValueError("pronosticos no tiene filas")
    if reales.null_count() > 0:
        raise ValueError("reales no puede tener valores faltantes")

    if descartados.len() != pronosticos.height:
        raise ValueError("descartados debe tener el mismo largo")
    datos = pronosticos.filter(~descartados)
    reales = reales.filter(~descartados)

    if sum(datos.null_count().row(0)) > 0:
        raise ValueError("Quedan pronósticos faltantes después de descartar")
    if reales.len() == 0:
        raise ValueError("No quedan filas para evaluar")

    filas = []
    for regla in datos.columns:
        filas.append(
            {
                "regla": regla,
                "n": reales.len(),
                "MAE": mae(reales, datos[regla]),
                "RMSE": rmse(reales, datos[regla]),
            }
        )
    return pl.DataFrame(filas)


def persistence_forecast(X: pl.DataFrame) -> pl.Series:
    """Baseline de persistencia: repite la temperatura del origen."""
    if "temp_lag_0" not in X.columns:
        raise ValueError("X debe incluir temp_lag_0")
    return X["temp_lag_0"].alias("pronostico")


def daily_persistence_forecast(
    X: pl.DataFrame,
    temperaturas: pl.DataFrame,
    horizonte: int = 12,
) -> pl.Series:
    """Baseline de persistencia diaria: «igual que ayer» a la hora del target.

    El target de cada fila es la temperatura de `hora + horizonte`. La regla
    la pronostica con la temperatura observada 24 horas antes de ese target,
    en `hora + horizonte - 24`, que se busca por hora en `temperaturas`
    (columnas `hora` y `temp`, por ejemplo, la estación limpia). Con
    `horizonte` entre 1 y 24, esa hora no es posterior al origen, así que la
    regla no usa información futura. Devuelve una serie `pronostico` con una
    fila por cada fila de `X`, en el mismo orden.

    No rellena los huecos. Cuando la hora de ayer no está observada, la regla
    no tiene pronóstico y devuelve `null`. Al comparar las reglas en el
    notebook, esas filas se excluyen de todas ellas; las features con
    faltantes se conservan para LightGBM.
    """
    raise NotImplementedError(
        "Completen daily_persistence_forecast antes de ejecutar esta celda."
    )


def climatology_forecast(
    X_train: pl.DataFrame,
    y_train: pl.Series,
    X: pl.DataFrame,
    horizonte: int = 12,
) -> pl.Series:
    """Baseline de climatología: media de train por mes y hora del objetivo.

    `X_train` e `y_train` son las filas de entrenamiento: `X_train` aporta la
    hora del origen (columna `hora`) e `y_train`, la temperatura que se
    observó `horizonte` horas después. La media se calcula con la hora a la
    que se pronostica, no con la del origen. Si una combinación de mes y hora
    no aparece en train, usa la media general de train. Devuelve una serie
    `pronostico` con una fila por cada fila de `X`.
    """
    raise NotImplementedError(
        "Completen climatology_forecast antes de ejecutar esta celda."
    )


def make_expanding_folds(
    indice: pl.Series,
    anios: tuple[int, ...],
    purga_horas: int = 24,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Construye folds anuales con ventana expansiva y purga.

    Para cada año `Y`, el train son todas las filas anteriores al 1 de enero
    de `Y` menos `purga_horas`, y la validation son las filas de `Y`. La purga
    deja un hueco de al menos el horizonte máximo: sin ella, el objetivo de la
    última fila de train caería dentro del año que se evalúa.

    `indice` es la columna `hora` de `X`. Devuelve posiciones enteras de esa
    columna, no fechas: son las que usa `walk_forward` para seleccionar filas.
    """
    raise NotImplementedError(
        "Completen make_expanding_folds antes de ejecutar esta celda."
    )


def walk_forward(
    X: pl.DataFrame,
    y: pl.Series,
    modelo,
    folds: list[tuple[np.ndarray, np.ndarray]],
) -> pl.DataFrame:
    """Evalúa `modelo` sobre folds de ventana expansiva o móvil.

    `X` trae la hora del origen en la columna `hora`; el modelo no la recibe:
    se ajusta y predice con las demás columnas. Para cada fold ajusta una
    copia del modelo con las filas de train y predice las de validation.
    Devuelve una tabla con las columnas `hora` (el origen), `fold`, `real` y
    `pronostico`.
    """
    raise NotImplementedError(
        "Completen walk_forward antes de ejecutar esta celda."
    )


def recall_evento(real: pl.Series, alerta: pl.Series) -> float:
    """Proporción de eventos reales que la alerta avisó."""
    real = np.asarray(real, dtype=bool)
    alerta = np.asarray(alerta, dtype=bool)
    eventos = real.sum()
    if eventos == 0:
        raise ValueError("No hay eventos reales para evaluar el recall")
    return float((real & alerta).sum() / eventos)


def tasa_falsas_alarmas(real: pl.Series, alerta: pl.Series) -> float:
    """Proporción de noches sin evento en que la alerta se encendió."""
    real = np.asarray(real, dtype=bool)
    alerta = np.asarray(alerta, dtype=bool)
    calmas = (~real).sum()
    if calmas == 0:
        raise ValueError("No hay noches sin evento para evaluar la tasa")
    return float((~real & alerta).sum() / calmas)


def costo_alerta(
    real: pl.Series,
    alerta: pl.Series,
    costo_por_alerta: float = 400_000.0,
    costo_helada: float = 20_000_000.0,
) -> float:
    """Costo total de una regla de alerta.

    Toda noche con alerta cuesta `costo_por_alerta`, la parafina, sea una
    falsa alarma o una helada real. Cada helada sin aviso cuesta
    `costo_helada`, porque el evento no se evitó.
    """
    real = np.asarray(real, dtype=bool)
    alerta = np.asarray(alerta, dtype=bool)
    if real.shape != alerta.shape:
        raise ValueError("real y alerta deben tener el mismo largo")

    no_avisadas = (real & ~alerta).sum()
    return float(alerta.sum() * costo_por_alerta + no_avisadas * costo_helada)


def mejor_umbral(
    real: pl.Series,
    pronostico: pl.Series,
    costo_por_alerta: float = 400_000.0,
    costo_helada: float = 20_000_000.0,
) -> tuple[float, float]:
    """Busca el umbral de temperatura que minimiza el costo de la alerta.

    Recorre los valores pronosticados y se queda con el primero que alcanza el
    costo mínimo. Devuelve `(umbral, costo)`: se enciende la alerta cuando el
    pronóstico es menor que el umbral. El umbral se elige en validation y se
    aplica una sola vez en test.
    """
    raise NotImplementedError(
        "Completen mejor_umbral antes de ejecutar esta celda."
    )
