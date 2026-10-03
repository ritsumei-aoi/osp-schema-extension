"""Verify graded anti-symmetry and super-Jacobi for generated C(n+1) data."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path


Bracket = dict[str, Fraction]
BracketTable = dict[tuple[str, str], Bracket]


def _add_scaled(target: Bracket, source: Bracket, scale: Fraction) -> None:
    for label, coeff in source.items():
        target[label] = target.get(label, Fraction(0)) + scale * coeff
        if not target[label]:
            del target[label]


def _format_bracket(bracket: Bracket) -> str:
    if not bracket:
        return "0"
    terms = ", ".join(
        f"{label}: {coeff}" for label, coeff in sorted(bracket.items())
    )
    return "{" + terms + "}"


def _load_schema(path: Path) -> tuple[list[str], dict[str, int], BracketTable]:
    data = json.loads(path.read_text(encoding="utf-8"))
    labels = data["basis"]["odd"] + data["basis"]["even"]
    parity = data["parity"]
    if set(labels) != set(parity):
        raise ValueError(f"{path}: basis and parity entries do not match.")

    brackets: defaultdict[tuple[str, str], Bracket] = defaultdict(dict)
    for row in data["structure_constants"]:
        key = row["X"], row["Y"]
        result = row["Z"]
        if row.get("sign_rule") != "graded":
            raise ValueError(f"{path}: unexpected sign_rule in {row!r}.")
        coeff = Fraction(row["coeff"])
        brackets[key][result] = brackets[key].get(result, Fraction(0)) + coeff
        if not brackets[key][result]:
            del brackets[key][result]
    return labels, parity, dict(brackets)


def _check_antisymmetry(
    labels: list[str], parity: dict[str, int], brackets: BracketTable
) -> list[str]:
    failures = []
    for left, right in product(labels, repeat=2):
        actual = brackets.get((left, right), {})
        reverse = brackets.get((right, left), {})
        factor = Fraction(-1 if parity[left] * parity[right] == 0 else 1)
        expected = {label: factor * coeff for label, coeff in reverse.items()}
        if actual != expected:
            failures.append(
                f"[{left},{right}): expected {_format_bracket(expected)}, "
                f"found {_format_bracket(actual)}"
            )
    return failures


def _bracket_linear(
    left: str, right_terms: Bracket, brackets: BracketTable
) -> Bracket:
    result: Bracket = {}
    for right, scale in right_terms.items():
        _add_scaled(result, brackets.get((left, right), {}), scale)
    return result


def _check_super_jacobi(
    labels: list[str],
    parity: dict[str, int],
    brackets: BracketTable,
) -> list[str]:
    failures = []
    for x, y, z in product(labels, repeat=3):
        jacobi: Bracket = {}
        cyclic_terms = (
            (
                x,
                brackets.get((y, z), {}),
                -1 if parity[x] * parity[z] else 1,
            ),
            (
                y,
                brackets.get((z, x), {}),
                -1 if parity[y] * parity[x] else 1,
            ),
            (
                z,
                brackets.get((x, y), {}),
                -1 if parity[z] * parity[y] else 1,
            ),
        )
        for outer, inner, sign in cyclic_terms:
            _add_scaled(
                jacobi,
                _bracket_linear(outer, inner, brackets),
                Fraction(sign),
            )
        if jacobi:
            failures.append(
                f"({x},{y},{z}): Jacobi sum {_format_bracket(jacobi)}"
            )
    return failures


def verify_file(path: Path) -> tuple[int, int, list[str], list[str]]:
    labels, parity, brackets = _load_schema(path)
    anti_failures = _check_antisymmetry(labels, parity, brackets)
    jacobi_failures = _check_super_jacobi(labels, parity, brackets)
    return len(labels) ** 2, len(labels) ** 3, anti_failures, jacobi_failures


def verify_all(data_dir: Path) -> bool:
    all_passed = True
    for n in (1, 2, 3):
        path = data_dir / f"C_{n}_structure.json"
        if not path.is_file():
            print(f"{path}: FAIL (file not found)")
            all_passed = False
            continue
        try:
            pair_count, triple_count, anti_failures, jacobi_failures = verify_file(path)
        except (KeyError, ValueError, json.JSONDecodeError) as error:
            print(f"{path}: FAIL (invalid schema data: {error})")
            all_passed = False
            continue

        passed = not anti_failures and not jacobi_failures
        status = "PASS" if passed else "FAIL"
        print(
            f"{path}: {status} — checked {pair_count} ordered pairs and "
            f"{triple_count} triples; anti-symmetry failures: "
            f"{len(anti_failures)}, super-Jacobi failures: {len(jacobi_failures)}"
        )
        for failure in anti_failures[:5]:
            print(f"  anti-symmetry: {failure}")
        if len(anti_failures) > 5:
            print(f"  ... and {len(anti_failures) - 5} more anti-symmetry failures")
        for failure in jacobi_failures[:5]:
            print(f"  super-Jacobi: {failure}")
        if len(jacobi_failures) > 5:
            print(f"  ... and {len(jacobi_failures) - 5} more super-Jacobi failures")
        all_passed = all_passed and passed
    return all_passed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data",
        help="Directory containing C_1_structure.json through C_3_structure.json",
    )
    args = parser.parse_args()
    raise SystemExit(0 if verify_all(args.data_dir) else 1)


if __name__ == "__main__":
    main()
