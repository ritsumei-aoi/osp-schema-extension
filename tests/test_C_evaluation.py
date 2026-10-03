from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

from src.evaluate_C_structure import build_evaluated_schema


@pytest.mark.parametrize("n", (1, 2, 3))
def test_all_plus_evaluation_matches_schema2(n: int) -> None:
    evaluated = build_evaluated_schema(n)
    generated = json.loads(
        (Path("data") / f"C_{n}_evaluated_all_plus.json").read_text(
            encoding="utf-8"
        )
    )
    gamma = json.loads(
        (Path("data") / f"C_{n}_gamma.json").read_text(encoding="utf-8")
    )["inhomogeneous_deformation"]["gamma_coefficients"]
    structure = json.loads(
        (Path("data") / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )["structure_constants"]

    assert evaluated["gb_assignment"]["profile"] == "all_plus"
    assert evaluated["gb_assignment"]["entries"] == [
        [1] * (2 * n),
        [1] * (2 * n),
    ]
    assert generated == evaluated
    output = {
        (row["X"], row["Y"], row["Z"]): (
            row["base_coeff"],
            row["kappa_coeff"],
        )
        for row in evaluated["structure_constants"]
    }
    expected_base = {
        (row["X"], row["Y"], row["Z"]): Fraction(row["coeff"])
        for row in structure
    }
    expected_gamma: dict[tuple[str, str, str], Fraction] = {}
    for row in gamma:
        key = row["X"], row["Y"], row["Z"]
        expected_gamma[key] = (
            expected_gamma.get(key, Fraction(0)) + Fraction(row["coeff"])
        )
    expected_keys = {
        key
        for key in set(expected_base) | set(expected_gamma)
        if expected_base.get(key, Fraction(0)) != 0
        or expected_gamma.get(key, Fraction(0)) != 0
    }

    assert set(output) == expected_keys
    for key in expected_keys:
        assert output[key] == (
            str(expected_base.get(key, Fraction(0))),
            str(expected_gamma.get(key, Fraction(0))),
        )
