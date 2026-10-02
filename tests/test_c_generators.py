import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from C_generators import generate_schema


def _coefficient(value):
    numerator, *denominator = value.split("/")
    return int(numerator) / int(denominator[0]) if denominator else int(numerator)


def test_basis_counts_and_parity_for_supported_ranks():
    for n in (1, 2, 3):
        schema = generate_schema(n)
        even = schema["basis"]["even"]
        odd = schema["basis"]["odd"]
        assert len(even) == 2 * n * n + n + 1
        assert len(odd) == 4 * n
        assert schema["algebra"]["dimension"]["total"] == len(even) + len(odd)
        assert set(schema["parity"]) == set(even + odd)
        assert all(schema["parity"][name] == 0 for name in even)
        assert all(schema["parity"][name] == 1 for name in odd)
        assert len(schema["generator_realization"]["realizations"]) == len(even) + len(odd)


def test_structure_constants_are_closed_and_parity_homogeneous():
    schema = generate_schema(3)
    parity = schema["parity"]
    basis = set(parity)
    for bracket in schema["structure_constants"]:
        assert bracket["X"] in basis
        assert bracket["Y"] in basis
        assert bracket["Z"] in basis
        assert _coefficient(bracket["coeff"]) != 0
        assert parity[bracket["Z"]] == (parity[bracket["X"]] + parity[bracket["Y"]]) % 2


def test_every_independent_nonzero_pair_is_emitted_once():
    schema = generate_schema(2)
    basis_order = schema["basis"]["even"] + schema["basis"]["odd"]
    indices = {name: index for index, name in enumerate(basis_order)}
    triples = [
        (entry["X"], entry["Y"], entry["Z"])
        for entry in schema["structure_constants"]
    ]
    assert all(indices[x] <= indices[y] for x, y, _ in triples)
    assert len(triples) == len(set(triples))


def test_rejects_invalid_rank():
    import pytest

    with pytest.raises(ValueError, match="at least 1"):
        generate_schema(0)


def test_graded_jacobi_identity_for_all_generated_ranks():
    for n in (1, 2, 3):
        schema = generate_schema(n)
        basis = schema["basis"]["even"] + schema["basis"]["odd"]
        indices = {name: index for index, name in enumerate(basis)}
        parity = schema["parity"]
        constants = {}
        for entry in schema["structure_constants"]:
            key = (entry["X"], entry["Y"])
            constants.setdefault(key, {})[entry["Z"]] = Fraction(entry["coeff"])

        def bracket(x, y):
            if indices[x] <= indices[y]:
                return constants.get((x, y), {})
            sign = -1 if parity[x] * parity[y] else 1
            return {
                z: -sign * coeff
                for z, coeff in constants.get((y, x), {}).items()
            }

        def bracket_linear(x, terms):
            result = {}
            for y, coeff in terms.items():
                for z, value in bracket(x, y).items():
                    result[z] = result.get(z, Fraction()) + coeff * value
            return {z: coeff for z, coeff in result.items() if coeff}

        for x in basis:
            for y in basis:
                for z in basis:
                    terms = []
                    cyclic = (
                        (x, y, z, parity[x] * parity[z]),
                        (y, z, x, parity[y] * parity[x]),
                        (z, x, y, parity[z] * parity[y]),
                    )
                    for first, second, third, exponent in cyclic:
                        inner = bracket(second, third)
                        outer = bracket_linear(first, inner)
                        sign = -1 if exponent % 2 else 1
                        terms.append({
                            name: sign * coeff for name, coeff in outer.items()
                        })
                    total = {}
                    for term in terms:
                        for name, coeff in term.items():
                            total[name] = total.get(name, Fraction()) + coeff
                    assert not any(total.values()), (n, x, y, z, total)
