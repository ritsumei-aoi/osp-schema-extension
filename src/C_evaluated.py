from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Any

import C_gamma as cgamma
import C_generators as cg

_EVALUATED_SCHEMA_CACHE: dict[tuple[int, str], dict[str, Any]] = {}


def evaluated_path(n: int, profile_name: str, data_dir: Path | None = None) -> Path:
    base = data_dir or Path("data")
    return base / f"C_{n}_evaluated_{profile_name}.json"


def load_gamma_schema(n: int, data_dir: Path | None = None) -> dict[str, Any]:
    path = cgamma.gamma_path(n, data_dir)
    return json.loads(path.read_text(encoding="utf-8"))


def gamma_labels_from_schema(gamma_schema: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for row in gamma_schema["inhomogeneous_deformation"]["gb_matrix"]["entries"]:
        labels.extend(row)
    return labels


def build_profile_assignments(n: int, profile_name: str) -> dict[str, Any]:
    if profile_name not in {"gb_zero", "gb_one"}:
        raise ValueError(f"Unsupported evaluation profile: {profile_name}")

    value = Fraction(0 if profile_name == "gb_zero" else 1)
    description = (
        "All gb deformation parameters are set to zero."
        if profile_name == "gb_zero"
        else "All gb deformation parameters are set to 1."
    )
    gb_values = {label: value for label in cgamma.gb_labels_in_order(n)}
    return {
        "name": profile_name,
        "assignment_type": "explicit",
        "description": description,
        "gb_values": gb_values,
    }


def serialize_profile(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": profile["name"],
        "assignment_type": profile["assignment_type"],
        "description": profile["description"],
        "gb_values": {
            label: cg.fraction_to_str(value) for label, value in profile["gb_values"].items()
        },
    }


def evaluate_linear_coefficient(coefficients: dict[str, str], gb_values: dict[str, Fraction]) -> Fraction:
    total = Fraction(0)
    for label, coeff in coefficients.items():
        if label not in gb_values:
            raise KeyError(f"Missing gb assignment for {label}")
        total += Fraction(coeff) * gb_values[label]
    return total


def evaluate_gamma_matrix(
    gamma_schema: dict[str, Any],
    gb_values: dict[str, Fraction],
) -> list[dict[str, Any]]:
    evaluated_entries: list[dict[str, Any]] = []
    for entry in gamma_schema["inhomogeneous_deformation"]["gamma_matrix"]:
        value = evaluate_linear_coefficient(entry["coeff"], gb_values)
        if not value:
            continue
        evaluated_entries.append(
            {
                "X": entry["X"],
                "Y": entry["Y"],
                "Z": entry["Z"],
                "coeff": cg.fraction_to_str(value),
                "sign_rule": entry["sign_rule"],
            }
        )
    return evaluated_entries


def build_consistency_report(
    n: int,
    profile_name: str,
    structure_schema: dict[str, Any],
    gamma_schema: dict[str, Any],
    evaluated_gamma_entries: list[dict[str, Any]],
    profile: dict[str, Any],
) -> dict[str, Any]:
    expected_labels = cgamma.gb_labels_in_order(n)
    gamma_labels = gamma_labels_from_schema(gamma_schema)
    profile_labels = list(profile["gb_values"].keys())
    recovers_schema_1 = profile_name == "gb_zero" and not evaluated_gamma_entries
    return {
        "structure_file": f"C_{n}_structure.json",
        "gamma_file": f"C_{n}_gamma.json",
        "profile_matches_expected_gb_labels": profile_labels == expected_labels,
        "profile_matches_gamma_matrix": profile_labels == gamma_labels,
        "evaluated_gamma_nonzero_count": len(evaluated_gamma_entries),
        "gb_zero_recovers_schema_1": recovers_schema_1,
    }


def build_metadata(n: int, profile_name: str) -> dict[str, Any]:
    return {
        "generated_by": "src/C_evaluated.py",
        "generation_date": date.today().isoformat(),
        "references": [
            "docs/math/C_inhomogeneous_definition.md",
            "docs/json_schema_specification.md",
            f"data/C_{n}_structure.json",
            f"data/C_{n}_gamma.json",
        ],
        "profile_name": profile_name,
        "structure_file": f"C_{n}_structure.json",
        "gamma_file": f"C_{n}_gamma.json",
    }


def build_evaluated_schema(
    n: int,
    profile_name: str = "gb_zero",
    data_dir: Path | None = None,
) -> dict[str, Any]:
    cache_key = (n, profile_name)
    if data_dir is None and cache_key in _EVALUATED_SCHEMA_CACHE:
        return deepcopy(_EVALUATED_SCHEMA_CACHE[cache_key])

    structure_schema = cgamma.load_structure_schema(n, data_dir)
    gamma_schema = load_gamma_schema(n, data_dir)
    profile = build_profile_assignments(n, profile_name)

    evaluated_gamma_entries = evaluate_gamma_matrix(gamma_schema, profile["gb_values"])
    if profile_name == "gb_zero" and evaluated_gamma_entries:
        raise ValueError("gb_zero must annihilate every evaluated gamma term")

    schema = {
        "schema_version": "5.0",
        "algebra": structure_schema["algebra"],
        "basis": structure_schema["basis"],
        "parity": structure_schema["parity"],
        "central_elements": structure_schema["central_elements"],
        "evaluation_profile": serialize_profile(profile),
        "evaluation_relation": "[X, Y]_eval = [X, Y]_0 + kappa * gamma_eval(X, Y)",
        "evaluated_structure_constants": deepcopy(structure_schema["structure_constants"]),
        "evaluated_deformation": evaluated_gamma_entries,
        "consistency_with_schema_2": build_consistency_report(
            n,
            profile_name,
            structure_schema,
            gamma_schema,
            evaluated_gamma_entries,
            profile,
        ),
        "metadata": build_metadata(n, profile_name),
    }

    if data_dir is None:
        _EVALUATED_SCHEMA_CACHE[cache_key] = deepcopy(schema)
    return deepcopy(schema)


def write_evaluated_json(
    n: int,
    profile_name: str,
    out_path: Path,
    data_dir: Path | None = None,
) -> Path:
    schema = build_evaluated_schema(n, profile_name, data_dir)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate C(n+1) Schema 3 evaluated JSON files.")
    parser.add_argument(
        "--profile",
        choices=("gb_zero", "gb_one"),
        required=True,
        help="Approved gb evaluation profile",
    )
    parser.add_argument("--n", type=int, choices=(1, 2, 3), help="Bosonic rank n to generate")
    parser.add_argument("--all", action="store_true", help="Generate n=1,2,3")
    parser.add_argument("--out", type=Path, help="Output file path for a single n run")
    parser.add_argument("--outdir", type=Path, default=Path("data"), help="Output directory for --all")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.all == bool(args.n):
        raise SystemExit("Specify exactly one of --n or --all")

    if args.all:
        for n in (1, 2, 3):
            path = write_evaluated_json(n, args.profile, evaluated_path(n, args.profile, args.outdir))
            print(f"Wrote {path}")
        return

    out_path = args.out or evaluated_path(args.n, args.profile, args.outdir)
    path = write_evaluated_json(args.n, args.profile, out_path)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
