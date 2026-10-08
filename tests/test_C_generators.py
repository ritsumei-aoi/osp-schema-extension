import json
from fractions import Fraction

import pytest

from src.C_generators import (
    _bracket,
    _generator_data,
    _pbw_order,
    build_schema,
    generate_files,
)
from src.verify_C_structure import verify_schema


@pytest.mark.parametrize(
    ("n", "even_count", "odd_count", "total"),
    [(1, 4, 4, 8), (2, 11, 8, 19), (3, 22, 12, 34)],
)
def test_schema_basis_dimensions_and_parity(n, even_count, odd_count, total):
    schema = build_schema(n, generation_date="2026-10-08")
    basis = schema["basis"]
    assert len(basis["even"]) == even_count
    assert len(basis["odd"]) == odd_count
    assert schema["algebra"]["dimension"]["total"] == total
    assert set(schema["parity"]) == set(basis["even"] + basis["odd"])
    assert all(schema["parity"][label] == 0 for label in basis["even"])
    assert all(schema["parity"][label] == 1 for label in basis["odd"])
    assert "kappa" not in schema["parity"]
    assert "K" not in schema["parity"]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_are_closed_and_have_correct_parity(n):
    schema = build_schema(n, generation_date="2026-10-08")
    parity = schema["parity"]
    generators, _, _ = _generator_data(n)
    pbw = _pbw_order(n)
    by_pair = {}
    for entry in schema["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        coefficient = entry["coeff"]
        assert z in parity
        assert parity[z] == (parity[x] + parity[y]) % 2
        assert coefficient not in ("0", "-0")
        by_pair.setdefault((x, y), []).append(entry)

    for i, x in enumerate(pbw):
        for y in pbw[i:]:
            bracket = _bracket(
                generators[x], generators[y], parity[x], parity[y]
            )
            assert bool(bracket) == ((x, y) in by_pair)


def test_generated_files_are_valid_json(tmp_path):
    paths = generate_files(
        tmp_path, ranks=(1, 2, 3), generation_date="2026-10-08"
    )
    assert [path.name for path in paths] == [
        "C_1_structure.json",
        "C_2_structure.json",
        "C_3_structure.json",
    ]
    for path in paths:
        schema = json.loads(path.read_text(encoding="utf-8"))
        assert schema["schema_version"] == "5.0"
        assert schema["central_elements"]["kappa"]["parity"] == 1
        assert schema["central_elements"]["K"]["parity"] == 0


def test_rank_three_structure_constants_satisfy_super_jacobi():
    schema = build_schema(3, generation_date="2026-10-08")
    parity = schema["parity"]
    basis = _pbw_order(3)
    brackets = {}
    for entry in schema["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        coefficient = Fraction(entry["coeff"])
        brackets.setdefault((x, y), {})[z] = coefficient
        reverse_sign = -1 if (parity[x] * parity[y]) % 2 == 0 else 1
        brackets.setdefault((y, x), {})[z] = coefficient * reverse_sign

    def bracket(x, y):
        return brackets.get((x, y), {})

    for x in basis:
        for y in basis:
            for z in basis:
                terms = {}
                for sign, left, right in (
                    (-1 if parity[x] * parity[z] % 2 else 1, x, (y, z)),
                    (-1 if parity[y] * parity[x] % 2 else 1, y, (z, x)),
                    (-1 if parity[z] * parity[y] % 2 else 1, z, (x, y)),
                ):
                    for inner, inner_coeff in bracket(*right).items():
                        for result, outer_coeff in bracket(left, inner).items():
                            terms[result] = (
                                terms.get(result, Fraction(0))
                                + sign * inner_coeff * outer_coeff
                            )
                assert not any(terms.values()), (x, y, z, terms)


@pytest.mark.parametrize(("n", "dimension"), [(1, 8), (2, 19), (3, 34)])
def test_verifier_checks_all_pairs_and_triples(n, dimension):
    result = verify_schema(build_schema(n, generation_date="2026-10-08"))
    assert result["generators"] == dimension
    assert result["pair_checks"] == dimension**2
    assert result["triple_checks"] == dimension**3
