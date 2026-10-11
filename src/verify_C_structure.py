#!/usr/bin/env python3
"""Strictly verify generated C(n+1) Schema 1 structure constants."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

if __package__:
    from .C_generators import graded_bracket, normal_order_word
else:
    from C_generators import graded_bracket, normal_order_word

Polynomial = dict[tuple[str, ...], Fraction]


class VerificationError(ValueError):
    """Raised when a Schema 1 file fails mathematical or structural checks."""


@dataclass(frozen=True)
class VerificationReport:
    source: str
    dimension: int
    nonzero_records: int
    ordered_pairs: int
    ordered_triples: int


def _add_scaled(
    target: Polynomial,
    source: Polynomial,
    scale: Fraction,
) -> None:
    for word, coefficient in source.items():
        total = target.get(word, Fraction()) + scale * coefficient
        if total:
            target[word] = total
        else:
            target.pop(word, None)


def _polynomial_from_realization(realization: dict[str, Any], label: str) -> Polynomial:
    standard_form = realization.get("standard_form")
    if not isinstance(standard_form, list):
        raise VerificationError(f"{label}: standard_form must be a list")

    polynomial: Polynomial = {}
    for term in standard_form:
        if not isinstance(term, dict) or not {"words", "coeff"} <= set(term):
            raise VerificationError(f"{label}: malformed standard_form term {term!r}")
        if not isinstance(term["words"], list) or not all(
            isinstance(word, str) for word in term["words"]
        ):
            raise VerificationError(f"{label}: oscillator words must be string lists")
        try:
            coefficient = Fraction(term["coeff"])
        except (TypeError, ValueError, ZeroDivisionError) as error:
            raise VerificationError(
                f"{label}: invalid rational coefficient {term['coeff']!r}"
            ) from error
        for word, factor in normal_order_word(term["words"]).items():
            polynomial[word] = polynomial.get(word, Fraction()) + coefficient * factor
            if not polynomial[word]:
                del polynomial[word]
    return polynomial


def _combine_generator_polynomials(
    coefficients: dict[str, Fraction],
    polynomials: dict[str, Polynomial],
) -> Polynomial:
    result: Polynomial = {}
    for label, coefficient in coefficients.items():
        _add_scaled(result, polynomials[label], coefficient)
    return result


def _record_data(
    schema: dict[str, Any],
) -> tuple[
    list[str],
    dict[str, int],
    dict[str, Polynomial],
    dict[tuple[str, str], dict[str, Fraction]],
]:
    try:
        basis = schema["basis"]
        even = basis["even"]
        odd = basis["odd"]
        parity = schema["parity"]
        realizations = schema["generator_realization"]["realizations"]
        records = schema["structure_constants"]
    except (KeyError, TypeError) as error:
        raise VerificationError(f"missing or malformed Schema 1 fields: {error}") from error

    if not isinstance(even, list) or not isinstance(odd, list):
        raise VerificationError("basis.even and basis.odd must be arrays")
    if not all(isinstance(label, str) for label in even + odd):
        raise VerificationError("basis labels must be strings")
    labels = odd + even
    if len(set(labels)) != len(labels):
        raise VerificationError("basis contains duplicate labels")
    if not isinstance(parity, dict) or set(parity) != set(labels):
        raise VerificationError("parity keys must match the complete basis")
    if any(parity[label] not in (0, 1) for label in labels):
        raise VerificationError("basis parities must be 0 or 1")
    if any(parity[label] != 0 for label in even):
        raise VerificationError("an even basis generator has odd parity")
    if any(parity[label] != 1 for label in odd):
        raise VerificationError("an odd basis generator has even parity")
    if not isinstance(realizations, dict) or set(realizations) != set(labels):
        raise VerificationError("realizations must cover the complete basis")
    if not isinstance(records, list):
        raise VerificationError("structure_constants must be an array")

    polynomials = {
        label: _polynomial_from_realization(realizations[label], label)
        for label in labels
    }
    if any(not polynomial for polynomial in polynomials.values()):
        raise VerificationError("a basis generator has a zero oscillator realization")

    records_by_pair: dict[tuple[str, str], dict[str, Fraction]] = defaultdict(dict)
    seen: set[tuple[str, str, str]] = set()
    required_record_keys = {"X", "Y", "Z", "coeff", "sign_rule"}
    for record in records:
        if not isinstance(record, dict) or set(record) != required_record_keys:
            raise VerificationError(f"malformed structure-constant record: {record!r}")
        x, y, z = record["X"], record["Y"], record["Z"]
        if x not in parity or y not in parity or z not in parity:
            raise VerificationError(f"record refers to a non-basis label: {record!r}")
        if record["sign_rule"] != "graded":
            raise VerificationError(f"unsupported sign_rule in record: {record!r}")
        try:
            coefficient = Fraction(record["coeff"])
        except (TypeError, ValueError, ZeroDivisionError) as error:
            raise VerificationError(
                f"invalid structure-constant coefficient: {record!r}"
            ) from error
        if not coefficient:
            raise VerificationError(f"zero coefficient must not be serialized: {record!r}")
        key = (x, y, z)
        if key in seen:
            raise VerificationError(f"duplicate structure-constant record: {record!r}")
        seen.add(key)
        records_by_pair[(x, y)][z] = coefficient

    return labels, parity, polynomials, records_by_pair


def verify_schema(
    schema: dict[str, Any],
    source: str = "<memory>",
) -> VerificationReport:
    """Verify explicit directed records, graded anti-symmetry, and Super Jacobi."""
    if not isinstance(schema, dict):
        raise VerificationError(f"{source}: schema root must be an object")
    labels, parity, polynomials, records_by_pair = _record_data(schema)

    for (x, y), outputs in records_by_pair.items():
        if x == y:
            continue
        for z, coefficient in outputs.items():
            reverse = records_by_pair.get((y, x), {})
            if z not in reverse:
                raise VerificationError(
                    f"{source}: Missing explicit reverse-order record "
                    f"({y}, {x}, {z}) for ({x}, {y}, {z})"
                )
            expected = -((-1) ** (parity[x] * parity[y])) * coefficient
            if reverse[z] != expected:
                raise VerificationError(
                    f"{source}: Wrong reverse-order coefficient for "
                    f"({y}, {x}, {z}): expected {expected}, got {reverse[z]}"
                )

    dimension = len(labels)
    for x in labels:
        for y in labels:
            direct = graded_bracket(
                polynomials[x],
                polynomials[y],
                parity[x],
                parity[y],
            )
            serialized = _combine_generator_polynomials(
                records_by_pair.get((x, y), {}),
                polynomials,
            )
            if direct != serialized:
                raise VerificationError(
                    f"{source}: serialized bracket does not match oscillator "
                    f"realizations for ({x}, {y})"
                )

            reverse = records_by_pair.get((y, x), {})
            factor = -((-1) ** (parity[x] * parity[y]))
            expected = {label: factor * value for label, value in reverse.items()}
            if records_by_pair.get((x, y), {}) != expected:
                raise VerificationError(
                    f"{source}: graded anti-symmetry fails for ({x}, {y})"
                )

    def bracket(x: str, y: str) -> dict[str, Fraction]:
        return records_by_pair.get((x, y), {})

    def bracket_with_element(
        x: str,
        element: dict[str, Fraction],
    ) -> dict[str, Fraction]:
        result: dict[str, Fraction] = {}
        for inner, coefficient in element.items():
            _add_scaled(result, bracket(x, inner), coefficient)
        return result

    for x, y, z in product(labels, repeat=3):
        px, py, pz = parity[x], parity[y], parity[z]
        jacobi: dict[str, Fraction] = {}
        terms = (
            ((-1) ** (px * pz), x, bracket(y, z)),
            ((-1) ** (py * px), y, bracket(z, x)),
            ((-1) ** (pz * py), z, bracket(x, y)),
        )
        for sign, outer, inner in terms:
            _add_scaled(
                jacobi,
                bracket_with_element(outer, inner),
                Fraction(sign),
            )
        if jacobi:
            raise VerificationError(
                f"{source}: Super Jacobi fails for ({x}, {y}, {z}): {jacobi}"
            )

    record_count = sum(len(outputs) for outputs in records_by_pair.values())
    return VerificationReport(
        source=source,
        dimension=dimension,
        nonzero_records=record_count,
        ordered_pairs=dimension**2,
        ordered_triples=dimension**3,
    )


def verify_file(path: str | Path) -> VerificationReport:
    """Load and verify one generated Schema 1 JSON file."""
    input_path = Path(path)
    try:
        schema = json.loads(input_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise VerificationError(f"{input_path}: could not load JSON: {error}") from error
    return verify_schema(schema, source=str(input_path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify C(n+1) structure constants for graded anti-symmetry and Super Jacobi."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Directory containing C_{n}_structure.json files.",
    )
    args = parser.parse_args(argv)

    failures = 0
    for n in (1, 2, 3):
        path = args.data_dir / f"C_{n}_structure.json"
        try:
            report = verify_file(path)
        except VerificationError as error:
            print(f"FAIL {path}: {error}")
            failures += 1
            continue
        print(
            f"PASS {report.source}: dimension={report.dimension}, "
            f"records={report.nonzero_records}, "
            f"ordered_pairs={report.ordered_pairs}, "
            f"ordered_triples={report.ordered_triples}"
        )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
