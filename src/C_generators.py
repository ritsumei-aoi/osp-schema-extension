"""Generate exact Schema 1 structure data for C(n+1)=osp(2|2n)."""

from __future__ import annotations

import json
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import TypeAlias

Word: TypeAlias = tuple[str, ...]
Polynomial: TypeAlias = dict[Word, Fraction]


def _format_fraction(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _labels(n: int) -> tuple[list[str], list[str]]:
    even = ["H_eps", *(f"H_{k}" for k in range(1, n + 1))]
    even.extend(f"E_2del{k}_p" for k in range(1, n + 1))
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.extend(
                f"E_del{i}_del{j}_{signs}"
                for signs in ("pp", "pm", "mp", "mm")
            )
    even.extend(f"E_2del{k}_m" for k in range(1, n + 1))
    odd = [
        f"E_eps1_del{k}_{signs}"
        for k in range(1, n + 1)
        for signs in ("pp", "pm", "mp", "mm")
    ]
    return even, odd


def _normal_word(word: Word, n: int) -> Polynomial:
    rank = {"a_1_p": 0, "a_1_m": 1}
    for k in range(1, n + 1):
        rank[f"b_{k}_p"] = 2 + 2 * (k - 1)
        rank[f"b_{k}_m"] = 3 + 2 * (k - 1)

    for i in range(len(word) - 1):
        left, right = word[i], word[i + 1]
        if left == right and left in {"a_1_p", "a_1_m"}:
            return {}
        if rank[left] <= rank[right]:
            continue

        swapped = word[:i] + (right, left) + word[i + 2 :]
        result = {key: -value for key, value in _normal_word(swapped, n).items()} if (
            left == "a_1_m" and right == "a_1_p"
        ) else _normal_word(swapped, n)
        contraction = Fraction(0)
        contracted_word = word[:i] + word[i + 2 :]
        if left == "a_1_m" and right == "a_1_p":
            contraction = Fraction(1)
        elif left.startswith("b_") and right.startswith("b_"):
            left_index, left_sign = left[2:].split("_")
            right_index, right_sign = right[2:].split("_")
            if left_sign == "m" and right_sign == "p" and left_index == right_index:
                contraction = Fraction(1)
        if contraction:
            for key, value in _normal_word(contracted_word, n).items():
                result[key] = result.get(key, Fraction(0)) + contraction * value
                if not result[key]:
                    del result[key]
        return result
    return {word: Fraction(1)}


def _add_scaled(target: Polynomial, source: Polynomial, scale: Fraction) -> None:
    for word, coefficient in source.items():
        target[word] = target.get(word, Fraction(0)) + scale * coefficient
        if not target[word]:
            del target[word]


def _multiply(left: Polynomial, right: Polynomial, n: int) -> Polynomial:
    result: Polynomial = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            normalized = _normal_word(left_word + right_word, n)
            _add_scaled(result, normalized, left_coefficient * right_coefficient)
    return result


def _bracket(left: Polynomial, right: Polynomial, n: int, parity: int) -> Polynomial:
    first = _multiply(left, right, n)
    second = _multiply(right, left, n)
    _add_scaled(first, second, Fraction(-1 if parity == 0 else 1))
    return first


def _monomial(*words: str, coefficient: Fraction = Fraction(1)) -> Polynomial:
    return {tuple(words): coefficient}


def _realizations(n: int) -> dict[str, Polynomial]:
    result: dict[str, Polynomial] = {
        "H_eps": {
            ("a_1_p", "a_1_m"): Fraction(1),
            (): Fraction(-1, 2),
        }
    }
    for k in range(1, n + 1):
        result[f"H_{k}"] = {
            (f"b_{k}_p", f"b_{k}_m"): Fraction(1),
            (): Fraction(1, 2),
        }
        result[f"E_2del{k}_p"] = _monomial(
            f"b_{k}_p", f"b_{k}_p", coefficient=Fraction(1, 2)
        )
        result[f"E_2del{k}_m"] = _monomial(
            f"b_{k}_m", f"b_{k}_m", coefficient=Fraction(1, 2)
        )
        for signs, fermion in (
            ("pp", "a_1_p"),
            ("pm", "a_1_p"),
            ("mp", "a_1_m"),
            ("mm", "a_1_m"),
        ):
            boson = f"b_{k}_{signs[1]}"
            result[f"E_eps1_del{k}_{signs}"] = _monomial(fermion, boson)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            result[f"E_del{i}_del{j}_pp"] = _monomial(f"b_{i}_p", f"b_{j}_p")
            result[f"E_del{i}_del{j}_pm"] = _monomial(f"b_{i}_p", f"b_{j}_m")
            result[f"E_del{i}_del{j}_mp"] = _monomial(f"b_{i}_m", f"b_{j}_p")
            result[f"E_del{i}_del{j}_mm"] = _monomial(f"b_{i}_m", f"b_{j}_m")
    return result


def _inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    augmented = [
        row[:] + [Fraction(i == j) for j in range(size)]
        for i, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if augmented[row][column]), None
        )
        if pivot is None:
            raise ValueError("The generator realizations are linearly dependent")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(size):
            if row == column or not augmented[row][column]:
                continue
            scale = augmented[row][column]
            augmented[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(augmented[row], augmented[column])
            ]
    return [row[size:] for row in augmented]


