"""Unit tests for Schema 3 (Evaluated structure) for C(n+1)."""

from collections import defaultdict
from fractions import Fraction
import json
from pathlib import Path
import pytest


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema3_json_conformance_and_consistency_with_schema2(n):
    eval_path = Path(f"data/C_{n}_evaluated.json")
    gamma_path = Path(f"data/C_{n}_gamma.json")
    assert eval_path.exists()
    assert gamma_path.exists()

    with open(eval_path, "r", encoding="utf-8") as f:
        edata = json.load(f)
    with open(gamma_path, "r", encoding="utf-8") as f:
        gdata = json.load(f)

    # Required top-level keys
    required_keys = [
        "schema_version",
        "algebra",
        "central_elements",
        "gb_assignment",
        "basis",
        "parity",
        "evaluated_deformation",
        "metadata",
    ]
    for k in required_keys:
        assert k in edata, f"Missing top-level key {k} in Schema 3"

    # Consistency with Schema 2
    assert edata["schema_version"] == gdata["schema_version"]
    assert edata["algebra"] == gdata["algebra"]
    assert edata["central_elements"] == gdata["central_elements"]
    assert edata["basis"] == gdata["basis"]
    assert edata["parity"] == gdata["parity"]

    # Verify gb assignment values
    gb_vals = edata["gb_assignment"]["values"]
    assert len(gb_vals) == 4 * n

    # Recompute evaluated sum directly from Schema 2 and compare
    expected_sum = defaultdict(Fraction)
    for entry in gdata["inhomogeneous_deformation"]["gamma_coefficients"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        gb = entry["gb"]
        coeff = Fraction(entry["coeff"])
        expected_sum[(x, y, z)] += coeff * Fraction(gb_vals[gb])

    actual_sum = defaultdict(Fraction)
    for entry in edata["evaluated_deformation"]["evaluated_coefficients"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        actual_sum[(x, y, z)] = Fraction(entry["coeff"])

    all_keys = set(expected_sum.keys()) | set(actual_sum.keys())
    for k in all_keys:
        exp_val = expected_sum.get(k, Fraction(0))
        act_val = actual_sum.get(k, Fraction(0))
        assert act_val == exp_val, f"Mismatch at {k}: actual={act_val}, expected={exp_val}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_properties(n):
    with open(f"data/C_{n}_evaluated.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    parities = data["parity"]
    all_gens = data["basis"]["odd"] + data["basis"]["even"]
    eval_table = {}
    for entry in data["evaluated_deformation"]["evaluated_coefficients"]:
        eval_table[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])

    for x in all_gens:
        for y in all_gens:
            px, py = parities[x], parities[y]
            sign = -1 if (px * py == 1) else 1
            for z in all_gens:
                c_xy = eval_table.get((x, y, z), Fraction(0))
                c_yx = eval_table.get((y, x, z), Fraction(0))
                # Anti-symmetry
                assert c_yx == -sign * c_xy, f"Anti-symmetry failure for [{x}, {y}] -> {z}"

                # Parity
                if c_xy != 0:
                    pz = parities[z]
                    assert pz == (px + py + 1) % 2
