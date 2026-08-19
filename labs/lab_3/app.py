"""Interfaz Streamlit del mini proyecto PixelLab.

Este archivo lo entrega el curso: no hay que modificarlo. Importa la librería
de los estudiantes desde ``src.pixellab`` y les permite probar cada etapa en
vivo mientras la van completando.

La app acompaña el desarrollo desde la Etapa 2: si un módulo todavía no
existe o un método falla, lo avisa en pantalla en lugar de caerse.
"""

from __future__ import annotations

import io
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

from src.pixellab.carga import cargar_imagen

# --- Importación tolerante --------------------------------------------------
# Durante las Etapas 2 y 3 solo existe `imagen.py`, y `kernels.py` aparece
# recién en la Etapa 6. Importar de golpe dejaría la app inutilizable justo
# cuando más sirve, así que lo que falta se marca como ausente.
try:
    from src.pixellab.imagen import Imagen
except ImportError:
    Imagen = None

try:
    from src.pixellab.procesamiento import LibImagen
except ImportError:
    LibImagen = None

try:
    from src.pixellab.kernels import KERNELS
except ImportError:
    KERNELS = None

RUTA_DATOS = Path("data")
IMAGENES_PREDEFINIDAS = ["gato1.jpg", "gato2.jpg", "gato3.jpg"]

CANALES = ("R", "G", "B")
COLORES_CANAL = ["#e45756", "#54a24b", "#4c78a8"]

FUENTE_EJEMPLO = "Ejemplo del curso"
FUENTE_SUBIDA = "Subir una imagen"

EJES_VOLTEO = {"horizontal (h)": "h", "vertical (v)": "v"}

# El orden de esta tupla es solo el orden en que aparecen en el menú: el orden
# de aplicación lo decide quien usa la app al seleccionarlas.
OPERACIONES = (
    "Negativo",
    "Escala de grises",
    "Canal",
    "Volteo",
    "Convolución",
    "Suma",
    "Resta",
    "Multiplicación",
    "Mezcla con otra imagen",
    "Saturación",
    "Contraste",
)

# Estado inicial de cada control. El botón "Reiniciar" restaura exactamente
# este diccionario, así que agregar un control aquí basta para que el botón
# también lo cubra.
VALORES_INICIALES = {
    "fuente": FUENTE_EJEMPLO,
    "imagen_ejemplo": IMAGENES_PREDEFINIDAS[0],
    "operaciones": [],
    "canal": "r",
    "volteo": "horizontal (h)",
    "kernel": None,
    "sumando": 0,
    "suma_por_la_derecha": False,
    "sustraendo": 0,
    "resta_por_la_derecha": False,
    "factor": 1.0,
    "imagen_mezcla": IMAGENES_PREDEFINIDAS[1],
    "operador_mezcla": "+",
    "saturacion": 1.0,
    "contraste": 0.0,
    "histograma_log": False,
}

# Qué controles pertenecen a cada operación. Sirve para el botón de reinicio
# individual que acompaña a cada bloque de parámetros. "Negativo" y "Escala de
# grises" no aparecen porque no tienen nada que configurar.
PARAMETROS = {
    "Canal": ["canal"],
    "Volteo": ["volteo"],
    "Convolución": ["kernel"],
    "Suma": ["sumando", "suma_por_la_derecha"],
    "Resta": ["sustraendo", "resta_por_la_derecha"],
    "Multiplicación": ["factor"],
    "Mezcla con otra imagen": ["imagen_mezcla", "operador_mezcla"],
    "Saturación": ["saturacion"],
    "Contraste": ["contraste"],
}


# --- Utilidades de la app ---------------------------------------------------
# Nada de lo que sigue forma parte del proyecto: son ayudas de la interfaz.


@st.cache_data(show_spinner=False)
def cargar_ejemplo(nombre: str) -> np.ndarray:
    """Lee una imagen de ``data/`` y la deja en caché entre reruns."""
    return cargar_imagen(RUTA_DATOS / nombre)


