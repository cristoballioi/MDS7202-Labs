# Procedencia de los datos

Estas fuentes son una copia en Parquet de las cuatro tablas necesarias para el
Laboratorio 6. Se versionan como excepción porque el pipeline debe poder
reconstruirse sin credenciales ni descargas durante la sesión.

- Fuente canónica: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
- Cobertura: órdenes de marketplaces brasileños entre 2016 y 2018.
- Transformación aplicada: CSV de la fuente a Parquet Zstandard, sin eliminar
  columnas ni filas de estas cuatro tablas.
- Clasificación: datos comerciales anonimizados; los identificadores se tratan
  como internos y pseudonimizados.

| Archivo | SHA-256 |
| --- | --- |
| `customers.parquet` | `548e77b66c971d18b3b6efe5354b2f6208ba26a2deb10518451d9aba7187531d` |
| `orders.parquet` | `368f23668a1958daa54a7bcdfa95b8e04a3801796f428ecc4d6f8b7557760e85` |
| `order_items.parquet` | `02d284e9900789ee22de82057ac5fd4242c21e49a7ac173f6a395422f4cb52d0` |
| `payments.parquet` | `49e3f02d7bf9e6f266f03b974476df01518041313e9cc8d9d55dac65c4c08684` |

La fuente original debe revisarse para sus condiciones de uso y atribución.
