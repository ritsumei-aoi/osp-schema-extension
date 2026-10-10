#!/usr/bin/env python3
"""Generate and verify symbolic Schema 4 coboundary data for C(n+1)."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from C_gamma import _load_structure
from C_generators import (
    AlgebraBasis,
    build_basis,
    generate_structure_constants,
)


def _format_fraction(value: Fraction) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def _parameter_for(source: str, target: str, source_parity: int) -> str:
    family = "phi" if source_parity == 0 else "psi"
    return f"{family}__{target}__from__{source}"


def _map_images(
    basis: AlgebraBasis,
) -> tuple[dict[str, tuple[tuple[str, str], ...]], list[dict[str, str]]]:
    images: dict[str, tuple[tuple[str, str], ...]] = {}
    coefficients: list[dict[str, str]] = []
    for source_labels, target_labels, source_parity in (
        (basis.even, basis.odd, 0),
        (basis.odd, basis.even, 1),
    ):
        for source in source_labels:
            image = []
            for target in target_labels:
                parameter = _parameter_for(source, target, source_parity)
                image.append((target, parameter))
                coefficients.append(
                    {
                        "parameter": parameter,
                        "source": source,
                        "target": target,
                    }
                )
            images[source] = tuple(image)
    return images, coefficients


def _structure_map(
    structure_data: dict[str, object], basis: AlgebraBasis
) -> dict[tuple[str, str], dict[str, Fraction]]:
    records = structure_data.get("structure_constants")
    if not isinstance(records, list):
        raise ValueError("Schema 1 structure_constants must be a list")

    result: dict[tuple[str, str], dict[str, Fraction]] = {}
    allowed = set(basis.parity)
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(
                f"Schema 1 structure_constants[{index}] must be an object"
            )
        try:
            left, right, output = record["X"], record["Y"], record["Z"]
            coefficient = Fraction(record["coeff"])
            sign_rule = record["sign_rule"]
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"Invalid Schema 1 structure_constants[{index}]") from exc
        if (
            not all(isinstance(label, str) for label in (left, right, output))
            or
            left not in allowed
            or right not in allowed
            or output not in allowed
            or not isinstance(sign_rule, str)
            or sign_rule != "graded"
            or not coefficient
        ):
            raise ValueError(
                f"Invalid Schema 1 bracket entry at index {index}"
            )
        expected_parity = (basis.parity[left] + basis.parity[right]) % 2
        if basis.parity[output] != expected_parity:
            raise ValueError(f"Schema 1 bracket parity mismatch at index {index}")
        outputs = result.setdefault((left, right), {})
        if output in outputs:
            raise ValueError(
                f"Duplicate Schema 1 bracket term {(left, right, output)}"
            )
        outputs[output] = coefficient

    expected: dict[tuple[str, str], dict[str, Fraction]] = {}
    for record in generate_structure_constants(basis):
        expected.setdefault((record["X"], record["Y"]), {})[record["Z"]] = Fraction(
            record["coeff"]
        )
    if result != expected:
        raise ValueError("Schema 1 brackets disagree with the generated C(n+1) basis")
    return result


def _derive_coboundary(
    basis: AlgebraBasis, structure_data: dict[str, object]
) -> tuple[list[dict[str, object]], int, int]:
    brackets = _structure_map(structure_data, basis)
    images, coefficients = _map_images(basis)
    parameters = [entry["parameter"] for entry in coefficients]
    records: list[dict[str, object]] = []
    term_count = 0
    checked_pairs = 0

    for left in basis.pbw:
        left_parity = basis.parity[left]
        for right in basis.pbw:
            right_parity = basis.parity[right]
            accumulated: dict[tuple[str, str], Fraction] = {}

            def add(output: str, parameter: str, coefficient: Fraction) -> None:
                key = (output, parameter)
                accumulated[key] = accumulated.get(key, Fraction()) + coefficient
                if not accumulated[key]:
                    del accumulated[key]

            first_factor = Fraction(-1 if left_parity else 1)
            for image_label, parameter in images[right]:
                for output, coefficient in brackets.get(
                    (left, image_label), {}
                ).items():
                    add(output, parameter, first_factor * coefficient)

            second_exponent = ((left_parity + 1) * right_parity) % 2
            second_factor = Fraction(1 if second_exponent else -1)
            for image_label, parameter in images[left]:
                for output, coefficient in brackets.get(
                    (right, image_label), {}
                ).items():
                    add(output, parameter, second_factor * coefficient)

            for intermediate, bracket_coefficient in brackets.get(
                (left, right), {}
            ).items():
                for output, parameter in images[intermediate]:
                    add(output, parameter, -bracket_coefficient)

            checked_pairs += 1
            for output in basis.pbw:
                terms = [
                    {
                        "parameter": parameter,
                        "scalar": _format_fraction(accumulated[(output, parameter)]),
                    }
                    for parameter in parameters
                    if (output, parameter) in accumulated
                ]
                if not terms:
                    continue
                if basis.parity[output] != (left_parity + right_parity + 1) % 2:
                    raise ValueError(
                        f"Odd coboundary output parity mismatch for [{left},{right}]"
                    )
                records.append(
                    {
                        "X": left,
                        "Y": right,
                        "Z": output,
                        "coeff": terms,
                        "sign_rule": "graded",
                    }
                )
                term_count += len(terms)
    return records, checked_pairs, term_count


def _validate_date(generation_date: str) -> str:
    try:
        parsed = date.fromisoformat(generation_date)
    except (TypeError, ValueError) as exc:
        raise ValueError("generation_date must use YYYY-MM-DD format") from exc
    if parsed.isoformat() != generation_date:
        raise ValueError("generation_date must use YYYY-MM-DD format")
    return generation_date


def build_coboundary_schema(
    basis: AlgebraBasis,
    structure_data: dict[str, object],
    generation_date: str | None = None,
) -> tuple[dict[str, object], int, int]:
    if generation_date is None:
        generation_date = date.today().isoformat()
    generation_date = _validate_date(generation_date)
    records, checked_pairs, term_count = _derive_coboundary(basis, structure_data)
    _, coefficients = _map_images(basis)
    even_count = len(basis.even)
    odd_count = len(basis.odd)
    return (
        {
            "schema_version": structure_data["schema_version"],
            "schema_layer": 4,
            "schema_type": "coboundary_structure",
            "algebra": structure_data["algebra"],
            "basis": structure_data["basis"],
            "parity": structure_data["parity"],
            "odd_linear_map": {
                "parity": 1,
                "global_scale": "1",
                "parameter_count": len(coefficients),
                "parameterization": (
                    "f(e_a) = sum_mu phi__o_mu__from__e_a * o_mu; "
                    "f(o_mu) = sum_a psi__e_a__from__o_mu * e_a"
                ),
                "coefficients": coefficients,
                "dimensions": {
                    "even_basis_count": even_count,
                    "odd_basis_count": odd_count,
                },
            },
            "coboundary_definition": (
                "(delta f)(X,Y) = (-1)^p(X)[X,f(Y)] "
                "- (-1)^((p(X)+1)p(Y))[Y,f(X)] - f([X,Y])"
            ),
            "coboundary_constants": records,
            "metadata": {
                "generated_by": "C_coboundary.py",
                "generation_date": generation_date,
                "source_schema": f"C_{basis.n}_structure.json",
                "references": [
                    "C(n+1) = osp(2|2n) mathematical definition",
                    "Coboundary operator definition (odd linear map)",
                ],
            },
        },
        checked_pairs,
        term_count,
    )


def _coefficient_map(
    records: object, basis: AlgebraBasis
) -> dict[tuple[str, str, str, str], Fraction]:
    if not isinstance(records, list):
        raise ValueError("coboundary_constants must be a list")
    allowed = set(basis.parity)
    result: dict[tuple[str, str, str, str], Fraction] = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"coboundary_constants[{index}] must be an object")
        try:
            left, right, output = record["X"], record["Y"], record["Z"]
            terms, sign_rule = record["coeff"], record["sign_rule"]
        except (KeyError, TypeError) as exc:
            raise ValueError(f"Invalid coboundary_constants[{index}]") from exc
        if (
            left not in allowed
            or right not in allowed
            or output not in allowed
            or sign_rule != "graded"
            or not isinstance(terms, list)
            or not terms
        ):
            raise ValueError(f"Invalid coboundary_constants[{index}]")
        if basis.parity[output] != (
            basis.parity[left] + basis.parity[right] + 1
        ) % 2:
            raise ValueError(
                f"Coboundary output parity mismatch at index {index}"
            )
        for term in terms:
            try:
                parameter = term["parameter"]
                scalar = Fraction(term["scalar"])
            except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
                raise ValueError(
                    f"Invalid coefficient term in coboundary_constants[{index}]"
                ) from exc
            if not isinstance(parameter, str) or not scalar:
                raise ValueError(
                    f"Invalid coefficient term in coboundary_constants[{index}]"
                )
            key = (left, right, output, parameter)
            if key in result:
                raise ValueError(f"Duplicate coboundary coefficient {key}")
            result[key] = scalar
    return result


def verify_coboundary_schema(
    basis: AlgebraBasis,
    structure_data: dict[str, object],
    coboundary_data: dict[str, object],
) -> tuple[int, int]:
    try:
        generation_date = coboundary_data["metadata"]["generation_date"]
    except (KeyError, TypeError) as exc:
        raise ValueError("Schema 4 metadata is missing its generation date") from exc
    expected, checked_pairs, term_count = build_coboundary_schema(
        basis, structure_data, generation_date
    )
    if coboundary_data != expected:
        _coefficient_map(coboundary_data.get("coboundary_constants"), basis)
        raise ValueError("Schema 4 data does not match the Layer 1 coboundary")

    coefficient_map = _coefficient_map(
        coboundary_data["coboundary_constants"], basis
    )
    for (left, right, output, parameter), coefficient in coefficient_map.items():
        reverse_key = (right, left, output, parameter)
        sign = -1 if basis.parity[left] * basis.parity[right] == 0 else 1
        if coefficient_map.get(reverse_key) != sign * coefficient:
            raise ValueError(
                f"Missing or incorrect reverse coboundary orientation for "
                f"{left},{right},{output},{parameter}"
            )
    if len(coboundary_data["odd_linear_map"]["coefficients"]) != (
        2 * len(basis.even) * len(basis.odd)
    ):
        raise ValueError("Odd-map coefficient count does not match basis dimensions")
    return checked_pairs, term_count


def generate_files(
    ranks: Iterable[int], data_dir: Path, generation_date: str | None = None
) -> list[tuple[Path, int, int, int]]:
    prepared: list[tuple[Path, AlgebraBasis, dict[str, object], dict[str, object], int, int]] = []
    seen_ranks: set[int] = set()
    for n in ranks:
        if not isinstance(n, int) or isinstance(n, bool) or n < 1:
            raise ValueError(f"Invalid bosonic rank: {n!r}")
        if n in seen_ranks:
            raise ValueError(f"Duplicate bosonic rank: {n}")
        seen_ranks.add(n)

        basis = build_basis(n)
        structure_path = data_dir / f"C_{n}_structure.json"
        if not structure_path.is_file():
            raise FileNotFoundError(f"Schema 1 file does not exist: {structure_path}")
        structure_data = _load_structure(structure_path, basis)
        if structure_data.get("schema_version") != "5.0":
            raise ValueError(f"{structure_path}: schema_version must be '5.0'")
        schema, checked_pairs, term_count = build_coboundary_schema(
            basis, structure_data, generation_date
        )
        destination = data_dir / f"C_{n}_coboundary.json"
        prepared.append(
            (destination, basis, structure_data, schema, checked_pairs, term_count)
        )

    generated: list[tuple[Path, int, int, int]] = []
    for destination, basis, structure_data, schema, checked_pairs, term_count in prepared:
        destination.write_text(
            json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        persisted = json.loads(destination.read_text(encoding="utf-8"))
        verified_pairs, verified_terms = verify_coboundary_schema(
            basis, structure_data, persisted
        )
        if (verified_pairs, verified_terms) != (checked_pairs, term_count):
            raise RuntimeError("Internal Schema 4 verification count mismatch")
        generated.append(
            (destination, verified_pairs, len(schema["coboundary_constants"]), verified_terms)
        )
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ranks",
        type=int,
        nargs="+",
        default=[1, 2, 3],
        help="Bosonic ranks to generate (default: 1 2 3)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Directory containing Schema 1 files and receiving Schema 4 files",
    )
    arguments = parser.parse_args()
    for path, pair_count, record_count, term_count in generate_files(
        arguments.ranks, arguments.data_dir
    ):
        print(
            f"{path}: verified {pair_count} ordered pairs, {record_count} "
            f"coboundary records, and {term_count} parameter terms"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
