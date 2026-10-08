#!/usr/bin/env python3
"""Check the dimension/count data in cn1_triviality_verification.json."""

import json
from pathlib import Path


ARTIFACT = Path(__file__).with_name("cn1_triviality_verification.json")


def expected_counts(n):
    even = 2 * n * n + n + 1
    odd = 4 * n
    ee_pairs = even * (even - 1) // 2
    oo_pairs = odd * (odd + 1) // 2
    mixed_pairs = even * odd
    slots = ee_pairs + oo_pairs + mixed_pairs
    equations = odd * (ee_pairs + oo_pairs) + even * mixed_pairs
    return even, odd, slots, equations


def main():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["linear_system"]["classification_computable_from_supplied_definitions"] is False
    assert artifact["linear_system"]["parameter_to_cocycle_matrix_G_n"] is None
    assert artifact["linear_system"]["odd_coboundary_matrix_D_n"] is None
    for case in artifact["cases"]:
        n = case["n"]
        even, odd, slots, equations = expected_counts(n)
        assert case["even_dimension"] == even
        assert case["odd_dimension"] == odd
        assert case["gb_parameter_count"] == 4 * n
        assert len(case["gb_parameter_labels"]) == 4 * n
        assert case["odd_map_coefficient_count"] == 2 * even * odd
        assert case["independent_odd_2_cochain_input_slots"] == slots
        assert case["scalar_odd_2_cochain_equations"] == equations
        assert case["gb_parameter_labels"] == [
            f"gb[{sigma},{j},{s}]"
            for sigma in ("+", "-")
            for j in range(1, n + 1)
            for s in ("+", "-")
        ]
    print(
        f"Verified parity/dimension counts for n=1..3; "
        f"triviality classification remains underdetermined because G_n and D_n are absent."
    )


if __name__ == "__main__":
    main()
