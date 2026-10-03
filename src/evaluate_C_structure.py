"""Evaluate C(n+1) structure constants at the all-plus gb assignment."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path


def _fraction_string(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sum_rows(rows: list[dict], coefficient: str) -> dict:
    result: dict[tuple[str, str, str], Fraction] = {}
    for row in rows:
        key = row["X"], row["Y"], row["Z"]
        result[key] = result.get(key, Fraction(0)) + Fraction(row[coefficient])
    return {key: value for key, value in result.items() if value}


def _verify_graded_skew(
    constants: dict[tuple[str, str, str], dict[str, Fraction]],
    parity: dict[str, int],
) -> None:
    for (left, right, result), coeffs in constants.items():
        reverse = constants.get((right, left, result), {})
        factor = -1 if parity[left] * parity[right] == 0 else 1
        for field, coeff in coeffs.items():
            if coeff != factor * reverse.get(field, Fraction(0)):
                raise ValueError(
                    "Evaluated graded skew-symmetry failed at "
                    f"({left}, {right}, {result}, {field})."
                )


def build_evaluated_schema(n: int, data_dir: Path = Path("data")) -> dict:
    schema1_path = data_dir / f"C_{n}_structure.json"
    schema2_path = data_dir / f"C_{n}_gamma.json"
    schema1 = _read_json(schema1_path)
    schema2 = _read_json(schema2_path)
    expected_algebra = ("C", 1, n)
    for source in (schema1, schema2):
        algebra = source["algebra"]
        actual = algebra["family"], algebra["m"], algebra["n"]
        if actual != expected_algebra:
            raise ValueError(f"{source.get('metadata', {})}: wrong algebra rank.")
    if schema2["base_schema"] != schema1_path.name:
        raise ValueError(f"{schema2_path}: base_schema reference does not match.")

    deformation = schema2["inhomogeneous_deformation"]
    matrix = deformation["gb_matrix"]
    columns = [
        f"b_{mode}_{sign}"
        for mode in range(1, n + 1)
        for sign in ("p", "m")
    ]
    rows = ["a_1_p", "a_1_m"]
    if matrix["shape"] != [2, 2 * n]:
        raise ValueError(f"{schema2_path}: invalid gb matrix shape.")
    if matrix["row_labels"] != rows or matrix["column_labels"] != columns:
        raise ValueError(f"{schema2_path}: unexpected gb matrix ordering.")
    if deformation["parameter_parity"]["gb_scalar"] != 0:
        raise ValueError(f"{schema2_path}: gb parameters must be ordinary scalars.")

    parameter_names = {
        parameter for row in matrix["entries"] for parameter in row
    }
    if len(parameter_names) != 4 * n:
        raise ValueError(f"{schema2_path}: gb matrix does not contain 4n entries.")
    gamma_rows = deformation["gamma_coefficients"]
    if any(row["parameter"] not in parameter_names for row in gamma_rows):
        raise ValueError(f"{schema2_path}: gamma refers to an unknown parameter.")

    base_coeffs = _sum_rows(schema1["structure_constants"], "coeff")
    evaluated_gamma = _sum_rows(gamma_rows, "coeff")
    base_generators = schema1["basis"]["odd"] + schema1["basis"]["even"]
    valid_results = set(base_generators) | {"K"}
    if any(result not in valid_results for _, _, result in evaluated_gamma):
        raise ValueError(f"{schema2_path}: gamma result is outside the declared basis.")

    combined: dict[tuple[str, str, str], dict[str, Fraction]] = {}
    for key in set(base_coeffs) | set(evaluated_gamma):
        base = base_coeffs.get(key, Fraction(0))
        kappa = evaluated_gamma.get(key, Fraction(0))
        if base or kappa:
            combined[key] = {"base_coeff": base, "kappa_coeff": kappa}

    parity = schema1["parity"] | {"K": 0}
    _verify_graded_skew(combined, parity)

    generator_order = base_generators + ["K"]
    positions = {label: index for index, label in enumerate(generator_order)}
    pair_positions = {label: index for index, label in enumerate(base_generators)}
    constants = [
        {
            "X": left,
            "Y": right,
            "Z": result,
            "base_coeff": _fraction_string(coeffs["base_coeff"]),
            "kappa_coeff": _fraction_string(coeffs["kappa_coeff"]),
            "sign_rule": "graded",
        }
        for (left, right, result), coeffs in sorted(
            combined.items(),
            key=lambda item: (
                pair_positions[item[0][0]],
                pair_positions[item[0][1]],
                positions[item[0][2]],
            ),
        )
    ]

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "osp": f"osp(2|{2 * n})",
        },
        "source_schemas": {
            "schema_1": schema1_path.name,
            "schema_2": schema2_path.name,
        },
        "gb_assignment": {
            "profile": "all_plus",
            "shape": [2, 2 * n],
            "row_labels": rows,
            "column_labels": columns,
            "entries": [[1] * (2 * n), [1] * (2 * n)],
        },
        "evaluation": {
            "substitution": "All gb parameters are set to +1.",
            "kappa": "Formal odd central element with kappa^2 = 0.",
            "expression": "base_coeff + kappa * kappa_coeff",
            "coefficient_order": "kappa is factored to the left.",
        },
        "structure_constants": constants,
        "metadata": {
            "generated_by": "src/evaluate_C_structure.py",
            "generation_date": date.today().isoformat(),
            "profile": "all_plus",
        },
    }


def generate_files(data_dir: Path = Path("data")) -> list[Path]:
    evaluated = [
        (n, build_evaluated_schema(n, data_dir)) for n in (1, 2, 3)
    ]
    written = []
    for n, schema in evaluated:
        destination = data_dir / f"C_{n}_evaluated_all_plus.json"
        destination.write_text(
            json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written.append(destination)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data",
        help="Directory containing Schemas 1 and 2 and receiving Schema 3 files",
    )
    args = parser.parse_args()
    for path in generate_files(args.data_dir):
        print(path)


if __name__ == "__main__":
    main()
