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

El programa recibe una fecha, valida las mediciones y cuenta las situaciones de
riesgo por sensor.

```bash
uv run python main.py --fecha 2026-06-15
```

```text
Estación Parcela Norte — 2026-06-15
Temperatura    3 lecturas en riesgo
Viento         2 lecturas en riesgo
Humedad        5 lecturas en riesgo

Descartadas: 2 lecturas inválidas
Total: 10 situaciones de riesgo
```

> 📊 **Evaluación**
>
> El mini proyecto tiene un máximo de **6,0 puntos**. La nota se calcula como
> `nota = 1,0 + puntaje obtenido`: 0,0 puntos corresponden a nota 1,0 y
> 6,0 puntos corresponden a nota 7,0.

| Etapa | Contenido | Puntaje |
|---|---|---:|
| 1 | Estructura del proyecto | 0,3 |
| 2 | Clase `Sensor` | 0,4 |
| 3 | Herencia y sensores concretos | 1,0 |
| 4 | Abstracción, encapsulación y propiedades | 1,0 |
| 5 | Polimorfismo y reporte | 1,1 |
| 6 | Validación y excepciones | 1,1 |
| 7 | Orquestador | 0,3 |
| 8 | Pruebas automáticas | 0,2 |
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
├── errores.py
├── sensores.py
└── reporte.py

tests/
└── test_sensores.py

main.py
```

El archivo `lecturas.csv` contiene las columnas `fecha`, `hora`,
`sensor` y `valor`. `datos.py` entrega la función `cargar_lecturas`,
que agrupa las mediciones por sensor para una fecha. No modifiquen ese archivo.

> ⚠️ **Aviso**
>
> Un umbral de riesgo indica cuándo el cultivo está en peligro. Un rango físico
> indica cuándo una medición puede provenir de un sensor funcionando. No son la
> misma cosa: `-2 °C` es una medición válida, pero también es riesgosa.

El archivo contiene algunas mediciones físicamente imposibles. Estas deben
descartarse durante la etapa de validación.

## Etapa 1 — Estructura del proyecto (0,3 puntos)

Prepare el proyecto:

- cree `src/agroalerta/`, `tests/` y `data/`;
- cree `src/agroalerta/__init__.py`;
- copie `datos.py` y `lecturas.csv` desde el material entregado;
- mantenga `main.py` ejecutable;
- no modifique `datos.py`.

> 🧪 **Comprobación**
>
> Ejecute `uv run python main.py`. El programa debe iniciar sin errores.

## Etapa 2 — La clase `Sensor` (0,4 puntos)

En `src/agroalerta/sensores.py`, cree una clase `Sensor` que:

- reciba `nombre` y `unidad` en el constructor;
- guarde ambos valores como atributos;
- defina `es_riesgo(valor)` con type hints;
- devuelva temporalmente `False` desde `es_riesgo`.

## Etapa 3 — Herencia y sensores concretos (1,0 punto)

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

| Sensor | Normal | Riesgoso | Inválido |
|---|---|---|---|
| Temperatura | `18 °C` | `-2 °C`, `42 °C` | `-300 °C` |
| Viento | `10 km/h` | `30 km/h` | `250 km/h` |
| Humedad | `70 %` | `90 %` | `110 %` |

> ⚠️ **Aviso**
>
> Para la temperatura se usa `or`, no `and`: una temperatura puede ser
> riesgosa por estar demasiado baja o demasiado alta.

## Etapa 4 — Abstracción, encapsulación y propiedades (1,0 punto)

Mejore las clases anteriores:

- haga que `Sensor` herede de `ABC`;
- marque `es_riesgo` como método abstracto;
- renombre los umbrales a `_minimo` y `_maximo`;
- agregue la propiedad `rango_seguro`.

La propiedad debe producir un texto coherente para ambos casos:

- sensores con mínimo y máximo: `entre 0 y 40 °C`;
- sensores con un solo extremo: por ejemplo, `bajo 25 km/h`.

> 🧪 **Comprobación**
>
> `SensorTemperatura(0, 40).rango_seguro` debe describir el rango y
> `Sensor("generico", "unidades")` debe producir `TypeError` después de hacer
> abstracta la clase base.

> ❓ **Pregunta para el notebook**
>
> ¿Qué comunica el prefijo `_` si todavía es posible acceder al atributo desde
> fuera de la clase?

## Etapa 5 — Polimorfismo y reporte (1,1 puntos)

Cree `src/agroalerta/reporte.py` con:

```python
def contar_riesgos(sensores, lecturas):
    ...
