"""Verify graded antisymmetry and the super-Jacobi identity for C(n+1) data."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any

Vector = dict[str, Fraction]
BracketTable = dict[tuple[str, str], Vector]


def _pbw_order(n: int) -> list[str]:
    negative_odd = [
        f"E_eps1_del{k}_{suffix}"
        for k in range(1, n + 1)
        for suffix in ("mp", "mm")
    ]
    negative_even = [
        f"E_del{i}_del{j}_{suffix}"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
        for suffix in ("mp", "mm")
    ] + [f"E_2del{k}_m" for k in range(1, n + 1)]
    cartan = [f"H_{k}" for k in range(1, n + 2)]
    positive_even = [
        f"E_del{i}_del{j}_{suffix}"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
        for suffix in ("pm", "pp")
    ] + [f"E_2del{k}_p" for k in range(1, n + 1)]
    positive_odd = [
        f"E_eps1_del{k}_{suffix}"
        for k in range(1, n + 1)
        for suffix in ("pm", "pp")
    ]
    return negative_odd + negative_even + cartan + positive_even + positive_odd


def _load_structure(path: Path) -> tuple[list[str], dict[str, int], BracketTable]:
    data = json.loads(path.read_text(encoding="utf-8"))
    n = data["algebra"]["n"]
    if data["algebra"]["family"] != "C" or data["algebra"]["m"] != 1:
        raise ValueError(f"{path}: expected a C(n+1) schema with m=1")

    order = _pbw_order(n)
    even = data["basis"]["even"]
    odd = data["basis"]["odd"]
    expected_labels = set(order)
    if set(even) | set(odd) != expected_labels:
        raise ValueError(f"{path}: basis labels do not match rank-{n} PBW basis")
    if set(even) & set(odd):
        raise ValueError(f"{path}: a generator appears in both parity lists")

    parity = data["parity"]
    if set(parity) != expected_labels:
        raise ValueError(f"{path}: parity map does not cover exactly the basis")
    if any(parity[label] != 0 for label in even) or any(
        parity[label] != 1 for label in odd
    ):
        raise ValueError(f"{path}: basis lists disagree with parity map")

    order_index = {label: index for index, label in enumerate(order)}
    brackets: defaultdict[tuple[str, str], dict[str, Fraction]] = defaultdict(dict)
    for entry in data["structure_constants"]:
        left, right, result = entry["X"], entry["Y"], entry["Z"]
        if left not in order_index or right not in order_index or result not in order_index:
            raise ValueError(f"{path}: structure constant references an unknown generator")
        if order_index[left] > order_index[right]:
            raise ValueError(f"{path}: pair ({left}, {right}) is not in PBW order")
        if entry["sign_rule"] != "graded":
            raise ValueError(f"{path}: unsupported sign rule {entry['sign_rule']!r}")
        coefficient = Fraction(entry["coeff"])
        if not coefficient:
            raise ValueError(f"{path}: zero coefficient stored for ({left}, {right}, {result})")
        key = (left, right)
        if result in brackets[key]:
            raise ValueError(f"{path}: duplicate output term for ({left}, {right}, {result})")
        brackets[key][result] = coefficient
        if parity[result] != (parity[left] + parity[right]) % 2:
            raise ValueError(
                f"{path}: parity mismatch in [{left}, {right}] = {result}"
            )
    return order, parity, dict(brackets)


def _bracket(
    left: str,
    right: str,
    parity: dict[str, int],
    order_index: dict[str, int],
    brackets: BracketTable,
) -> Vector:
    if order_index[left] <= order_index[right]:
        return brackets.get((left, right), {})
    canonical = brackets.get((right, left), {})
    sign = -1 if parity[left] * parity[right] % 2 else 1
    return {label: -sign * value for label, value in canonical.items()}


def _bracket_linear(
    left: str,
    right_vector: Vector,
    parity: dict[str, int],
    order_index: dict[str, int],
    brackets: BracketTable,
) -> Vector:
    result: defaultdict[str, Fraction] = defaultdict(Fraction)
    for right, coefficient in right_vector.items():
        for label, value in _bracket(
            left, right, parity, order_index, brackets
        ).items():
            result[label] += coefficient * value
    return {label: value for label, value in result.items() if value}


def verify_file(path: Path) -> dict[str, Any]:
    order, parity, brackets = _load_structure(path)
    order_index = {label: index for index, label in enumerate(order)}
    failures: list[str] = []
    pair_checks = 0

    for left in order:
        for right in order:
            pair_checks += 1
            forward = _bracket(left, right, parity, order_index, brackets)
            reverse = _bracket(right, left, parity, order_index, brackets)
            expected = {
                label: -((-1) ** (parity[left] * parity[right])) * coefficient
                for label, coefficient in reverse.items()
            }
            if forward != expected:
                if len(failures) < 20:
                    failures.append(
                        f"graded antisymmetry failed for ({left}, {right}): "
                        f"{forward} != {expected}"
                    )
            if left == right and parity[left] == 0 and forward:
                if len(failures) < 20:
                    failures.append(
                        f"even diagonal bracket is nonzero for {left}: {forward}"
                    )

    triple_checks = 0
    for x in order:
        for y in order:
            for z in order:
                triple_checks += 1
                terms = (
                    _bracket_linear(
                        x, _bracket(y, z, parity, order_index, brackets),
                        parity, order_index, brackets,
                    ),
                    _bracket_linear(
                        y, _bracket(z, x, parity, order_index, brackets),
                        parity, order_index, brackets,
                    ),
                    _bracket_linear(
                        z, _bracket(x, y, parity, order_index, brackets),
                        parity, order_index, brackets,
                    ),
                )
                signs = (
                    (-1) ** (parity[x] * parity[z]),
                    (-1) ** (parity[y] * parity[x]),
                    (-1) ** (parity[z] * parity[y]),
                )
                total: defaultdict[str, Fraction] = defaultdict(Fraction)
                for sign, vector in zip(signs, terms):
                    for label, coefficient in vector.items():
                        total[label] += sign * coefficient
                nonzero = {label: value for label, value in total.items() if value}
                if nonzero and len(failures) < 20:
                    failures.append(
                        f"super-Jacobi failed for ({x}, {y}, {z}): {nonzero}"
                    )

    return {
        "file": path.name,
        "pass": not failures,
        "generator_count": len(order),
        "pair_checks": pair_checks,
        "triple_checks": triple_checks,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
    )
    args = parser.parse_args()

    overall_pass = True
    for n in (1, 2, 3):
        path = args.data_dir / f"C_{n}_structure.json"
        if not path.is_file():
            print(f"{path.name}: FAIL; file not found at {path}")
            overall_pass = False
            continue
        report = verify_file(path)
        status = "PASS" if report["pass"] else "FAIL"
        print(
            f"{report['file']}: {status}; generators={report['generator_count']}, "
            f"antisymmetry pairs={report['pair_checks']}, "
            f"super-Jacobi triples={report['triple_checks']}"
        )
        for failure in report["failures"]:
            print(f"  {failure}")
        overall_pass = overall_pass and report["pass"]
    print(f"Overall: {'PASS' if overall_pass else 'FAIL'}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
