from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Any

import C_generators as cg

Word = tuple[str, ...]
Expression = dict[Word, Fraction]
GammaCorrection = dict[str, Expression]
GammaBasisMap = dict[str, dict[str, Fraction]]

_GAMMA_SCHEMA_CACHE: dict[int, dict[str, Any]] = {}
_GAMMA_BRACKET_CACHE: dict[tuple[int, str, str], GammaBasisMap] = {}


def parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def parse_expression(standard_form: list[dict[str, Any]]) -> Expression:
    expr: Expression = {}
    for entry in standard_form:
        expr[tuple(entry["words"])] = parse_fraction(entry["coeff"])
    return cg.clean_expression(expr)


def structure_path(n: int, data_dir: Path | None = None) -> Path:
    base = data_dir or Path("data")
    return base / f"C_{n}_structure.json"


def gamma_path(n: int, data_dir: Path | None = None) -> Path:
    base = data_dir or Path("data")
    return base / f"C_{n}_gamma.json"


def load_structure_schema(n: int, data_dir: Path | None = None) -> dict[str, Any]:
    path = structure_path(n, data_dir)
    return json.loads(path.read_text(encoding="utf-8"))


def load_generator_expressions_from_schema(schema: dict[str, Any]) -> dict[str, Expression]:
    realizations = schema["generator_realization"]["realizations"]
    return {
        name: parse_expression(payload["standard_form"])
        for name, payload in realizations.items()
    }


def gb_label(fermion_label: str, boson_label: str) -> str:
    fermion = fermion_label.replace("_", "")
    boson = boson_label.replace("_", "")
    return f"gb_{fermion}_{boson}"


def gb_columns(n: int) -> list[str]:
    columns = []
    for index in range(1, n + 1):
        columns.extend([f"b_{index}_p", f"b_{index}_m"])
    return columns


def gb_rows() -> list[str]:
    return ["a_1_p", "a_1_m"]


def gb_labels_in_order(n: int) -> list[str]:
    return [gb_label(row, column) for row in gb_rows() for column in gb_columns(n)]


def clean_gamma_correction(correction: GammaCorrection) -> GammaCorrection:
    result: GammaCorrection = {}
    for label, expr in correction.items():
        cleaned = cg.clean_expression(expr)
        if cleaned:
            result[label] = cleaned
    return result


def add_scaled_correction(target: GammaCorrection, correction: GammaCorrection, scale: Fraction) -> None:
    for label, expr in correction.items():
        bucket = target.setdefault(label, {})
        cg.add_scaled_expression(bucket, expr, scale)
        if not bucket:
            del target[label]


def normalize_word_with_gamma(word: Word) -> tuple[Expression, GammaCorrection]:
    if len(word) < 2:
        return {word: Fraction(1)}, {}

    for index in range(len(word) - 1):
        left = word[index]
        right = word[index + 1]
        prefix = word[:index]
        suffix = word[index + 2 :]

        if left == right and cg.is_fermion(left):
            return {}, {}

        if left == "a_1_m" and right == "a_1_p":
            undeformed: Expression = {}
            correction: GammaCorrection = {}

            left_u, left_c = normalize_word_with_gamma(prefix + suffix)
            right_u, right_c = normalize_word_with_gamma(prefix + ("a_1_p", "a_1_m") + suffix)

            cg.add_scaled_expression(undeformed, left_u, Fraction(1))
            cg.add_scaled_expression(undeformed, right_u, Fraction(-1))
            add_scaled_correction(correction, left_c, Fraction(1))
            add_scaled_correction(correction, right_c, Fraction(-1))
            return cg.clean_expression(undeformed), clean_gamma_correction(correction)

        if cg.is_boson(left) and cg.is_boson(right):
            left_index, left_sign = cg.parse_boson(left)
            right_index, right_sign = cg.parse_boson(right)
            if left_sign == "m" and right_sign == "p" and left_index == right_index:
                undeformed = {}
                correction = {}

                left_u, left_c = normalize_word_with_gamma(prefix + suffix)
                right_u, right_c = normalize_word_with_gamma(prefix + (right, left) + suffix)

                cg.add_scaled_expression(undeformed, left_u, Fraction(1))
                cg.add_scaled_expression(undeformed, right_u, Fraction(1))
                add_scaled_correction(correction, left_c, Fraction(1))
                add_scaled_correction(correction, right_c, Fraction(1))
                return cg.clean_expression(undeformed), clean_gamma_correction(correction)

        if cg.is_boson(left) and cg.is_fermion(right):
            undeformed, correction = normalize_word_with_gamma(prefix + (right, left) + suffix)
            label = gb_label(right, left)
            corr_expr = cg.normalize_word(prefix + suffix)
            bucket = correction.setdefault(label, {})
            cg.add_scaled_expression(bucket, corr_expr, Fraction(-1))
            if not bucket:
                del correction[label]
            return cg.clean_expression(undeformed), clean_gamma_correction(correction)

        if cg.oscillator_sort_key(left) > cg.oscillator_sort_key(right):
            return normalize_word_with_gamma(prefix + (right, left) + suffix)

    return {word: Fraction(1)}, {}


