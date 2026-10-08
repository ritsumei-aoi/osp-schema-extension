import json
from fractions import Fraction
from pathlib import Path

import pytest

from src.evaluate_C import evaluate_schema1_gamma


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluation_preserves_base_and_substitutes_all_parameters(n):
    data_dir = Path("data")
    structure = json.loads(
        (data_dir / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    gamma = json.loads(
        (data_dir / f"C_{n}_gamma.json").read_text(encoding="utf-8")
    )
    positive = evaluate_schema1_gamma(structure, gamma, sign=1)
    negative = evaluate_schema1_gamma(structure, gamma, sign=-1)
    base = {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["coeff"])
        for entry in structure["structure_constants"]
    }
    plus = {
        (entry["X"], entry["Y"], entry["Z"]): (
            Fraction(entry["base_coeff"]),
            Fraction(entry["kappa_coeff"]),
        )
        for entry in positive["evaluated_structure_constants"]
    }
    minus = {
        (entry["X"], entry["Y"], entry["Z"]): (
            Fraction(entry["base_coeff"]),
            Fraction(entry["kappa_coeff"]),
        )
        for entry in negative["evaluated_structure_constants"]
    }

    assert len(positive["evaluation"]["assignment"]) == 4 * n
    assert set(positive["evaluation"]["assignment"].values()) == {"1"}
    assert set(negative["evaluation"]["assignment"].values()) == {"-1"}
    assert all(plus[key][0] == value for key, value in base.items())
    assert all(minus[key][0] == value for key, value in base.items())
    for key in set(plus) | set(minus):
        assert plus.get(key, (Fraction(0), Fraction(0)))[0] == minus.get(
            key, (Fraction(0), Fraction(0))
        )[0]
        assert plus.get(key, (Fraction(0), Fraction(0)))[1] == -minus.get(
            key, (Fraction(0), Fraction(0))
        )[1]
