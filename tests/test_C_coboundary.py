import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_coboundary import build_coboundary


@pytest.mark.parametrize("n", (1, 2, 3))
def test_odd_map_and_coboundary_are_consistent(n):
    root = Path(__file__).resolve().parents[1]
    structure = json.loads(
        (root / "data" / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    coboundary = build_coboundary(structure)
    even_count = len(structure["basis"]["even"])
    odd_count = len(structure["basis"]["odd"])
    map_coefficients = coboundary["linear_map_f"]["coefficients"]
    assert len(map_coefficients) == 2 * even_count * odd_count
    assert coboundary["linear_map_f"]["parameter_count"] == len(map_coefficients)
    assert all(item["parity"] == 0 for item in map_coefficients)

    parity = structure["parity"]
    order = coboundary["pbw_order"]
    order_index = {label: index for index, label in enumerate(order)}
    parameter_names = {item["parameter"] for item in map_coefficients}
    terms = coboundary["coboundary"]["coefficients"]
    term_keys = set()
    table = defaultdict(dict)
    for term in terms:
        key = (term["X"], term["Y"], term["phi_parameter"], term["Z"])
        assert key not in term_keys
        term_keys.add(key)
        assert term["phi_parameter"] in parameter_names
        assert order_index[term["X"]] <= order_index[term["Y"]]
        assert parity[term["Z"]] == (parity[term["X"]] + parity[term["Y"]] + 1) % 2
        assert Fraction(term["coeff"])
        table[(term["X"], term["Y"], term["phi_parameter"])][term["Z"]] = Fraction(
            term["coeff"]
        )

    def delta(left, right, parameter):
        if order_index[left] <= order_index[right]:
            return table.get((left, right, parameter), {})
        vector = table.get((right, left, parameter), {})
        sign = -1 if parity[left] * parity[right] % 2 else 1
        return {label: -sign * coefficient for label, coefficient in vector.items()}

    for left in order:
        for right in order:
            for parameter in parameter_names:
                forward = delta(left, right, parameter)
                reverse = delta(right, left, parameter)
                expected = {
                    label: -((-1) ** (parity[left] * parity[right])) * coefficient
                    for label, coefficient in reverse.items()
                }
                assert forward == expected


@pytest.mark.parametrize("n", (1, 2, 3))
def test_committed_coboundary_matches_generator(n):
    root = Path(__file__).resolve().parents[1]
    data = root / "data"
    structure = json.loads(
        (data / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    committed = json.loads(
        (data / f"C_{n}_coboundary.json").read_text(encoding="utf-8")
    )
    generated = build_coboundary(structure)
    committed["metadata"]["generation_date"] = generated["metadata"]["generation_date"]
    assert committed == generated
