# Datos del Laboratorio 8

## Origen y licencia

Los dos archivos provienen del [Superheroes NLP Dataset](https://www.kaggle.com/datasets/jonathanbesomi/superheroes-nlp-dataset),
publicado en Kaggle por Jonathan Besomi con licencia **CC0: Public Domain**.
Sus autores lo obtuvieron de [superherodb](https://www.superherodb.com/). Es
un scrape: los valores son los que se publicaron en ese sitio, con sus
inconsistencias.

La partición en dos archivos viene de una edición anterior del curso, que usó
el mismo dataset:

| Archivo | Filas | Qué es |
| --- | ---: | --- |
| `catalogo.csv` | 1 367 | Catálogo con el que se construyen las representaciones. `name` es único. |
| `nuevos.csv` | 84 | Personajes que llegan después. Ningún nombre está en el catálogo. Trae una fila duplicada de forma exacta y dos filas sin `name`. |

Los CSV del laboratorio se adaptaron eliminando las 50 columnas `has_*`
precalculadas: cada CSV conserva las otras 32 columnas y todas sus filas
y valores originales. Los poderes se codifican durante el laboratorio desde
`superpowers`; el vocabulario se aprende solo del catálogo. El archivo
histórico en `src/old/` se conserva sin cambios.

No modificar estos archivos: las transformaciones se hacen en el notebook y en
`src/heroverse/`.

## Columnas usadas en el laboratorio

Se leen con el esquema que infiere Polars: los seis puntajes quedan como enteros,
las demás, salvo el índice, como texto. La primera
columna, sin nombre, es ese índice, heredado de la edición anterior; no
identifica al personaje.

| Columna | Contenido |
| --- | --- |
| `name` | Nombre del personaje en superherodb; identifica una fila. |
| `intelligence_score`, `strength_score`, `speed_score`, `durability_score`, `power_score`, `combat_score` | Puntajes de 0 a 100. |
| `overall_score` | Puntaje global de superherodb. Trae `"-"` (sin dato) e `"∞"`. |
| `height` | Altura en dos unidades, como `"6'2 • 188 cm"` o `"49'2 • 15.0 meters"`; `"-"` si no hay dato. |
| `weight` | Peso en dos unidades, como `"198 lb • 89 kg"` o `"6,600 lb • 3.0 tons"`; `"-"` si no hay dato. |
| `first_appearance` | Primera publicación; a veces incluye el año entre paréntesis. |
| `creator` | Editorial o franquicia (`Marvel Comics`, `DC Comics`, `Shueisha`, …). |
| `alignment` | `Good`, `Bad` o `Neutral`. Vacía en `nuevos.csv`. |
| `gender`, `type_race`, `eye_color`, `hair_color` | Categóricas con nulos. |
| `superpowers` | Lista de poderes serializada como texto, por ejemplo `"['Flight', 'Super Strength']"`. |
| `powers_text` | Descripción de los poderes, en inglés. |
| `history_text` | Historia del personaje, en inglés. |
