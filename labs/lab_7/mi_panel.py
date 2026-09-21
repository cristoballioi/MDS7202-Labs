"""Andamiaje del panel de la Parte 2. Renómbrenlo si quieren.

MATERIAL PROVISTO. Lo que ya está escrito acá —los imports, la configuración
de la página y el cargador de datos— es infraestructura y no se evalúa: son
las mismas líneas para cualquier panel sobre este dataset. Lo que sí se evalúa
son las cuatro secciones de más abajo.

Las secciones están en un orden que funciona, pero no es obligatorio:
reordenarlas o renombrarlas no descuenta. Lo que se corrige es que las cuatro
cosas estén y que cada gráfico explique por qué está ahí.

Para trabajar:

    uv run streamlit run mi_panel.py

Streamlit reejecuta el archivo completo cada vez que alguien mueve un control,
así que el navegador se actualiza solo al guardar.
"""

from pathlib import Path

import polars as pl
import streamlit as st

RUTA_DATOS = Path(__file__).parent / "data" / "raw" / "penguins.csv"

st.set_page_config(
    page_title="Pingüinos de Palmer", page_icon="🐧", layout="wide"
)
st.title("🐧 Pingüinos del archipiélago de Palmer")


@st.cache_data
def cargar_datos() -> pl.DataFrame:
    """Lee el CSV sin modificarlo.

    `null_values=["NA"]` es necesario: el archivo viene de R, donde `NA` marca
    los faltantes. Sin ese argumento, polars lee las columnas numéricas como
    texto. Con él, los nulos quedan adentro — que es lo que queremos, porque
    este laboratorio no limpia nada.
    """
    return pl.read_csv(RUTA_DATOS, null_values=["NA"])


df = cargar_datos()

raise NotImplementedError(
    "Completen las cuatro secciones de este archivo y borren esta línea "
    "antes de ejecutar el programa."
)

# --- 1) La tabla interactiva -----------------------------------------------
#
# Una tabla con el dataset que el lector pueda ordenar por cualquier columna y
# filtrar con al menos dos controles: uno categórico y uno de rango numérico.
# Esos mismos filtros deben afectar también a los cuatro gráficos. Los
# registros sin valor en la columna del filtro numérico quedan fuera de la
# selección filtrada. Si ningún registro cumple los filtros, muestren un aviso.
#
# Ordenar y buscar los trae `st.dataframe` de fábrica, sin programar nada.
# Filtrar no: los controles devuelven la selección y ustedes filtran el
# DataFrame antes de pasárselo a la tabla. Denle formato a las columnas, que
# `flipper_length_mm` no es un encabezado para mostrarle a un cliente.
#
#   https://docs.streamlit.io/develop/api-reference/data/st.dataframe
#   https://docs.streamlit.io/develop/api-reference/data/st.column_config
#   https://docs.streamlit.io/develop/api-reference/widgets/st.multiselect
#   https://docs.streamlit.io/develop/api-reference/widgets/st.slider

# Su código aquí


# --- 2) La calidad de los datos --------------------------------------------
#
# Un informe visible en la página, calculado sobre el CSV completo aunque se
# apliquen filtros: qué columnas tienen nulos y cuántos, cuál es el valor
# inesperado de `sex` y cómo pueden afectar esos problemas los recuentos,
# filtros o gráficos del panel.
#
# Las cifras se calculan desde `df`, no se escriben a mano: si el
# archivo cambiara, un número escrito a mano queda mintiendo.
#
#   https://docs.streamlit.io/develop/api-reference/status/st.warning

# Su código aquí


# --- 3) Los cuatro gráficos ------------------------------------------------
#
# Cuatro gráficos a elección, de al menos dos tipos distintos. Pueden reusar
# los de la Parte 1 o construir otros. Van a necesitar `plotly.express`:
# impórtenlo arriba, con el resto.
#
# Cada gráfico lleva, JUNTO A ÉL Y VISIBLE EN LA PÁGINA, por qué esa
# información es útil y por qué eligieron esa visualización. Un comentario en
# el código no cuenta: quien abre el panel no lee el código.
#
#   https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart
#   https://docs.streamlit.io/develop/api-reference/text/st.caption
#   https://docs.streamlit.io/develop/api-reference/layout/st.columns

# Su código aquí


# --- 4) El tema --------------------------------------------------------------
#
# Este no se programa acá: vive en `.streamlit/config.toml`, al lado de este
# archivo. Ya existe, con las claves comentadas — descoméntenlas y decidan sus
# colores.
#
# Para comprobar que el suyo está haciendo algo: renombren el archivo,
# reinicien el panel y vean si cambia. Si no cambia, no lo configuraron.
#
#   https://docs.streamlit.io/develop/concepts/configuration/theming
