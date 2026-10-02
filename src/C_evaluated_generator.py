"""Evaluate C(n+1) gamma data at the approved representative sign profile."""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from sympy import Poly, Rational, Symbol, expand, sympify

_BOSON_LABEL = re.compile(r"^b_(\d+)_(p|m)$")


class EvaluationError(ValueError):
    """Invalid input schema or failed evaluated-structure consistency check."""


@dataclass(frozen=True)
class EvaluationReport:
    rank: int
    parameter_count: int
    symbolic_gamma_entries: int
    evaluated_gamma_entries: int
    cocycle_triples: int


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise EvaluationError(f"Duplicate JSON object key: {key}")
        result[key] = value
    return result


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as source:
            schema = json.load(source, object_pairs_hook=_reject_duplicate_keys)
    except OSError as error:
        raise EvaluationError(f"Cannot read {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise EvaluationError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(schema, dict):
        raise EvaluationError(f"{path}: top-level JSON value must be an object")
    return schema


def _basis_and_parity(
    n: int, schema1: dict[str, Any], schema2: dict[str, Any]
) -> tuple[list[str], dict[str, int]]:
    try:
        algebra = schema1["algebra"]
        even = schema1["basis"]["even"]
        odd = schema1["basis"]["odd"]
        parity = schema1["parity"]
    except (KeyError, TypeError) as error:
        raise EvaluationError(f"Schema 1 is missing basis fields: {error}") from error

    if schema1.get("schema_version") != "5.0":
        raise EvaluationError("Schema 1 must use schema_version '5.0'")
    if algebra.get("family") != "C" or algebra.get("m") != 1 or algebra.get("n") != n:
        raise EvaluationError(f"Schema 1 rank/family does not match C({n + 1})")
    if schema2.get("schema_version") != "5.0" or schema2.get("algebra") != algebra:
        raise EvaluationError("Schema 2 algebra does not match Schema 1")
    if not isinstance(even, list) or not isinstance(odd, list):
        raise EvaluationError("Schema 1 basis.even and basis.odd must be arrays")
    labels = odd + even
    if not all(isinstance(label, str) for label in labels):
        raise EvaluationError("Schema 1 basis labels must be strings")
    if len(labels) != len(set(labels)):
        raise EvaluationError("Schema 1 basis contains duplicate labels")
    if len(even) != 2 * n**2 + n + 1 or len(odd) != 4 * n:
        raise EvaluationError("Schema 1 basis dimensions do not match the requested rank")
    if not isinstance(parity, dict) or set(parity) != set(labels):
        raise EvaluationError("Schema 1 parity keys must match the basis exactly")
    if any(type(parity[label]) is not int for label in labels):
        raise EvaluationError("Schema 1 parities must be integer values")
    if any(parity[label] != (0 if label in even else 1) for label in labels):
        raise EvaluationError("Schema 1 basis parities are inconsistent")
    return labels, parity


def _parameter_assignment(
    n: int, deformation: dict[str, Any]
) -> tuple[list[str], dict[str, int]]:
    try:
        matrix = deformation["gb_matrix"]
        rows = matrix["row_labels"]
        columns = matrix["column_labels"]
        entries = matrix["entries"]
    except (KeyError, TypeError) as error:
        raise EvaluationError(f"Schema 2 is missing gb_matrix fields: {error}") from error

    expected_rows = ["a_1_p", "a_1_m"]
    expected_columns = [
        f"b_{index}_{sign}"
        for index in range(1, n + 1)
        for sign in ("p", "m")
    ]
    if rows != expected_rows or columns != expected_columns:
        raise EvaluationError("Schema 2 gb_matrix labels are not in the approved order")
    if matrix.get("parameter_parity") != 0:
        raise EvaluationError("Schema 2 gb parameters must have parity 0")
    if (
        not isinstance(entries, list)
        or len(entries) != 2
        or any(not isinstance(row, list) or len(row) != 2 * n for row in entries)
    ):
        raise EvaluationError("Schema 2 gb_matrix must have shape 2 x 2n")

    parameters = [parameter for row in entries for parameter in row]
    if not all(isinstance(parameter, str) for parameter in parameters):
        raise EvaluationError("Schema 2 gb_matrix entries must be parameter names")
    if len(parameters) != 4 * n or len(set(parameters)) != 4 * n:
        raise EvaluationError("Schema 2 gb_matrix must contain 4n distinct parameters")

    assignment: dict[str, int] = {}
    for row_index, row_label in enumerate(expected_rows):
        fermion_sign = row_label.rsplit("_", 1)[1]
        for column_index, column_label in enumerate(expected_columns):
            match = _BOSON_LABEL.fullmatch(column_label)
            if match is None:
                raise EvaluationError(f"Invalid gb_matrix boson label: {column_label}")
            boson_index, boson_sign = match.groups()
            parameter = entries[row_index][column_index]
            expected_name = f"gb_a1_{fermion_sign}_b{boson_index}_{boson_sign}"
            if parameter != expected_name:
                raise EvaluationError(
                    f"Unexpected parameter at ({row_label}, {column_label}): "
                    f"{parameter!r}, expected {expected_name!r}"
                )
            assignment[parameter] = (
                -1 if row_label == "a_1_m" and boson_sign == "p" else 1
            )
    return parameters, assignment


def _validate_deformed_relations(
    n: int, deformation: dict[str, Any], parameters: list[str]
) -> None:
    relations = deformation.get("deformed_relations")
    matrix = deformation["gb_matrix"]
    if not isinstance(relations, list) or len(relations) != 4 * n:
        raise EvaluationError("Schema 2 must contain one deformed relation per parameter")
    expected = {
        (column, row, matrix["entries"][row_index][column_index])
        for row_index, row in enumerate(matrix["row_labels"])
        for column_index, column in enumerate(matrix["column_labels"])
    }
    actual: set[tuple[Any, Any, Any]] = set()
    for index, record in enumerate(relations):
        if not isinstance(record, dict):
            raise EvaluationError(f"deformed_relations[{index}] must be an object")
        if record.get("coefficient") != "-1" or record.get("central_element") != "κ":
            raise EvaluationError(f"deformed_relations[{index}] uses an unexpected convention")
        actual.add((record.get("X"), record.get("Y"), record.get("parameter")))
    if actual != expected or len(actual) != len(relations):
        raise EvaluationError("Schema 2 deformed relations do not cover gb_matrix entries")
    if set(parameters) != {parameter for _, _, parameter in expected}:
        raise EvaluationError("Schema 2 deformed relations omit gb parameters")


def _load_brackets(
    records: Any, labels: list[str], field_name: str
) -> dict[tuple[str, str], dict[str, Rational]]:
    if not isinstance(records, list):
        raise EvaluationError(f"{field_name} must be an array")
    label_set = set(labels)
    brackets: dict[tuple[str, str], dict[str, Rational]] = {}
    seen: set[tuple[str, str, str]] = set()
    required = {"X", "Y", "Z", "coeff", "sign_rule"}
    for index, record in enumerate(records):
        if not isinstance(record, dict) or set(record) != required:
            raise EvaluationError(
                f"{field_name}[{index}] must have fields {sorted(required)}"
            )
        x, y, z = record["X"], record["Y"], record["Z"]
        if any(not isinstance(label, str) or label not in label_set for label in (x, y, z)):
            raise EvaluationError(f"{field_name}[{index}] uses an unknown basis label")
        if record["sign_rule"] != "graded" or not isinstance(record["coeff"], str):
            raise EvaluationError(f"{field_name}[{index}] has invalid coefficient metadata")
        try:
            coefficient = Rational(record["coeff"])
        except (TypeError, ValueError, ZeroDivisionError) as error:
            raise EvaluationError(f"{field_name}[{index}] has a non-rational coefficient") from error
        if coefficient == 0 or str(coefficient) != record["coeff"]:
            raise EvaluationError(f"{field_name}[{index}] must store a nonzero canonical rational")
        triplet = (x, y, z)
        if triplet in seen:
            raise EvaluationError(f"{field_name} contains duplicate record {triplet}")
        seen.add(triplet)
        brackets.setdefault((x, y), {})[z] = coefficient
    return brackets


def _evaluate_gamma_records(
    records: Any,
    labels: list[str],
    parity: dict[str, int],
    parameters: list[str],
    assignment: dict[str, int],
) -> list[dict[str, str]]:
    if not isinstance(records, list):
        raise EvaluationError("Schema 2 gamma_structure must be an array")
    symbols = {parameter: Symbol(parameter) for parameter in parameters}
    label_set = set(labels)
    seen: set[tuple[str, str, str]] = set()
    evaluated: list[dict[str, str]] = []

    for index, record in enumerate(records):
        required = {"X", "Y", "Z", "coeff", "sign_rule"}
        if not isinstance(record, dict) or set(record) != required:
            raise EvaluationError(
                f"gamma_structure[{index}] must have fields {sorted(required)}"
            )
        x, y, z = record["X"], record["Y"], record["Z"]
        if any(not isinstance(label, str) or label not in label_set for label in (x, y, z)):
            raise EvaluationError(f"gamma_structure[{index}] uses an unknown basis label")
        if record["sign_rule"] != "graded" or not isinstance(record["coeff"], str):
            raise EvaluationError(f"gamma_structure[{index}] has invalid metadata")
        if parity[z] != (parity[x] + parity[y] + 1) % 2:
            raise EvaluationError(f"gamma_structure[{index}] has an invalid output parity")

        triplet = (x, y, z)
        if triplet in seen:
            raise EvaluationError(f"Schema 2 gamma_structure has duplicate record {triplet}")
        seen.add(triplet)
        try:
            expression = expand(sympify(record["coeff"], locals=symbols, rational=True))
            unknown_symbols = expression.free_symbols - set(symbols.values())
            if unknown_symbols:
                raise EvaluationError(
                    f"gamma_structure[{index}] uses unknown symbols: {unknown_symbols}"
                )
            polynomial = Poly(expression, *symbols.values())
        except (TypeError, ValueError, SyntaxError) as error:
            raise EvaluationError(f"gamma_structure[{index}] has an invalid expression") from error
        if polynomial.coeff_monomial(1) or any(
            sum(monomial) != 1 for monomial, _ in polynomial.terms()
        ):
            raise EvaluationError(f"gamma_structure[{index}] is not homogeneous linear in gb")

        coefficient = Rational(expression.subs({
            symbols[name]: assignment[name] for name in parameters
        }))
        if coefficient:
            evaluated.append(
                {
                    "X": x,
                    "Y": y,
                    "Z": z,
                    "coeff": str(coefficient),
                    "sign_rule": "graded",
                }
            )
    return evaluated


def _add_scaled(
    destination: dict[str, Rational],
    source: dict[str, Rational],
    scale: Rational,
) -> None:
    for label, coefficient in source.items():
        value = destination.get(label, Rational(0)) + scale * coefficient
        if value:
            destination[label] = value
        else:
            destination.pop(label, None)


def _gamma_on_base_bracket(
    x: str,
    inner: dict[str, Rational],
    gamma: dict[tuple[str, str], dict[str, Rational]],
) -> dict[str, Rational]:
    result: dict[str, Rational] = {}
    for y, coefficient in inner.items():
        _add_scaled(result, gamma.get((x, y), {}), coefficient)
    return result


def _base_on_gamma_bracket(
    x: str,
    inner: dict[str, Rational],
    base: dict[tuple[str, str], dict[str, Rational]],
) -> dict[str, Rational]:
    result: dict[str, Rational] = {}
    for y, coefficient in inner.items():
        _add_scaled(result, base.get((x, y), {}), coefficient)
    return result


def _verify_gamma_identities(
    labels: list[str],
    parity: dict[str, int],
    base_records: Any,
    gamma_records: list[dict[str, str]],
) -> int:
    base: dict[tuple[str, str], dict[str, Rational]] = {}
    for (x, y), bracket in _load_brackets(base_records, labels, "structure_constants").items():
        base[(x, y)] = bracket
    gamma = _load_brackets(gamma_records, labels, "evaluated_gamma_structure")

    for x in labels:
        for y in labels:
            sign = -1 if parity[x] * parity[y] else 1
            for z in labels:
                forward = gamma.get((x, y), {}).get(z, Rational(0))
                reverse = gamma.get((y, x), {}).get(z, Rational(0))
                if forward != -sign * reverse:
                    raise EvaluationError(
                        f"Evaluated gamma graded anti-symmetry fails at ({x}, {y}, {z})"
                    )

    checks = 0
    for x in labels:
        for y in labels:
            for z in labels:
                checks += 1
                first = _gamma_on_base_bracket(x, base.get((y, z), {}), gamma)
                _add_scaled(
                    first,
                    _base_on_gamma_bracket(x, gamma.get((y, z), {}), base),
                    Rational(-1 if parity[x] else 1),
                )
                second = _gamma_on_base_bracket(y, base.get((z, x), {}), gamma)
                _add_scaled(
                    second,
                    _base_on_gamma_bracket(y, gamma.get((z, x), {}), base),
                    Rational(-1 if parity[y] else 1),
                )
                third = _gamma_on_base_bracket(z, base.get((x, y), {}), gamma)
                _add_scaled(
                    third,
                    _base_on_gamma_bracket(z, gamma.get((x, y), {}), base),
                    Rational(-1 if parity[z] else 1),
                )

                residual: dict[str, Rational] = {}
                _add_scaled(residual, first, Rational(-1 if parity[x] * parity[z] else 1))
                _add_scaled(residual, second, Rational(-1 if parity[y] * parity[x] else 1))
                _add_scaled(residual, third, Rational(-1 if parity[z] * parity[y] else 1))
                if residual:
                    raise EvaluationError(
                        f"First-order Super Jacobi fails at ({x}, {y}, {z}): {residual}"
                    )
    return checks


def evaluate_gamma_schema(
    n: int, schema1: dict[str, Any], schema2: dict[str, Any]
) -> tuple[dict[str, Any], EvaluationReport]:
    """Substitute the approved signs and validate the evaluated gamma data."""
    labels, parity = _basis_and_parity(n, schema1, schema2)
    deformation = schema2.get("inhomogeneous_deformation")
    if not isinstance(deformation, dict):
        raise EvaluationError("Schema 2 inhomogeneous_deformation must be an object")
    parameters, assignment = _parameter_assignment(n, deformation)
    _validate_deformed_relations(n, deformation, parameters)
    evaluated_gamma = _evaluate_gamma_records(
        deformation.get("gamma_structure"),
        labels,
        parity,
        parameters,
        assignment,
    )

    evaluated_schema = deepcopy(schema2)
    evaluated_deformation = evaluated_schema["inhomogeneous_deformation"]
    evaluated_deformation.pop("gamma_structure")
    evaluated_deformation["parameter_assignment"] = assignment
    evaluated_deformation["evaluated_gamma_structure"] = evaluated_gamma
    evaluated_schema["structure_constants"] = deepcopy(schema1["structure_constants"])

    triple_checks = _verify_gamma_identities(
        labels,
        parity,
        evaluated_schema["structure_constants"],
        evaluated_gamma,
    )
    metadata = evaluated_schema.get("metadata")
    if not isinstance(metadata, dict):
        raise EvaluationError("Schema 2 metadata must be an object")
    metadata["generated_by"] = "C_evaluated_generator.py"
    metadata["generation_date"] = date.today().isoformat()
    references = metadata.get("references")
    if not isinstance(references, list):
        raise EvaluationError("Schema 2 metadata.references must be an array")
    evaluated_reference = "C(n+1) evaluated Schema 3, representative rank-two gb sign profile"
    if evaluated_reference not in references:
        references.append(evaluated_reference)

    report = EvaluationReport(
        rank=n,
        parameter_count=len(parameters),
        symbolic_gamma_entries=len(deformation["gamma_structure"]),
        evaluated_gamma_entries=len(evaluated_gamma),
        cocycle_triples=triple_checks,
    )
    return evaluated_schema, report


def write_evaluated_schema(
    n: int,
    schema1_dir: str | Path = "data",
    schema2_dir: str | Path = "data",
    output_dir: str | Path = "data",
) -> tuple[Path, EvaluationReport]:
    """Generate one C_n evaluated JSON after checking its Schema 1/2 inputs."""
    schema1_path = Path(schema1_dir) / f"C_{n}_structure.json"
    schema2_path = Path(schema2_dir) / f"C_{n}_gamma.json"
    schema1 = _load_json(schema1_path)
    schema2 = _load_json(schema2_path)
    evaluated_schema, report = evaluate_gamma_schema(n, schema1, schema2)
    output_path = Path(output_dir) / f"C_{n}_evaluated.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(evaluated_schema, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("n", nargs="+", type=int, help="Bosonic rank(s), e.g. 1 2 3")
    parser.add_argument("--schema1-dir", default="data")
    parser.add_argument("--schema2-dir", default="data")
    parser.add_argument("--output-dir", default="data")
    args = parser.parse_args()
    try:
        for rank in args.n:
            path, report = write_evaluated_schema(
                rank,
                args.schema1_dir,
                args.schema2_dir,
                args.output_dir,
            )
            print(
                f"{path}: {report.parameter_count} parameters, "
                f"{report.evaluated_gamma_entries}/{report.symbolic_gamma_entries} "
                f"nonzero evaluated gamma records, "
                f"{report.cocycle_triples} cocycle triples passed"
            )
    except EvaluationError as error:
        print(f"Evaluation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