def kernels_disponibles() -> tuple[dict[str, np.ndarray], str | None]:
    """Entrega los kernels de ``src/pixellab/kernels.py`` y un aviso si faltan.

    La app usa los kernels que escriben los estudiantes en la Etapa 6, no una
    copia propia: así el trabajo de esa etapa se ve funcionando.
    """
    if KERNELS is None:
        return {}, (
            "Todavía no existe `src/pixellab/kernels.py` (Etapa 6). "
            "Cuando lo creen, sus kernels aparecerán acá."
        )
    try:
        kernels = dict(KERNELS)
    except (TypeError, ValueError):
        return {}, (
            "`KERNELS` no tiene el formato pedido: debe ser una lista de "
            "tuplas `(nombre, kernel)`."
        )
    if not kernels:
        return {}, "`KERNELS` está vacío: la Etapa 6 pide al menos 5 kernels."
    return kernels, None


def a_uint8(arreglo: np.ndarray) -> np.ndarray:
    """Deja el arreglo listo para ``st.image`` sin tocar la librería."""
    return np.clip(np.asarray(arreglo), 0, 255).astype("uint8")


def png_en_bytes(arreglo: np.ndarray) -> bytes:
    """Serializa el resultado como PNG para el botón de descarga."""
    buffer = io.BytesIO()
    Image.fromarray(a_uint8(arreglo)).save(buffer, format="PNG")
    return buffer.getvalue()


def histograma(arreglo: np.ndarray) -> pd.DataFrame:
    """Cuenta cuántos píxeles hay en cada intensidad, por canal."""
    valores = a_uint8(arreglo)
    conteos = {
        canal: np.bincount(valores[:, :, i].ravel(), minlength=256)
        for i, canal in enumerate(CANALES)
    }
    return pd.DataFrame(conteos, index=pd.RangeIndex(256, name="Intensidad"))


def grafico_histograma(arreglo: np.ndarray, logaritmica: bool) -> alt.Chart:
    """Dibuja el histograma por canal.

    Una sola intensidad puede concentrar toda la imagen: por ejemplo,
    ``get_channel(img, "r")`` deja los canales verde y azul completos en 0, y
    ese bin vale alto x ancho (651.750 píxeles en ``gato1.jpg``). En escala
    lineal ese pico aplasta el resto de la curva, así que la escala
    logarítmica —``symlog``, que sí admite el valor 0— permite ver las dos
    cosas a la vez.
    """
    datos = (
        histograma(arreglo)
        .reset_index()
        .melt(id_vars="Intensidad", var_name="Canal", value_name="Píxeles")
    )
    if logaritmica:
        # `symlog` reparte el eje por órdenes de magnitud, así que las marcas
        # útiles son las potencias de 10 (más el 0, que sí admite).
        maximo = int(datos["Píxeles"].max())
        escala = alt.Scale(type="symlog")
        eje = alt.Axis(values=[0, *(10**k for k in range(1, len(str(maximo))))])
    else:
        escala = alt.Scale(type="linear")
        eje = alt.Axis()

    return (
        alt.Chart(datos)
        .mark_line(interpolate="step")
        .encode(
            x=alt.X("Intensidad:Q", scale=alt.Scale(domain=[0, 255])),
            y=alt.Y("Píxeles:Q", scale=escala, axis=eje),
            color=alt.Color(
                "Canal:N",
                scale=alt.Scale(domain=list(CANALES), range=COLORES_CANAL),
            ),
        )
        .properties(height=260)
    )


def estadisticas(arreglo: np.ndarray) -> pd.DataFrame:
    """Resume cada canal reduciendo sobre los ejes de filas y columnas.

    Todas las columnas salen de una reducción con ``axis=(0, 1)``: se agrega
    sobre alto y ancho, y queda un valor por canal.
    """
    valores = np.asarray(arreglo)
    return pd.DataFrame(
        {
            "Mínimo": valores.min(axis=(0, 1)),
            "Máximo": valores.max(axis=(0, 1)),
            "Media": valores.mean(axis=(0, 1)).round(2),
            "Desv. est.": valores.std(axis=(0, 1)).round(2),
            "% en 0": (valores <= 0).mean(axis=(0, 1)).round(4) * 100,
            "% en 255": (valores >= 255).mean(axis=(0, 1)).round(4) * 100,
        },
        index=list(CANALES),
    )


