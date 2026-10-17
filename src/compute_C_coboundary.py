"""
C(n+1) = osp(2|2n) Coboundary Structure (Schema 4) Generator
Computes the coboundary operator delta f of an odd linear map f and generates Schema 4 JSON for n=1, 2, 3.
"""

import json
import os
import sys
import argparse
from fractions import Fraction
from collections import defaultdict
from typing import Dict, Any, Tuple, List

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")

def compute_coboundary_structure(n: int, scaling: Fraction = Fraction(1, 1)) -> Dict[str, Any]:
    structure_file = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    if not os.path.exists(structure_file):
        raise FileNotFoundError(f"Missing Schema 1 file: {structure_file}")

    with open(structure_file, "r", encoding="utf-8") as f:
        s1 = json.load(f)

    basis_even = s1["basis"]["even"]
    basis_odd = s1["basis"]["odd"]
    all_basis = basis_even + basis_odd
    basis_idx = {g: idx for idx, g in enumerate(all_basis)}
    parity = s1["parity"]
    dim_g = len(all_basis)

    # Base structure constants c_{XY}^Z
    c_base = defaultdict(Fraction)
    for entry in s1["structure_constants"]:
        c_base[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])

    def bracket(X_vec: Dict[str, Fraction], Y_vec: Dict[str, Fraction]) -> Dict[str, Fraction]:
        res = defaultdict(Fraction)
        for X, cx in X_vec.items():
            if cx == 0: continue
            for Y, cy in Y_vec.items():
                if cy == 0: continue
                c_xy = cx * cy
                for Z in all_basis:
                    c = c_base.get((X, Y, Z), Fraction(0, 1))
                    if c != 0:
                        res[Z] += c_xy * c
        return {k: v for k, v in res.items() if v != 0}

    # Theta is the uniform sum of all 4n odd generators with given scaling
    Theta_vec = {O: scaling for O in basis_odd}

    # Map f: f(X) = [X, Theta]
    # f is an odd linear map: f(g_0) in g_1, f(g_1) in g_0
    f_components = defaultdict(Fraction)
    for X in all_basis:
        pX = parity[X]
        b = bracket({X: Fraction(1, 1)}, Theta_vec)
        for Z, coeff in b.items():
            if coeff != 0:
                f_components[(X, Z)] = coeff

    # Sort non-zero components deterministically
    sorted_f_components = []
    for (src, tgt), coeff in sorted(f_components.items(), key=lambda item: (basis_idx[item[0][0]], basis_idx[item[0][1]])):
        c_str = str(coeff) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
        sorted_f_components.append({
            "source": src,
            "target": tgt,
            "coeff": c_str
        })

    # (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    delta_f = defaultdict(Fraction)

    for X in all_basis:
        pX = parity[X]
        s1_sign = -Fraction(1, 1) if pX == 1 else Fraction(1, 1)

        # f(X) as a vector
        f_X_vec = {tgt: coeff for (src, tgt), coeff in f_components.items() if src == X}

        for Y in all_basis:
            pY = parity[Y]
            s2_sign = - (-Fraction(1, 1) if ((pX + 1) * pY) % 2 == 1 else Fraction(1, 1))

            # f(Y) as a vector
            f_Y_vec = {tgt: coeff for (src, tgt), coeff in f_components.items() if src == Y}

            # Term 1: (-1)^pX [X, f(Y)]
            term1 = bracket({X: Fraction(1, 1)}, f_Y_vec)
            for Z, coeff in term1.items():
                delta_f[(X, Y, Z)] += s1_sign * coeff

            # Term 2: - (-1)^{(pX+1)pY} [Y, f(X)]
            term2 = bracket({Y: Fraction(1, 1)}, f_X_vec)
            for Z, coeff in term2.items():
                delta_f[(X, Y, Z)] += s2_sign * coeff

            # Term 3: - f([X, Y])
            # [X, Y] in standard basis
            for k in all_basis:
                c_XY_k = c_base.get((X, Y, k), Fraction(0, 1))
                if c_XY_k != 0:
                    for (src, tgt), f_coeff in f_components.items():
                        if src == k:
                            delta_f[(X, Y, tgt)] -= c_XY_k * f_coeff

    # Format coboundary structure
    coboundary_entries = []
    for (X, Y, Z), coeff in delta_f.items():
        if coeff != 0:
            c_str = str(coeff) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
            coboundary_entries.append({
                "X": X,
                "Y": Y,
                "Z": Z,
                "coeff": c_str,
                "sign_rule": "graded"
            })

    # Sort deterministically
    coboundary_entries.sort(key=lambda e: (basis_idx[e["X"]], basis_idx[e["Y"]], basis_idx[e["Z"]]))

    scaling_str = str(scaling) if scaling.denominator == 1 else f"{scaling.numerator}/{scaling.denominator}"

    return {
        "schema_version": "5.0",
        "algebra": s1["algebra"],
        "central_elements": s1["central_elements"],
        "basis": s1["basis"],
        "parity": s1["parity"],
        "map_f": {
            "type": "odd_linear_map",
            "configuration": "inner_odd_generator_sum",
            "generator_Theta": "sum_{sigma, j, s} E_eps1_del{j}_{sigma}{s}",
            "scaling": scaling_str,
            "definition": "f(X) = [X, Theta]",
            "description": "Odd linear map induced by right supercommutation with the uniform sum of all 4n odd root generators",
            "matrix_shape": [dim_g, dim_g],
            "non_zero_components": sorted_f_components
        },
        "coboundary_operator": {
            "formula": "(\\delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])",
            "sign_rule": "graded"
        },
        "coboundary_structure": coboundary_entries,
        "metadata": {
            "generated_by": "src/compute_C_coboundary.py",
            "generation_date": "2026-10-17",
            "source_structure_file": f"data/C_{n}_structure.json",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)",
                "docs/math/C_coboundary_definition.md"
            ]
        }
    }

def main():
    parser = argparse.ArgumentParser(description="Generate Schema 4 Coboundary Structure JSON for C(n+1)")
    parser.add_argument("--scaling", default="1", help="Scaling factor alpha for generator Theta (default: 1)")
    parser.add_argument("--ranks", nargs="+", type=int, default=[1, 2, 3],
                        help="Bosonic ranks n to compute (default: 1 2 3)")
    args = parser.parse_args()

    scaling = Fraction(args.scaling)
    os.makedirs(DATA_DIR, exist_ok=True)

    for n in args.ranks:
        data = compute_coboundary_structure(n, scaling=scaling)

        primary_file = os.path.join(DATA_DIR, f"C_{n}_coboundary.json")
        with open(primary_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        alias_file = os.path.join(DATA_DIR, f"C_{n}_coboundary_all_plus.json")
        with open(alias_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"Generated {primary_file} & {alias_file}:")
        print(f"  - Non-zero map f components: {len(data['map_f']['non_zero_components'])}")
        print(f"  - Non-zero coboundary brackets: {len(data['coboundary_structure'])}")

if __name__ == "__main__":
    main()
