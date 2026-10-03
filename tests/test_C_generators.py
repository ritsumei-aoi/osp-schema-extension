from __future__ import annotations

from itertools import product

import pytest

from src.C_generators import (
    _build_generators,
    _super_bracket,
    build_schema,
)


EXPECTED_COUNTS = {
    1: (4, 4, 8),
    2: (11, 8, 19),
    3: (22, 12, 34),
}


@pytest.mark.parametrize("n", (1, 2, 3))
def test_basis_counts_parity_and_dimensions(n: int) -> None:
    schema = build_schema(n)
    even_count, odd_count, total_count = EXPECTED_COUNTS[n]
    basis = schema["basis"]

    assert len(basis["even"]) == even_count
    assert len(basis["odd"]) == odd_count
    assert len(set(basis["even"] + basis["odd"])) == total_count
    assert len(schema["parity"]) == total_count
    assert set(schema["parity"].values()) == {0, 1}
    assert sum(schema["parity"].values()) == odd_count
    assert schema["algebra"]["dimension"] == {
        "total": total_count,
        "even": even_count,
        "odd": odd_count,
    }
    assert schema["oscillator_generators"]["fermions"]["labels"] == [
        "a_1_p",
        "a_1_m",
    ]
    assert schema["oscillator_generators"]["bosons"]["count"] == 2 * n


@pytest.mark.parametrize("n", (1, 2, 3))
def test_structure_constants_are_closed_and_homogeneous(n: int) -> None:
    schema = build_schema(n)
    parity = schema["parity"]
    pair_positions = set()

    for entry in schema["structure_constants"]:
        left, right, result = entry["X"], entry["Y"], entry["Z"]
        assert left in parity and right in parity and result in parity
        assert (parity[left] + parity[right]) % 2 == parity[result]
        pair_positions.add((left, right))

    assert len(pair_positions) > 0
    assert all(
        (right, left) in pair_positions
        for left, right in pair_positions
        if left != right
    )
    assert all(
        (label, label) not in pair_positions
        for label in schema["basis"]["even"]
    )


@pytest.mark.parametrize("n", (1, 2, 3))
def test_realized_super_jacobi_identity(n: int) -> None:
    even, odd, realizations = _build_generators(n)
    labels = odd + even
    parity = {label: 1 for label in odd}
    parity.update({label: 0 for label in even})

    for x, y, z in product(labels, repeat=3):
        first = _super_bracket(
            realizations[x],
            _super_bracket(
                realizations[y], realizations[z], parity[y], parity[z]
            ),
            parity[x],
            (parity[y] + parity[z]) % 2,
        )
        second = _super_bracket(
            realizations[y],
            _super_bracket(
                realizations[z], realizations[x], parity[z], parity[x]
            ),
            parity[y],
            (parity[z] + parity[x]) % 2,
        )
        third = _super_bracket(
            realizations[z],
            _super_bracket(
                realizations[x], realizations[y], parity[x], parity[y]
            ),
            parity[z],
            (parity[x] + parity[y]) % 2,
        )

        jacobi = {}
        first_sign = -1 if parity[x] * parity[z] else 1
        second_sign = -1 if parity[y] * parity[x] else 1
        third_sign = -1 if parity[z] * parity[y] else 1
        for term, coeff in first.items():
            jacobi[term] = jacobi.get(term, 0) + first_sign * coeff
        for term, coeff in second.items():
            jacobi[term] = jacobi.get(term, 0) + second_sign * coeff
        for term, coeff in third.items():
            jacobi[term] = jacobi.get(term, 0) + third_sign * coeff
        assert not {term: coeff for term, coeff in jacobi.items() if coeff}, (
            f"Super-Jacobi failed for n={n}, triple {(x, y, z)}."
        )