def valor_inicial(clave: str):
    """Valor por defecto efectivo de un control.

    Coincide con ``VALORES_INICIALES`` salvo para el kernel: ahí el inicial es
    ``None`` porque los nombres los eligen los estudiantes, y el control se
    resuelve al primero de su lista.
    """
    if clave == "kernel" and KERNELS_APP:
        return next(iter(KERNELS_APP))
    return VALORES_INICIALES[clave]


def valor(clave: str):
    """Lee un control, incluso si todavía no se ha dibujado en el sidebar.

    Los controles de parámetros aparecen solo cuando su operación está en el
    pipeline, así que su llave puede no existir en ``st.session_state``.
    """
    return st.session_state.get(clave, VALORES_INICIALES[clave])


def reiniciar_claves(claves: list[str]) -> None:
    """Devuelve un grupo de controles a su valor inicial.

    Borra las llaves en vez de reasignarlas: al desaparecer del estado, cada
    widget vuelve a tomar el valor por defecto con el que fue declarado.
    """
    for clave in claves:
        st.session_state.pop(clave, None)


def reiniciar() -> None:
    """Devuelve todos los controles a su estado inicial."""
    reiniciar_claves(list(VALORES_INICIALES))
    # Cambiarle la llave al file_uploader es la forma de vaciarlo.
    st.session_state["carga_id"] = st.session_state.get("carga_id", 0) + 1


def mover(operacion: str, desplazamiento: int) -> None:
    """Cambia de lugar una operación dentro del pipeline.

    Se ejecuta como callback, es decir antes de que el script vuelva a
    correr: por eso puede escribir sobre la llave del ``multiselect``.
    """
    orden = list(st.session_state["operaciones"])
    origen = orden.index(operacion)
    destino = origen + desplazamiento
    if 0 <= destino < len(orden):
        orden[origen], orden[destino] = orden[destino], orden[origen]
        st.session_state["operaciones"] = orden


def encabezado_tarjeta(operacion: str, posicion: int, total: int) -> None:
    """Título de la tarjeta con los controles para subirla o bajarla."""
    with st.container(horizontal=True, vertical_alignment="center"):
        st.markdown(f"**{posicion + 1}. {operacion}**")
        st.button(
            ":material/keyboard_arrow_up:",
            key=f"sube_{operacion}",
            on_click=mover,
            args=(operacion, -1),
            disabled=posicion == 0,
            type="tertiary",
            help=f"Aplicar {operacion} antes.",
        )
        st.button(
            ":material/keyboard_arrow_down:",
            key=f"baja_{operacion}",
            on_click=mover,
            args=(operacion, 1),
            disabled=posicion == total - 1,
            type="tertiary",
            help=f"Aplicar {operacion} después.",
        )


def boton_reinicio(operacion: str) -> None:
    """Dibuja el botón que reinicia solo los parámetros de una operación.

    Queda deshabilitado cuando ya están en su valor inicial, para que se vea
    de un vistazo si esa operación fue configurada o no.
    """
    claves = PARAMETROS[operacion]
    sin_cambios = all(valor(clave) == valor_inicial(clave) for clave in claves)
    st.button(
        "Restablecer",
        icon=":material/restart_alt:",
        type="tertiary",
        key=f"reinicio_{operacion}",
        on_click=reiniciar_claves,
        args=(claves,),
        disabled=sin_cambios,
        help=f"Devuelve los parámetros de {operacion} a su valor inicial.",
    )


# --- Estado -----------------------------------------------------------------
st.set_page_config(page_title="PixelLab", page_icon="🎨", layout="wide")

st.session_state.setdefault("carga_id", 0)

st.title("PixelLab 🎨")
st.caption(
    "Prueben en vivo su librería de procesamiento de imágenes con NumPy."
)

if Imagen is None:
    st.error(
        "No se pudo importar `Imagen` desde `src/pixellab/imagen.py`. "
        "Completen la Etapa 2 y ejecuten la app desde la carpeta `Lab3Tarea`."
    )
    st.stop()

KERNELS_APP, AVISO_KERNELS = kernels_disponibles()
LIB = LibImagen() if LibImagen is not None else None


