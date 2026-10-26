# Datos del Laboratorio 10

Esta carpeta recibe `letras.csv`, que el equipo docente entrega por un enlace
aparte. El archivo no está en el repositorio: descárguenlo y cópienlo aquí antes
de abrir el notebook.

## Origen

Las etiquetas vienen de **MoodyLyrics4Q**, un dataset de 2 000 canciones con 500
en cada cuadrante del modelo de Russell: `happy`, `angry`, `sad` y `relaxed`.
Sus autores etiquetaron cada canción a partir de los tags de los usuarios de
Last.fm. El CSV original trae solo artista, título y etiqueta, y se descarga
desde [la página de Erion Çano](https://softeng.polito.it/erion).

Las letras las obtuvo el equipo docente en octubre de 2026 con la API de
[lrclib](https://lrclib.net), buscando cada canción por artista y título. Si la
API no devolvía una letra con el mismo título y un artista que coincidiera, la
columna `Lyrics` quedó vacía. Por eso algunas canciones no tienen letra, y
ustedes las cuentan en la Etapa 1.

El idioma de cada letra lo detectó el equipo docente con `TextCat`, el clasificador de
idioma de [nltk](https://www.nltk.org), sobre los primeros 1 000 caracteres de la letra. Es un
clasificador aproximado: no distingue bien el español de otros idiomas y se equivoca con
algunas letras cortas. En la Etapa 1 se usa solo para excluir las canciones que no están en
inglés.

Cita de los autores:

> Çano, E. y Morisio, M. (2017). *Music Mood Dataset Creation Based on Last.fm
> Tags*. Fourth International Conference on Artificial Intelligence and
> Applications (AIAP 2017), Viena. doi: 10.5121/csit.2017.70603.

## Columnas

| Columna | Qué contiene |
| --- | --- |
| `Index` | identificador de la canción en MoodyLyrics4Q (`ML1`, `ML2`, …) |
| `Artist` | artista |
| `Title` | título de la canción |
| `Mood` | etiqueta: `happy`, `angry`, `sad` o `relaxed` |
| `Lyrics` | letra completa en texto plano; vacía si no se encontró |
| `Idioma` | código ISO 639-3 del idioma de la letra, detectado por el equipo docente con el clasificador de idioma de nltk (`eng` es inglés; `und`, indeterminado, o sin letra) |

## Derechos de autor

Las letras de canciones tienen derechos de autor. Se entregan solo para el uso de
este curso: no las redistribuyan, no las publiquen y no las suban a ningún
repositorio. MoodyLyrics4Q no declara una licencia; sus autores piden citar el
artículo si lo usan.

Hay un solo uso en que las letras salen del computador: en la Etapa 4, las 372 letras del test
se envían a un servicio externo (OpenRouter, que las pasa al proveedor del modelo Jev), con la clave
que entrega el equipo docente. Es solo para este curso y para ese ejercicio: no las usen con
ningún otro servicio.
