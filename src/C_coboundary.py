"""Generate generic coboundary coefficients for an odd map on C(n+1)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from pathlib import Path


def _parameter(source: str, target: str) -> str:
    return f"phi_{source}__to__{target}"


def build_coboundary(schema1_path: Path) -> dict:
    schema1 = json.loads(schema1_path.read_text())
    algebra = schema1["algebra"]
    basis = schema1["basis"]["even"] + schema1["basis"]["odd"]
    parity = schema1["parity"]
    brackets: dict[tuple[str, str], dict[str, Fraction]] = defaultdict(dict)
    for term in schema1["structure_constants"]:
        key = (term["X"], term["Y"])
        brackets[key][term["Z"]] = (
            brackets[key].get(term["Z"], Fraction(0)) + Fraction(term["coeff"])
        )

    f_terms = []
    outputs: dict[str, list[tuple[str, str]]] = {}
    for source in basis:
        outputs[source] = []
        for target in basis:
            if parity[source] == parity[target]:
                continue
            parameter = _parameter(source, target)
            outputs[source].append((target, parameter))
            f_terms.append({
                "input": source,
                "output": target,
                "parameter": parameter,
                "coefficient_parity": 0,
            })

    coefficients: dict[tuple[str, str, str, str], Fraction] = defaultdict(Fraction)
    for x in basis:
        px = parity[x]
        for y in basis:
            py = parity[y]
            first_sign = -1 if px else 1
            second_exponent = ((px + 1) * py) % 2
            second_sign = -1 if second_exponent == 0 else 1

            for target, parameter in outputs[y]:
                for z, coeff in brackets[(x, target)].items():
                    coefficients[(x, y, z, parameter)] += first_sign * coeff

            for target, parameter in outputs[x]:
                for z, coeff in brackets[(y, target)].items():
                    coefficients[(x, y, z, parameter)] += second_sign * coeff

            for intermediate, bracket_coeff in brackets[(x, y)].items():
                for target, parameter in outputs[intermediate]:
                    coefficients[(x, y, target, parameter)] -= bracket_coeff

    coboundary_terms = [
        {
            "X": x,
            "Y": y,
            "Z": z,
            "parameter": parameter,
            "coeff": str(coeff),
            "sign_rule": "graded",
        }
        for (x, y, z, parameter), coeff in sorted(coefficients.items())
        if coeff
    ]
    return {
        "schema_version": "5.0",
        "algebra": algebra,
        "basis_reference": schema1_path.name,
        "odd_linear_map": {
            "parity": 1,
            "coefficient_parity": 0,
            "formula": "f(X) = sum_target phi_{X,target} * target, p(target)=p(X)+1 mod 2",
            "parameters": f_terms,
        },
        "coboundary": {
            "formula": (
                "(delta f)(X,Y) = (-1)^p(X)[X,f(Y)] "
                "- (-1)^((p(X)+1)p(Y))[Y,f(X)] - f([X,Y])"
            ),
            "coefficients": coboundary_terms,
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "docs/math/C_coboundary_definition.md",
                schema1_path.name,
            ],
        },
    }


def generate_all(data_dir: Path, ranks=(1, 2, 3)) -> list[Path]:
    paths = []
    for n in ranks:
        path = data_dir / f"C_{n}_coboundary.json"
        path.write_text(json.dumps(
            build_coboundary(data_dir / f"C_{n}_structure.json"),
            indent=2,
            ensure_ascii=False,
        ) + "\n")
        paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    args = parser.parse_args()
    for path in generate_all(args.data_dir, args.ranks):
        print(path)


if __name__ == "__main__":
    main()