# --- Controles --------------------------------------------------------------
with st.sidebar:
    st.button(
        "Reiniciar todo",
        icon=":material/refresh:",
        on_click=reiniciar,
        width="stretch",
        help="Devuelve todos los controles a su estado inicial.",
    )

    st.subheader("Imagen")
    fuentes = [FUENTE_EJEMPLO, FUENTE_SUBIDA]
    st.radio(
        "Origen",
        fuentes,
        index=fuentes.index(VALORES_INICIALES["fuente"]),
        key="fuente",
    )

    subida = None
    if valor("fuente") == FUENTE_EJEMPLO:
        st.selectbox(
            "Archivo",
            IMAGENES_PREDEFINIDAS,
            index=IMAGENES_PREDEFINIDAS.index(
                VALORES_INICIALES["imagen_ejemplo"]
            ),
            key="imagen_ejemplo",
        )
    else:
        archivo = st.file_uploader(
            "Imagen propia",
            type=["jpg", "jpeg", "png"],
            key=f"archivo_{st.session_state['carga_id']}",
        )
        if archivo is None:
            st.caption(f"Sin archivo: se usa `{valor('imagen_ejemplo')}`.")
        else:
            try:
                subida = np.array(
                    Image.open(archivo).convert("RGB"), dtype="int"
                )
            except Exception as error:
                st.error(f"No se pudo leer el archivo subido: {error}")

    st.subheader("Pipeline")
    # Sin `default`: los botones de orden escriben esta llave desde un
    # callback, y mezclar ambas fuentes provoca un aviso de Streamlit. El
    # valor inicial (la lista vacía) es el que el widget toma por su cuenta.
    seleccionadas = st.multiselect(
        "Operaciones a aplicar",
        OPERACIONES,
        key="operaciones",
        placeholder="Sin operaciones (resultado = original)",
        help=(
            "Se aplican en el orden en que las seleccionen, y ese orden se "
            "cambia con las flechas de cada tarjeta. El orden importa: "
            "comparen negativo → canal contra canal → negativo."
        ),
    )

    # Una tarjeta por operación, en el orden en que se aplican. La tienen
    # todas, incluso las que no configuran nada, porque en el encabezado están
    # los controles para cambiarlas de lugar.
    if seleccionadas:
        st.caption("Orden de aplicación")

    for posicion, operacion in enumerate(seleccionadas):
        with st.container(border=True):
            encabezado_tarjeta(operacion, posicion, len(seleccionadas))

            if operacion == "Canal":
                canales_rgb = ["r", "g", "b"]
                st.selectbox(
                    "Canal a conservar",
                    canales_rgb,
                    index=canales_rgb.index(VALORES_INICIALES["canal"]),
                    key="canal",
                )

            elif operacion == "Volteo":
                ejes = list(EJES_VOLTEO)
                st.selectbox(
                    "Eje del volteo",
                    ejes,
                    index=ejes.index(VALORES_INICIALES["volteo"]),
                    key="volteo",
                )

            elif operacion == "Convolución":
                if not KERNELS_APP:
                    st.warning(AVISO_KERNELS)
                    continue
                # Los nombres de los kernels los deciden los estudiantes, así
                # que el inicial es simplemente el primero de su lista.
                st.selectbox("Kernel", list(KERNELS_APP), index=0, key="kernel")

            elif operacion == "Suma":
                st.slider(
                    "Sumar escalar",
                    0,
                    255,
                    VALORES_INICIALES["sumando"],
                    key="sumando",
                )
                st.checkbox(
                    "Sumar por la derecha: `escalar + imagen`",
                    value=VALORES_INICIALES["suma_por_la_derecha"],
                    key="suma_por_la_derecha",
                    help="Usa `__radd__`. La suma es conmutativa.",
                )

            elif operacion == "Resta":
                st.slider(
                    "Restar escalar",
                    0,
                    255,
                    VALORES_INICIALES["sustraendo"],
                    key="sustraendo",
                )
                st.checkbox(
                    "Restar por la derecha: `escalar - imagen`",
                    value=VALORES_INICIALES["resta_por_la_derecha"],
                    key="resta_por_la_derecha",
                    help=(
                        "Usa `__rsub__`. La resta NO es conmutativa: comparen "
                        "el resultado con la casilla marcada y sin marcar."
                    ),
                )

            elif operacion == "Multiplicación":
                st.slider(
                    "Multiplicar escalar",
                    0.0,
                    2.0,
                    VALORES_INICIALES["factor"],
                    key="factor",
                )

            elif operacion == "Mezcla con otra imagen":
                st.selectbox(
                    "Segunda imagen",
                    IMAGENES_PREDEFINIDAS,
                    index=IMAGENES_PREDEFINIDAS.index(
                        VALORES_INICIALES["imagen_mezcla"]
                    ),
                    key="imagen_mezcla",
                )
                st.segmented_control(
                    "Operador",
                    ["+", "-", "*"],
                    default=VALORES_INICIALES["operador_mezcla"],
                    key="operador_mezcla",
                    help=(
                        "Operar dos `Imagen` exige que sus dimensiones "
                        "calcen. Las tres fotos tienen tamaños distintos: "
                        "prueben mezclar dos diferentes y lean el error."
                    ),
                )

            elif operacion == "Saturación":
                st.slider(
                    "Ajuste de saturación",
                    -1.0,
                    3.0,
                    VALORES_INICIALES["saturacion"],
                    key="saturacion",
                )

            elif operacion == "Contraste":
                st.slider(
                    "Ajuste de contraste",
                    -100.0,
                    100.0,
                    VALORES_INICIALES["contraste"],
                    key="contraste",
                )

            if operacion in PARAMETROS:
                boton_reinicio(operacion)


