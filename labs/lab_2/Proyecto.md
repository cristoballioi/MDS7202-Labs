# Mini Proyecto: AgroAlerta

**IA7202: Laboratorio de Programación Científica para Ciencia de Datos**

Este documento contiene las instrucciones prácticas del mini proyecto. Avancen
con el notebook: cuando aparezca una alerta del mini proyecto, completen la
etapa correspondiente y vuelvan al notebook.

## Objetivo

Construir un programa que analice las mediciones de una estación meteorológica
agrícola. La estación tiene tres sensores:

| Sensor | Condición de riesgo | Unidad |
|---|---|---|
| Temperatura | bajo 0 °C o sobre 40 °C | °C |
| Viento | sobre 25 km/h | km/h |
| Humedad | sobre 85 % | % |

El programa recibe una fecha, revisa las mediciones de ese día y cuenta las
situaciones de riesgo por sensor.

```bash
uv run python main.py --fecha 2026-06-15
```

```text
Estación Parcela Norte — 2026-06-15
Temperatura    3 lecturas en riesgo
Viento         2 lecturas en riesgo
Humedad        5 lecturas en riesgo

Total: 10 situaciones de riesgo
```

> 📊 **Evaluación**
>
> El mini proyecto tiene un máximo de **6,0 puntos**. La nota se calcula como
> `nota = 1,0 + puntaje obtenido`: 0,0 puntos corresponden a nota 1,0 y
> 6,0 puntos corresponden a nota 7,0.

| Etapa | Contenido | Puntaje |
|---|---|---:|
| 1 | Estructura del proyecto | 0,4 |
| 2 | Clase `Sensor` | 0,6 |
| 3 | Herencia y sensores concretos | 1,2 |
| 4 | Abstracción, encapsulación y propiedades | 1,2 |
| 5 | Polimorfismo y reporte | 1,4 |
| 6 | Orquestador | 0,3 |
| 7 | Pruebas automáticas | 0,3 |
| Salida | Preguntas de comprensión | 0,6 |
| **Total** |  | **6,0** |

## Archivos del proyecto

La estructura relevante debe quedar así:

```text
data/
└── lecturas.csv

src/agroalerta/
├── __init__.py
├── datos.py          # entregado; no modificar
├── sensores.py
└── reporte.py

tests/
└── test_sensores.py

main.py
```

El archivo `lecturas.csv` contiene las columnas `fecha`, `hora`,
`sensor` y `valor`. `datos.py` entrega la función `cargar_lecturas`,
que agrupa las mediciones por sensor para una fecha. No modifiquen ese archivo.

> 📌 **Idea clave**
>
> Un umbral de riesgo indica cuándo el cultivo está en peligro; no dice nada
> sobre el clima "normal". Por ejemplo, `-2 °C` es una temperatura perfectamente
> corriente en invierno y, aun así, es riesgosa para el cultivo.

## Etapa 1 — Estructura del proyecto (0,4 puntos)

Prepare el proyecto:

- cree `src/agroalerta/`, `tests/` y `data/`;
- cree `src/agroalerta/__init__.py`;
- copie `datos.py` y `lecturas.csv` desde el material entregado;
- mantenga `main.py` ejecutable;
- no modifique `datos.py`.

> 🧪 **Comprobación**
>
> Ejecute `uv run python main.py`. El programa debe iniciar sin errores.

## Etapa 2 — La clase `Sensor` (0,6 puntos)

En `src/agroalerta/sensores.py`, cree una clase `Sensor` que:

- reciba `nombre` y `unidad` en el constructor;
- guarde ambos valores como atributos;
- defina `es_riesgo(valor)` con type hints;
- devuelva temporalmente `False` desde `es_riesgo`.

## Etapa 3 — Herencia y sensores concretos (1,2 puntos)

Cree tres subclases de `Sensor`:

| Clase | Constructor | Nombre y unidad | Regla de riesgo |
|---|---|---|---|
| `SensorTemperatura` | `(minimo, maximo)` | `temperatura`, `°C` | `valor < minimo` o `valor > maximo` |
| `SensorViento` | `(maximo)` | `viento`, `km/h` | `valor > maximo` |
| `SensorHumedad` | `(maximo)` | `humedad`, `%` | `valor > maximo` |

Cada subclase debe:

- heredar de `Sensor`;
- llamar a `super().__init__`;
- recibir sus umbrales por el constructor;
- guardar los umbrales como atributos;
- sobrescribir `es_riesgo`.

Los ejemplos del proyecto usarán esta configuración:

```python
SensorTemperatura(0, 40)
SensorViento(25)
SensorHumedad(85)
```

Valores de referencia:

| Sensor | Normal | Riesgoso |
|---|---|---|
| Temperatura | `18 °C` | `-2 °C`, `42 °C` |
| Viento | `10 km/h` | `30 km/h` |
| Humedad | `70 %` | `90 %` |

