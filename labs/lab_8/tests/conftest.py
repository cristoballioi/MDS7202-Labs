import polars as pl
import pytest

from src.heroverse.columns import PUNTAJES


@pytest.fixture
def personajes_crudos() -> pl.DataFrame:
    """Tres personajes con los formatos del scrape y el esquema inferido."""
    return pl.DataFrame(
        {
            "name": ["Atlas", "Brisa", "Coloso"],
            "creator": ["Marvel Comics", "DC Comics", None],
            "gender": ["Male", "Female", None],
            "type_race": ["Human", "Mutant", None],
            "alignment": ["Good", "Bad", "Neutral"],
            **{c: [50, 80, 100] for c in PUNTAJES},
            "height": ["6'2 • 188 cm", "-", "49'2 • 15.0 meters"],
            "weight": ["198 lb • 89 kg", "-", "6,600 lb • 3.0 tons"],
            "first_appearance": [
                "Hulk Vol 2 #2 (April, 2008)",
                "X-Men 2099 #1",
                None,
            ],
            "superpowers": [
                "['Flight', 'Super Strength']",
                "[]",
                "['Magic']",
            ],
            "powers_text": ["Flies fast.", None, "Casts spells."],
        }
    )
