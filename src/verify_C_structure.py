"""Verify graded skew-symmetry and the Super Jacobi identity in C(n+1) JSON."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


def _add_scaled(
    target: dict[str, Fraction],
    source: dict[str, Fraction],
    scale: Fraction = Fraction(1),
) -> None:
    for label, coefficient in source.items():
        target[label] += scale * coefficient
        if not target[label]:
            del target[label]


def _scale(
    source: dict[str, Fraction], factor: Fraction
) -> dict[str, Fraction]:
    return {
        label: coefficient * factor
        for label, coefficient in source.items()
        if coefficient * factor
    }


def verify_structure(data: dict) -> dict:
    """Return exact graded-skew and super-Jacobi verification results."""
    even = data["basis"]["even"]
    odd = data["basis"]["odd"]
    labels = even + odd
    label_set = set(labels)
    parity = data["parity"]

    if len(label_set) != len(labels):
        raise ValueError("Basis contains duplicate generator labels")
    if set(parity) != label_set:
        raise ValueError("Parity keys do not match the basis generator labels")
    if any(parity[label] not in (0, 1) for label in labels):
        raise ValueError("Generator parity must be 0 or 1")

    brackets: dict[tuple[str, str], dict[str, Fraction]] = {}
    duplicate_records = []
    for entry in data["structure_constants"]:
        left = entry["X"]
        right = entry["Y"]
        result = entry["Z"]
        if left not in label_set or right not in label_set or result not in label_set:
            raise ValueError(f"Structure constant references unknown generator: {entry}")
        key = (left, right)
        value = Fraction(entry["coeff"])
        bracket = brackets.setdefault(key, {})
        if result in bracket:
            duplicate_records.append((left, right, result))
        bracket[result] = bracket.get(result, Fraction(0)) + value

    antisymmetry_failures = []
    for left in labels:
        for right in labels:
            factor = 1 if parity[left] * parity[right] % 2 else -1
            expected = _scale(brackets.get((right, left), {}), Fraction(factor))
            actual = brackets.get((left, right), {})
            if actual != expected:
                if len(antisymmetry_failures) < 10:
                    differing_results = set(actual) | set(expected)
                    difference = {
                        result: (
                            actual.get(result, Fraction(0)),
                            expected.get(result, Fraction(0)),
                        )
                        for result in differing_results
                        if actual.get(result, Fraction(0))
                        != expected.get(result, Fraction(0))
                    }
                    antisymmetry_failures.append((left, right, difference))

    def bracket_vector(left: str, right_vector: dict[str, Fraction]) -> dict[str, Fraction]:
        result: dict[str, Fraction] = defaultdict(Fraction)
        for right, coefficient in right_vector.items():
            for output, bracket_coefficient in brackets.get((left, right), {}).items():
                result[output] += coefficient * bracket_coefficient
        return {label: coefficient for label, coefficient in result.items() if coefficient}

    jacobi_failure_count = 0
    jacobi_failure_examples = []
    for x in labels:
        for y in labels:
            for z in labels:
                first_sign = Fraction(-1 if parity[x] * parity[z] % 2 else 1)
                second_sign = Fraction(-1 if parity[y] * parity[x] % 2 else 1)
                third_sign = Fraction(-1 if parity[z] * parity[y] % 2 else 1)

                jacobi: dict[str, Fraction] = defaultdict(Fraction)
                _add_scaled(jacobi, bracket_vector(x, brackets.get((y, z), {})), first_sign)
                _add_scaled(jacobi, bracket_vector(y, brackets.get((z, x), {})), second_sign)
                _add_scaled(jacobi, bracket_vector(z, brackets.get((x, y), {})), third_sign)
                if jacobi:
                    jacobi_failure_count += 1
                    if len(jacobi_failure_examples) < 10:
                        jacobi_failure_examples.append((x, y, z, dict(jacobi)))

    return {
        "generator_count": len(labels),
        "ordered_pairs_checked": len(labels) ** 2,
        "ordered_triples_checked": len(labels) ** 3,
        "unique_ordered_brackets": len(brackets),
        "duplicate_records": duplicate_records,
        "antisymmetry_failures": antisymmetry_failures,
        "jacobi_failure_count": jacobi_failure_count,
        "jacobi_failure_examples": jacobi_failure_examples,
    }


def verify_file(path: Path) -> tuple[int, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    result = verify_structure(data)
    return data["algebra"]["n"], result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
    )
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    arguments = parser.parse_args()

    overall_pass = True
    for n in arguments.ranks:
        path = arguments.data_dir / f"C_{n}_structure.json"
        rank, result = verify_file(path)
        antisymmetry_pass = not result["antisymmetry_failures"]
        jacobi_pass = result["jacobi_failure_count"] == 0
        rank_pass = (
            antisymmetry_pass
            and jacobi_pass
            and not result["duplicate_records"]
        )
        overall_pass = overall_pass and rank_pass

        print(
            f"C_{rank}: {'PASS' if rank_pass else 'FAIL'}; "
            f"generators={result['generator_count']}, "
            f"ordered_pairs={result['ordered_pairs_checked']}, "
            f"ordered_brackets={result['unique_ordered_brackets']}, "
            f"ordered_triples={result['ordered_triples_checked']}"
        )
        print(
            f"  graded skew-symmetry: "
            f"{'PASS' if antisymmetry_pass else 'FAIL'} "
            f"({len(result['antisymmetry_failures'])} failure examples)"
        )
        print(
            f"  Super Jacobi: "
            f"{'PASS' if jacobi_pass else 'FAIL'} "
            f"({result['jacobi_failure_count']} failing triples)"
        )

        if result["duplicate_records"]:
            print(f"  duplicate records: {result['duplicate_records'][:10]}")
        if result["antisymmetry_failures"]:
            print("  graded skew-symmetry examples:")
            for failure in result["antisymmetry_failures"]:
                print(f"    {failure}")
        if result["jacobi_failure_examples"]:
            print("  Super Jacobi examples:")
            for failure in result["jacobi_failure_examples"]:
                print(f"    {failure}")
        if not antisymmetry_pass:
            print(
                "  diagnosis: inspect ordered-pair coverage, generator parity, "
                "and graded sign handling."
            )
        if not jacobi_pass and antisymmetry_pass:
            print(
                "  diagnosis: the bracket table is graded-skew but not Lie-superalgebra "
                "consistent; inspect oscillator realizations and structure coefficients."
            )

    print(f"Overall: {'PASS' if overall_pass else 'FAIL'}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
