# Laboratorio 10 — Radio fcFM: ¿se puede conocer el ánimo de una canción por su letra?

Desde la raíz del laboratorio, instalen las dependencias:

```bash
uv sync --locked --all-groups
```

El trabajo se hace en `notebooks/Lab10_Enunciado.ipynb` y en los módulos de
`src/radio_fcfm/`, salvo `contratos.py` y `tracking.py`, que vienen implementados.
Después de completar cada etapa, ejecuten:

```bash
uv run pytest -m etapa1
uv run pytest -m etapa2
uv run pytest -m etapa3
uv run pytest -m etapa4
```

`letras.csv` se descarga del enlace que comparte el equipo docente y se copia en
`data/raw/`. Su origen y su aviso de derechos de autor están en
`data/raw/README.md`. En la Etapa 4, las canciones propias se pegan en la celda
del notebook, solo en inglés: las letras tienen derechos de autor, así que
antes de hacer `commit` hay que volver a dejar la letra de ejemplo. Ningún
modelo del laboratorio necesita GPU, y solo la subsección de Jev usa la red.