def _coordinate_solver(
    names: list[str], realizations: dict[str, Polynomial]
) -> tuple[list[Word], list[list[Fraction]]]:
    monomials = sorted(set().union(*(set(realizations[name]) for name in names)))
    columns = [
        [realizations[name].get(word, Fraction(0)) for name in names]
        for word in monomials
    ]
    echelon: list[list[Fraction]] = []
    selected: list[int] = []
    for index, row in enumerate(columns):
        reduced = row[:]
        for pivot, base in zip(
            (next((j for j, value in enumerate(line) if value), -1) for line in echelon),
            echelon,
        ):
            if pivot >= 0 and reduced[pivot]:
                scale = reduced[pivot]
                reduced = [
                    value - scale * base_value
                    for value, base_value in zip(reduced, base)
                ]
        pivot = next((j for j, value in enumerate(reduced) if value), None)
        if pivot is None:
            continue
        scale = reduced[pivot]
        reduced = [value / scale for value in reduced]
        echelon.append(reduced)
        selected.append(index)
        if len(selected) == len(names):
            break
    if len(selected) != len(names):
        raise ValueError("Could not find independent coordinates for the basis")
    square = [columns[index] for index in selected]
    return [monomials[index] for index in selected], _inverse(square)


def _coordinates(
    polynomial: Polynomial,
    coordinate_words: list[Word],
    inverse: list[list[Fraction]],
) -> list[Fraction]:
    values = [polynomial.get(word, Fraction(0)) for word in coordinate_words]
    return [
        sum((coefficient * value for coefficient, value in zip(row, values)), Fraction(0))
        for row in inverse
    ]


def generate_structure(n: int) -> dict:
    if n < 1:
        raise ValueError("The bosonic rank n must be positive")
    even, odd = _labels(n)
    names = odd + even
    parity = {name: int(name in odd) for name in names}
    realizations = _realizations(n)
    coordinate_words, inverse = _coordinate_solver(names, realizations)
    constants = []
    for x_index, x in enumerate(names):
        for y in names[x_index:]:
            bracket = _bracket(
                realizations[x], realizations[y], n, parity[x] * parity[y]
            )
            coefficients = _coordinates(bracket, coordinate_words, inverse)
            reconstructed: Polynomial = {}
            for name, coefficient in zip(names, coefficients):
                _add_scaled(reconstructed, realizations[name], coefficient)
            if reconstructed != bracket:
                raise ValueError(f"Bracket [{x},{y}] is outside the stated basis")
            for z, coefficient in zip(names, coefficients):
                if coefficient:
                    constants.append(
                        {
                            "X": x,
                            "Y": y,
                            "Z": z,
                            "coeff": _format_fraction(coefficient),
                            "sign_rule": "graded",
                        }
                    )

    def realization_json(name: str) -> dict:
        polynomial = realizations[name]
        return {
            "standard_form": [
                {"words": list(word), "coeff": _format_fraction(coefficient)}
                for word, coefficient in sorted(polynomial.items())
            ],
            "parity": parity[name],
        }

    total = len(names)
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n)",
            },
            "dimension": {
                "total": total,
                "even": len(even),
                "odd": len(odd),
            },
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "count": 2,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "One standard fermionic pair a_1^+, a_1^-",
            },
            "bosons": {
                "rank": n,
                "count": 2 * n,
                "labels": [
                    label
                    for k in range(1, n + 1)
                    for label in (f"b_{k}_p", f"b_{k}_m")
                ],
                "parity": 0,
                "description": "Bosonic oscillator pairs b_k^+, b_k^- for k=1,...,n",
            },
        },
        "oscillator_relations": {
            "fermion_anticommutators": {
                "description": "Canonical anticommutation relations",
                "relations": {
                    "pair": "{a_1_m, a_1_p} = 1",
                    "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0",
                },
            },
            "boson_commutators": {
                "description": "Canonical commutation relations",
                "relations": {
                    "same_type": "[b_i^s, b_j^s] = 0 for s in {+,-}",
                    "conjugate_pair": "[b_i^-, b_j^+] = delta_ij",
                },
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^s, a_1^t] = 0 in the undeformed algebra"
            },
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "central": True,
                "nilpotent": True,
                "relation": "kappa^2 = 0",
            },
            "K": {
                "parity": 0,
                "central": True,
                "identified_with_scalar": 1,
            },
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": (
                "PBW: kappa, then odd block, then even block; K=1 excluded"
            ),
        },
        "parity": parity,
        "generator_realization": {
            "description": "Normal-ordered oscillator realization",
            "ordering": [
                "a_1_p",
                "a_1_m",
                *[
                    label
                    for k in range(1, n + 1)
                    for label in (f"b_{k}_p", f"b_{k}_m")
                ],
            ],
            "realizations": {
                name: realization_json(name) for name in names
            },
        },
        "structure_constants": constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "docs/math/Cn1_definition.md",
            ],
        },
    }


def write_structure(n: int, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"C_{n}_structure.json"
    path.write_text(
        json.dumps(generate_structure(n), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    for rank in (1, 2, 3):
        print(write_structure(rank, root / "data"))
