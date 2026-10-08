#!/usr/bin/env python3
"""Evaluate C(n+1) gamma data at a formal uniform sign assignment."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path


def evaluate_schema1_gamma(structure, gamma_schema, sign=1):
    if sign not in (-1, 0, 1):
        raise ValueError("sign must be -1, 0, or 1")
    n = structure["algebra"]["n"]
    if gamma_schema["algebra"]["n"] != n:
        raise ValueError("Schema 1 and Schema 2 ranks differ")
    deformation = gamma_schema["inhomogeneous_deformation"]
    parameters = {
        item["label"]
        for item in deformation["gb_matrix"]["parameters"]
    }
    expected_parameters = 4 * n
    if len(parameters) != expected_parameters:
        raise ValueError(
            f"Expected {expected_parameters} gb parameters, found {len(parameters)}"
        )
    if gamma_schema["source_schema1"] != f"C_{n}_structure.json":
        raise ValueError("Schema 2 points to the wrong Schema 1 rank")

    basis = set(structure["parity"])
    basis.add("K")
    pbw = list(structure["generator_realization"]["realizations"])
    order = {label: index for index, label in enumerate(pbw)}
    order["K"] = len(order)
    evaluated = {}
    for entry in structure["structure_constants"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        evaluated.setdefault(key, {"base": Fraction(0), "kappa": Fraction(0)})
        evaluated[key]["base"] += Fraction(entry["coeff"])

    seen_parameters = set()
    for entry in deformation["gamma_coefficients"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        if x not in structure["parity"] or y not in structure["parity"]:
            raise ValueError(f"Gamma entry references an unknown input: {entry}")
        if z not in basis:
            raise ValueError(f"Gamma entry references an unknown output: {entry}")
        value = Fraction(0)
        for term in entry["coefficients"]:
            parameter = term["parameter"]
            if parameter not in parameters:
                raise ValueError(f"Unknown gb parameter {parameter}")
            seen_parameters.add(parameter)
            value += Fraction(term["coeff"]) * sign
        if value:
            key = (x, y, z)
            evaluated.setdefault(key, {"base": Fraction(0), "kappa": Fraction(0)})
            evaluated[key]["kappa"] += value
    if seen_parameters != parameters:
        missing = sorted(parameters - seen_parameters)
        raise ValueError(f"Gamma data does not use all gb parameters: {missing}")

    ordered_keys = sorted(
        evaluated,
        key=lambda key: (
            order[key[0]],
            order[key[1]],
            order[key[2]],
        ),
    )
    constants = []
    for x, y, z in ordered_keys:
        base = evaluated[(x, y, z)]["base"]
        kappa = evaluated[(x, y, z)]["kappa"]
        if not base and not kappa:
            continue
        constants.append({
            "X": x,
            "Y": y,
            "Z": z,
            "base_coeff": _fraction_string(base),
            "kappa_coeff": _fraction_string(kappa),
        })

    assignment = {
        parameter: str(sign)
        for parameter in sorted(parameters)
    }
    return {
        "schema_version": "5.0",
        "algebra": structure["algebra"],
        "source_schema1": f"C_{n}_structure.json",
        "source_schema2": f"C_{n}_gamma.json",
        "evaluation": {
            "label": {
                1: "all_gb_plus_one",
                0: "all_gb_zero",
                -1: "all_gb_minus_one",
            }[sign],
            "assignment": assignment,
            "parameter_domain": (
                "homogeneous zero specialization"
                if sign == 0
                else "formal specialization"
            ),
            "note": (
                "Zero is a parity-homogeneous value for the odd parameters."
                if sign == 0
                else "The assigned nonzero real sign is formal; it is not a "
                "parity-homogeneous value for a parity-odd parameter."
            ),
        },
        "central_elements": structure["central_elements"],
        "evaluated_structure_constants": constants,
        "metadata": {
            "generated_by": "src/evaluate_C.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "Schema 1 and Schema 2 files named above",
                "docs/json_schema_specification.md",
            ],
        },
    }


def _fraction_string(value):
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def generate_files(data_dir="data", ranks=(1, 2, 3), sign=1):
    root = Path(data_dir)
    paths = []
    for n in ranks:
        structure_path = root / f"C_{n}_structure.json"
        gamma_path = root / f"C_{n}_gamma.json"
        with structure_path.open(encoding="utf-8") as stream:
            structure = json.load(stream)
        with gamma_path.open(encoding="utf-8") as stream:
            gamma_schema = json.load(stream)
        evaluated = evaluate_schema1_gamma(structure, gamma_schema, sign=sign)
        path = root / f"C_{n}_evaluated.json"
        path.write_text(
            json.dumps(evaluated, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        paths.append(path)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--ranks", nargs="+", type=int, default=[1, 2, 3])
    parser.add_argument("--sign", type=int, choices=(-1, 0, 1), default=1)
    args = parser.parse_args()
    for path in generate_files(args.data_dir, args.ranks, sign=args.sign):
        print(path)


if __name__ == "__main__":
    main()
