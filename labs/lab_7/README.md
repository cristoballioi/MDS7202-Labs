# Laboratorio 7 — Visualización de datos: EDA y reportería

Dos partes sobre el dataset de pingüinos de Palmer: una de visualización y
análisis exploratorio en el notebook, y un panel de Streamlit que construyen
ustedes.

El laboratorio es **exploratorio**: el dataset se mira como llega, con sus
valores faltantes y sus rarezas. Acá no se limpia nada. Cuando un gráfico se
niegue a dibujarse con los datos así, el ajuste va en ese gráfico y se deja
escrito — no en el dataset.

Todos los comandos se ejecutan desde esta carpeta, donde está
`pyproject.toml`.

## Comenzar

```bash
uv sync
```

El notebook está en `notebooks/Lab7_Enunciado.ipynb`.

Los gráficos **no vienen escritos**: cada entregable declara qué quiere y con
qué condiciones, y la función y sus argumentos salen de la documentación de
Plotly, enlazada en el recuadro anterior a cada uno.

## Estructura

```text
notebooks/Lab7_Enunciado.ipynb   el enunciado completo
data/raw/penguins.csv            el dataset, para las dos partes
mi_panel.py                      andamiaje del panel de la Parte 2
.streamlit/config.toml           andamiaje de su tema
```

`mi_panel.py` trae los imports, la configuración de la página y el cargador de
datos ya escritos —infraestructura, no se evalúa— y las cuatro secciones
vacías, cada una con lo que tiene que producir y el enlace a la documentación
que lo explica. Ejecutado tal cual se detiene con un `NotImplementedError`:
bórrenlo cuando empiecen. Pueden renombrar el archivo.

`.streamlit/config.toml` viene con las claves comentadas. Descoméntenlas y
decidan sus colores; dejarlo tal cual es dejar el tema de fábrica.

No hay un panel de ejemplo resuelto: los requisitos están en el enunciado y las
decisiones son suyas.

## Antes de entregar

```bash
uv run ruff check .
uv run ruff format --check .
```

Reinicien el kernel y ejecuten el notebook completo. Abran su panel con
`uv run streamlit run mi_panel.py` y revisen que la terminal no muestre errores
ni advertencias de deprecación.
