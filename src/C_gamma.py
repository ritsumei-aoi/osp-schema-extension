#!/usr/bin/env python3
"""Generate and verify Schema 2 gamma data for C(n+1) = osp(2|2n)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from C_generators import (
    AlgebraBasis,
    _express_in_basis,
    _normal_order_word,
    build_basis,
)

Word = tuple[str, ...]
Polynomial = dict[Word, Fraction]
GammaPolynomial = dict[tuple[str, Word], Fraction]
NormalForm = tuple[
    tuple[tuple[Word, Fraction], ...],
    tuple[tuple[str, Word, Fraction], ...],
]


def _atom_key(atom: str) -> tuple[int, int]:
    if atom == "a_1_p":
        return (0, 0)
    if atom == "a_1_m":
        return (1, 0)
    family, rank, sign = atom.split("_")
    if family != "b" or sign not in {"p", "m"}:
        raise ValueError(f"Unknown oscillator label: {atom}")
    return (2 if sign == "p" else 3, int(rank))


def _parameter_for(fermion: str, boson: str) -> str:
    fermion_label = fermion.replace("a_1_", "a1_")
    boson_label = boson.replace("b_", "b")
    return f"gb_{fermion_label}_{boson_label}"


def _prefix_parity(word: Word) -> int:
    return sum(atom.startswith("a_") for atom in word) % 2


def _accumulate(
    target: dict[object, Fraction],
    source: dict[object, Fraction],
    factor: Fraction = Fraction(1),
) -> None:
    for key, coefficient in source.items():
        target[key] = target.get(key, Fraction()) + factor * coefficient
        if not target[key]:
            del target[key]


def _accumulate_normal_form(
    base: dict[Word, Fraction],
    gamma: dict[tuple[str, Word], Fraction],
    normal_form: NormalForm,
    factor: Fraction = Fraction(1),
) -> None:
    _accumulate(base, dict(normal_form[0]), factor)
    _accumulate(
        gamma,
        {
            (parameter, word): coefficient
            for parameter, word, coefficient in normal_form[1]
        },
        factor,
    )


@lru_cache(maxsize=None)
def _normal_order_deformed_word(word: Word) -> NormalForm:
    """Normal-order one word to first order in gb*kappa, with kappa on the left."""
    for index in range(len(word) - 1):
        left, right = word[index], word[index + 1]
        left_key, right_key = _atom_key(left), _atom_key(right)
        is_fermion_pair = left.startswith("a_") and right.startswith("a_")
        is_boson_pair = left.startswith("b_") and right.startswith("b_")

        if is_fermion_pair and left == right:
            return (), ()

        if left_key > right_key:
            prefix, suffix = word[:index], word[index + 2 :]
            swapped = prefix + (right, left) + suffix
            swapped_form = _normal_order_deformed_word(swapped)
            base: dict[Word, Fraction] = defaultdict(Fraction)
            gamma: dict[tuple[str, Word], Fraction] = defaultdict(Fraction)
            swap_sign = Fraction(-1) if is_fermion_pair else Fraction(1)
            _accumulate_normal_form(base, gamma, swapped_form, swap_sign)

            if is_fermion_pair and left == "a_1_m" and right == "a_1_p":
                _accumulate_normal_form(
                    base, gamma, _normal_order_deformed_word(prefix + suffix)
                )
            elif (
                is_boson_pair
                and left.split("_")[1] == right.split("_")[1]
                and left.endswith("_m")
                and right.endswith("_p")
            ):
                _accumulate_normal_form(
                    base, gamma, _normal_order_deformed_word(prefix + suffix)
                )
            elif left.startswith("b_") and right.startswith("a_"):
                parameter = _parameter_for(right, left)
                contraction_sign = Fraction(
                    -1 if _prefix_parity(prefix) == 0 else 1
                )
                for normalized, coefficient in _normal_order_word(prefix + suffix):
                    key = (parameter, normalized)
                    gamma[key] += contraction_sign * coefficient
                    if not gamma[key]:
                        del gamma[key]

            return (
                tuple(
                    (item, coefficient)
                    for item, coefficient in sorted(base.items())
                    if coefficient
                ),
                tuple(
                    (parameter, item, coefficient)
                    for (parameter, item), coefficient in sorted(gamma.items())
                    if coefficient
                ),
            )

    return ((word, Fraction(1)),), ()


def _multiply_deformed(
    left: Polynomial, right: Polynomial
) -> tuple[Polynomial, GammaPolynomial]:
    base: dict[Word, Fraction] = defaultdict(Fraction)
    gamma: dict[tuple[str, Word], Fraction] = defaultdict(Fraction)
    for first, first_coefficient in left.items():
        for second, second_coefficient in right.items():
            normal_base, normal_gamma = _normal_order_deformed_word(first + second)
            factor = first_coefficient * second_coefficient
            for word, coefficient in normal_base:
                base[word] += factor * coefficient
            for parameter, word, coefficient in normal_gamma:
                gamma[(parameter, word)] += factor * coefficient
    return (
        {word: coefficient for word, coefficient in base.items() if coefficient},
        {key: coefficient for key, coefficient in gamma.items() if coefficient},
    )


def _bracket_deformed(
    basis: AlgebraBasis, left: str, right: str
) -> tuple[Polynomial, GammaPolynomial]:
    forward_base, forward_gamma = _multiply_deformed(
        basis.realizations[left], basis.realizations[right]
    )
    reverse_base, reverse_gamma = _multiply_deformed(
        basis.realizations[right], basis.realizations[left]
    )
    reverse_factor = Fraction(
        -1 if basis.parity[left] * basis.parity[right] == 0 else 1
    )
    base: dict[Word, Fraction] = defaultdict(Fraction)
    gamma: dict[tuple[str, Word], Fraction] = defaultdict(Fraction)
    _accumulate(base, forward_base)
    _accumulate(base, reverse_base, reverse_factor)
    _accumulate(gamma, forward_gamma)
    _accumulate(gamma, reverse_gamma, reverse_factor)
    return (
        {word: coefficient for word, coefficient in base.items() if coefficient},
        {key: coefficient for key, coefficient in gamma.items() if coefficient},
    )


def _format_fraction(value: Fraction) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def _parameter_matrix(n: int) -> tuple[list[str], list[str], list[list[str]]]:
    rows = ["a_1_p", "a_1_m"]
    columns = [
        label
        for rank in range(1, n + 1)
        for label in (f"b_{rank}_p", f"b_{rank}_m")
    ]
    entries = [
        [_parameter_for(row, column) for column in columns]
        for row in rows
    ]
    return rows, columns, entries


def _gamma_projection_basis(basis: AlgebraBasis) -> AlgebraBasis:
    parity = dict(basis.parity)
    parity["K"] = 0
    realizations = dict(basis.realizations)
    realizations["K"] = {(): Fraction(1)}
    realization_data = dict(basis.realization_data)
    realization_data["K"] = {
        "standard_form": [{"words": [], "coeff": "1"}],
        "frappat_form": "1",
        "parity": 0,
        "note": "Distinguished scalar identity; not a PBW basis generator",
    }
    return AlgebraBasis(
        n=basis.n,
        even=(*basis.even, "K"),
        odd=basis.odd,
        pbw=(*basis.pbw, "K"),
        parity=parity,
        realizations=realizations,
        realization_data=realization_data,
    )


def _load_structure(path: Path, basis: AlgebraBasis) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        if data["algebra"]["n"] != basis.n:
            raise ValueError(f"{path}: rank does not match its filename")
        if data["basis"]["even"] != list(basis.even):
            raise ValueError(f"{path}: even basis differs from generated basis")
        if data["basis"]["odd"] != list(basis.odd):
            raise ValueError(f"{path}: odd basis differs from generated basis")
        if data["parity"] != dict(basis.parity):
            raise ValueError(f"{path}: parity map differs from generated basis")
        records = data["structure_constants"]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"{path}: missing or invalid Schema 1 fields") from exc
    if not isinstance(records, list):
        raise ValueError(f"{path}: structure_constants must be a list")
    return data


def _structure_bracket(
    structure_data: dict[str, object],
) -> dict[tuple[str, str], dict[str, Fraction]]:
    bracket: dict[tuple[str, str], dict[str, Fraction]] = {}
    for record in structure_data["structure_constants"]:
        key = (record["X"], record["Y"])
        output = record["Z"]
        coefficient = Fraction(record["coeff"])
        outputs = bracket.setdefault(key, {})
        if output in outputs:
            raise ValueError(f"Duplicate Schema 1 bracket term {key + (output,)}")
        outputs[output] = coefficient
    return bracket


def _derive_gamma(
    basis: AlgebraBasis, structure_data: dict[str, object]
) -> tuple[list[dict[str, object]], int]:
    stored_bracket = _structure_bracket(structure_data)
    projection_basis = _gamma_projection_basis(basis)
    records: list[dict[str, object]] = []
    checked_pairs = 0
    parameter_order = [
        parameter for row in _parameter_matrix(basis.n)[2] for parameter in row
    ]

    for left in basis.pbw:
        for right in basis.pbw:
            base_bracket, gamma_polynomial = _bracket_deformed(basis, left, right)
            base_coordinates = (
                _express_in_basis(base_bracket, basis) if base_bracket else {}
            )
            if base_coordinates != stored_bracket.get((left, right), {}):
                raise ValueError(
                    f"Undeformed oscillator bracket disagrees with Schema 1 "
                    f"for [{left},{right}]"
                )
            checked_pairs += 1

            by_parameter: dict[str, Polynomial] = defaultdict(dict)
            for (parameter, word), coefficient in gamma_polynomial.items():
                by_parameter[parameter][word] = coefficient
            coefficients: dict[str, dict[str, Fraction]] = defaultdict(dict)
            for parameter, polynomial in by_parameter.items():
                coordinates = _express_in_basis(polynomial, projection_basis)
                for output, coefficient in coordinates.items():
                    coefficients[output][parameter] = coefficient

            for output in (*basis.pbw, "K"):
                terms = [
                    {
                        "parameter": parameter,
                        "scalar": _format_fraction(
                            coefficients[output][parameter]
                        ),
                    }
                    for parameter in parameter_order
                    if coefficients.get(output, {}).get(parameter)
                ]
                if terms:
                    records.append(
                        {
                            "X": left,
                            "Y": right,
                            "Z": output,
                            "coeff": terms,
                            "sign_rule": "graded",
                        }
                    )
    return records, checked_pairs


def build_gamma_schema(
    basis: AlgebraBasis,
    structure_data: dict[str, object],
    generation_date: str | None = None,
) -> tuple[dict[str, object], int]:
    if generation_date is None:
        generation_date = date.today().isoformat()
    rows, columns, entries = _parameter_matrix(basis.n)
    records, checked_pairs = _derive_gamma(basis, structure_data)
    return (
        {
            "schema_version": structure_data["schema_version"],
            "schema_layer": 2,
            "schema_type": "inhomogeneous_deformation",
            "algebra": structure_data["algebra"],
            "basis": structure_data["basis"],
            "parity": structure_data["parity"],
            "central_elements": structure_data["central_elements"],
            "scalar_output": {
                "label": "K",
                "parity": 0,
                "central": True,
                "value": "1",
                "outside_pbw_basis": True,
                "interpretation": "Scalar terms are retained explicitly; triviality is considered up to scalar.",
            },
            "inhomogeneous_deformation": {
                "description": "First-order gb deformation of C(n+1) oscillator brackets",
                "fermion_boson_commutator": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa",
                "bracket": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)",
                "parameter_parity": 0,
                "deformation_term_parity": 1,
                "parameter_count": 4 * basis.n,
                "gb_matrix": {
                    "shape": [len(rows), len(columns)],
                    "row_labels": rows,
                    "column_labels": columns,
                    "entries": entries,
                },
                "normal_ordering": "kappa is placed on the left; terms of order kappa^2 are discarded",
            },
            "gamma_constants": records,
            "metadata": {
                "generated_by": "C_gamma.py",
                "generation_date": generation_date,
                "source_schema": f"C_{basis.n}_structure.json",
                "references": [
                    "C(n+1) = osp(2|2n) mathematical definition",
                    "C(n+1) inhomogeneous deformation definition",
                    "Coboundary operator definition (triviality up to scalar)",
                ],
            },
        },
        checked_pairs,
    )


def _parse_gamma_records(
    gamma_data: dict[str, object], basis: AlgebraBasis, parameters: set[str]
) -> dict[tuple[str, str, str, str], Fraction]:
    records = gamma_data.get("gamma_constants")
    if not isinstance(records, list):
        raise ValueError("gamma_constants must be a list")
    allowed_outputs = set(basis.parity) | {"K"}
    gamma_map: dict[tuple[str, str, str, str], Fraction] = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"gamma_constants[{index}] must be an object")
        try:
            left, right, output = record["X"], record["Y"], record["Z"]
            terms, sign_rule = record["coeff"], record["sign_rule"]
        except (KeyError, TypeError) as exc:
            raise ValueError(f"Invalid gamma_constants[{index}]") from exc
        if left not in basis.parity or right not in basis.parity or output not in allowed_outputs:
            raise ValueError(f"Unknown generator or scalar output in gamma_constants[{index}]")
        if output == "K" and gamma_data["scalar_output"] != {
            "label": "K",
            "parity": 0,
            "central": True,
            "value": "1",
            "outside_pbw_basis": True,
            "interpretation": "Scalar terms are retained explicitly; triviality is considered up to scalar.",
        }:
            raise ValueError("K output metadata does not match the approved scalar convention")
        if output != "K" and basis.parity[output] != (
            basis.parity[left] + basis.parity[right] + 1
        ) % 2:
            raise ValueError(
                f"Gamma output parity is inconsistent in gamma_constants[{index}]"
            )
        if sign_rule != "graded" or not isinstance(terms, list) or not terms:
            raise ValueError(
                f"Invalid coefficient or sign_rule in gamma_constants[{index}]"
            )
        for term in terms:
            try:
                parameter, scalar_text = term["parameter"], term["scalar"]
                scalar = Fraction(scalar_text)
            except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
                raise ValueError(
                    f"Invalid coefficient term in gamma_constants[{index}]"
                ) from exc
            if parameter not in parameters or not scalar:
                raise ValueError(
                    f"Unknown parameter or zero coefficient in gamma_constants[{index}]"
                )
            key = (left, right, output, parameter)
            if key in gamma_map:
                raise ValueError(f"Duplicate gamma coefficient {key}")
            gamma_map[key] = scalar
    return gamma_map


def verify_gamma_schema(
    basis: AlgebraBasis,
    structure_data: dict[str, object],
    gamma_data: dict[str, object],
) -> tuple[int, int]:
    expected_records, checked_pairs = _derive_gamma(basis, structure_data)
    if gamma_data.get("schema_layer") != 2:
        raise ValueError("Schema 2 must declare schema_layer = 2")
    for key in ("algebra", "basis", "parity", "central_elements"):
        if gamma_data.get(key) != structure_data[key]:
            raise ValueError(f"Schema 2 field {key!r} does not match Schema 1")

    rows, columns, entries = _parameter_matrix(basis.n)
    parameter_names = {parameter for row in entries for parameter in row}
    deformation = gamma_data.get("inhomogeneous_deformation")
    if not isinstance(deformation, dict):
        raise ValueError("Missing inhomogeneous_deformation object")
    if deformation.get("gb_matrix") != {
        "shape": [2, 2 * basis.n],
        "row_labels": rows,
        "column_labels": columns,
        "entries": entries,
    }:
        raise ValueError("gb_matrix labels, ordering, or dimensions are incorrect")
    if deformation.get("parameter_count") != 4 * basis.n:
        raise ValueError("gb parameter count is incorrect")
    if deformation.get("parameter_parity") != 0:
        raise ValueError("Each gb parameter must be an ordinary scalar")
    if deformation.get("deformation_term_parity") != 1:
        raise ValueError("The gb*kappa deformation term must be odd")
    if deformation.get("fermion_boson_commutator") != (
        "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa"
    ):
        raise ValueError("The approved Option A mixed relation is not recorded")
    scalar_output = gamma_data.get("scalar_output")
    if not isinstance(scalar_output, dict) or scalar_output.get("label") != "K":
        raise ValueError("The distinguished K scalar output is missing")
    if (
        scalar_output.get("parity") != 0
        or scalar_output.get("central") is not True
        or scalar_output.get("value") != "1"
        or scalar_output.get("outside_pbw_basis") is not True
    ):
        raise ValueError("K scalar metadata is inconsistent with Schema 1")

    gamma_map = _parse_gamma_records(gamma_data, basis, parameter_names)
    expected_map = {
        (record["X"], record["Y"], record["Z"], term["parameter"]): Fraction(
            term["scalar"]
        )
        for record in expected_records
        for term in record["coeff"]
    }
    if gamma_map != expected_map:
        raise ValueError(
            "Serialized gamma coefficients disagree with oscillator recomputation"
        )

    for (left, right, output, parameter), coefficient in gamma_map.items():
        reverse_key = (right, left, output, parameter)
        sign = -1 if basis.parity[left] * basis.parity[right] == 0 else 1
        if gamma_map.get(reverse_key) != sign * coefficient:
            raise ValueError(
                f"Missing or incorrect reverse gamma orientation for "
                f"{left},{right},{output}"
            )

    if basis.n == 1:
        required_terms = {
            ("E_eps1_del1_pp", "H_1", "H_1", "gb_a1_p_b1_p"): Fraction(1),
            ("E_eps1_del1_pp", "H_1", "K", "gb_a1_p_b1_p"): Fraction(1),
            ("E_eps1_del1_pp", "H_1", "E_2del1_p", "gb_a1_p_b1_m"): Fraction(1),
        }
        if any(gamma_map.get(key) != value for key, value in required_terms.items()):
            raise ValueError("Rank-1 gamma scalar regression check failed")
    return checked_pairs, len(gamma_map)


def generate_files(
    ranks: Iterable[int], data_dir: Path, generation_date: str | None = None
) -> list[tuple[Path, int, int]]:
    generated: list[tuple[Path, int, int]] = []
    for n in ranks:
        basis = build_basis(n)
        structure_path = data_dir / f"C_{n}_structure.json"
        if not structure_path.is_file():
            raise FileNotFoundError(f"Schema 1 file does not exist: {structure_path}")
        structure_data = _load_structure(structure_path, basis)
        schema, checked_pairs = build_gamma_schema(
            basis, structure_data, generation_date=generation_date
        )
        destination = data_dir / f"C_{n}_gamma.json"
        destination.write_text(
            json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        persisted = json.loads(destination.read_text(encoding="utf-8"))
        verified_pairs, term_count = verify_gamma_schema(
            basis, structure_data, persisted
        )
        if verified_pairs != checked_pairs:
            raise RuntimeError("Internal verification pair count mismatch")
        generated.append((destination, verified_pairs, term_count))
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
        help="Directory containing Schema 1 files and receiving Schema 2 files",
    )
    arguments = parser.parse_args()
    for path, pair_count, term_count in generate_files(
        arguments.ranks, arguments.data_dir
    ):
        print(
            f"{path}: verified {pair_count} ordered pairs and "
            f"{term_count} gamma coefficient terms"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
