"""Draft exact structure-constant generator for C(n+1).

Run this script to write C_1_structure.json, C_2_structure.json, and
C_3_structure.json to data/. Import build_schema() to compute a schema
without writing files.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import TypeAlias


FermionWord: TypeAlias = tuple[int, ...]  # 0: a_1^+, 1: a_1^-
BosonToken: TypeAlias = tuple[int, int]  # (mode, 0 for +, 1 for -)
BosonWord: TypeAlias = tuple[BosonToken, ...]
Monomial: TypeAlias = tuple[FermionWord, BosonWord]
Polynomial: TypeAlias = dict[Monomial, Fraction]
Realization = dict[str, Polynomial]

_FERMION_LABELS = ("a_1_p", "a_1_m")
_BOSON_SIGNS = (0, 1)
_SUFFIXES = ("pp", "pm", "mp", "mm")
_SUFFIX_SIGNS = {
    "pp": (0, 0),
    "pm": (0, 1),
    "mp": (1, 0),
    "mm": (1, 1),
}


def _clean(poly: Polynomial) -> Polynomial:
    return {word: coeff for word, coeff in poly.items() if coeff}


def _add_scaled(
    target: dict, source: dict, scale: Fraction
) -> None:
    for key, coeff in source.items():
        target[key] = target.get(key, Fraction(0)) + scale * coeff
        if not target[key]:
            del target[key]


def _fermion_order_key(word: FermionWord) -> tuple[int, ...]:
    return word


@lru_cache(maxsize=None)
def _normal_order_fermions(word: FermionWord) -> tuple[tuple[FermionWord, Fraction], ...]:
    for index in range(len(word) - 1):
        left, right = word[index], word[index + 1]
        if left == right:
            return ()
        if left > right:
            prefix, suffix = word[:index], word[index + 2 :]
            swapped = prefix + (right, left) + suffix
            contracted = prefix + suffix
            result: dict[FermionWord, Fraction] = {}
            for normal, coeff in _normal_order_fermions(swapped):
                result[normal] = result.get(normal, Fraction(0)) - coeff
            for normal, coeff in _normal_order_fermions(contracted):
                result[normal] = result.get(normal, Fraction(0)) + coeff
            return tuple(
                (normal, coeff)
                for normal, coeff in result.items()
                if coeff
            )
    return ((word, Fraction(1)),)


def _boson_order_key(token: BosonToken) -> tuple[int, int]:
    mode, sign = token
    return sign, mode


@lru_cache(maxsize=None)
def _normal_order_bosons(word: BosonWord) -> tuple[tuple[BosonWord, Fraction], ...]:
    for index in range(len(word) - 1):
        left, right = word[index], word[index + 1]
        if _boson_order_key(left) > _boson_order_key(right):
            prefix, suffix = word[:index], word[index + 2 :]
            swapped = prefix + (right, left) + suffix
            result: dict[BosonWord, Fraction] = {}
            for normal, coeff in _normal_order_bosons(swapped):
                result[normal] = result.get(normal, Fraction(0)) + coeff
            if left[1] == 1 and right[1] == 0 and left[0] == right[0]:
                contracted = prefix + suffix
                for normal, coeff in _normal_order_bosons(contracted):
                    result[normal] = result.get(normal, Fraction(0)) + coeff
            return tuple(
                (normal, coeff)
                for normal, coeff in result.items()
                if coeff
            )
    return ((word, Fraction(1)),)


def _multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for (left_fermions, left_bosons), left_coeff in left.items():
        for (right_fermions, right_bosons), right_coeff in right.items():
            coeff = left_coeff * right_coeff
            fermions = _normal_order_fermions(left_fermions + right_fermions)
            bosons = _normal_order_bosons(left_bosons + right_bosons)
            for normal_fermions, fermion_coeff in fermions:
                for normal_bosons, boson_coeff in bosons:
                    monomial = normal_fermions, normal_bosons
                    result[monomial] = (
                        result.get(monomial, Fraction(0))
                        + coeff * fermion_coeff * boson_coeff
                    )
    return _clean(result)


def _super_bracket(
    left: Polynomial,
    right: Polynomial,
    left_parity: int,
    right_parity: int,
) -> Polynomial:
    result = _multiply(left, right)
    sign = -1 if left_parity and right_parity else 1
    _add_scaled(result, _multiply(right, left), Fraction(-sign))
    return _clean(result)


def _monomial(
    fermions: FermionWord = (), bosons: BosonWord = (), coeff: int | Fraction = 1
) -> Polynomial:
    value = Fraction(coeff)
    if not value:
        return {}
    result: Polynomial = {}
    for normal_fermions, fermion_coeff in _normal_order_fermions(fermions):
        for normal_bosons, boson_coeff in _normal_order_bosons(bosons):
            key = normal_fermions, normal_bosons
            result[key] = (
                result.get(key, Fraction(0))
                + value * fermion_coeff * boson_coeff
            )
    return _clean(result)


def _sum_polynomials(*terms: tuple[Polynomial, int | Fraction]) -> Polynomial:
    result: Polynomial = {}
    for poly, coeff in terms:
        _add_scaled(result, poly, Fraction(coeff))
    return _clean(result)


def _build_generators(n: int) -> tuple[list[str], list[str], Realization]:
    if n < 1:
        raise ValueError("The bosonic rank n must be at least 1.")

    even: list[str] = [f"H_{index}" for index in range(1, n + 2)]
    even.extend(f"E_2del{index}_p" for index in range(1, n + 1))
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.extend(
                (
                    f"E_del{i}_del{j}_pp",
                    f"E_del{i}_del{j}_pm",
                )
            )
    even.extend(f"E_2del{index}_m" for index in range(1, n + 1))
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.extend(
                (
                    f"E_del{i}_del{j}_mm",
                    f"E_del{i}_del{j}_mp",
                )
            )

    odd = [
        f"E_eps1_del{index}_{suffix}"
        for index in range(1, n + 1)
        for suffix in _SUFFIXES
    ]
    realizations: Realization = {}

    realizations["H_1"] = _sum_polynomials(
        (_monomial((0, 1)), 1),
        (_monomial(bosons=((1, 0), (1, 1))), 1),
    )
    for index in range(2, n + 1):
        realizations[f"H_{index}"] = _sum_polynomials(
            (_monomial(bosons=((index - 1, 0), (index - 1, 1))), 1),
            (_monomial(bosons=((index, 0), (index, 1))), -1),
        )
    realizations[f"H_{n + 1}"] = _sum_polynomials(
        (_monomial(bosons=((n, 0), (n, 1))), -1),
        (_monomial(), Fraction(-1, 2)),
    )

    for index in range(1, n + 1):
        realizations[f"E_2del{index}_p"] = _monomial(
            bosons=((index, 0), (index, 0))
        )
        realizations[f"E_2del{index}_m"] = _monomial(
            bosons=((index, 1), (index, 1))
        )

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            realizations[f"E_del{i}_del{j}_pp"] = _monomial(
                bosons=((i, 0), (j, 0))
            )
            realizations[f"E_del{i}_del{j}_pm"] = _monomial(
                bosons=((i, 0), (j, 1))
            )
            realizations[f"E_del{i}_del{j}_mp"] = _monomial(
                bosons=((i, 1), (j, 0))
            )
            realizations[f"E_del{i}_del{j}_mm"] = _monomial(
                bosons=((i, 1), (j, 1))
            )

    for index in range(1, n + 1):
        for suffix, (fermion_sign, boson_sign) in _SUFFIX_SIGNS.items():
            realizations[f"E_eps1_del{index}_{suffix}"] = _monomial(
                fermions=(fermion_sign,),
                bosons=((index, boson_sign),),
            )

    if len(even) != 2 * n * n + n + 1 or len(odd) != 4 * n:
        raise AssertionError("Internal error: incorrect C(n+1) basis dimensions.")
    return even, odd, realizations


def _build_decomposer(realizations: Realization):
    pivots: dict[Monomial, tuple[Polynomial, dict[str, Fraction]]] = {}
    for label, vector in realizations.items():
        residual = dict(vector)
        combination = {label: Fraction(1)}
        for pivot, (normal, pivot_combination) in pivots.items():
            scale = residual.get(pivot, Fraction(0))
            if scale:
                _add_scaled(residual, normal, -scale)
                _add_scaled(combination, pivot_combination, -scale)
        if not residual:
            raise ValueError(f"Generator realization {label} is linearly dependent.")
        pivot = min(residual, key=lambda term: term)
        scale = residual[pivot]
        normalized = {term: coeff / scale for term, coeff in residual.items()}
        normalized_combination = {
            name: coeff / scale for name, coeff in combination.items() if coeff
        }
        pivots[pivot] = normalized, normalized_combination

    def decompose(poly: Polynomial) -> dict[str, Fraction]:
        residual = dict(poly)
        combination: dict[str, Fraction] = {}
        for pivot, (normal, pivot_combination) in pivots.items():
            scale = residual.get(pivot, Fraction(0))
            if scale:
                _add_scaled(residual, normal, -scale)
                _add_scaled(combination, pivot_combination, scale)
        if residual:
            raise ValueError(
                f"Bracket is outside the C(n+1) basis span: {residual!r}"
            )
        return {
            label: coeff for label, coeff in combination.items() if coeff
        }

    return decompose


def _fraction_string(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def _format_word(word: tuple[int, ...] | BosonWord) -> str:
    if not word:
        return "1"
    if word and isinstance(word[0], tuple):
        return " ".join(
            f"b_{mode}_{'p' if sign == 0 else 'm'}" for mode, sign in word
        )
    return " ".join(_FERMION_LABELS[sign] for sign in word)


def _frappat_form(label: str, n: int) -> str:
    if label == "H_1":
        return "a_1^+ a_1^- + b_1^+ b_1^-"
    if label.startswith("H_"):
        index = int(label[2:])
        if index == n + 1:
            return f"-b_{n}^+ b_{n}^- - 1/2"
        if index > 1:
            return f"b_{index - 1}^+ b_{index - 1}^- - b_{index}^+ b_{index}^-"
    if label.startswith("E_2del"):
        index, sign = label.removeprefix("E_2del").split("_")
        symbol = "+" if sign == "p" else "-"
        return f"(b_{index}^{symbol})^2"
    if label.startswith("E_del"):
        _, left, right, suffix = label.split("_")
        left = left.removeprefix("del")
        right = right.removeprefix("del")
        first = "+" if suffix[0] == "p" else "-"
        second = "+" if suffix[1] == "p" else "-"
        return f"b_{left}^{first} b_{right}^{second}"
    if label.startswith("E_eps1_del"):
        _, _, index, suffix = label.split("_")
        index = index.removeprefix("del")
        first = "+" if suffix[0] == "p" else "-"
        second = "+" if suffix[1] == "p" else "-"
        return f"a_1^{first} b_{index}^{second}"
    raise KeyError(f"Unknown generator label: {label}")


def _serialize_realization(
    label: str, poly: Polynomial, parity: int, n: int
) -> dict:
    terms = []
    for (fermions, bosons), coeff in sorted(poly.items()):
        words = tuple(
            _FERMION_LABELS[sign] for sign in fermions
        ) + tuple(
            f"b_{mode}_{'p' if sign == 0 else 'm'}" for mode, sign in bosons
        )
        terms.append({"words": list(words), "coeff": _fraction_string(coeff)})
    return {
        "standard_form": terms,
        "frappat_form": _frappat_form(label, n),
        "parity": parity,
    }


def _build_structure_constants(
    ordered_labels: list[str],
    parity: dict[str, int],
    realizations: Realization,
) -> list[dict[str, str]]:
    decompose = _build_decomposer(realizations)
    constants: list[dict[str, str]] = []
    for left_label in ordered_labels:
        for right_label in ordered_labels:
            bracket = _super_bracket(
                realizations[left_label],
                realizations[right_label],
                parity[left_label],
                parity[right_label],
            )
            if not bracket:
                continue
            for result_label, coeff in sorted(
                decompose(bracket).items(),
                key=lambda item: ordered_labels.index(item[0]),
            ):
                if (parity[left_label] + parity[right_label]) % 2 != parity[result_label]:
                    raise ValueError(
                        "Parity violation in bracket "
                        f"({left_label}, {right_label}) -> {result_label}."
                    )
                constants.append(
                    {
                        "X": left_label,
                        "Y": right_label,
                        "Z": result_label,
                        "coeff": _fraction_string(coeff),
                        "sign_rule": "graded",
                    }
                )
    return constants


def build_schema(n: int) -> dict:
    """Compute the complete Schema 1 object for bosonic rank n in memory."""
    even, odd, realizations = _build_generators(n)
    ordered_labels = odd + even
    parity = {label: 1 for label in odd}
    parity.update({label: 0 for label in even})
    structure_constants = _build_structure_constants(
        ordered_labels, parity, realizations
    )

    labels = [
        f"b_{index}_{sign}"
        for index in range(1, n + 1)
        for sign in ("p", "m")
    ]
    realization_records = {
        label: _serialize_realization(
            label, realizations[label], parity[label], n
        )
        for label in ordered_labels
    }

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n) with m=1",
            },
            "dimension": {
                "total": 2 * n * n + 5 * n + 1,
                "even": 2 * n * n + n + 1,
                "odd": 4 * n,
            },
            "dimension_formula": {
                "total": "2n^2+5n+1",
                "even": "2n^2+n+1",
                "odd": "4n",
            },
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "count": 2,
                "labels": list(_FERMION_LABELS),
                "parity": 1,
                "description": "Standard fermionic pair a_1^+, a_1^-",
            },
            "bosons": {
                "n": n,
                "count": 2 * n,
                "labels": labels,
                "description": "Bosonic oscillators b_k^+, b_k^- for k=1,...,n",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": (
                    "Canonical anticommutation relations for the standard "
                    "fermion pair"
                ),
                "relations": {
                    "conjugate_pair": "{a_1_m, a_1_p} = 1",
                    "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0",
                },
            },
            "bosonic_commutators": {
                "description": (
                    "Canonical commutation relations for bosonic oscillators"
                ),
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_ij",
                },
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0"
            },
        },
        "central_elements": {
            "kappa": {
                "label": "κ",
                "parity": 1,
                "central": True,
                "nilpotent": True,
                "relation": "κ^2 = 0",
                "in_basis": False,
            },
            "K": {
                "label": "K",
                "parity": 0,
                "central": True,
                "identified_with": "1",
                "in_basis": False,
                "description": "Even central identity element",
            },
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": (
                "PBW: κ < [odd generators, k ascending and suffix pp, pm, "
                "mp, mm] < [even: Cartan, positive roots, negative roots]; "
                "K = 1 is excluded"
            ),
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ", ".join(
                list(_FERMION_LABELS)
                + [
                    f"b_{index}_{sign}"
                    for index in range(1, n + 1)
                    for sign in ("p", "m")
                ]
            ),
            "realizations": realization_records,
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Frappat et al., arXiv:hep-th/9607161",
            ],
        },
    }


def generate_files(output_dir: Path = Path("data")) -> list[Path]:
    """Write the Schema 1 JSON files for n=1, 2, 3."""
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for n in (1, 2, 3):
        destination = output_dir / f"C_{n}_structure.json"
        destination.write_text(
            json.dumps(build_schema(n), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written.append(destination)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data"),
        help="Directory for generated C_n_structure.json files (default: data/)",
    )
    args = parser.parse_args()
    for path in generate_files(args.output_dir):
        print(path)


if __name__ == "__main__":
    main()
