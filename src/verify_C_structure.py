"""Verify graded skew-symmetry and super Jacobi for generated C structure files."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Iterable


Bracket = dict[tuple[str, str], dict[str, Fraction]]


def _add_scaled(
    target: dict[str, Fraction], source: dict[str, Fraction], scale: Fraction
) -> None:
    for label, coeff in source.items():
        target[label] = target.get(label, Fraction(0)) + scale * coeff
        if not target[label]:
            del target[label]


def _load_brackets(schema: dict) -> tuple[list[str], dict[str, int], Bracket, list[str]]:
    even = schema["basis"]["even"]
    odd = schema["basis"]["odd"]
    labels = odd + even
    parity = schema["parity"]
    label_order = {label: index for index, label in enumerate(labels)}
    errors: list[str] = []
    if set(parity) != set(labels):
        errors.append("parity map does not exactly cover the basis")

    brackets: Bracket = {}
    seen: set[tuple[str, str, str]] = set()
    pair_orientation: dict[frozenset[str], tuple[str, str]] = {}
    for index, item in enumerate(schema["structure_constants"]):
        x, y, z = item["X"], item["Y"], item["Z"]
        key = (x, y, z)
        if key in seen:
            errors.append(f"duplicate structure-constant term at index {index}: {key}")
            continue
        seen.add(key)
        if x not in parity or y not in parity or z not in parity:
            errors.append(f"unknown generator in structure-constant term at index {index}")
            continue
        if item.get("sign_rule") != "graded":
            errors.append(f"incorrect sign_rule at structure-constant index {index}")
        if label_order[x] > label_order[y]:
            errors.append(f"non-canonical generator pair at structure-constant index {index}")
        unordered_pair = frozenset((x, y))
        orientation = pair_orientation.setdefault(unordered_pair, (x, y))
        if orientation != (x, y):
            errors.append(f"generator pair is represented in both orientations: {unordered_pair}")
        coeff = Fraction(item["coeff"])
        brackets.setdefault((x, y), {})[z] = coeff
        if x != y:
            reverse_sign = -1 if parity[x] * parity[y] % 2 == 0 else 1
            reverse = brackets.setdefault((y, x), {})
            reverse[z] = reverse.get(z, Fraction(0)) + reverse_sign * coeff
            if not reverse[z]:
                del reverse[z]
    return labels, parity, brackets, errors


def verify_schema(schema: dict) -> dict:
    """Check every ordered pair and triple in one loaded Schema 1 object."""
    labels, parity, brackets, errors = _load_brackets(schema)

    checked_pairs = 0
    for x, y in product(labels, repeat=2):
        checked_pairs += 1
        relation = {}
        sign = -1 if parity[x] * parity[y] % 2 else 1
        _add_scaled(relation, brackets.get((x, y), {}), Fraction(1))
        _add_scaled(relation, brackets.get((y, x), {}), Fraction(sign))
        if relation:
            errors.append(f"graded skew-symmetry failed for ({x}, {y}): {relation}")

    checked_triples = 0
    for x, y, z in product(labels, repeat=3):
        checked_triples += 1
        jacobi: dict[str, Fraction] = {}
        terms = (
            (y, z, x, (-1) ** (parity[x] * parity[z])),
            (z, x, y, (-1) ** (parity[y] * parity[x])),
            (x, y, z, (-1) ** (parity[z] * parity[y])),
        )
        for inner_left, inner_right, outer, sign in terms:
            inner = brackets.get((inner_left, inner_right), {})
            nested: dict[str, Fraction] = {}
            for inner_result, inner_coeff in inner.items():
                for result, coeff in brackets.get((outer, inner_result), {}).items():
                    nested[result] = nested.get(result, Fraction(0)) + inner_coeff * coeff
            _add_scaled(jacobi, nested, Fraction(sign))
        if jacobi:
            errors.append(f"super Jacobi failed for ({x}, {y}, {z}): {jacobi}")

    return {
        "rank": schema["algebra"]["n"],
        "pairs_checked": checked_pairs,
        "triples_checked": checked_triples,
        "passed": not errors,
        "errors": errors,
    }


def verify_directory(data_dir: Path, ranks: Iterable[int] = (1, 2, 3)) -> list[dict]:
    reports = []
    for rank in ranks:
        path = data_dir / f"C_{rank}_structure.json"
        with path.open(encoding="utf-8") as source:
            schema = json.load(source)
        reports.append(verify_schema(schema))
    return reports


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    reports = verify_directory(args.data_dir)
    overall_pass = True
    for report in reports:
        status = "PASS" if report["passed"] else "FAIL"
        print(
            f"C_{report['rank']}: {status}; "
            f"{report['pairs_checked']} ordered pairs and "
            f"{report['triples_checked']} triples checked"
        )
        for error in report["errors"]:
            print(f"  {error}", file=sys.stderr)
        overall_pass = overall_pass and report["passed"]
    print(f"Overall: {'PASS' if overall_pass else 'FAIL'}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
