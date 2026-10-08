import json
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_coboundary import build_coboundary_schema


@pytest.mark.parametrize(("n", "f_count"), [(1, 32), (2, 176), (3, 528)])
def test_coboundary_coefficients_match_layer1_basis(n, f_count):
    structure = json.loads(
        Path(f"data/C_{n}_structure.json").read_text(encoding="utf-8")
    )
    schema = build_coboundary_schema(structure, generation_date="2026-10-08")
    parity = structure["parity"]
    labels = list(structure["generator_realization"]["realizations"])
    parameters = {
        item["parameter"]: item
        for item in schema["coboundary"]["linear_map"]["coefficients"]
    }
    entries = schema["coboundary"]["coboundary_coefficients"]

    assert len(parameters) == f_count
    assert schema["coboundary"]["nonzero_coefficient_count"] == len(entries)
    assert all(item["parity"] == 0 for item in parameters.values())
    assert all(
        parity[item["output"]] == 1 - parity[item["input"]]
        for item in parameters.values()
    )

    coefficients = {}
    for entry in entries:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        assert x in parity and y in parity and z in parity
        assert parity[z] == (parity[x] + parity[y] + 1) % 2
        key = (x, y)
        coefficients.setdefault(key, {})
        for term in entry["coefficients"]:
            assert term["parameter"] in parameters
            assert Fraction(term["coeff"]) != 0
            coefficients[key][(z, term["parameter"])] = Fraction(
                term["coeff"]
            )

    order = {label: index for index, label in enumerate(labels)}

    def bracket(x, y):
        if order[x] <= order[y]:
            return coefficients.get((x, y), {})
        reverse_factor = -1 if parity[x] * parity[y] % 2 == 0 else 1
        return {
            key: reverse_factor * value
            for key, value in coefficients.get((y, x), {}).items()
        }

    for x in labels:
        for y in labels:
            left = bracket(x, y)
            right = bracket(y, x)
            factor = -1 if parity[x] * parity[y] % 2 else 1
            keys = set(left) | set(right)
            assert all(
                left.get(key, Fraction(0))
                + factor * right.get(key, Fraction(0))
                == 0
                for key in keys
            )