```

La función recibe:

- una lista de objetos sensor;
- un diccionario como `{"temperatura": [2.1, -1.2], ...}`.

Debe devolver dos valores:

```python
conteo, descartadas = contar_riesgos(sensores, lecturas)
```

En esta etapa, antes de agregar la validación, `descartadas` puede ser siempre
cero. El conteo debe tener una entrada por sensor.

La función debe recorrer la lista y llamar a `sensor.es_riesgo(valor)`. No debe
usar `isinstance` ni tener una condición distinta para cada tipo de sensor.

> 📌 **Idea clave**
>
> El reporte trabaja con el comportamiento común de los sensores. Cada objeto
> conoce su propia regla de riesgo.

> ❓ **Pregunta para el notebook**
>
> Si se agrega un sensor de lluvia, ¿qué archivo debe modificarse y qué parte
> de `contar_riesgos` debería permanecer intacta?

## Etapa 6 — Validación y excepciones (1,1 puntos)

Cree `src/agroalerta/errores.py` con estas excepciones:

```python
class LecturaInvalidaError(Exception):
    """El valor medido es físicamente imposible."""


class DatosInsuficientesError(Exception):
    """No hay suficientes lecturas para concluir algo."""
```

Agregue a `Sensor` un método `validar(valor)` que levante
`LecturaInvalidaError` fuera de estos rangos físicos:

| Sensor | Rango físicamente posible |
|---|---|
| Temperatura | −50 a 60 °C |
| Viento | 0 a 200 km/h |
| Humedad | 0 a 100 % |

Además:

- use `try`/`except LecturaInvalidaError` en `contar_riesgos`;
- descarte las lecturas inválidas sin detener todo el programa;
- cuente las lecturas descartadas;
- levante `DatosInsuficientesError` si un sensor tiene menos de 20 lecturas
  válidas.

> ⚠️ **Aviso**
>
> Una lectura puede ser válida y riesgosa al mismo tiempo. Por ejemplo, `-2 °C`
> está dentro del rango físico de la temperatura, pero activa el riesgo de
> helada.

> ❓ **Pregunta para el notebook**
>
> ¿Por qué “no hay suficientes datos” no debe confundirse con “hubo cero
> situaciones de riesgo”?

## Etapa 7 — Orquestador (0,3 puntos)

Complete `main.py` para que coordine las piezas del proyecto:

- cree los tres sensores con los umbrales de AgroAlerta;
- lea la fecha recibida mediante `--fecha`;
- use `cargar_lecturas`;
- llame a `contar_riesgos`;
- muestre el reporte.

La infraestructura de línea de comandos y la función de impresión pueden
entregarse como código inicial. El objetivo de esta etapa es conectar los
módulos, no implementar un parser desde cero.

> 🧪 **Comprobación**
>
> `2026-06-15` debe producir `3`, `2`, `5`, `2` lecturas descartadas y
> total `10`. `2026-06-16` debe producir `0`, `4`, `2`, `1` lectura
> descartada y total `6`.

## Etapa 8 — Pruebas automáticas (0,2 puntos)

> 📖 **Definición**
>
> El *testing* es el proceso de ejecutar comprobaciones para detectar si el
> código cumple el comportamiento esperado. El *testing unitario* prueba una
> pieza pequeña y aislada, como una función o un método. En Python, `assert`
> verifica que una condición sea verdadera: si la condición es falsa, la
> prueba falla.

Cree `tests/test_sensores.py` con al menos estas pruebas:

1. Una temperatura bajo cero es riesgosa.
2. Un viento normal no es riesgoso.
3. Una lectura físicamente imposible levanta `LecturaInvalidaError`.
4. Menos de 20 lecturas válidas levanta `DatosInsuficientesError`.

Los nombres del archivo y de las funciones deben comenzar con `test_`.
En cada prueba use `assert` para expresar el resultado esperado. Para los casos
que deben fallar, use `pytest.raises(...)` y compruebe la excepción específica.

> 🧪 **Comprobación**
>
> Ejecute `uv run pytest` y confirme que todas las pruebas pasan.

## Preguntas de salida (0,6 puntos)

Responda en el notebook las tres preguntas marcadas como preguntas de salida.
Cada una vale `0,2` puntos. Se evaluará la comprensión de la idea, no la
redacción exacta de la respuesta.

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
correctos los conteos, las lecturas descartadas y el uso de la fecha.

## Entrega

Entregue el notebook completado y los archivos del mini proyecto:

- `src/agroalerta/` implementado;
- `main.py` funcionando;
- `tests/test_sensores.py` con las pruebas solicitadas;
- `data/lecturas.csv` en su lugar;
- respuestas a las tres preguntas de salida del notebook (0,6 puntos).
