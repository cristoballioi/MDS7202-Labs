# Laboratorio 11: La rodilla de don Nicasio

Desde la raíz del laboratorio, instalen las dependencias:

```bash
uv sync --locked --all-groups
```

La primera instalación tarda más que en otros laboratorios porque incluye
MLflow; háganla antes de la sesión.

El trabajo se entrega en `notebooks/Lab11_Enunciado.ipynb` y en los módulos
que indican los recuadros de ejercicio. La lectura, las
features y la explicabilidad vienen resueltas en `data.py`, `features.py` y
`explain.py`. En las etapas 3, 4 y 5, cada operación aparece primero explorada
en el notebook; después la llevan a una función en
`src/agroweather/backtest.py` o `src/agroweather/tuning.py`. Al terminar las
etapas 3, 4 y 5, ejecuten sus pruebas:

```bash
uv run pytest -m etapa3
uv run pytest -m etapa4
uv run pytest -m etapa5
```

Las etapas 1, 2, 6 y 7 no tienen pruebas: se corrigen leyendo las respuestas del
notebook. Los datos y su licencia están descritos en `data/raw/README.md`.

Los ejercicios de registro en MLflow se programan en las celdas
`# Su código aquí` del notebook, reemplazando el `raise NotImplementedError`.
Los ejercicios de funciones se programan en el módulo indicado, conservando
sus firmas.

Los cierres de etapa indican qué comprobar antes de guardar los cambios
y hacer commit. En la etapa 4 se registra una segunda configuración para
compararla con la referencia; la tabla de señales de la etapa 6 viene resuelta.

Desde la etapa 3, los experimentos se registran en MLflow. La conexión viene
resuelta en `src/agroweather/tracking.py` y guarda la base en `mlflow.db`, en
esta misma carpeta (Git la ignora). Para revisar los runs en el navegador:

```bash
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db
```

y abran `http://127.0.0.1:5000`.

El ejercicio 3.4 indica qué runs, parámetros e historial de métricas consultar
en la interfaz. En el ejercicio 4.3 comparan las dos configuraciones de backtest.
