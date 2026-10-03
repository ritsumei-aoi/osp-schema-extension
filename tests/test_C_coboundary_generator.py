import json
from pathlib import Path

import pytest
from sympy import Poly, Symbol, sympify

from src.C_coboundary_generator import (
    compute_coboundary_schema,
    write_coboundary_schema,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _read_schema(filename):
    with (DATA_DIR / filename).open(encoding="utf-8") as source:
        return json.load(source)


@pytest.mark.parametrize(
    ("n", "parameter_count", "record_count", "pair_checks"),
    ((1, 32, 212, 512), (2, 176, 2748, 6859), (3, 528, 13976, 39304)),
)
def test_general_odd_map_and_coboundary_are_serialized_exactly(
    n, parameter_count, record_count, pair_checks, tmp_path
):
    schema1 = _read_schema(f"C_{n}_structure.json")
    schema, report = compute_coboundary_schema(n, schema1)
    coboundary = schema["coboundary"]
    labels = schema1["basis"]["odd"] + schema1["basis"]["even"]
    parity = schema1["parity"]

    assert coboundary["map_parity"] == 1
    assert coboundary["parameter_parity"] == 0
    assert [entry["source"] for entry in coboundary["f_map"]] == labels
    all_parameters = []
    for entry in coboundary["f_map"]:
        source = entry["source"]
        expected_targets = [
            target for target in labels if parity[target] != parity[source]
        ]
        assert [term["target"] for term in entry["terms"]] == expected_targets
        for term in entry["terms"]:
            assert term["coefficient"] == (
                f"phi__{term['target']}__from__{source}"
            )
            all_parameters.append(term["coefficient"])

    assert len(all_parameters) == parameter_count
    assert len(set(all_parameters)) == parameter_count
    assert len(coboundary["coboundary_structure"]) == record_count
    assert report.parameter_count == parameter_count
    assert report.record_count == record_count
    assert report.graded_skew_checks == pair_checks

    symbols = {name: Symbol(name) for name in all_parameters}
    parameter_symbols = set(symbols.values())
    label_set = set(labels)
    for record in coboundary["coboundary_structure"]:
        assert {record["X"], record["Y"], record["Z"]} <= label_set
        assert record["sign_rule"] == "graded"
        expression = sympify(record["coeff"], locals=symbols)
        assert expression.free_symbols <= parameter_symbols
        polynomial = Poly(expression)
        assert polynomial.coeff_monomial(1) == 0
        assert all(sum(monomial) == 1 for monomial, _ in polynomial.terms())

    even_diagonal = {
        entry["X"]
        for entry in coboundary["coboundary_structure"]
        if entry["X"] == entry["Y"] and parity[entry["X"]] == 0
    }
    assert even_diagonal == set()

    saved = _read_schema(f"C_{n}_coboundary.json")
    saved_coboundary = saved["coboundary"]
    assert saved_coboundary["f_map"] == coboundary["f_map"]
    assert saved_coboundary["coboundary_structure"] == coboundary[
        "coboundary_structure"
    ]

    path, written_report = write_coboundary_schema(n, DATA_DIR, tmp_path)
    assert path.name == f"C_{n}_coboundary.json"
    assert written_report == report
    with path.open(encoding="utf-8") as source:
        round_trip = json.load(source)
    assert round_trip["coboundary"] == coboundary
