"""Interfaz gráfica del servicio de potabilidad, con Streamlit.

Es un cliente de la API: envía las mediciones a `POST /predict` y muestra la
respuesta. Uso, desde la raíz del laboratorio y con la API en ejecución:

    uv run streamlit run src/aguaapr/ui.py

Configuración: la misma de la API, en `config.py` (`APR_API_KEY` y `APR_GRUPO`,
que se muestra bajo el título). Además, `APR_API_URL` indica dónde está la API
(por defecto, `http://127.0.0.1:8000`).
"""

import json
import os
import sys
from pathlib import Path

import streamlit as st
from pydantic import ValidationError

# Streamlit pone en el path la carpeta del script, no la raíz del proyecto:
# sin esto, `from src.aguaapr...` falla con `No module named 'src'`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.aguaapr.config import get_settings
from src.aguaapr.constants import FEATURES, OPCIONALES, RANGOS
from src.aguaapr.ui_cliente import ErrorApi, consultar_api

# nombre, unidad, valor inicial (la mediana del CSV) y paso de cada medición
CAMPOS = {
    "ph": ("pH", "", 7.04, 0.1),
    "Hardness": ("Dureza", "mg/L", 197.0, 1.0),
    "Solids": ("Sólidos disueltos", "ppm", 20928.0, 100.0),
    "Chloramines": ("Cloraminas", "ppm", 7.13, 0.1),
    "Sulfate": ("Sulfatos", "mg/L", 333.0, 1.0),
    "Conductivity": ("Conductividad", "μS/cm", 422.0, 1.0),
    "Organic_carbon": ("Carbono orgánico", "ppm", 14.2, 0.1),
    "Trihalomethanes": ("Trihalometanos", "μg/L", 66.6, 1.0),
    "Turbidity": ("Turbidez", "NTU", 3.97, 0.1),
}

st.set_page_config(page_title="¿Es potable el agua?", page_icon="💧")
st.title("💧 ¿Es potable esta agua?")
try:
    settings = get_settings()
except ValidationError as error:
    faltan = ", ".join(f"APR_{e['loc'][0]}".upper() for e in error.errors())
    st.error(f"Falta la configuración: {faltan}. Revisen su archivo `.env`.")
    st.stop()
st.caption(f"Grupo: {settings.grupo}")
st.write(
    "Ingresen las nueve mediciones de una muestra. La interfaz las envía a la "
    "API del servicio, que consulta el modelo y devuelve la predicción."
)

with st.sidebar:
    st.header("Conexión")
    url_api = st.text_input(
        "Dirección de la API",
        value=os.environ.get("APR_API_URL", "http://127.0.0.1:8000"),
    )
    fuera_de_rango = st.checkbox(
        "Permitir valores fuera de rango",
        help="Quita los límites de cada campo para ver qué responde la API "
        "cuando una medición rompe el contrato.",
    )

medicion: dict[str, float | None] = {}
with st.form("medicion"):
    columnas = st.columns(3)
    for indice, nombre in enumerate(FEATURES):
        etiqueta, unidad, inicial, paso = CAMPOS[nombre]
        minimo, maximo = RANGOS[nombre]
        with columnas[indice % 3]:
            sin_dato = nombre in OPCIONALES and st.checkbox(
                f"Sin dato de {etiqueta.lower()}", key=f"sin_{nombre}"
            )
            valor = st.number_input(
                f"{etiqueta} ({unidad})" if unidad else etiqueta,
                value=inicial,
                min_value=None if fuera_de_rango else minimo,
                max_value=None if fuera_de_rango else maximo,
                step=paso,
                disabled=sin_dato,
                key=nombre,
            )
            medicion[nombre] = None if sin_dato else float(valor)
    enviar = st.form_submit_button("Predecir", type="primary")

if enviar:
    try:
        respuesta = consultar_api(
            url_api, settings.api_key.get_secret_value(), medicion
        )
    except ErrorApi as error:
        st.error(str(error))
    else:
        probabilidad = respuesta["probabilidad"]
        if respuesta["prediccion"] == 1:
            st.success(
                "**Potable**: el modelo estima que el agua se puede beber."
            )
        else:
            st.warning(
                "**No potable**: el modelo estima que el agua no es apta."
            )
        st.metric("Probabilidad de ser potable", f"{probabilidad:.0%}")
        st.progress(probabilidad)
        with st.expander("Ver la solicitud y la respuesta (JSON)"):
            st.code(json.dumps(medicion, indent=2), language="json")
            st.code(json.dumps(respuesta, indent=2), language="json")
