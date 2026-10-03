"""Generate the inhomogeneous gamma structure for C(n+1).

The script validates the undeformed bracket against Schema 1 and writes
C_1_gamma.json, C_2_gamma.json, and C_3_gamma.json to data/.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from functools import lru_cache
from itertools import product
from pathlib import Path
from typing import Hashable, TypeAlias, TypeVar

if __package__:
    from .C_generators import _build_decomposer, _build_generators
else:
    from C_generators import _build_decomposer, _build_generators


Token: TypeAlias = tuple[str, int] | tuple[str, int, int]
Word: TypeAlias = tuple[Token, ...]
Polynomial: TypeAlias = dict[Word, Fraction]
Parameter: TypeAlias = tuple[int, int, int]  # fermion sign, mode, boson sign
GammaPolynomial: TypeAlias = dict[tuple[Parameter, Word], Fraction]
Expression: TypeAlias = tuple[Polynomial, GammaPolynomial]
K = TypeVar("K", bound=Hashable)

_FERMION_NAMES = ("a_1_p", "a_1_m")


def _clean(terms: dict[K, Fraction]) -> dict[K, Fraction]:
    return {key: coeff for key, coeff in terms.items() if coeff}


def _add_scaled(
    target: dict[K, Fraction], source: dict[K, Fraction], scale: Fraction
) -> None:
    for key, coeff in source.items():
        target[key] = target.get(key, Fraction(0)) + scale * coeff
        if not target[key]:
            del target[key]


def _token_order(token: Token) -> tuple[int, ...]:
    if token[0] == "a":
        return 0, int(token[1])
    mode, sign = int(token[1]), int(token[2])
    return 1 + sign, mode


def _is_fermion(token: Token) -> bool:
    return token[0] == "a"


def _word_parity(word: Word) -> int:
    return sum(_is_fermion(token) for token in word) % 2


@lru_cache(maxsize=None)
def _normal_order_word(
    word: Word, deform_mixed: bool = True
) -> tuple[
    tuple[tuple[Word, Fraction], ...],
    tuple[tuple[Parameter, Word, Fraction], ...],
]:
    base: Polynomial = {}
    gamma: GammaPolynomial = {}

    def include(candidate: Word, scale: Fraction) -> None:
        normal_base, normal_gamma = _normal_order_word(candidate, deform_mixed)
        _add_scaled(base, dict(normal_base), scale)
        for parameter, normal_word, coeff in normal_gamma:
            key = parameter, normal_word
            gamma[key] = gamma.get(key, Fraction(0)) + scale * coeff
            if not gamma[key]:
                del gamma[key]

    for index in range(len(word) - 1):
        left, right = word[index], word[index + 1]
        if _is_fermion(left) and left == right:
            return (), ()
        if _token_order(left) <= _token_order(right):
            continue

        prefix, suffix = word[:index], word[index + 2 :]
        swapped = prefix + (right, left) + suffix

        if _is_fermion(left) and _is_fermion(right):
            include(swapped, Fraction(-1))
            include(prefix + suffix, Fraction(1))
        elif left[0] == "b" and right[0] == "b":
            include(swapped, Fraction(1))
            if left[1] == right[1]:
                include(prefix + suffix, Fraction(1))
        elif left[0] == "b" and right[0] == "a":
            include(swapped, Fraction(1))
            if deform_mixed:
                parameter = int(right[1]), int(left[1]), int(left[2])
                prefix_sign = -1 if _word_parity(prefix) else 1
                contraction = _normal_order_word(prefix + suffix, False)[0]
                for normal_word, coeff in contraction:
                    key = parameter, normal_word
                    gamma[key] = (
                        gamma.get(key, Fraction(0)) - prefix_sign * coeff
                    )
                    if not gamma[key]:
                        del gamma[key]
        else:
            raise AssertionError(f"Unexpected oscillator ordering: {left}, {right}")

        return (
            tuple(sorted(_clean(base).items())),
            tuple(
                (parameter, normal_word, coeff)
                for (parameter, normal_word), coeff in sorted(gamma.items())
                if coeff
            ),
        )

    return ((word, Fraction(1)),), ()


def _multiply(left: Expression, right: Expression) -> Expression:
    left_base, left_gamma = left
    right_base, right_gamma = right
    base_result: Polynomial = {}
    gamma_result: GammaPolynomial = {}

    for left_word, left_coeff in left_base.items():
        for right_word, right_coeff in right_base.items():
            scale = left_coeff * right_coeff
            normal_base, normal_gamma = _normal_order_word(left_word + right_word)
            _add_scaled(base_result, dict(normal_base), scale)
            for parameter, normal_word, coeff in normal_gamma:
                key = parameter, normal_word
                gamma_result[key] = (
                    gamma_result.get(key, Fraction(0)) + scale * coeff
                )

    for (parameter, left_word), left_coeff in left_gamma.items():
        for right_word, right_coeff in right_base.items():
            normal_base, _ = _normal_order_word(left_word + right_word, False)
            for normal_word, coeff in normal_base:
                key = parameter, normal_word
                gamma_result[key] = (
                    gamma_result.get(key, Fraction(0))
                    + left_coeff * right_coeff * coeff
                )

    for left_word, left_coeff in left_base.items():
        for (parameter, right_word), right_coeff in right_gamma.items():
            sign = -1 if _word_parity(left_word) else 1
            normal_base, _ = _normal_order_word(left_word + right_word, False)
            for normal_word, coeff in normal_base:
                key = parameter, normal_word
                gamma_result[key] = (
                    gamma_result.get(key, Fraction(0))
                    + sign * left_coeff * right_coeff * coeff
                )

    return _clean(base_result), _clean(gamma_result)


def _super_bracket(
    left: Expression,
    right: Expression,
    left_parity: int,
    right_parity: int,
) -> Expression:
    forward = _multiply(left, right)
    reverse = _multiply(right, left)
    sign = -1 if left_parity and right_parity else 1
    base = dict(forward[0])
    gamma = dict(forward[1])
    _add_scaled(base, reverse[0], Fraction(-sign))
    _add_scaled(gamma, reverse[1], Fraction(-sign))
    return _clean(base), _clean(gamma)


def _to_word_polynomial(source_poly: dict) -> Polynomial:
    result: Polynomial = {}
    for (fermions, bosons), coeff in source_poly.items():
        word: Word = tuple(("a", sign) for sign in fermions) + tuple(
            ("b", mode, sign) for mode, sign in bosons
        )
        result[word] = result.get(word, Fraction(0)) + coeff
    return _clean(result)


def _to_source_polynomial(poly: Polynomial) -> dict:
    result = {}
    for word, coeff in poly.items():
        split = next(
            (
                index
                for index, token in enumerate(word)
                if token[0] == "b"
            ),
            len(word),
        )
        fermions = tuple(int(token[1]) for token in word[:split])
        bosons = tuple(
            (int(token[1]), int(token[2])) for token in word[split:]
        )
        key = fermions, bosons
        result[key] = result.get(key, Fraction(0)) + coeff
    return _clean(result)


def _parameter_name(parameter: Parameter) -> str:
    fermion_sign, mode, boson_sign = parameter
    fermion = "p" if fermion_sign == 0 else "m"
    boson = "p" if boson_sign == 0 else "m"
    return f"gb_a1{fermion}_b{mode}{boson}"


def _parameter_matrix(n: int) -> dict:
    columns = [
        f"b_{mode}_{sign}"
        for mode in range(1, n + 1)
        for sign in ("p", "m")
    ]
    return {
        "shape": [2, 2 * n],
        "row_labels": list(_FERMION_NAMES),
        "column_labels": columns,
        "entries": [
            [
                _parameter_name(
                    (
                        fermion_sign,
                        mode,
                        0 if boson_sign == "p" else 1,
                    )
                )
                for mode in range(1, n + 1)
                for boson_sign in ("p", "m")
            ]
            for fermion_sign in (0, 1)
        ],
    }


def _fraction_string(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def _ordered_coefficients(
    poly: dict[str, Fraction], labels: list[str]
) -> dict[str, Fraction]:
    label_order = {label: index for index, label in enumerate(labels)}
    return {
        label: coeff
        for label, coeff in sorted(
            poly.items(), key=lambda item: label_order[item[0]]
        )
        if coeff
    }


def _expected_brackets(
    schema1: dict,
) -> dict[tuple[str, str], dict[str, Fraction]]:
    result: dict[tuple[str, str], dict[str, Fraction]] = {}
    for row in schema1["structure_constants"]:
        key = row["X"], row["Y"]
        values = result.setdefault(key, {})
        values[row["Z"]] = values.get(row["Z"], Fraction(0)) + Fraction(
            row["coeff"]
        )
    return result


def _check_cocycle(
    labels: list[str],
    parity: dict[str, int],
    base: dict[tuple[str, str], dict[str, Fraction]],
    gamma: dict[tuple[str, str, str, str], Fraction],
) -> None:
    by_pair: dict[tuple[str, str], dict[tuple[str, str], Fraction]] = defaultdict(
        dict
    )
    for (left, right, parameter, result), coeff in gamma.items():
        by_pair[(left, right)][parameter, result] = coeff

    for x, y, z in product(labels, repeat=3):
        cocycle: dict[tuple[str, str], Fraction] = {}
        cyclic_terms = (
            (x, y, z, -1 if parity[x] * parity[z] else 1),
            (y, z, x, -1 if parity[y] * parity[x] else 1),
            (z, x, y, -1 if parity[z] * parity[y] else 1),
        )
        for outer, middle_a, middle_b, sign in cyclic_terms:
            for intermediate, base_coeff in base.get(
                (middle_a, middle_b), {}
            ).items():
                for (parameter, result), gamma_coeff in by_pair.get(
                    (outer, intermediate), {}
                ).items():
                    key = parameter, result
                    cocycle[key] = (
                        cocycle.get(key, Fraction(0))
                        + sign * base_coeff * gamma_coeff
                    )

            adjoint_sign = -1 if parity[outer] else 1
            for (parameter, intermediate), gamma_coeff in by_pair.get(
                (middle_a, middle_b), {}
            ).items():
                for result, base_coeff in base.get(
                    (outer, intermediate), {}
                ).items():
                    key = parameter, result
                    cocycle[key] = (
                        cocycle.get(key, Fraction(0))
                        + sign * adjoint_sign * gamma_coeff * base_coeff
                    )

        nonzero = {key: coeff for key, coeff in cocycle.items() if coeff}
        if nonzero:
            raise ValueError(
                f"Gamma cocycle identity fails at ({x}, {y}, {z}): {nonzero}"
            )


def build_gamma_schema(n: int, data_dir: Path = Path("data")) -> dict:
    schema1_path = data_dir / f"C_{n}_structure.json"
    schema1 = json.loads(schema1_path.read_text(encoding="utf-8"))
    even, odd, source_realizations = _build_generators(n)
    if schema1["basis"]["even"] != even or schema1["basis"]["odd"] != odd:
        raise ValueError(f"{schema1_path}: basis does not match the generator.")
    labels = odd + even
    parity = schema1["parity"]
    source_decompose = _build_decomposer(source_realizations)
    gamma_realizations = dict(source_realizations)
    gamma_realizations["K"] = {((), ()): Fraction(1)}
    gamma_decompose = _build_decomposer(gamma_realizations)
    gamma_labels = labels + ["K"]
    realizations: dict[str, Expression] = {
        label: (_to_word_polynomial(source_realizations[label]), {})
        for label in labels
    }
    expected = _expected_brackets(schema1)
    parameter_names = {
        (fermion_sign, mode, boson_sign): _parameter_name(
            (fermion_sign, mode, boson_sign)
        )
        for fermion_sign in (0, 1)
        for mode in range(1, n + 1)
        for boson_sign in (0, 1)
    }

    gamma_rows = []
    gamma_table: dict[tuple[str, str, str, str], Fraction] = {}
    for left in labels:
        for right in labels:
            base_bracket, gamma_bracket = _super_bracket(
                realizations[left],
                realizations[right],
                parity[left],
                parity[right],
            )
            actual_base = source_decompose(_to_source_polynomial(base_bracket))
            actual_base = _ordered_coefficients(actual_base, labels)
            expected_base = _ordered_coefficients(
                expected.get((left, right), {}), labels
            )
            if actual_base != expected_base:
                raise ValueError(
                    f"Schema 1 mismatch at ({left}, {right}): "
                    f"generated {actual_base}, stored {expected_base}"
                )

            by_parameter: dict[Parameter, Polynomial] = {}
            for (parameter, word), coeff in gamma_bracket.items():
                poly = by_parameter.setdefault(parameter, {})
                poly[word] = poly.get(word, Fraction(0)) + coeff
            for parameter, poly in by_parameter.items():
                decomposed = gamma_decompose(_to_source_polynomial(poly))
                for result, coeff in _ordered_coefficients(
                    decomposed, gamma_labels
                ).items():
                    result_parity = parity.get(result, 0)
                    if result_parity != (
                        parity[left] + parity[right] + 1
                    ) % 2:
                        raise ValueError(
                            "Gamma parity mismatch at "
                            f"({left}, {right}) -> {result}."
                        )
                    parameter_name = parameter_names[parameter]
                    gamma_table[(left, right, parameter_name, result)] = coeff
                    gamma_rows.append(
                        {
                            "X": left,
                            "Y": right,
                            "parameter": parameter_name,
                            "Z": result,
                            "coeff": _fraction_string(coeff),
                        }
                    )

    for left in labels:
        for right in labels:
            factor = -1 if parity[left] * parity[right] == 0 else 1
            for parameter in parameter_names.values():
                for result in gamma_labels:
                    actual = gamma_table.get(
                        (left, right, parameter, result), Fraction(0)
                    )
                    reverse = gamma_table.get(
                        (right, left, parameter, result), Fraction(0)
                    )
                    if actual != factor * reverse:
                        raise ValueError(
                            "Gamma graded skew-symmetry mismatch at "
                            f"({left}, {right}, {parameter}, {result})."
                        )

    _check_cocycle(labels, parity, expected, gamma_table)

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "osp": f"osp(2|{2 * n})",
        },
        "base_schema": f"C_{n}_structure.json",
        "inhomogeneous_deformation": {
            "type": "inhomogeneous",
            "gb_matrix": _parameter_matrix(n),
            "oscillator_exchange_relations": {
                "forward": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa",
                "reverse": "[a_1^sigma, b_j^s] = +gb_{sigma,j,s} * kappa",
                "index_sets": {
                    "sigma": ["+", "-"],
                    "s": ["+", "-"],
                    "j": f"1,...,{n}",
                },
            },
            "parameter_parity": {
                "gb_scalar": 0,
                "kappa": 1,
                "gb_times_kappa": 1,
                "description": (
                    "The reference's parity-1 parameter convention denotes "
                    "the combined gb*kappa term; each gb entry is an "
                    "ordinary scalar."
                ),
            },
            "coefficient_order": "kappa * gb_parameter * Z",
            "nilpotency": "kappa^2 = 0; terms of order kappa^2 are discarded",
            "central_outputs": ["K"],
            "bracket_formula": (
                "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)"
            ),
            "gamma_coefficients": gamma_rows,
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                f"data/C_{n}_structure.json",
            ],
        },
    }


def generate_files(data_dir: Path = Path("data")) -> list[Path]:
    written = []
    for n in (1, 2, 3):
        destination = data_dir / f"C_{n}_gamma.json"
        schema = build_gamma_schema(n, data_dir)
        destination.write_text(
            json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written.append(destination)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data",
        help="Directory containing Schema 1 and receiving Schema 2 files",
    )
    args = parser.parse_args()
    for path in generate_files(args.data_dir):
        print(path)


if __name__ == "__main__":
    main()
