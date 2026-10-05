# Laboratorio 9 — Predecir biomasa en base a imágenes

Desde la raíz del laboratorio, instalen las dependencias:

```bash
uv sync --locked --all-groups
```

El trabajo se hace en `notebooks/Lab9_Enunciado.ipynb` y en los módulos de
`src/pasturecam/`, salvo `contratos.py` y `tracking.py`, que vienen
implementados. Después de completar cada etapa, ejecuten:

```bash
uv run pytest -m etapa1
uv run pytest -m etapa2
uv run pytest -m etapa3
uv run pytest -m etapa4
```

Los datos y su licencia están descritos en `data/raw/README.md`. El extractor
de imágenes se usa solo para inferencia: no hace falta GPU, pero la primera
vez que corran la Etapa 2 va a descargar sus pesos desde Hugging Face.