> ⚠️ **Aviso**
>
> Para la temperatura se usa `or`, no `and`: una temperatura puede ser
> riesgosa por estar demasiado baja o demasiado alta.

## Etapa 4 — Abstracción y encapsulación (0,6 puntos)

Mejore las clases anteriores:

- haga que `Sensor` herede de `ABC`;
- marque `es_riesgo` como método abstracto;
- renombre los umbrales a `_minimo` y `_maximo`;

> ❓ **Pregunta para el notebook**
>
> ¿Qué comunica el prefijo `_` si todavía es posible acceder al atributo desde
> fuera de la clase?

## Etapa 5 — Polimorfismo y reporte (2 puntos)

Cree `src/agroalerta/reporte.py` con:

```python
def contar_riesgos(sensores, lecturas):
    ...
```

La función recibe:

- una lista de objetos sensor;
- un diccionario como `{"temperatura": [2.1, -1.2], ...}`.

Debe devolver un diccionario con una entrada por sensor:

```python
conteo = contar_riesgos(sensores, lecturas)
# {"temperatura": 3, "viento": 2, "humedad": 5}
```

La función debe recorrer la lista y llamar a `sensor.es_riesgo(valor)`. No debe
usar `isinstance` ni tener una condición distinta para cada tipo de sensor.

Si un sensor no tiene lecturas para esa fecha, su conteo debe ser `0`.

> 📌 **Idea clave**
>
> El reporte trabaja con el comportamiento común de los sensores. Cada objeto
> conoce su propia regla de riesgo.

> ❓ **Pregunta para el notebook**
>
> Si se agrega un sensor de lluvia, ¿qué archivo debe modificarse y qué parte
> de `contar_riesgos` debería permanecer intacta?

## Etapa 6 — Orquestador (0,3 puntos)

Complete `main.py` para que coordine las piezas del proyecto:

- cree los tres sensores con los umbrales de AgroAlerta;
- lea la fecha recibida mediante `--fecha`;
- use `cargar_lecturas`;
- llame a `contar_riesgos`;
- muestre el reporte.


El siguiente código puede ser de utilidad para parsear la fecha del argumento (`argparse` es el módulo estándar para leer argumentos de la línea de comandos.):

```python
import argparse


def main():
    parser = argparse.ArgumentParser(description="AgroAlerta")
    parser.add_argument("--fecha", default="2026-06-15")
    args = parser.parse_args()
```




> 🧪 **Comprobación**
>
> `2026-06-15` debe producir `3`, `2`, `5` y total `10`. `2026-06-16` debe
> producir `0`, `4`, `2` y total `6`. Si ambas fechas dan lo mismo, no están
> usando el argumento `--fecha`.

## Etapa 7 — Pruebas automáticas (0,3 puntos)

> 📖 **Definición**
>
> El *testing* es el proceso de ejecutar comprobaciones para detectar si el
> código cumple el comportamiento esperado. El *testing unitario* prueba una
> pieza pequeña y aislada, como una función o un método. En Python, `assert`
> verifica que una condición sea verdadera: si la condición es falsa, la
> prueba falla.

Cree `tests/test_sensores.py` con al menos estas pruebas:

1. Una temperatura bajo cero es riesgosa.
2. Una temperatura templada no es riesgosa.
3. Un viento normal no es riesgoso.
4. `contar_riesgos` devuelve el conteo esperado para un conjunto pequeño de
   lecturas escrito a mano en la prueba.

Los nombres del archivo y de las funciones deben comenzar con `test_`.
En cada prueba use `assert` para expresar el resultado esperado. Una prueba no
debe limitarse a ejecutar el código: debe afirmar qué resultado se esperaba.

> 🧪 **Comprobación**
>
> Ejecute `uv run pytest` y confirme que todas las pruebas pasan.

## Preguntas de salida (0,6 puntos)

Responda en el notebook las tres preguntas marcadas como preguntas de salida.
Cada una vale `0,2` puntos. Dos se responden sobre el mini proyecto y la
tercera, sobre excepciones, se resuelve completamente dentro del notebook. Se
evaluará la comprensión de la idea, no la redacción exacta de la respuesta.

## Verificación final

Desde la raíz del proyecto, ejecute:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run python main.py --fecha 2026-06-15
uv run python main.py --fecha 2026-06-16
```

El formato exacto del texto del reporte no es obligatorio. Sí deben ser
correctos los conteos y el uso de la fecha.

## Entrega

Entregue el notebook completado y los archivos del mini proyecto:

- `src/agroalerta/` implementado;
- `main.py` funcionando;
- `tests/test_sensores.py` con las pruebas solicitadas;
- `data/lecturas.csv` en su lugar;
- respuestas a las tres preguntas de salida del notebook (0,6 puntos).
