"""Substitute a representative numeric gb assignment into Schema 2 data."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from pathlib import Path


def all_positive_assignment(n: int) -> dict[str, int]:
    if n < 1:
        raise ValueError("bosonic rank n must be a positive integer")
    return {
        f"gb_a_1_{fermion_sign}_b_{k}_{boson_sign}": 1
        for fermion_sign in ("p", "m")
        for k in range(1, n + 1)
        for boson_sign in ("p", "m")
    }


def evaluate_schema(schema1_path: Path, schema2_path: Path) -> dict:
    schema1 = json.loads(schema1_path.read_text())
    schema2 = json.loads(schema2_path.read_text())
    n = schema1["algebra"]["n"]
    if schema2["algebra"] != {
        "family": "C",
        "m": 1,
        "n": n,
        "cartan_type": f"C({n + 1})",
    }:
        raise ValueError("Schema 1 and Schema 2 algebra metadata do not match")
    assignment = all_positive_assignment(n)
    declared = {
        item["label"] for item in schema2["inhomogeneous_deformation"]["parameters"]
    }
    if set(assignment) != declared:
        raise ValueError("Schema 2 parameter set does not match the required 2 x 2n gb matrix")

    evaluated: dict[tuple[str, str, str], Fraction] = defaultdict(Fraction)
    for term in schema2["inhomogeneous_deformation"]["gamma_coefficients"]:
        if term["parameter"] not in assignment:
            raise ValueError(f"Unknown deformation parameter: {term['parameter']}")
        evaluated[(term["X"], term["Y"], term["Z"])] += (
            Fraction(term["coeff"]) * assignment[term["parameter"]]
        )
    gamma_terms = [
        {
            "X": x,
            "Y": y,
            "Z": z,
            "kappa_coeff": str(coefficient),
            "sign_rule": "graded",
        }
        for (x, y, z), coefficient in sorted(evaluated.items())
        if coefficient
    ]

    return {
        "schema_version": "5.0",
        "algebra": schema1["algebra"],
        "evaluation": {
            "assignment_name": "all_positive",
            "gb_assignment": assignment,
            "numeric_substitution_note": (
                "Formal coefficient evaluation only: assigning numeric +1 to odd "
                "gb parameters is not parity-preserving."
            ),
        },
        "base_structure_constants": schema1["structure_constants"],
        "evaluated_gamma_coefficients": gamma_terms,
        "bracket_formula": (
            "[X,Y]_evaluated = [X,Y]_0 + kappa * "
            "sum(kappa_coeff * Z) from evaluated_gamma_coefficients"
        ),
        "consistency": {
            "schema1_reference": schema2["schema1_reference"],
            "schema2_reference": schema2_path.name,
            "schema1_closed": schema2["inhomogeneous_deformation"]["consistency"]["schema1_closed"],
            "off_basis_terms": schema2["inhomogeneous_deformation"]["consistency"]["off_basis_terms"],
            "grading_consistent": schema2["inhomogeneous_deformation"]["consistency"]["grading_consistent"],
        },
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": date.today().isoformat(),
            "references": [schema1_path.name, schema2_path.name],
        },
    }


def generate_all(data_dir: Path, ranks=(1, 2, 3)) -> list[Path]:
    paths = []
    for n in ranks:
        path = data_dir / f"C_{n}_evaluated.json"
        evaluated = evaluate_schema(
            data_dir / f"C_{n}_structure.json",
            data_dir / f"C_{n}_gamma.json",
        )
        path.write_text(json.dumps(evaluated, indent=2, ensure_ascii=False) + "\n")
        paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    args = parser.parse_args()
    for path in generate_all(args.data_dir, args.ranks):
        print(path)


if __name__ == "__main__":
    main()