def multiply_expressions_with_gamma(left: Expression, right: Expression) -> tuple[Expression, GammaCorrection]:
    undeformed: Expression = {}
    correction: GammaCorrection = {}

    for left_word, left_coeff in left.items():
        for right_word, right_coeff in right.items():
            word_undeformed, word_correction = normalize_word_with_gamma(left_word + right_word)
            scale = left_coeff * right_coeff
            cg.add_scaled_expression(undeformed, word_undeformed, scale)
            add_scaled_correction(correction, word_correction, scale)

    return cg.clean_expression(undeformed), clean_gamma_correction(correction)


def correction_to_basis(n: int, correction: GammaCorrection) -> GammaBasisMap:
    result: GammaBasisMap = {}
    for label, expr in correction.items():
        basis_coeffs = decompose_gamma_expression_to_basis(n, expr)
        for generator, coeff in basis_coeffs.items():
            bucket = result.setdefault(generator, {})
            new_coeff = bucket.get(label, Fraction(0)) + coeff
            if new_coeff:
                bucket[label] = new_coeff
            elif label in bucket:
                del bucket[label]
            if not bucket:
                del result[generator]
    return result


def decompose_gamma_expression_to_basis(n: int, expr: Expression) -> dict[str, Fraction]:
    expressions = cg.build_generator_expressions(n)
    direct_word_map = cg.build_direct_word_map(expressions)
    cartan_names = [f"H_{index}" for index in range(1, n + 2)]
    cartan_expressions = [expressions[name] for name in cartan_names]
    constant_name = "K"
    constant_expression = {(): Fraction(1)}

    direct_coefficients: dict[str, Fraction] = {}
    cartan_expr: Expression = {}

    for word, coeff in cg.clean_expression(expr).items():
        if word in direct_word_map:
            name = direct_word_map[word]
            direct_coefficients[name] = direct_coefficients.get(name, Fraction(0)) + coeff
            continue

        if word == () or word in cg.cartan_number_words(n):
            cartan_expr[word] = cartan_expr.get(word, Fraction(0)) + coeff
            continue

        raise ValueError(f"Expression term {word} is outside the approved gamma target span for n={n}")

    result = {name: coeff for name, coeff in direct_coefficients.items() if coeff}
    if cg.clean_expression(cartan_expr):
        rows = cg.cartan_number_words(n) + [()]
        matrix: list[list[Fraction]] = []
        vector: list[Fraction] = []
        all_targets = cartan_expressions + [constant_expression]
        for row_word in rows:
            matrix.append([target.get(row_word, Fraction(0)) for target in all_targets])
            vector.append(cartan_expr.get(row_word, Fraction(0)))

        coefficients = cg.gaussian_solve(matrix, vector)
        names = cartan_names + [constant_name]
        reconstructed: Expression = {}
        for name, coeff in zip(names, coefficients):
            if not coeff:
                continue
            result[name] = coeff
            source_expr = constant_expression if name == constant_name else expressions[name]
            cg.add_scaled_expression(reconstructed, source_expr, coeff)

        if cg.clean_expression(reconstructed) != cg.clean_expression(cartan_expr):
            raise ValueError(
                f"Gamma decomposition mismatch for n={n}: expected {cartan_expr}, reconstructed {reconstructed}"
            )

    return {name: coeff for name, coeff in result.items() if coeff}


def add_scaled_gamma_basis_map(target: GammaBasisMap, source: GammaBasisMap, scale: Fraction) -> None:
    for generator, coeffs in source.items():
        bucket = target.setdefault(generator, {})
        for label, coeff in coeffs.items():
            new_coeff = bucket.get(label, Fraction(0)) + coeff * scale
            if new_coeff:
                bucket[label] = new_coeff
            elif label in bucket:
                del bucket[label]
        if not bucket:
            del target[generator]


