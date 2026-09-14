# Laboratorio 6 — El Pudú no pierde el rastro

Desde la raíz del laboratorio, instalen las dependencias y preparen DuckLake:

```bash
uv sync --locked --all-groups
uv run python -c 'import duckdb; con = duckdb.connect(); con.execute("INSTALL ducklake"); con.execute("LOAD ducklake")'
```

En otra terminal, inicien Prefect Server con `uv run prefect server start`.
La CLI usa el servidor local.

Después de completar cada etapa, ejecuten:

```bash
uv run pytest -m etapa1
uv run pytest -m etapa2
uv run pytest -m etapa3
uv run pytest -m etapa4
```
