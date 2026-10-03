"""Generate the symbolic coboundary structure for C(n+1)."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Any


class CoboundaryError(ValueError):
    """Invalid Schema 1 input or failed coboundary consistency check."""


@dataclass(frozen=True)
class CoboundaryReport:
    rank: int
    basis_size: int
    parameter_count: int
    record_count: int
    graded_skew_checks: int


BracketTable = dict[tuple[str, str], dict[str, Fraction]]
ParameterTerms = dict[str, Fraction]


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CoboundaryError(f"Duplicate JSON object key: {key}")
        result[key] = value
    return result


def _load_schema(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as source:
            schema = json.load(source, object_pairs_hook=_reject_duplicate_keys)
    except OSError as error:
        raise CoboundaryError(f"Cannot read {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise CoboundaryError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(schema, dict):
        raise CoboundaryError(f"{path}: top-level JSON value must be an object")
    return schema


def _validate_basis(
    n: int, schema1: dict[str, Any]
) -> tuple[list[str], dict[str, int]]:
    try:
        algebra = schema1["algebra"]
        even = schema1["basis"]["even"]
        odd = schema1["basis"]["odd"]
        parity = schema1["parity"]
    except (KeyError, TypeError) as error:
        raise CoboundaryError(f"Schema 1 is missing basis fields: {error}") from error

    if schema1.get("schema_version") != "5.0":
        raise CoboundaryError("Schema 1 must use schema_version '5.0'")
    if not isinstance(algebra, dict) or (
        algebra.get("family") != "C" or algebra.get("m") != 1 or algebra.get("n") != n
    ):
        raise CoboundaryError(f"Schema 1 rank/family does not match C({n + 1})")
    if not isinstance(even, list) or not isinstance(odd, list):
        raise CoboundaryError("Schema 1 basis.even and basis.odd must be arrays")
    if not all(isinstance(label, str) for label in even + odd):
        raise CoboundaryError("Schema 1 basis labels must be strings")
    if len(even) != 2 * n**2 + n + 1 or len(odd) != 4 * n:
        raise CoboundaryError("Schema 1 basis dimensions do not match the requested rank")

    labels = odd + even
    if len(labels) != len(set(labels)):
        raise CoboundaryError("Schema 1 basis contains duplicate labels")
    if not isinstance(parity, dict) or set(parity) != set(labels):
        raise CoboundaryError("Schema 1 parity keys must match the basis exactly")
    if any(type(parity[label]) is not int for label in labels):
        raise CoboundaryError("Schema 1 parities must be integer values")
    if any(parity[label] != (0 if label in even else 1) for label in labels):
        raise CoboundaryError("Schema 1 basis parities are inconsistent")
    return labels, parity


def _load_structure_constants(
    records: Any, labels: list[str]
) -> BracketTable:
    if not isinstance(records, list):
        raise CoboundaryError("Schema 1 structure_constants must be an array")
    label_set = set(labels)
    brackets: BracketTable = defaultdict(dict)
    seen: set[tuple[str, str, str]] = set()
    required_fields = {"X", "Y", "Z", "coeff", "sign_rule"}
    for index, record in enumerate(records):
        if not isinstance(record, dict) or set(record) != required_fields:
            raise CoboundaryError(
                f"structure_constants[{index}] must have fields "
                f"{sorted(required_fields)}"
            )
        x, y, z = record["X"], record["Y"], record["Z"]
        if any(not isinstance(label, str) or label not in label_set for label in (x, y, z)):
            raise CoboundaryError(
                f"structure_constants[{index}] references an unknown basis label"
            )
        if record["sign_rule"] != "graded" or not isinstance(record["coeff"], str):
            raise CoboundaryError(
                f"structure_constants[{index}] has invalid coefficient metadata"
            )
        try:
            coefficient = Fraction(record["coeff"])
        except (ValueError, ZeroDivisionError) as error:
            raise CoboundaryError(
                f"structure_constants[{index}] has an invalid rational coefficient"
            ) from error
        if coefficient == 0:
            raise CoboundaryError(
                f"structure_constants[{index}] stores a zero coefficient"
            )
        triplet = (x, y, z)
        if triplet in seen:
            raise CoboundaryError(f"Duplicate Schema 1 structure constant: {triplet}")
        seen.add(triplet)
        brackets[(x, y)][z] = coefficient
    return brackets


def _add_coefficient(
    result: dict[tuple[str, str, str], ParameterTerms],
    triplet: tuple[str, str, str],
    parameter: str,
    coefficient: Fraction,
) -> None:
    terms = result.setdefault(triplet, {})
    value = terms.get(parameter, Fraction(0)) + coefficient
    if value:
        terms[parameter] = value
    else:
        terms.pop(parameter, None)
    if not terms:
        result.pop(triplet, None)


def _parameter_name(target: str, source: str) -> str:
    return f"phi__{target}__from__{source}"


def _make_f_map(
    labels: list[str], parity: dict[str, int]
) -> tuple[list[dict[str, Any]], dict[str, list[tuple[str, str]]], list[str]]:
    f_map: list[dict[str, Any]] = []
    terms_by_source: dict[str, list[tuple[str, str]]] = {}
    parameters: list[str] = []

    for source in labels:
        terms = []
        for target in labels:
            if parity[target] == parity[source]:
                continue
            parameter = _parameter_name(target, source)
            terms.append((target, parameter))
            parameters.append(parameter)
        terms_by_source[source] = terms
        f_map.append(
            {
                "source": source,
                "terms": [
                    {"target": target, "coefficient": parameter}
                    for target, parameter in terms
                ],
            }
        )
    return f_map, terms_by_source, parameters


def _compute_coboundary(
    labels: list[str],
    parity: dict[str, int],
    brackets: BracketTable,
    terms_by_source: dict[str, list[tuple[str, str]]],
) -> dict[tuple[str, str, str], ParameterTerms]:
    result: dict[tuple[str, str, str], ParameterTerms] = {}
    for x in labels:
        for y in labels:
            first_scale = Fraction(-1 if parity[x] else 1)
            second_exponent = (parity[x] + 1) * parity[y]
            second_scale = Fraction(-1 if second_exponent % 2 == 0 else 1)

            for target, parameter in terms_by_source[y]:
                for z, coefficient in brackets.get((x, target), {}).items():
                    _add_coefficient(
                        result, (x, y, z), parameter, first_scale * coefficient
                    )

            for target, parameter in terms_by_source[x]:
                for z, coefficient in brackets.get((y, target), {}).items():
                    _add_coefficient(
                        result, (x, y, z), parameter, second_scale * coefficient
                    )

            for inner, bracket_coefficient in brackets.get((x, y), {}).items():
                for target, parameter in terms_by_source[inner]:
                    _add_coefficient(
                        result,
                        (x, y, target),
                        parameter,
                        -bracket_coefficient,
                    )
    return result


def _format_coefficient(terms: ParameterTerms, parameter_order: list[str]) -> str:
    pieces: list[str] = []
    for parameter in parameter_order:
        coefficient = terms.get(parameter, Fraction(0))
        if not coefficient:
            continue
        magnitude = abs(coefficient)
        body = parameter if magnitude == 1 else f"{magnitude}*{parameter}"
        if not pieces:
            pieces.append(f"-{body}" if coefficient < 0 else body)
        else:
            pieces.append(f" - {body}" if coefficient < 0 else f" + {body}")
    return "".join(pieces)


def _verify_coboundary(
    labels: list[str],
    parity: dict[str, int],
    terms: dict[tuple[str, str, str], ParameterTerms],
    parameters: list[str],
) -> int:
    parameter_set = set(parameters)
    for (x, y, z), coefficients in terms.items():
        if z not in labels or not set(coefficients) <= parameter_set:
            raise CoboundaryError(f"Coboundary output is outside its allowed basis: {(x, y, z)}")
        expected_parity = (parity[x] + parity[y] + 1) % 2
        if parity[z] != expected_parity:
            raise CoboundaryError(
                f"Coboundary parity mismatch for ({x}, {y}) -> {z}"
            )

    checks = 0
    for x in labels:
        for y in labels:
            sign = -1 if parity[x] * parity[y] else 1
            for z in labels:
                checks += 1
                forward = terms.get((x, y, z), {})
                reverse = terms.get((y, x, z), {})
                expected = {
                    parameter: -sign * coefficient
                    for parameter, coefficient in reverse.items()
                }
                if forward != expected:
                    raise CoboundaryError(
                        f"Graded anti-symmetry fails for ({x}, {y}) -> {z}"
                    )
    return checks


def compute_coboundary_schema(
    n: int, schema1: dict[str, Any]
) -> tuple[dict[str, Any], CoboundaryReport]:
    """Compute delta-f for a fully general parity-reversing endomorphism."""
    labels, parity = _validate_basis(n, schema1)
    brackets = _load_structure_constants(schema1.get("structure_constants"), labels)
    f_map, terms_by_source, parameters = _make_f_map(labels, parity)
    expected_parameter_count = (
        2 * len(schema1["basis"]["even"]) * len(schema1["basis"]["odd"])
    )
    if len(parameters) != expected_parameter_count or len(set(parameters)) != len(parameters):
        raise CoboundaryError("The general odd map parameter count is inconsistent")

    terms = _compute_coboundary(labels, parity, brackets, terms_by_source)
    skew_checks = _verify_coboundary(labels, parity, terms, parameters)
    structure = [
        {
            "X": x,
            "Y": y,
            "Z": z,
            "coeff": _format_coefficient(terms[(x, y, z)], parameters),
            "sign_rule": "graded",
        }
        for x in labels
        for y in labels
        for z in labels
        if (x, y, z) in terms
    ]

    schema = {
        "schema_version": "5.0",
        "algebra": schema1["algebra"],
        "coboundary": {
            "map_parity": 1,
            "parameter_parity": 0,
            "formula": (
                "(-1)^p(X)[X,f(Y)] - "
                "(-1)^((p(X)+1)p(Y))[Y,f(X)] - f([X,Y])"
            ),
            "f_map": f_map,
            "coboundary_structure": structure,
        },
        "metadata": {
            "generated_by": "C_coboundary_generator.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "C(n+1) coboundary definition, docs/math/C_coboundary_definition.md",
                "C(n+1) Schema 1, docs/json_schema_specification.md",
            ],
        },
    }
    report = CoboundaryReport(
        rank=n,
        basis_size=len(labels),
        parameter_count=len(parameters),
        record_count=len(structure),
        graded_skew_checks=skew_checks,
    )
    return schema, report


def write_coboundary_schema(
    n: int,
    schema1_dir: str | Path = "data",
    output_dir: str | Path = "data",
) -> tuple[Path, CoboundaryReport]:
    """Generate one Schema 4 file using its verified Schema 1 input."""
    schema1_path = Path(schema1_dir) / f"C_{n}_structure.json"
    schema1 = _load_schema(schema1_path)
    schema, report = compute_coboundary_schema(n, schema1)
    output_path = Path(output_dir) / f"C_{n}_coboundary.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("n", nargs="+", type=int, help="Bosonic rank(s), e.g. 1 2 3")
    parser.add_argument("--schema1-dir", default="data")
    parser.add_argument("--output-dir", default="data")
    args = parser.parse_args()
    try:
        for rank in args.n:
            path, report = write_coboundary_schema(
                rank, args.schema1_dir, args.output_dir
            )
            print(
                f"{path}: {report.parameter_count} f parameters, "
                f"{report.record_count} nonzero coboundary records, "
                f"{report.graded_skew_checks} graded anti-symmetry checks passed"
            )
    except CoboundaryError as error:
        print(f"Coboundary generation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
