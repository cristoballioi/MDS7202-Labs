"""Constantes del contrato de inferencia del servicio de potabilidad."""

FEATURES = [
    "ph",
    "Hardness",
    "Solids",
    "Chloramines",
    "Sulfate",
    "Conductivity",
    "Organic_carbon",
    "Trihalomethanes",
    "Turbidity",
]

# Un sensor puede fallar: solo estas tres mediciones admiten un valor ausente.
# Son las columnas que el CSV real trae incompletas.
OPCIONALES = ["ph", "Sulfate", "Trihalomethanes"]

# Rango físico aceptado por medición, como (mínimo, máximo). Es más amplio que
# lo observado en el CSV: una medición real nunca debe ser rechazada.
RANGOS = {
    "ph": (0.0, 14.0),
    "Hardness": (0.0, 500.0),
    "Solids": (0.0, 100_000.0),
    "Chloramines": (0.0, 15.0),
    "Sulfate": (0.0, 600.0),
    "Conductivity": (0.0, 1_000.0),
    "Organic_carbon": (0.0, 50.0),
    "Trihalomethanes": (0.0, 200.0),
    "Turbidity": (0.0, 10.0),
}