def gamma_in_basis(n: int, left_name: str, right_name: str) -> GammaBasisMap:
    cache_key = (n, left_name, right_name)
    if cache_key in _GAMMA_BRACKET_CACHE:
        return deepcopy(_GAMMA_BRACKET_CACHE[cache_key])

    schema = load_structure_schema(n)
    expressions = load_generator_expressions_from_schema(schema)
    parity = dict(schema["parity"])

    _, forward = multiply_expressions_with_gamma(expressions[left_name], expressions[right_name])
    _, reverse = multiply_expressions_with_gamma(expressions[right_name], expressions[left_name])

    result: GammaBasisMap = {}
    add_scaled_gamma_basis_map(result, correction_to_basis(n, forward), Fraction(1))
    sign = Fraction(-1 if (parity[left_name] * parity[right_name]) % 2 else 1)
    add_scaled_gamma_basis_map(result, correction_to_basis(n, reverse), -sign)

    _GAMMA_BRACKET_CACHE[cache_key] = deepcopy(result)
    return deepcopy(result)


def gamma_matrix_entries(n: int) -> list[dict[str, Any]]:
    schema = load_structure_schema(n)
    basis_order = list(schema["basis"]["odd"]) + list(schema["basis"]["even"])
    target_order = basis_order + ["K"]
    gb_order = gb_labels_in_order(n)
    entries: list[dict[str, Any]] = []

    for left in basis_order:
        for right in basis_order:
            gamma = gamma_in_basis(n, left, right)
            for result in target_order:
                coeffs = gamma.get(result)
                if not coeffs:
                    continue
                entries.append(
                    {
                        "X": left,
                        "Y": right,
                        "Z": result,
                        "coeff": {
                            label: cg.fraction_to_str(coeffs[label])
                            for label in gb_order
                            if label in coeffs and coeffs[label]
                        },
                        "sign_rule": "graded",
                    }
                )

    return entries


def build_inhomogeneous_deformation(n: int) -> dict[str, Any]:
    columns = gb_columns(n)
    rows = gb_rows()
    entries = [[gb_label(row, column) for column in columns] for row in rows]
    return {
        "exchange_relation": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa",
        "kappa_parity": 0,
        "gb_parameter_parity": 1,
        "gamma_target_convention": "Z ranges over the Schema 1 basis generators plus K when constant terms appear; kappa is factored out.",
        "gb_matrix": {
            "rows": rows,
            "columns": columns,
            "entries": entries,
        },
        "gamma_matrix": gamma_matrix_entries(n),
    }


def build_consistency_report(n: int, structure_schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "structure_file": f"C_{n}_structure.json",
        "algebra_match": structure_schema["algebra"] == cg.build_algebra_metadata(n),
        "basis_match": structure_schema["basis"] == cg.build_basis(n),
        "parity_match": structure_schema["parity"] == cg.build_parity_map(n),
        "central_elements_match": structure_schema["central_elements"] == cg.build_central_elements(),
    }


def build_metadata(n: int) -> dict[str, Any]:
    return {
        "generated_by": "src/C_gamma.py",
        "generation_date": date.today().isoformat(),
        "references": [
            "docs/math/C_inhomogeneous_definition.md",
            "docs/math/Cn1_definition.md",
            "docs/math/B0n_definition.md",
        ],
        "structure_file": f"C_{n}_structure.json",
    }


def build_gamma_schema(n: int) -> dict[str, Any]:
    if n in _GAMMA_SCHEMA_CACHE:
        return deepcopy(_GAMMA_SCHEMA_CACHE[n])

    structure_schema = load_structure_schema(n)
    schema = {
        "schema_version": "5.0",
        "algebra": structure_schema["algebra"],
        "basis": structure_schema["basis"],
        "parity": structure_schema["parity"],
        "central_elements": structure_schema["central_elements"],
        "inhomogeneous_deformation": build_inhomogeneous_deformation(n),
        "consistency_with_schema_1": build_consistency_report(n, structure_schema),
        "metadata": build_metadata(n),
    }
    _GAMMA_SCHEMA_CACHE[n] = deepcopy(schema)
    return deepcopy(schema)


def write_gamma_json(n: int, out_path: Path) -> Path:
    schema = build_gamma_schema(n)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate C(n+1) Schema 2 gamma JSON files.")
    parser.add_argument("--n", type=int, choices=(1, 2, 3), help="Bosonic rank n to generate")
    parser.add_argument("--all", action="store_true", help="Generate n=1,2,3")
    parser.add_argument("--out", type=Path, help="Output file path for a single n run")
    parser.add_argument("--outdir", type=Path, default=Path("data"), help="Output directory for --all")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.all == bool(args.n):
        raise SystemExit("Specify exactly one of --n or --all")

    if args.all:
        for n in (1, 2, 3):
            path = write_gamma_json(n, gamma_path(n, args.outdir))
            print(f"Wrote {path}")
        return

    out_path = args.out or gamma_path(args.n, args.outdir)
    path = write_gamma_json(args.n, out_path)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
