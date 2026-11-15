# Laboratorio 12 — Benchmark de carga y modelos con Spotify

Un laboratorio **experimental** sobre 200.000 canciones de Spotify: se mide
cuánto cuesta cargar los datos y cuánto cuesta predecir con ellos, y se
interpretan las mediciones. No hay módulos que escribir; el trabajo vive en el
notebook.

Todos los comandos se ejecutan desde esta carpeta, donde está
`pyproject.toml`.

## Comenzar

```bash
uv sync
```

El notebook está en `notebooks/Lab12_Enunciado.ipynb`.

## Estructura

```text
notebooks/Lab12_Enunciado.ipynb   el enunciado completo
data/raw/batch_01.parquet …       los 20 archivos Parquet de canciones
```

Las secciones 1.1 y 1.2 dejan una celda por completar; las secciones 2.1 y
2.2 traen todo el código resuelto y piden medir e interpretar. Los tiempos
dependen de su máquina: las respuestas deben citar sus propios números.
