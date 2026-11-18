# Datos crudos

`water_potability.csv` reúne nueve mediciones fisicoquímicas de 3 276 muestras
de agua y una etiqueta de potabilidad.

## Origen y licencia

- Fuente: conjunto de datos «Water Potability», publicado en Kaggle por Aditya
  Kadiwal (<https://www.kaggle.com/datasets/adityakadiwal/water-potability>).
  Los términos de uso están en la página del conjunto.

## Esquema

| Columna | Unidad | Descripción | Valores ausentes |
| --- | --- | --- | --- |
| `ph` | pH | Acidez del agua, de 0 a 14 | 491 |
| `Hardness` | mg/L | Dureza: sales de calcio y magnesio disueltas | 0 |
| `Solids` | ppm | Sólidos totales disueltos | 0 |
| `Chloramines` | ppm | Cloraminas, usadas como desinfectante | 0 |
| `Sulfate` | mg/L | Sulfatos disueltos | 781 |
| `Conductivity` | μS/cm | Conductividad eléctrica | 0 |
| `Organic_carbon` | ppm | Carbono orgánico total | 0 |
| `Trihalomethanes` | μg/L | Subproductos de la cloración | 162 |
| `Turbidity` | NTU | Turbidez: qué tan turbia se ve el agua | 0 |
| `Potability` | 0 o 1 | 1 si el agua es potable, 0 si no lo es | 0 |

Los valores ausentes están vacíos en el CSV. El archivo se trata como inmutable:
no se edita ni se reemplaza.
