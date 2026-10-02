import json
from pathlib import Path

import pytest
from sympy import Rational, Symbol, sympify

from src.C_evaluated_generator import evaluate_gamma_schema, write_evaluated_schema

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _read_schema(filename):
    with (DATA_DIR / filename).open(encoding="utf-8") as source:
        return json.load(source)


@pytest.mark.parametrize(
    ("n", "entry_count", "triple_count"),
    ((1, 92, 512), (2, 568, 6859), (3, 1660, 39304)),
)
def test_evaluated_schema_is_exact_schema2_substitution(
    n, entry_count, triple_count, tmp_path
):
    schema1 = _read_schema(f"C_{n}_structure.json")
    schema2 = _read_schema(f"C_{n}_gamma.json")
    evaluated, report = evaluate_gamma_schema(n, schema1, schema2)
    deformation = schema2["inhomogeneous_deformation"]
    evaluated_deformation = evaluated["inhomogeneous_deformation"]

    expected_assignment = {}
    for row_index, row_label in enumerate(deformation["gb_matrix"]["row_labels"]):
        for column_index, column_label in enumerate(
            deformation["gb_matrix"]["column_labels"]
        ):
            parameter = deformation["gb_matrix"]["entries"][row_index][column_index]
            expected_assignment[parameter] = (
                -1 if row_label == "a_1_m" and column_label.endswith("_p") else 1
            )
    assert evaluated_deformation["parameter_assignment"] == expected_assignment
    assert evaluated["structure_constants"] == schema1["structure_constants"]
    assert len(evaluated_deformation["evaluated_gamma_structure"]) == entry_count

    symbols = {name: Symbol(name) for name in expected_assignment}
    substitutions = {
        symbols[name]: value for name, value in expected_assignment.items()
    }
    expected_gamma = {}
    for record in deformation["gamma_structure"]:
        coefficient = Rational(
            sympify(record["coeff"], locals=symbols).subs(substitutions)
        )
        if coefficient:
            expected_gamma[(record["X"], record["Y"], record["Z"])] = str(
                coefficient
            )
    actual_gamma = {
        (record["X"], record["Y"], record["Z"]): record["coeff"]
        for record in evaluated_deformation["evaluated_gamma_structure"]
    }
    assert actual_gamma == expected_gamma
    saved = _read_schema(f"C_{n}_evaluated.json")
    saved_deformation = saved["inhomogeneous_deformation"]
    assert saved_deformation["parameter_assignment"] == expected_assignment
    assert {
        (record["X"], record["Y"], record["Z"]): record["coeff"]
        for record in saved_deformation["evaluated_gamma_structure"]
    } == expected_gamma
    assert saved["structure_constants"] == schema1["structure_constants"]
    assert report.parameter_count == 4 * n
    assert report.symbolic_gamma_entries == entry_count
    assert report.evaluated_gamma_entries == entry_count
    assert report.cocycle_triples == triple_count

    path, written_report = write_evaluated_schema(
        n, DATA_DIR, DATA_DIR, tmp_path
    )
    assert path.name == f"C_{n}_evaluated.json"
    assert written_report == report
    with path.open(encoding="utf-8") as source:
        round_trip = json.load(source)
    assert round_trip["inhomogeneous_deformation"][
        "evaluated_gamma_structure"
    ] == evaluated_deformation["evaluated_gamma_structure"]
