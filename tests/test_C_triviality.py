import json
from pathlib import Path

import pytest

from src.C_triviality import analyze_rank

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_central_obstruction_forces_zero_gb_profile(n):
    report = analyze_rank(n)
    assert report["central_obstruction_rank"] == report["parameter_count"] == 4 * n
    assert report["all_plus_has_central_mismatch"]
    assert report["necessary_condition"] == "all gb parameters are zero"
    assert report["sufficient_at_zero"]


def test_rank_one_all_plus_discrepancy_has_no_coboundary_target():
    evaluated = json.loads((ROOT / "data" / "C_1_evaluated.json").read_text(encoding="utf-8"))
    coboundary = json.loads((ROOT / "data" / "C_1_coboundary.json").read_text(encoding="utf-8"))
    example = next(
        entry for entry in evaluated["evaluated_structure_constants"]
        if entry["kappa_order"] == 1
        and entry["X"] == "H_1"
        and entry["Y"] == "E_eps1_del1_pm"
        and entry["Z"] == "K"
    )

    assert example["coeff"] == "1"
    assert all(
        entry["Z"] != "K"
        for entry in coboundary["coboundary_definition"]["coboundary_coefficients"]
    )
