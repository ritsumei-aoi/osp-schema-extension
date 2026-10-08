#!/usr/bin/env python3
"""Generate formal Schema 2 gamma coefficients for C(n+1)."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path

if __package__:
    from .C_generators import _atom_order, _decompose, _generator_data, _pbw_order
else:
    from C_generators import _atom_order, _decompose, _generator_data, _pbw_order


def _parameter_for_crossing(boson, fermion):
    return f"gb_a1_{fermion[1]}_b{boson[1]}_{boson[2]}"


def _normal_order_deformed(word, parameter=None):
    """Normal-order one word, retaining at most one formal kappa correction."""
    for index in range(len(word) - 1):
        left, right = word[index:index + 2]
        if left[0] == right[0] == "a" and left == right:
            return {}
        if _atom_order(left) <= _atom_order(right):
            continue

        swapped = word[:index] + (right, left) + word[index + 2:]
        if left[0] == right[0] == "a":
            reordered = _normal_order_deformed(swapped, parameter)
            contracted = _normal_order_deformed(
                word[:index] + word[index + 2:], parameter
            )
            result = {}
            for key, coeff in reordered.items():
                result[key] = result.get(key, 0) - coeff
            for key, coeff in contracted.items():
                result[key] = result.get(key, 0) + coeff
            return {key: coeff for key, coeff in result.items() if coeff}
        if left[0] == right[0] == "b" and left[1] == right[1]:
            reordered = _normal_order_deformed(swapped, parameter)
            contracted = _normal_order_deformed(
                word[:index] + word[index + 2:], parameter
            )
            result = {}
            for key, coeff in reordered.items():
                result[key] = result.get(key, 0) + coeff
            for key, coeff in contracted.items():
                result[key] = result.get(key, 0) + coeff
            return {key: coeff for key, coeff in result.items() if coeff}

        reordered = _normal_order_deformed(swapped, parameter)
        if left[0] == "b" and right[0] == "a" and parameter is None:
            # b_j^s a_1^sigma = a_1^sigma b_j^s - gb_{sigma,j,s} kappa
            contraction_word = word[:index] + word[index + 2:]
            correction_parameter = _parameter_for_crossing(left, right)
            for (contracted_word, _), coeff in _normal_order_deformed(
                contraction_word, correction_parameter
            ).items():
                key = (contracted_word, correction_parameter)
                reordered[key] = reordered.get(key, 0) - coeff
        return reordered
    return {(word, parameter): 1}


def _deformed_product(left, right):
    result = {}
    for left_word, left_coeff in left.items():
        for right_word, right_coeff in right.items():
            for (word, parameter), coeff in _normal_order_deformed(
                left_word + right_word
            ).items():
                key = (word, parameter)
                result[key] = (
                    result.get(key, 0) + left_coeff * right_coeff * coeff
                )
    return {key: coeff for key, coeff in result.items() if coeff}


def _gamma_bracket(left, right, left_parity, right_parity):
    result = {}
    for product, scale in (
        (_deformed_product(left, right), 1),
        (
            _deformed_product(right, left),
            -1 if left_parity * right_parity % 2 == 0 else 1,
        ),
    ):
        for key, coeff in product.items():
            if key[1] is None:
                continue
            result[key] = result.get(key, 0) + scale * coeff
    return {key: coeff for key, coeff in result.items() if coeff}


def calculate_gamma(n):
    """Return nonzero formal gamma coefficients for bosonic rank n."""
    generators, parity, _ = _generator_data(n)
    pbw = _pbw_order(n)
    gamma_generators = dict(generators)
    gamma_generators["K"] = {(): Fraction(1)}
    gamma_basis = [*pbw, "K"]
    output = {}
    for i, x in enumerate(pbw):
        for y in pbw[i:]:
            bracket = _gamma_bracket(
                generators[x], generators[y], parity[x], parity[y]
            )
            by_parameter = {}
            for (word, parameter), coeff in bracket.items():
                by_parameter.setdefault(parameter, {})[word] = coeff
            for parameter, polynomial in by_parameter.items():
                coefficients = _decompose(
                    polynomial, gamma_generators, gamma_basis
                )
                for z, coeff in coefficients.items():
                    key = (x, y, z)
                    output.setdefault(key, {})[parameter] = coeff
    entries = []
    for (x, y, z), parameter_coefficients in sorted(
        output.items(),
        key=lambda item: (
            pbw.index(item[0][0]),
            pbw.index(item[0][1]),
            (pbw.index(item[0][2]) if item[0][2] in pbw else len(pbw)),
        ),
    ):
        entries.append({
            "X": x,
            "Y": y,
            "Z": z,
            "coefficients": [
                {"parameter": parameter, "coeff": str(coeff)}
                for parameter, coeff in sorted(parameter_coefficients.items())
                if coeff
            ],
        })
    return entries


def build_gamma_schema(n, generation_date=None):
    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    parameters = [
        {
            "label": f"gb_a1_{fermion_sign}_b{i}_{boson_sign}",
            "fermion": f"a_1_{fermion_sign}",
            "boson": f"b_{i}_{boson_sign}",
            "parity": 1,
        }
        for fermion_sign in ("p", "m")
        for i in range(1, n + 1)
        for boson_sign in ("p", "m")
    ]
    gamma = calculate_gamma(n)
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "dimension": {
                "total": 2 * n * n + 5 * n + 1,
                "even": 2 * n * n + n + 1,
                "odd": 4 * n,
            },
        },
        "source_schema1": f"C_{n}_structure.json",
        "central_elements": {
            "kappa": {"parity": 1, "nilpotent": True, "relation": "kappa^2 = 0"},
            "K": {"parity": 0, "identity": True, "relation": "K = 1"},
        },
        "inhomogeneous_deformation": {
            "type": "gb",
            "gb_matrix": {
                "shape": [2, 2 * n],
                "row_labels": ["a_1_p", "a_1_m"],
                "column_labels": [
                    label
                    for i in range(1, n + 1)
                    for label in (f"b_{i}_p", f"b_{i}_m")
                ],
                "parameters": parameters,
                "relation": (
                    "[b_j^s, a_1^sigma] = "
                    "-gb_{sigma,j,s} * kappa"
                ),
                "coefficient_convention": (
                    "gb labels are formal coefficients; the parity annotation "
                    "is metadata from C_inhomogeneous_definition.md"
                ),
            },
            "gamma_coefficients": gamma,
            "nonzero_gamma_count": len(gamma),
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": generation_date or date.today().isoformat(),
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "docs/json_schema_specification.md",
                "docs/math/Cn1_definition.md",
            ],
        },
    }


def generate_files(output_dir, ranks=(1, 2, 3), generation_date=None):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    paths = []
    for n in ranks:
        schema = build_gamma_schema(n, generation_date=generation_date)
        path = output_path / f"C_{n}_gamma.json"
        path.write_text(
            json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        paths.append(path)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="data")
    parser.add_argument("--ranks", nargs="+", type=int, default=[1, 2, 3])
    args = parser.parse_args()
    for path in generate_files(args.output_dir, args.ranks):
        print(path)


if __name__ == "__main__":
    main()