# --- Procesamiento ----------------------------------------------------------
if subida is not None:
    arreglo = subida
else:
    arreglo = cargar_ejemplo(valor("imagen_ejemplo"))

imagen_original = Imagen(arreglo)


def exigir_lib() -> LibImagen:
    """Falla con un mensaje claro si `LibImagen` todavía no existe."""
    if LIB is None:
        raise NotImplementedError(
            "Aún no existe `LibImagen` en src/pixellab/procesamiento.py "
            "(Etapas 4 a 6)."
        )
    return LIB


def op_convolucion(img: Imagen) -> Imagen:
    nombre = valor("kernel")
    if not KERNELS_APP or nombre not in KERNELS_APP:
        raise NotImplementedError(
            "No hay kernels disponibles en `src/pixellab/kernels.py` (Etapa 6)."
        )
    return exigir_lib().conv_channel(img, KERNELS_APP[nombre])


def op_mezcla(img: Imagen) -> Imagen:
    otra = Imagen(cargar_ejemplo(valor("imagen_mezcla")))
    operador = valor("operador_mezcla")
    if operador == "+":
        return img + otra
    if operador == "-":
        return img - otra
    return img * otra


# Cada operación es una función `Imagen -> Imagen`. Las que usan escalares
# ejercitan los dunders de `Imagen`; el resto delega en `LibImagen`.
IMPLEMENTACIONES = {
    "Negativo": lambda img: exigir_lib().to_negative(img),
    "Escala de grises": lambda img: exigir_lib().to_gray(img),
    "Canal": lambda img: exigir_lib().get_channel(img, valor("canal")),
    "Volteo": lambda img: exigir_lib().flip(img, EJES_VOLTEO[valor("volteo")]),
    "Convolución": op_convolucion,
    "Suma": lambda img: (
        valor("sumando") + img
        if valor("suma_por_la_derecha")
        else img + valor("sumando")
    ),
    "Resta": lambda img: (
        valor("sustraendo") - img
        if valor("resta_por_la_derecha")
        else img - valor("sustraendo")
    ),
    "Multiplicación": lambda img: img * valor("factor"),
    "Mezcla con otra imagen": op_mezcla,
    "Saturación": lambda img: exigir_lib().set_saturation(
        img, valor("saturacion")
    ),
    "Contraste": lambda img: exigir_lib().set_contrast(img, valor("contraste")),
}

imagen = imagen_original
traza: list[tuple[str, bool, str]] = []

for nombre in seleccionadas:
    try:
        imagen = IMPLEMENTACIONES[nombre](imagen)
    except Exception as error:
        # Se atrapa cualquier excepción a propósito: una etapa a medio hacer
        # debe producir un aviso, no tumbar la app.
        traza.append((nombre, False, f"{type(error).__name__}: {error}"))
    else:
        traza.append((nombre, True, ""))


# --- Salida -----------------------------------------------------------------
def describir(img: Imagen) -> str:
    alto, ancho, canales = img.imagen.shape
    peso = img.imagen.nbytes / 1e6
    return (
        f"{alto} x {ancho} x {canales} · `{img.imagen.dtype}` · {peso:.1f} MB"
    )


