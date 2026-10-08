"""Compute symbolic inhomogeneous gamma coefficients for C(n+1)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import TypeAlias

import sympy as sp

from C_generators import _coordinate_solver, _labels, _realizations

Word: TypeAlias = tuple[str, ...]
Term: TypeAlias = tuple[Word, int]
Polynomial: TypeAlias = dict[Term, sp.Expr]


def _parity(word: Word) -> int:
    return sum(label.startswith("a_1_") for label in word) % 2


def _normal_word(word: Word, rank: int, deform: bool = True) -> Polynomial:
    order = {"a_1_p": 0, "a_1_m": 1}
    for k in range(1, rank + 1):
        order[f"b_{k}_p"] = 2 + 2 * (k - 1)
        order[f"b_{k}_m"] = 3 + 2 * (k - 1)

    for index in range(len(word) - 1):
        left, right = word[index], word[index + 1]
        if left == right and left in {"a_1_p", "a_1_m"}:
            return {}
        if order[left] <= order[right]:
            continue

        prefix, suffix = word[:index], word[index + 2 :]
        swapped = prefix + (right, left) + suffix
        fermion_swap = left == "a_1_m" and right == "a_1_p"
        result = {
            term: (-coefficient if fermion_swap else coefficient)
            for term, coefficient in _normal_word(swapped, rank, deform).items()
        }
        contraction = sp.Integer(0)
        if fermion_swap:
            contraction = sp.Integer(1)
        elif left.startswith("b_") and right.startswith("b_"):
            left_index, left_sign = left[2:].split("_")
            right_index, right_sign = right[2:].split("_")
            if left_sign == "m" and right_sign == "p" and left_index == right_index:
                contraction = sp.Integer(1)
        if contraction:
            for term, coefficient in _normal_word(prefix + suffix, rank, deform).items():
                result[term] = result.get(term, 0) + contraction * coefficient
                if not result[term]:
                    del result[term]

        if deform and left.startswith("b_") and right.startswith("a_"):
            fermion_sign = right[-1]
            boson_index, boson_sign = left[2:].split("_")
            parameter = sp.Symbol(
                f"gb_a1_{fermion_sign}_b{boson_index}_{boson_sign}"
            )
            moved_sign = -1 if _parity(prefix) else 1
            for term, coefficient in _normal_word(
                prefix + suffix, rank, deform=False
            ).items():
                key = (term[0], 1)
                result[key] = result.get(key, 0) - (
                    moved_sign * parameter * coefficient
                )
                if not result[key]:
                    del result[key]
        return result
    return {(word, 0): sp.Integer(1)}


def _add_scaled(
    target: Polynomial, source: Polynomial, scale: sp.Expr = sp.Integer(1)
) -> None:
    for term, coefficient in source.items():
        target[term] = sp.expand(target.get(term, 0) + scale * coefficient)
        if not target[term]:
            del target[term]


def _multiply(left: Polynomial, right: Polynomial, rank: int) -> Polynomial:
    result: Polynomial = {}
    for (left_word, left_kappa), left_coefficient in left.items():
        for (right_word, right_kappa), right_coefficient in right.items():
            if left_kappa and right_kappa:
                continue
            move_sign = -1 if right_kappa and _parity(left_word) else 1
            normal = _normal_word(
                left_word + right_word, rank, deform=not (left_kappa or right_kappa)
            )
            for (word, correction_kappa), coefficient in normal.items():
                term = (word, left_kappa + right_kappa + correction_kappa)
                if term[1] > 1:
                    continue
                result[term] = result.get(term, 0) + (
                    move_sign * left_coefficient * right_coefficient * coefficient
                )
                if not result[term]:
                    del result[term]
    return result


def _bracket(
    left: Polynomial, right: Polynomial, rank: int, sign: int
) -> Polynomial:
    result = _multiply(left, right, rank)
    _add_scaled(result, _multiply(right, left, rank), sp.Integer(-1 if sign == 0 else 1))
    return result


def _structure_lookup(data: dict) -> dict[tuple[str, str], dict[str, sp.Rational]]:
    result: dict[tuple[str, str], dict[str, sp.Rational]] = {}
    for entry in data["structure_constants"]:
        coefficients = result.setdefault((entry["X"], entry["Y"]), {})
        coefficients[entry["Z"]] = coefficients.get(entry["Z"], 0) + sp.Rational(
            entry["coeff"]
        )
    return result


def _parameter_matrix(rank: int) -> dict:
    columns = [
        f"b_{k}_{sign}"
        for k in range(1, rank + 1)
        for sign in ("p", "m")
    ]
    rows = ["a_1_p", "a_1_m"]
    return {
        "rows": rows,
        "columns": columns,
        "values": [
            [
                f"gb_a1_{fermion[-1]}_{boson.replace('b_', 'b')}"
                for boson in columns
            ]
            for fermion in rows
        ],
    }


def generate_gamma(rank: int, structure: dict) -> dict:
    even, odd = _labels(rank)
    names = odd + even
    parity = structure["parity"]
    realizations = _realizations(rank)
    coordinate_words, inverse = _coordinate_solver(names, realizations)
    gamma_names = names + ["K"]
    gamma_realizations = {**realizations, "K": {(): sp.Integer(1)}}
    gamma_coordinate_words, gamma_inverse = _coordinate_solver(
        gamma_names, gamma_realizations
    )
    base = _structure_lookup(structure)
    gamma = []

    for left_index, x in enumerate(names):
        for y in names[left_index:]:
            bracket = _bracket(
                {(word, 0): coefficient for word, coefficient in realizations[x].items()},
                {(word, 0): coefficient for word, coefficient in realizations[y].items()},
                rank,
                parity[x] * parity[y],
            )
            ordinary: dict[Word, sp.Expr] = {}
            deformed: dict[Word, sp.Expr] = {}
            for (word, kappa), coefficient in bracket.items():
                target = deformed if kappa else ordinary
                target[word] = target.get(word, 0) + coefficient
            expected = base.get((x, y), {})
            coordinates = [
                sp.simplify(
                    sum(
                        (factor * ordinary.get(word, 0) for factor, word in zip(row, coordinate_words)),
                        sp.Integer(0),
                    )
                )
                for row in inverse
            ]
            reconstructed: dict[Word, sp.Expr] = {}
            for z, coefficient in zip(names, coordinates):
                for word, factor in realizations[z].items():
                    reconstructed[word] = sp.expand(
                        reconstructed.get(word, 0) + coefficient * factor
                    )
            ordinary = {word: value for word, value in ordinary.items() if value}
            reconstructed = {
                word: value for word, value in reconstructed.items() if value
            }
            if ordinary != reconstructed:
                raise ValueError(f"Undeformed part of [{x},{y}] changed under gb rules")
            expected_reconstructed = {
                word: sp.Integer(0) for word in ()
            }
            for z, coefficient in expected.items():
                for word, factor in realizations[z].items():
                    expected_reconstructed[word] = sp.expand(
                        expected_reconstructed.get(word, 0)
                        + coefficient * factor
                    )
            expected_reconstructed = {
                word: value
                for word, value in expected_reconstructed.items()
                if value
            }
            if expected_reconstructed != ordinary:
                raise ValueError(f"Schema 1 mismatch for the bracket [{x},{y}]")
            gamma_coordinates = [
                sp.simplify(
                    sum(
                        (
                            factor * deformed.get(word, 0)
                            for factor, word in zip(row, gamma_coordinate_words)
                        ),
                        sp.Integer(0),
                    )
                )
                for row in gamma_inverse
            ]
            gamma_reconstructed: dict[Word, sp.Expr] = {}
            for z, coefficient in zip(gamma_names, gamma_coordinates):
                if not coefficient:
                    continue
                for word, factor in gamma_realizations[z].items():
                    gamma_reconstructed[word] = sp.expand(
                        gamma_reconstructed.get(word, 0) + coefficient * factor
                    )
            if {
                word: value for word, value in gamma_reconstructed.items() if value
            } != {word: value for word, value in deformed.items() if value}:
                raise ValueError(f"Gamma bracket [{x},{y}] is outside the basis")
            for z, coefficient in zip(gamma_names, gamma_coordinates):
                coefficient = sp.factor(coefficient)
                if coefficient:
                    gamma.append(
                        {
                            "X": x,
                            "Y": y,
                            "Z": z,
                            "coeff": str(coefficient),
                        }
                    )

    result = copy.deepcopy(structure)
    result["inhomogeneous_deformation"] = {
        "generated_by": "src/C_gamma.py",
        "gb_matrix": _parameter_matrix(rank),
        "parameter_parity": 1,
        "gamma_coefficients": gamma,
        "definition": "[b_j^s, a_1^sigma] = -gb_sigma,j,s * kappa",
    }
    return result


def write_gamma(rank: int, data_dir: Path) -> Path:
    structure_path = data_dir / f"C_{rank}_structure.json"
    with structure_path.open(encoding="utf-8") as source:
        structure = json.load(source)
    path = data_dir / f"C_{rank}_gamma.json"
    path.write_text(
        json.dumps(generate_gamma(rank, structure), indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    for n in (1, 2, 3):
        print(write_gamma(n, root / "data"))
