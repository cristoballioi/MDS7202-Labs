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

# import agregado por nosotros
import plotly.express as px
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
st.subheader("Explorador y tabla de datos")

# Filtro categórico por especie estabilizado
# Se agrega sorted() para mantener el orden y key para conservar la selección del usuario
especies_disponibles = sorted(df["species"].drop_nulls().unique().to_list())
especies_seleccionadas = st.multiselect(
    "Seleccione las especies a visualizar:",
    options=especies_disponibles,
    default=especies_disponibles,
    key="filtro_especies",
)

min_masa = int(df.select(pl.col("body_mass_g").min()).item() or 0)
max_masa = int(df.select(pl.col("body_mass_g").max()).item() or 6500)
rango_masa = st.slider(
    "Seleccione el rango de masa corporal (g):",
    min_value=min_masa,
    max_value=max_masa,
    value=(min_masa, max_masa),
)

# Filtrado del DataFrame usando Polars (corregido)
df_filtrado = df.filter(
    pl.col("species").is_in(especies_seleccionadas)
    & pl.col("body_mass_g").is_between(
        rango_masa[0], rango_masa[1], closed="both"
    )
)

# Comprobar si la selección queda vacía y mostrar un aviso
if df_filtrado.height == 0:
    st.warning("No hay registros que cumplan con los filtros seleccionados.")
else:
    st.dataframe(
        df_filtrado,
        use_container_width=True,
        column_config={
            "species": st.column_config.TextColumn("Especie"),
            "island": st.column_config.TextColumn("Isla"),
            "culmen_length_mm": st.column_config.NumberColumn(
                "Largo del pico (mm)", format="%.1f"
            ),
            "culmen_depth_mm": st.column_config.NumberColumn(
                "Alto del pico (mm)", format="%.1f"
            ),
            "flipper_length_mm": st.column_config.NumberColumn(
                "Largo de aleta (mm)", format="%d"
            ),
            "body_mass_g": st.column_config.NumberColumn(
                "Masa corporal (g)", format="%d"
            ),
            "sex": st.column_config.TextColumn("Sexo"),
        },
    )


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
st.subheader("Informe de calidad de los datos")

# Calculamos los nulos sobre el dataframe original completo (df)
nulos_por_columna = df.null_count().to_dicts()[0]
# Filtramos solo las columnas que tienen más de 0 nulos
columnas_con_nulos = {
    col: cant for col, cant in nulos_por_columna.items() if cant > 0
}

# Contamos cuántos registros tienen el valor inesperado "." en la columna sex
sexo_inesperado = df.filter(pl.col("sex") == ".").height

# Mostramos un mensaje de advertencia en el panel con los resultados calculados
st.warning(
    "Observaciones sobre los datos originales:\n\n"
    f"- Valores nulos: Hay datos faltantes en {columnas_con_nulos}. "
    "Esto causa que los gráficos numéricos y los filtros excluyan estas filas automáticamente, "
    "dejando fuera a esos pingüinos del análisis visual.\n"
    f"- Valores inesperados: La columna sex tiene {sexo_inesperado} registro con el valor '.'. "
    "Si se agrupa por sexo, se creará una categoría adicional sin sentido biológico, "
    "distorsionando los conteos totales."
)


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
st.subheader("Visualizaciones Interactivas")

# Creamos dos columnas en la página para mostrar los gráficos en formato cuadrícula
col1, col2 = st.columns(2)

with col1:
    # Gráfico 1: Dispersión (Scatter)
    fig_scatter = px.scatter(
        df_filtrado,
        x="flipper_length_mm",
        y="body_mass_g",
        color="species",
        title="Relación entre aleta y masa corporal",
        labels={
            "flipper_length_mm": "Largo de aleta (mm)",
            "body_mass_g": "Masa (g)",
            "species": "Especie",
        },
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption(
        "Este gráfico de dispersión es útil para identificar la correlación entre el largo de la aleta y la masa corporal. Se eligió esta visualización porque permite ver el comportamiento individual de cada pingüino y cómo se agrupan por especie."
    )

    # Gráfico 2: Diagrama de caja (Box)
    fig_box = px.box(
        df_filtrado,
        x="species",
        y="body_mass_g",
        color="species",
        title="Distribución de masa por especie",
        labels={"species": "Especie", "body_mass_g": "Masa (g)"},
    )
    st.plotly_chart(fig_box, use_container_width=True)
    st.caption(
        "El diagrama de caja es útil para comparar los cuartiles, la mediana y detectar valores atípicos en la masa corporal. Se eligió porque resume perfectamente las diferencias estadísticas entre los grupos sin saturar la vista."
    )

with col2:
    # Gráfico 3: Histograma superpuesto
    fig_hist = px.histogram(
        df_filtrado,
        x="body_mass_g",
        color="species",
        barmode="overlay",
        opacity=0.7,
        title="Frecuencia de masa corporal",
        labels={"body_mass_g": "Masa corporal (g)", "species": "Especie"},
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    st.caption(
        "El histograma es útil para observar la forma de la distribución de los datos de masa. Se eligió con barras superpuestas para comparar dónde se concentran los pesos de cada especie simultáneamente."
    )

    # Gráfico 4: Anillos (Sunburst) de composición
    # Manejamos los nulos temporalmente solo para este gráfico
    df_sunburst = df_filtrado.with_columns(
        pl.col("island").fill_null("Nulo"), pl.col("species").fill_null("Nulo")
    )
    fig_sunburst = px.sunburst(
        df_sunburst,
        path=["species", "island"],
        title="Proporción de especies por isla",
    )
    st.plotly_chart(fig_sunburst, use_container_width=True)
    st.caption(
        "El gráfico de anillos (sunburst) es útil para entender la composición jerárquica del dataset. Se eligió porque hace muy evidente de un solo vistazo qué proporción de cada especie habita en cada isla."
    )


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
