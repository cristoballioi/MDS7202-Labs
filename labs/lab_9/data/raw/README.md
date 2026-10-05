# Datos crudos — Lab9: biomasa de pradera

## Origen

Subconjunto del dataset público **CSIRO Image2Biomass**, descrito en el paper:

> CSIRO Image2Biomass: *a benchmark dataset for predicting pasture biomass from ground-level RGB images*,
> arXiv:2510.22916.

El dataset completo tiene 1162 fotos cenitales de cuadrantes de pradera de 70 × 30 cm, de las cuales **357 tienen
etiqueta pública**. Este laboratorio usa solo esas 357 imágenes etiquetadas y su tabla de mediciones.

## Licencia

El dataset se distribuye con licencia **CC BY-SA 4.0**. Esa licencia exige atribución (la cita de arriba), indicar los
cambios realizados (ver «Transformación aplicada a las imágenes») y que cualquier material derivado se distribuya bajo
la misma licencia.

## Cómo obtener los datos

El repositorio no incluye `mediciones.csv` ni `imagenes/`: el equipo docente comparte un enlace de descarga. Hay que descargarlos y pegarlos en esta carpeta, de modo que queden `data/raw/mediciones.csv` y `data/raw/imagenes/`.

## Archivos

- `mediciones.csv`: la tabla de mediciones en **formato largo** (una fila por imagen y por objetivo), renombrada
  desde la tabla original del dataset. 357 imágenes × 5 objetivos = 1785 filas.
- `imagenes/`: las 357 fotos etiquetadas, en formato `.jpg`.

## Columnas de `mediciones.csv`

| Columna | Significado |
| --- | --- |
| `sample_id` | Identificador único de la fila (imagen + objetivo). |
| `image_path` | Ruta a la imagen, relativa a `data/raw/` (reescrita a `imagenes/<archivo>.jpg`). |
| `Sampling_Date` | Fecha de muestreo. Variable de grupo usada en la validación cruzada del laboratorio (28 fechas únicas). |
| `State` | Estado australiano donde se tomó la muestra (4 niveles). |
| `Species` | Especie o mezcla de especies del cuadrante. Se usa solo para describir los datos. |
| `Pre_GSHH_NDVI` | NDVI satelital previo al muestreo. Se usa solo para describir los datos. |
| `Height_Ave_cm` | Altura promedio medida con plato medidor — el baseline agronómico que el laboratorio compara contra la foto. |
| `target_name` | Nombre del objetivo de esta fila: `Dry_Green_g`, `Dry_Dead_g`, `Dry_Clover_g`, `GDM_g` o `Dry_Total_g`. |
| `target` | Valor del objetivo, en gramos por cuadrante. |

Los cinco objetivos cumplen los invariantes `GDM_g = Dry_Green_g + Dry_Clover_g` y
`Dry_Total_g = Dry_Green_g + Dry_Dead_g + Dry_Clover_g`, con una tolerancia de **0,5 g** (356 de 357 filas cumplen
exacto, y la única excepción difiere en 0,31 g, probablemente por redondeo distinto en la medición de campo original).

## Transformación aplicada a las imágenes

Las fotos originales vienen normalizadas a 2000 × 1000 px (~3 MB cada una). Se **redujeron a 1000 × 500 px** con
reescalado bicúbico, lo que deja la carpeta en ~103 MB.
