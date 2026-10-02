#!/usr/bin/env python3
"""Validate the repository-derived C(n+1) triviality evidence artifact."""

import json
from pathlib import Path


ARTIFACT = Path(__file__).with_name("cn1_triviality_artifacts.json")


def main() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["artifact_version"] == 1
    assert data["status"] == (
        "adjoint_valued_problem_underdetermined_and_definitions_inconsistent"
    )

    for case in data["cases"]:
        n = case["n"]
        assert case["even_dimension"] == 2 * n**2 + n + 1
        assert case["odd_dimension"] == 4 * n
        assert case["total_dimension"] == case["even_dimension"] + case["odd_dimension"]
        assert case["parameter_count"] == 4 * n

    parity = data["formulas_from_definitions"]["oscillator_parity"]
    assert parity["bracket"] == (parity["b"] + parity["a"]) % 2
    assert parity["right_hand_side"] == (
        parity["declared_gb"] + parity["kappa"]
    ) % 2
    assert parity["consistent"] is False
    assert parity["required_gb_if_kappa_is_odd"] == (
        parity["bracket"] - parity["kappa"]
    ) % 2

    targets = data["target_space_analysis"]
    assert targets["literal_extension"] == "g direct_sum C*kappa"
    assert targets["intersection"] == "zero"
    assert targets["intended_adjoint_module_map_specified"] is False
    assert targets["meaning_of_up_to_scalar_specified"] is False

    print(
        json.dumps(
            {
                "artifact": ARTIFACT.name,
                "validated_cases": [case["n"] for case in data["cases"]],
                "dimension_and_parameter_counts": "consistent",
                "declared_parity_assignment": "inconsistent",
                "literal_coboundary_target_intersection": "zero",
                "adjoint_valued_triviality_decidable_from_inputs": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
