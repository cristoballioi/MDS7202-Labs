# PixelLab — material inicial

Este directorio es la copia de trabajo para estudiantes del Laboratorio 3.
Los comandos se ejecutan desde `Lab3Tarea`, no desde la raíz del repositorio.

La app, los datos y los tests son material entregado por el curso. La app de
Streamlit sirve para experimentar y comprobar la integración, pero no deben
modificarla ni entregarla como trabajo propio.

## Comenzar

```bash
uv sync
uv run pytest -m etapa2
uv run streamlit run app.py
```

Antes de implementar cada etapa, lean los tests asociados en `tests/` y
ejecuten el marcador correspondiente. El enunciado explica qué archivos son
entregados y qué partes deben completar.

```bash
uv run pytest -m etapa3
uv run pytest -m etapa4
uv run pytest -m etapa5
uv run pytest -m etapa6
uv run pytest
```

## Archivos entregados y archivos por completar

- `app.py`, `src/pixellab/carga.py`, `data/` y todos los archivos de `tests/`
  son provistos por el curso: no los modifiquen.
- `src/pixellab/imagen.py`, `src/pixellab/procesamiento.py` y
  `src/pixellab/kernels.py` contienen stubs y espacios de trabajo para el
  proyecto.
- `notebooks/Lab3_Enunciado.ipynb` contiene las instrucciones y
  `notebooks/Lab3_Teoria.ipynb` contiene el material previo.

Esta carpeta contiene únicamente material para estudiantes.
