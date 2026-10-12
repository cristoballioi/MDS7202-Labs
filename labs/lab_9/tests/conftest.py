import polars as pl
import pytest

OBJETIVOS = [
    "Dry_Green_g",
    "Dry_Dead_g",
    "Dry_Clover_g",
    "GDM_g",
    "Dry_Total_g",
]


@pytest.fixture
def mediciones_largo() -> pl.DataFrame:
    """Dos imágenes con sus 5 objetivos, en el formato largo original."""
    cuadrantes = [
        ("imagenes/A.jpg", "2020/1/1", "Tas", 5.0, 10.0, 5.0, 2.0),
        ("imagenes/B.jpg", "2020/1/15", "NSW", 8.0, 20.0, 0.0, 0.0),
        ("imagenes/C.jpg", "2020/1/15", "NSW", 6.0, 15.0, 3.0, 1.0),
    ]
    filas = []
    for img, fecha, estado, altura, green, dead, clover in cuadrantes:
        valores = {
            "Dry_Green_g": green,
            "Dry_Dead_g": dead,
            "Dry_Clover_g": clover,
            "GDM_g": green + clover,
            "Dry_Total_g": green + dead + clover,
        }
        for nombre in OBJETIVOS:
            filas.append(
                {
                    "sample_id": f"{img}__{nombre}",
                    "image_path": img,
                    "Sampling_Date": fecha,
                    "State": estado,
                    "Height_Ave_cm": altura,
                    "target_name": nombre,
                    "target": valores[nombre],
                }
            )
    return pl.DataFrame(filas)
