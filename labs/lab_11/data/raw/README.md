# Datos crudos

`curico_2016_2021.parquet` contiene observaciones horarias de la estación
meteorológica de Curicó (id `85629` de Meteostat) entre el 1 de enero de 2016
a las 00:00 y el 31 de diciembre de 2021 a las 23:00, hora local de
`America/Santiago`.

## Origen y licencia

- Fuente: [Meteostat](https://meteostat.net/), estación `85629` (latitud
  −34,97; longitud −71,23; 228 m s. n. m.).
- Meteostat reúne reportes METAR de la estación aeronáutica y el resumen
  horario ISD-Lite de NOAA. ISD-Lite es CC0; METAR no declara una licencia
  propia. Antes de redistribuir el archivo fuera del curso hay que confirmar
  esos términos. Ver `LICENSE`.
- Descarga: 28 de octubre de 2026 con `meteostat` 2.1.5, función
  `hourly("85629", ...)`, zona `America/Santiago`.

## Esquema

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `time` | fecha con zona horaria | Hora local de la observación (`America/Santiago`) |
| `temp` | °C | Temperatura del aire |
| `rhum` | % | Humedad relativa |
| `pres` | hPa | Presión en la estación, no reducida al nivel del mar |
| `wspd` | km/h | Velocidad del viento |
| `wdir` | grados | Dirección desde donde sopla: 0° norte, 90° este; 0° y 360° son la misma dirección |
| `cldc` | oktas (0 a 8) | Cobertura de nubes: 0 despejado, 4 medio cubierto, 8 totalmente cubierto. Solo `isd_lite` |
| `coco` | código | Fenómeno reportado por METAR: 5 niebla, 7 lluvia débil, 8 lluvia, 9 lluvia fuerte, 12 aguanieve, 17 chubasco, 18 chubasco fuerte, 25 tormenta; 0 fuera de la tabla. Solo `metar` |
| `<variable>_source` | texto | `isd_lite` o `metar`, según el instrumento; no es una feature |

Una **okta** es un octavo de la bóveda celeste. `cldc` mide **cuánto** cielo está
cubierto; `coco` etiqueta **qué fenómeno** se reportó. No son intercambiables:
una noche de niebla puede tener `coco = 5` y `cldc` faltante, y una noche
despejada puede tener `cldc = 0` y `coco = null` porque no se reportó ningún
fenómeno.

## Advertencias

- El archivo trae 51.095 filas de las 52.608 horas posibles (97,1 %). Faltan
  1.513 horas y ningún hueco supera las 20 horas. Al completar la grilla
  horaria, esas horas quedan como filas con valores faltantes.
- La serie mezcla dos instrumentos. En 2016 la mayoría de las horas viene de
  `isd_lite`; desde 2017 pesa más `metar`.
- Por omisión, `meteostat.hourly()` rellena los huecos con el pronóstico de
  MET Norway. El archivo **enmascara** todo valor cuya columna
  `<variable>_source` sea `metno_forecast`: un pronóstico no es una medición y
  usarlo como verdad contaminaría la evaluación. Por eso hay variables con más
  faltantes que otras.
- Hay seis días de 25 horas y seis de 23 horas por el cambio de horario. Un
  `shift(24)` sobre filas no siempre equivale a 24 horas: conviene completar
  la grilla horaria antes de calcular lags.
- El 13 de marzo de 2018 a las 09:00 `wspd` marca 176 km/h, muy por encima del
  percentil 99,9 (28 km/h). En este laboratorio se trata como un dato inválido.
- `cldc` solo existe en `isd_lite` (35 % de cobertura) y `coco` solo en METAR
  (15,7 %). Un `null` en `coco` mezcla «no hubo fenómeno» con «no se informó»:
  no se rellena con cero. Hay 35 filas con código 0, fuera de la tabla de
  Meteostat, que se tratan como inválidas. Los códigos observados son 5
  (niebla), 7 (lluvia débil), 8 (lluvia), 9 (lluvia fuerte), 12 (aguanieve),
  17 (chubasco), 18 (chubasco fuerte) y 25 (tormenta).
- `wdir` es un ángulo: 0° y 360° son la misma dirección. Por eso el laboratorio
  usa componentes `u` y `v`.
- No hay precipitación medida utilizable para todo el período, así que el
  archivo no incluye `prcp`.
