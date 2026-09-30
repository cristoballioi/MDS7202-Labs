# Laboratorio 8 — El Multiverso Porteño

Desde la raíz del laboratorio, instalen las dependencias:

```bash
uv sync --locked --all-groups
```

El trabajo se hace en `notebooks/Lab8_Enunciado.ipynb` y en los módulos de
`src/heroverse/`. Después de completar cada etapa, ejecuten:

```bash
uv run pytest -m etapa1
uv run pytest -m etapa2
uv run pytest -m etapa3
uv run pytest -m etapa5
```

La etapa 4 no tiene pruebas: se comprueba mirando las proyecciones del
notebook. Los datos y su licencia están descritos en `data/raw/README.md`.
