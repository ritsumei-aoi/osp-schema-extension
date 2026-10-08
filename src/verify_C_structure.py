"""Verify graded skew-symmetry and the super Jacobi identity in C schemas."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class VerificationError(ValueError):
    pass


def _add_scaled(target: dict[str, Fraction], source: dict[str, Fraction], scale: Fraction) -> None:
    for label, coefficient in source.items():
        target[label] = target.get(label, Fraction(0)) + scale * coefficient
        if not target[label]:
            del target[label]


def verify_file(path: Path) -> dict:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read JSON from {path}: {exc}") from exc

    basis = schema.get("basis", {})
    labels = basis.get("odd", []) + basis.get("even", [])
    parity = schema.get("parity", {})
    constants = schema.get("structure_constants", [])
    if not labels or set(labels) != set(parity):
        raise VerificationError(f"{path}: basis and parity map do not agree")

    order = {label: index for index, label in enumerate(labels)}
    brackets: dict[tuple[str, str], dict[str, Fraction]] = {}
    for entry in constants:
        try:
            x, y, z = entry["X"], entry["Y"], entry["Z"]
            coefficient = Fraction(entry["coeff"])
        except (KeyError, ValueError, ZeroDivisionError, TypeError) as exc:
            raise VerificationError(f"{path}: malformed structure constant {entry!r}") from exc
        if x not in order or y not in order or z not in order:
            raise VerificationError(f"{path}: structure constant references an unknown generator")
        if order[x] > order[y]:
            raise VerificationError(f"{path}: pair ({x}, {y}) is not in canonical order")
        if not coefficient:
            raise VerificationError(f"{path}: zero coefficient stored for ({x}, {y}, {z})")
        pair = (x, y)
        outputs = brackets.setdefault(pair, {})
        if z in outputs:
            raise VerificationError(f"{path}: duplicate output {z} for pair ({x}, {y})")
        outputs[z] = coefficient

    def bracket(x: str, y: str) -> dict[str, Fraction]:
        if (x, y) in brackets:
            return brackets[x, y]
        if (y, x) not in brackets:
            return {}
        sign = -1 if parity[x] * parity[y] == 0 else 1
        return {z: sign * coefficient for z, coefficient in brackets[y, x].items()}

    antisymmetry_checks = 0
    failures: list[str] = []
    for x in labels:
        for y in labels:
            lhs = bracket(y, x)
            sign = -1 if parity[x] * parity[y] == 0 else 1
            rhs = {z: sign * coefficient for z, coefficient in bracket(x, y).items()}
            antisymmetry_checks += 1
            if lhs != rhs:
                failures.append(f"graded skew-symmetry fails for ({x}, {y})")

    jacobi_checks = 0
    for x in labels:
        for y in labels:
            for z in labels:
                signs = (
                    -1 if parity[x] * parity[z] else 1,
                    -1 if parity[y] * parity[x] else 1,
                    -1 if parity[z] * parity[y] else 1,
                )
                jacobi: dict[str, Fraction] = {}
                for outer, inner_left, inner_right, sign in (
                    (x, y, z, signs[0]),
                    (y, z, x, signs[1]),
                    (z, x, y, signs[2]),
                ):
                    for inner, coefficient in bracket(inner_left, inner_right).items():
                        _add_scaled(jacobi, bracket(outer, inner), sign * coefficient)
                jacobi_checks += 1
                if jacobi:
                    failures.append(f"super Jacobi fails for ({x}, {y}, {z}): {jacobi}")

    dimension = schema.get("algebra", {}).get("dimension", {}).get("total")
    if dimension != len(labels):
        failures.append(f"declared dimension {dimension} does not match basis size {len(labels)}")
    return {
        "path": path,
        "n": schema.get("algebra", {}).get("n"),
        "dimension": len(labels),
        "structure_constants": len(constants),
        "antisymmetry_checks": antisymmetry_checks,
        "jacobi_checks": jacobi_checks,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        default=[ROOT / "data" / f"C_{n}_structure.json" for n in (1, 2, 3)],
    )
    args = parser.parse_args()
    reports = []
    for path in args.files:
        try:
            report = verify_file(path)
        except VerificationError as exc:
            print(f"FAIL {path}: {exc}")
            return 1
        reports.append(report)
        status = "PASS" if not report["failures"] else "FAIL"
        print(
            f"{status} {path}: n={report['n']}, dimension={report['dimension']}, "
            f"structure_constants={report['structure_constants']}, "
            f"antisymmetry_pairs={report['antisymmetry_checks']}, "
            f"Jacobi_triples={report['jacobi_checks']}"
        )
        for failure in report["failures"][:20]:
            print(f"  {failure}")
        if report["failures"]:
            remaining = len(report["failures"]) - 20
            if remaining > 0:
                print(f"  ... and {remaining} additional failures")
    return int(any(report["failures"] for report in reports))


if __name__ == "__main__":
    sys.exit(main())
