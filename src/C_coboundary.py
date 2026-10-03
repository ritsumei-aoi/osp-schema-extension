"""Generate symbolic odd-map coboundaries for C(n+1)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from pathlib import Path


def _fraction_string(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _parameter_name(target: str, source: str) -> str:
    return f"phi__{target}__from__{source}"


def _build_f_map(even: list[str], odd: list[str]) -> tuple[dict, dict]:
    terms: dict[str, list[tuple[str, str]]] = {}
    even_to_odd = {
        "input_parity": 0,
        "output_parity": 1,
        "row_labels": odd,
        "column_labels": even,
        "coefficients": [],
    }
    for target in odd:
        row = []
        for source in even:
            parameter = _parameter_name(target, source)
            row.append(parameter)
            terms.setdefault(source, []).append((target, parameter))
        even_to_odd["coefficients"].append(row)

    odd_to_even = {
        "input_parity": 1,
        "output_parity": 0,
        "row_labels": even,
        "column_labels": odd,
        "coefficients": [],
    }
    for target in even:
        row = []
        for source in odd:
            parameter = _parameter_name(target, source)
            row.append(parameter)
            terms.setdefault(source, []).append((target, parameter))
        odd_to_even["coefficients"].append(row)

    return terms, {
        "even_to_odd": even_to_odd,
        "odd_to_even": odd_to_even,
    }


def _load_brackets(schema1: dict) -> dict[tuple[str, str], dict[str, Fraction]]:
    brackets: dict[tuple[str, str], dict[str, Fraction]] = defaultdict(dict)
    for row in schema1["structure_constants"]:
        key = row["X"], row["Y"]
        result = row["Z"]
        brackets[key][result] = (
            brackets[key].get(result, Fraction(0)) + Fraction(row["coeff"])
        )
    return dict(brackets)


def _accumulate(
    output: dict[tuple[str, str, str], dict[str, Fraction]],
    key: tuple[str, str, str],
    parameter: str,
    coeff: Fraction,
) -> None:
    if not coeff:
        return
    terms = output.setdefault(key, {})
    terms[parameter] = terms.get(parameter, Fraction(0)) + coeff
    if not terms[parameter]:
        del terms[parameter]
    if not terms:
        del output[key]


def _compute_coboundary(
    generators: list[str],
    parity: dict[str, int],
    f_terms: dict[str, list[tuple[str, str]]],
    brackets: dict[tuple[str, str], dict[str, Fraction]],
) -> dict[tuple[str, str, str], dict[str, Fraction]]:
    delta: dict[tuple[str, str, str], dict[str, Fraction]] = {}
    for left in generators:
        for right in generators:
            p_left, p_right = parity[left], parity[right]

            first_sign = Fraction(-1 if p_left else 1)
            for image, parameter in f_terms[right]:
                for result, coeff in brackets.get((left, image), {}).items():
                    _accumulate(
                        delta,
                        (left, right, result),
                        parameter,
                        first_sign * coeff,
                    )

            second_exponent = (p_left + 1) * p_right
            second_sign = Fraction(-1 if second_exponent % 2 == 0 else 1)
            for image, parameter in f_terms[left]:
                for result, coeff in brackets.get((right, image), {}).items():
                    _accumulate(
                        delta,
                        (left, right, result),
                        parameter,
                        second_sign * coeff,
                    )

            for intermediate, bracket_coeff in brackets.get(
                (left, right), {}
            ).items():
                for result, parameter in f_terms[intermediate]:
                    _accumulate(
                        delta,
                        (left, right, result),
                        parameter,
                        -bracket_coeff,
                    )
    return delta


def _verify_coboundary(
    delta: dict[tuple[str, str, str], dict[str, Fraction]],
    generators: list[str],
    parity: dict[str, int],
) -> None:
    for (left, right, result), terms in delta.items():
        if parity[result] != (parity[left] + parity[right] + 1) % 2:
            raise ValueError(
                f"Coboundary parity mismatch at ({left}, {right}) -> {result}."
            )
        factor = -1 if parity[left] * parity[right] == 0 else 1
        reverse = delta.get((right, left, result), {})
        for parameter, coeff in terms.items():
            if coeff != factor * reverse.get(parameter, Fraction(0)):
                raise ValueError(
                    "Coboundary graded skew-symmetry mismatch at "
                    f"({left}, {right}, {result}, {parameter})."
                )
    if any(result not in generators for _, _, result in delta):
        raise ValueError("Coboundary result is outside the Layer 1 basis.")


def build_coboundary_schema(n: int, data_dir: Path = Path("data")) -> dict:
    schema1_path = data_dir / f"C_{n}_structure.json"
    schema1 = _read_json(schema1_path)
    algebra = schema1["algebra"]
    if (algebra["family"], algebra["m"], algebra["n"]) != ("C", 1, n):
        raise ValueError(f"{schema1_path}: unexpected algebra family or rank.")

    even = schema1["basis"]["even"]
    odd = schema1["basis"]["odd"]
    generators = odd + even
    parity = schema1["parity"]
    f_terms, f_blocks = _build_f_map(even, odd)
    brackets = _load_brackets(schema1)
    delta = _compute_coboundary(generators, parity, f_terms, brackets)
    _verify_coboundary(delta, generators, parity)

    generator_order = {label: index for index, label in enumerate(generators)}
    parameter_order = {}
    for block in f_blocks.values():
        for row in block["coefficients"]:
            for parameter in row:
                parameter_order[parameter] = len(parameter_order)
    coefficients = [
        {
            "X": left,
            "Y": right,
            "Z": result,
            "terms": [
                {
                    "parameter": parameter,
                    "coeff": _fraction_string(coeff),
                }
                for parameter, coeff in sorted(
                    terms.items(),
                    key=lambda item: parameter_order[item[0]],
                )
            ],
        }
        for (left, right, result), terms in sorted(
            delta.items(),
            key=lambda item: (
                generator_order[item[0][0]],
                generator_order[item[0][1]],
                generator_order[item[0][2]],
            ),
        )
    ]

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "osp": f"osp(2|{2 * n})",
        },
        "source_schema": schema1_path.name,
        "linear_map_f": {
            "parity": 1,
            "normalization": "unit",
            "definition": (
                "f(Z_j) = sum_i phi_ij Z_i, with p(Z_i) = p(Z_j) + 1 mod 2"
            ),
            **f_blocks,
        },
        "coboundary_operator": {
            "formula": (
                "(delta f)(X,Y) = (-1)^p(X)[X,f(Y)] "
                "- (-1)^((p(X)+1)p(Y))[Y,f(X)] - f([X,Y])"
            ),
            "bracket_source": schema1_path.name,
            "coefficient_scaling": "No additional factor; unit normalization.",
        },
        "coboundary_coefficients": coefficients,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "docs/math/C_coboundary_definition.md",
                schema1_path.name,
            ],
        },
    }


def generate_files(data_dir: Path = Path("data")) -> list[Path]:
    schemas = [
        (n, build_coboundary_schema(n, data_dir)) for n in (1, 2, 3)
    ]
    written = []
    for n, schema in schemas:
        destination = data_dir / f"C_{n}_coboundary.json"
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
        help="Directory containing Schema 1 and receiving Schema 4 files",
    )
    args = parser.parse_args()
    for path in generate_files(args.data_dir):
        print(path)


if __name__ == "__main__":
    main()
