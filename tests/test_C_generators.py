import json
from fractions import Fraction
from itertools import product
from pathlib import Path

import pytest

from src.C_generators import generate_schema
from src.verify_C_structure import verify_directory


@pytest.mark.parametrize(
    ("n", "even_count", "odd_count", "total"),
    [(1, 4, 4, 8), (2, 11, 8, 19), (3, 22, 12, 34)],
)
def test_schema_basis_parity_and_dimensions(n, even_count, odd_count, total):
    schema = generate_schema(n)
    even = schema["basis"]["even"]
    odd = schema["basis"]["odd"]

    assert len(even) == even_count
    assert len(odd) == odd_count
    assert schema["algebra"]["dimension"]["total"] == total
    assert schema["algebra"]["dimension"]["even"] == even_count
    assert schema["algebra"]["dimension"]["odd"] == odd_count
    assert schema["basis"]["ordering_convention"].startswith("PBW: κ < [odd]")
    assert even[: n + 1] == [f"H_{k}" for k in range(1, n + 2)]
    assert even[n + 1 : n + 1 + n] == [
        f"E_2del{k}_p" for k in range(1, n + 1)
    ]
    assert odd == [
        f"E_eps1_del{k}_{suffix}"
        for k in range(1, n + 1)
        for suffix in ("pp", "pm", "mp", "mm")
    ]
    assert set(schema["parity"]) == set(even + odd)
    assert all(schema["parity"][label] == 0 for label in even)
    assert all(schema["parity"][label] == 1 for label in odd)
    assert len(schema["generator_realization"]["realizations"]) == total
    assert all(
        schema["generator_realization"]["realizations"][label]["parity"]
        == schema["parity"][label]
        for label in even + odd
    )


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_are_well_formed_and_closed(n):
    schema = generate_schema(n)
    labels = set(schema["parity"])
    constants = schema["structure_constants"]

    assert constants
    assert all(
        item["X"] in labels
        and item["Y"] in labels
        and item["Z"] in labels
        and item["sign_rule"] == "graded"
        for item in constants
    )
    assert all(item["coeff"] not in {"0", "0/1"} for item in constants)
    assert len(
        {(item["X"], item["Y"], item["Z"]) for item in constants}
    ) == len(constants)


def test_schema_is_json_serializable():
    encoded = json.dumps(generate_schema(1))
    assert json.loads(encoded)["schema_version"] == "5.0"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_generated_data_files_match_schema_contract(n):
    path = Path(__file__).parents[1] / "data" / f"C_{n}_structure.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["n"] == n
    assert schema["oscillator_generators"]["fermions"]["labels"] == [
        "a_1_p",
        "a_1_m",
    ]
    assert set(schema) == {
        "schema_version",
        "algebra",
        "oscillator_generators",
        "oscillator_relations",
        "central_elements",
        "basis",
        "parity",
        "generator_realization",
        "structure_constants",
        "metadata",
    }
    assert len(schema["parity"]) == (
        schema["algebra"]["dimension"]["even"]
        + schema["algebra"]["dimension"]["odd"]
    )


def test_committed_json_passes_independent_verification():
    data_dir = Path(__file__).parents[1] / "data"
    reports = verify_directory(data_dir)
    assert all(report["passed"] for report in reports)
    assert [report["triples_checked"] for report in reports] == [
        8**3,
        19**3,
        34**3,
    ]


def test_invalid_rank_is_rejected():
    with pytest.raises(ValueError, match="positive integer"):
        generate_schema(0)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_satisfy_super_jacobi(n):
    schema = generate_schema(n)
    parity = schema["parity"]
    labels = list(schema["basis"]["odd"]) + list(schema["basis"]["even"])
    brackets = {}
    for item in schema["structure_constants"]:
        x, y, z = item["X"], item["Y"], item["Z"]
        coeff = Fraction(item["coeff"])
        brackets.setdefault((x, y), {})[z] = coeff
        reverse_sign = -1 if parity[x] * parity[y] % 2 == 0 else 1
        brackets.setdefault((y, x), {})[z] = reverse_sign * coeff

    def bracket(x, y):
        return brackets.get((x, y), {})

    def add_scaled(target, source, scale):
        for label, coeff in source.items():
            target[label] = target.get(label, Fraction(0)) + scale * coeff
            if not target[label]:
                del target[label]

    for x, y, z in product(labels, repeat=3):
        jacobi = {}
        terms = (
            (y, z, x, (-1) ** (parity[x] * parity[z])),
            (z, x, y, (-1) ** (parity[y] * parity[x])),
            (x, y, z, (-1) ** (parity[z] * parity[y])),
        )
        for inner_left, inner_right, outer, sign in terms:
            inner = bracket(inner_left, inner_right)
            for inner_result, inner_coeff in inner.items():
                add_scaled(
                    jacobi,
                    {
                        result: inner_coeff * coeff
                        for result, coeff in bracket(outer, inner_result).items()
                    },
                    Fraction(sign),
                )
        assert not jacobi, (x, y, z, jacobi)
