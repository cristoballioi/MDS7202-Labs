import polars as pl
import pytest
from polars.testing import assert_frame_equal

from src.pudulake.bronze import read_sources

pytestmark = pytest.mark.etapa1


def test_lee_las_cuatro_fuentes_parquet(raw_dir):
    sources = read_sources(raw_dir)

    assert set(sources) == {"orders", "customers", "order_items", "payments"}
    for name in sources:
        expected = pl.read_parquet(raw_dir / f"{name}.parquet")
        assert_frame_equal(sources[name], expected)


def test_informa_una_fuente_bronze_ausente(raw_dir):
    (raw_dir / "payments.parquet").unlink()

    with pytest.raises(FileNotFoundError, match="payments"):
        read_sources(raw_dir)
