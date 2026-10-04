from __future__ import annotations

from pathlib import Path

import pytest

from src.search_C_triviality import analyze_rank


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


@pytest.mark.parametrize(
    ("rank", "phi_count", "image_rank", "parameter_count"),
    ((1, 32, 28, 4), (2, 176, 168, 8), (3, 528, 516, 12)),
)
def test_gamma_classes_are_independent_modulo_coboundaries(
    rank: int, phi_count: int, image_rank: int, parameter_count: int
) -> None:
    result = analyze_rank(rank, DATA_DIR)
    assert result["phi_count"] == phi_count
    assert result["coboundary_rank"] == image_rank
    assert result["parameter_count"] == parameter_count
    assert result["quotient_rank"] == parameter_count
    assert not result["all_plus_trivial"]
    assert len(result["isolated_K_witnesses"]) == parameter_count
    assert all(
        witness["Z"] == "K" and witness["coeff"] in {"1/2", "-1/2"}
        for witness in result["isolated_K_witnesses"].values()
    )
