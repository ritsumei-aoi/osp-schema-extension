"""Generate C(n+1) inhomogeneous-deformation (Schema 2) data."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

from src.C_generators import (
    ROOT,
    _basis,
    _coefficient,
    _oscillator_order,
    _realizations,
    _span_coordinates,
)

FERMIONS = ("p", "m")
BOSON_SIGNS = ("p", "m")


def _parameters(n: int) -> list[dict[str, str | int]]:
    return [
        {
            "label": f"gb_a1_{fermion}_b{k}_{boson}",
            "fermion": f"a_1_{fermion}",
            "boson": f"b_{k}_{boson}",
            "parity": 1,
        }
        for fermion in FERMIONS
        for k in range(1, n + 1)
        for boson in BOSON_SIGNS
    ]


def _deformed_normalizer(n: int):
    order = {name: index for index, name in enumerate(_oscillator_order(n))}

    @lru_cache(maxsize=None)
    def normalize(word: tuple[str, ...]):
        for i in range(len(word) - 1):
            left, right = word[i], word[i + 1]
            prefix, suffix = word[:i], word[i + 2 :]
            if left in ("a_1_p", "a_1_m") and right == left:
                return ()
            if left == "a_1_m" and right == "a_1_p":
                return _combine(
                    normalize(prefix + (right, left) + suffix),
                    Fraction(-1),
                    normalize(prefix + suffix),
                    Fraction(1),
                )
            if left.startswith("b_") and right.startswith("b_"):
                left_index, left_sign = left[2:].split("_")
                right_index, right_sign = right[2:].split("_")
                if left_index == right_index and left_sign == "m" and right_sign == "p":
                    return _combine(
                        normalize(prefix + (right, left) + suffix),
                        Fraction(1),
                        normalize(prefix + suffix),
                        Fraction(1),
                    )
            if order[left] > order[right]:
                if left.startswith("b_") and right.startswith("a_"):
                    fermion_sign = right.rsplit("_", 1)[1]
                    boson_label = left
                    parameter = f"gb_a1_{fermion_sign}_b{boson_label[2:]}"
                    correction = tuple(
                        (remaining, parameter, coefficient)
                        for remaining, introduced_parameter, coefficient in normalize(prefix + suffix)
                        if introduced_parameter is None
                    )
                    return _combine(
                        normalize(prefix + (right, left) + suffix),
                        Fraction(1),
                        correction,
                        Fraction(-1),
                    )
                return normalize(prefix + (right, left) + suffix)
        return ((word, None, Fraction(1)),)

    return normalize


def _combine(left, left_scale, right, right_scale):
    terms: dict[tuple[tuple[str, ...], str | None], Fraction] = {}
    for polynomial, scale in ((left, left_scale), (right, right_scale)):
        for word, parameter, coefficient in polynomial:
            key = (word, parameter)
            terms[key] = terms.get(key, Fraction(0)) + scale * coefficient
    return tuple(
        (word, parameter, coefficient)
        for (word, parameter), coefficient in terms.items()
        if coefficient
    )


def _multiply(left, right, normalize):
    result: dict[tuple[tuple[str, ...], str | None], Fraction] = {}
    for (left_word, left_parameter), left_coefficient in left.items():
        for (right_word, right_parameter), right_coefficient in right.items():
            if left_parameter and right_parameter:
                continue
            inherited_parameter = left_parameter or right_parameter
            for word, introduced_parameter, coefficient in normalize(left_word + right_word):
                if inherited_parameter and introduced_parameter:
                    continue
                parameter = inherited_parameter or introduced_parameter
                key = (word, parameter)
                result[key] = (
                    result.get(key, Fraction(0))
                    + left_coefficient * right_coefficient * coefficient
                )
    return {key: value for key, value in result.items() if value}


def _graded_bracket(left, right, left_parity, right_parity, normalize):
    result = _multiply(left, right, normalize)
    sign = -1 if left_parity * right_parity % 2 == 0 else 1
    for key, coefficient in _multiply(right, left, normalize).items():
        result[key] = result.get(key, Fraction(0)) + sign * coefficient
    return {key: coefficient for key, coefficient in result.items() if coefficient}


def build_gamma_schema(n: int) -> dict:
    if n < 1:
        raise ValueError("Bosonic rank n must be at least 1")
    even, odd = _basis(n)
    labels = odd + even
    parity = {label: 0 for label in even} | {label: 1 for label in odd}
    forms = _realizations(n)
    gamma_forms = {**forms, "K": {(): Fraction(1)}}
    deformed_forms = {
        label: {(word, None): coefficient for word, coefficient in polynomial.items()}
        for label, polynomial in forms.items()
    }
    normalize = _deformed_normalizer(n)
    coordinates = _span_coordinates(gamma_forms, labels + ["K"])
    base_coordinates = _span_coordinates(forms, labels)
    source_path = ROOT / "data" / f"C_{n}_structure.json"
    try:
        source_schema = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load Schema 1 source {source_path}: {exc}") from exc
    if source_schema.get("algebra", {}).get("n") != n:
        raise ValueError(f"Schema 1 source {source_path} has the wrong bosonic rank")
    if source_schema.get("basis", {}).get("even") != even or source_schema.get("basis", {}).get("odd") != odd:
        raise ValueError(f"Schema 1 source {source_path} has an incompatible basis")
    source_brackets: dict[tuple[str, str], dict[str, Fraction]] = {}
    for entry in source_schema.get("structure_constants", []):
        source_brackets.setdefault((entry["X"], entry["Y"]), {})[entry["Z"]] = Fraction(entry["coeff"])
    parameters = _parameters(n)
    gamma_coefficients = []
    consistency_checks = 0

    for left_index, left_label in enumerate(labels):
        for right_label in labels[left_index:]:
            result = _graded_bracket(
                deformed_forms[left_label],
                deformed_forms[right_label],
                parity[left_label],
                parity[right_label],
                normalize,
            )
            undeformed = {
                word: coefficient
                for (word, parameter), coefficient in result.items()
                if parameter is None
            }
            computed_base = base_coordinates(undeformed)
            if computed_base != source_brackets.get((left_label, right_label), {}):
                raise ValueError(
                    f"undeformed bracket ({left_label}, {right_label}) disagrees "
                    f"with {source_path.name}"
                )
            consistency_checks += 1
            parameter_terms: dict[str, dict[tuple[str, ...], Fraction]] = {}
            for (word, parameter), coefficient in result.items():
                if parameter is None:
                    continue
                parameter_terms.setdefault(parameter, {})[word] = coefficient
            for parameter, polynomial in sorted(parameter_terms.items()):
                try:
                    decomposed = coordinates(polynomial)
                except ValueError as exc:
                    raise ValueError(
                        f"Gamma term for ({left_label}, {right_label}) with "
                        f"{parameter} is outside the C({n + 1}) basis: {exc}"
                    ) from exc
                for output, coefficient in sorted(decomposed.items()):
                    gamma_coefficients.append({
                        "X": left_label,
                        "Y": right_label,
                        "Z": output,
                        "parameter": parameter,
                        "coeff": _coefficient(coefficient),
                    })

    exchange_relations = [
        {
            "boson": parameter["boson"],
            "fermion": parameter["fermion"],
            "parameter": parameter["label"],
            "relation": (
                f"[{parameter['boson']}, {parameter['fermion']}] = "
                f"-{parameter['label']} * kappa"
            ),
        }
        for parameter in parameters
    ]
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
        },
        "source_schema": f"C_{n}_structure.json",
        "consistency": {
            "source_schema": f"C_{n}_structure.json",
            "undeformed_bracket_pairs_verified": consistency_checks,
        },
        "gb_matrix": {
            "shape": [2, 2 * n],
            "rows": ["a_1_p", "a_1_m"],
            "columns": [f"b_{k}_{sign}" for k in range(1, n + 1) for sign in BOSON_SIGNS],
            "parameters": parameters,
        },
        "inhomogeneous_deformation": {
            "parameter_parity": 1,
            "central_element": "kappa",
            "relation": "[b_j^s, a_1^sigma] = -gb_{a_1^sigma,b_j^s} * kappa",
            "exchange_relations": exchange_relations,
            "gamma_convention": "For each listed pair, gamma(X,Y) includes coeff * parameter * Z; Z may be K for a scalar term; reversed pairs follow graded skew-symmetry.",
            "gamma_coefficients": gamma_coefficients,
        },
        "metadata": {
            "generated_by": "src/C_gamma_generator.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "docs/json_schema_specification.md",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for n in args.ranks:
        schema = build_gamma_schema(n)
        path = args.output_dir / f"C_{n}_gamma.json"
        path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")


if __name__ == "__main__":
    main()