# Ancho fijo de previsualización: deja las dos imágenes lado a lado y el
# estado del pipeline visible sin tener que hacer scroll. La descarga entrega
# el resultado en su resolución original.
ANCHO_VISTA = 430

col_izq, col_der = st.columns(2)
with col_izq:
    st.subheader("Original")
    st.image(a_uint8(imagen_original.imagen), channels="RGB", width=ANCHO_VISTA)
    st.caption(describir(imagen_original))
with col_der:
    st.subheader("Resultado")
    st.image(a_uint8(imagen.imagen), channels="RGB", width=ANCHO_VISTA)
    st.caption(describir(imagen))
    st.download_button(
        "Descargar resultado",
        data=png_en_bytes(imagen.imagen),
        file_name="resultado.png",
        mime="image/png",
        icon=":material/download:",
    )

# Pipeline: qué se aplicó, en qué orden y qué falló. Va en un contenedor con
# borde porque es el feedback principal cuando algo de la librería falla.
fallidas = [(nombre, detalle) for nombre, ok, detalle in traza if not ok]

with st.container(border=True):
    if traza:
        pasos = " → ".join(
            f"{'✅' if aplicada else '⚠️'} {nombre}"
            for nombre, aplicada, _ in traza
        )
        st.markdown(f"**Pipeline:** `Original` → {pasos} → `Resultado`")
    else:
        st.markdown(
            "**Pipeline:** sin operaciones seleccionadas, el resultado es "
            "idéntico al original."
        )

    for nombre, detalle in fallidas:
        st.warning(f"**{nombre}** no se pudo aplicar — {detalle}")

    if seleccionadas and not fallidas:
        st.success("Todas las operaciones se aplicaron con su librería.")

if not np.issubdtype(np.asarray(imagen.imagen).dtype, np.integer):
    st.warning(
        f"El resultado quedó con `dtype` **{imagen.imagen.dtype}**, no "
        "entero. La Etapa 3 pide cerrar los operadores con `.astype(int)`: "
        "matplotlib y Streamlit interpretan los arreglos flotantes en el "
        "rango [0.0, 1.0], no [0, 255]. La app lo corrigió solo para poder "
        "dibujar la imagen."
    )

st.divider()

st.subheader("Histogramas por canal")
st.caption(
    "Cuántos píxeles hay en cada intensidad de 0 a 255. Las operaciones que "
    "saturan acumulan píxeles en los extremos: esa información no se "
    "recupera después."
)
st.checkbox(
    "Escala logarítmica en el eje vertical",
    value=VALORES_INICIALES["histograma_log"],
    key="histograma_log",
    help=(
        "Útil cuando una sola intensidad concentra casi todos los píxeles: "
        "por ejemplo, al conservar un canal los otros dos quedan enteros "
        "en 0 y su pico tapa el resto de la curva."
    ),
)
log = valor("histograma_log")

col_hist_izq, col_hist_der = st.columns(2)
with col_hist_izq:
    st.markdown("**Original**")
    st.altair_chart(
        grafico_histograma(imagen_original.imagen, log), width="stretch"
    )
with col_hist_der:
    st.markdown("**Resultado**")
    st.altair_chart(grafico_histograma(imagen.imagen, log), width="stretch")

with st.expander("Estadísticas por canal (reducciones con `axis=(0, 1)`)"):
    col_est_izq, col_est_der = st.columns(2)
    with col_est_izq:
        st.markdown("**Original**")
        st.dataframe(estadisticas(imagen_original.imagen))
    with col_est_der:
        st.markdown("**Resultado**")
        st.dataframe(estadisticas(imagen.imagen))

if "Convolución" in seleccionadas and KERNELS_APP:
    nombre_kernel = valor("kernel")
    if nombre_kernel in KERNELS_APP:
        st.subheader(f"Kernel `{nombre_kernel}`")
        st.caption(
            "Esta matriz sale de su `src/pixellab/kernels.py`. Cada píxel del "
            "resultado es la suma ponderada de sus vecinos usando estos pesos."
        )
        st.dataframe(
            pd.DataFrame(KERNELS_APP[nombre_kernel]),
            width=360,
            hide_index=True,
        )
