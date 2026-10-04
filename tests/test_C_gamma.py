import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_gamma import _normal_order_word, build_gamma
from src.C_generators import _generator_data


@pytest.mark.parametrize("n", (1, 2, 3))
def test_gamma_matrix_and_schema_1_consistency(n):
    root = Path(__file__).resolve().parents[1]
    structure = json.loads(
        (root / "data" / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    gamma = build_gamma(n, structure)
    matrix = gamma["gb_matrix"]
    parameters = matrix["parameters"]
    assert matrix["shape"] == [2, 2 * n]
    assert len(parameters) == 4 * n
    assert len({item["label"] for item in parameters}) == 4 * n
    assert matrix["entries"] == [
        [item["label"] for item in parameters[: 2 * n]],
        [item["label"] for item in parameters[2 * n :]],
    ]
    assert gamma["consistency"]["basis_matches_schema_1"]
    assert gamma["consistency"]["parity_matches_schema_1"]
    assert gamma["consistency"]["parity_status"] == "formal_only"

    full_order, parity, _ = _generator_data(n)
    order_index = {label: index for index, label in enumerate(full_order)}
    basis = set(structure["basis"]["even"] + structure["basis"]["odd"])
    allowed_outputs = basis | {"K"}
    parameter_labels = {item["label"] for item in parameters}
    assert gamma["algebra"] == structure["algebra"]
    for entry in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        assert entry["X"] in basis and entry["Y"] in basis
        assert order_index[entry["X"]] <= order_index[entry["Y"]]
        assert entry["gb_parameter"] in parameter_labels
        assert entry["Z"] in allowed_outputs
        assert Fraction(entry["coeff"])
        assert entry["sign_rule"] == "graded"

    gamma_table = defaultdict(dict)
    for entry in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        gamma_table[
            (entry["X"], entry["Y"], entry["gb_parameter"])
        ][entry["Z"]] = Fraction(entry["coeff"])

    def gamma_bracket(left, right, parameter):
        if order_index[left] <= order_index[right]:
            return gamma_table.get((left, right, parameter), {})
        result = gamma_table.get((right, left, parameter), {})
        sign = -1 if parity[left] * parity[right] % 2 else 1
        return {label: -sign * value for label, value in result.items()}

    for left in full_order:
        for right in full_order:
            for parameter in parameter_labels:
                forward = gamma_bracket(left, right, parameter)
                reverse = gamma_bracket(right, left, parameter)
                expected = {
                    label: -((-1) ** (parity[left] * parity[right])) * value
                    for label, value in reverse.items()
                }
                assert forward == expected


def test_deformed_oscillator_relation_and_first_order_truncation():
    terms = dict(_normal_order_word(("b_1_p", "a_1_p")))
    assert terms == {
        (None, ("a_1_p", "b_1_p")): Fraction(1),
        ("gb_a_1_p_b_1_p", ()): Fraction(1),
    }

    quadratic = dict(_normal_order_word(("b_1_p", "a_1_p", "b_1_p", "a_1_p")))
    assert any(parameter is not None for parameter, _ in quadratic)
    assert all(
        parameter is None or parameter.startswith("gb_")
        for parameter, _ in quadratic
    )


@pytest.mark.parametrize("n", (1, 2, 3))
def test_committed_gamma_matches_generator(n):
    root = Path(__file__).resolve().parents[1]
    structure = json.loads(
        (root / "data" / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    committed = json.loads(
        (root / "data" / f"C_{n}_gamma.json").read_text(encoding="utf-8")
    )
    generated = build_gamma(n, structure)
    committed["metadata"]["generation_date"] = generated["metadata"]["generation_date"]
    assert committed == generated
