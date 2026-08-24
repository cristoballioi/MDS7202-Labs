# Laboratorio 4 — Temperaturas CRU

Procesamiento tabular con Polars: explorar, validar, construir fechas y agregar
temperaturas medias mensuales del conjunto de datos CRU.

Todos los comandos se ejecutan desde esta carpeta, donde está
`pyproject.toml`.

## Comenzar

```bash
uv sync
uv run jupyter lab
```

También pueden abrir `notebooks/Lab4_Enunciado.ipynb` en VS Code.

El proyecto ya viene armado. El notebook es el espacio de experimentación y
los módulos de `src/meteolab/` contienen las funciones que deben completar.

## Orden de trabajo

1. Explorar el CSV CRU y describir sus columnas, países, períodos y nulos.
2. Leer el archivo con Polars y comparar las lecturas eager y lazy.
3. Declarar y validar el esquema.
4. Limpiar la tabla y conservar solo las temperaturas medias mensuales.
5. Construir fechas y agregaciones a partir de las filas mensuales.
6. Calcular anomalías usando ventanas por país y mes.
7. Construir pipelines lazy para reproducir el análisis.

Después de cada etapa, ejecuten la marca correspondiente:

```bash
uv run pytest -m etapa1
uv run pytest -m etapa2
uv run pytest -m etapa3
uv run pytest -m etapa4
uv run pytest -m etapa5
uv run pytest -m etapa6
uv run pytest
```

## Archivos que deben completar

- `src/meteolab/carga.py`;
- `src/meteolab/esquema.py`;
- `src/meteolab/limpieza.py`;
- `src/meteolab/derivadas.py`;
- `src/meteolab/metricas.py`;
- `src/meteolab/reporte.py`;
- `notebooks/Lab4_Enunciado.ipynb`, con las preguntas respondidas.

El CSV CRU, los gráficos Plotly y las pruebas son archivos provistos por el curso.
No modifiquen esos archivos.

## Antes de entregar

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Reinicien el kernel y ejecuten el notebook completo antes de entregar.
