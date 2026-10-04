"""
C_coboundary.py: Computation of the coboundary operator (delta f) for C(n+1) = osp(2|2n)
across n=1, 2, 3. Generates Schema 4 JSON datasets (C_{n}_coboundary.json).
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
import sys
from typing import Dict, List, Tuple, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.C_generators import build_basis


def load_structure_constants(n: int) -> Tuple[List[str], Dict[str, int], Dict[Tuple[str, str, str], Fraction]]:
    """Loads basis, parity, and structure constants from Schema 1."""
    filepath = os.path.join("data", f"C_{n}_structure.json")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Schema 1 file {filepath} not found.")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    basis_list = data["basis"]["odd"] + data["basis"]["even"]
    parities = data["parity"]

    bracket_dict: Dict[Tuple[str, str, str], Fraction] = defaultdict(Fraction)
    for entry in data["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        c = Fraction(entry["coeff"])
        bracket_dict[(x, y, z)] = c
        if x != y:
            p_x = parities[x]
            p_y = parities[y]
            sign = -1 if (p_x * p_y % 2 == 1) else 1
            bracket_dict[(y, x, z)] = -sign * c

    return basis_list, parities, bracket_dict


def define_canonical_odd_map(basis_info: Dict[str, Any]) -> Dict[str, Dict[str, Fraction]]:
    """
    Defines a canonical odd linear map f: g -> g reversing parity.
    Pairs the even basis with the odd basis up to min(dim(even), dim(odd)).
    """
    even_gens = basis_info["even"]
    odd_gens = basis_info["odd"]
    m = min(len(even_gens), len(odd_gens))

    f_map: Dict[str, Dict[str, Fraction]] = defaultdict(dict)
    for k in range(m):
        f_map[even_gens[k]][odd_gens[k]] = Fraction(1)
        f_map[odd_gens[k]][even_gens[k]] = Fraction(1)

    return f_map


def compute_coboundary(basis_list: List[str],
                       parities: Dict[str, int],
                       brackets: Dict[Tuple[str, str, str], Fraction],
                       f_map: Dict[str, Dict[str, Fraction]]) -> List[Dict[str, Any]]:
    """
    Computes (delta f)(X, Y) for X <= Y in PBW order:
    (delta f)(X, Y) = (-1)^p(X) [X, f(Y)] - (-1)^((p(X)+1)p(Y)) [Y, f(X)] - f([X, Y]).
    """
    delta_f: Dict[Tuple[str, str, str], Fraction] = defaultdict(Fraction)

    for i, x in enumerate(basis_list):
        p_x = parities[x]
        s1 = -1 if (p_x % 2 == 1) else 1
        for j in range(i, len(basis_list)):
            y = basis_list[j]
            p_y = parities[y]
            s2 = -1 if ((p_x + 1) * p_y % 2 == 1) else 1

            # Term 1: (-1)^p(X) [X, f(Y)]
            for f_y, c_fy in f_map.get(y, {}).items():
                for z in basis_list:
                    c = brackets.get((x, f_y, z), Fraction(0))
                    if c != 0:
                        delta_f[(x, y, z)] += s1 * c_fy * c

            # Term 2: - (-1)^((p(X)+1)p(Y)) [Y, f(X)]
            for f_x, c_fx in f_map.get(x, {}).items():
                for z in basis_list:
                    c = brackets.get((y, f_x, z), Fraction(0))
                    if c != 0:
                        delta_f[(x, y, z)] -= s2 * c_fx * c

            # Term 3: - f([X, Y])
            for m_gen in basis_list:
                c_xy = brackets.get((x, y, m_gen), Fraction(0))
                if c_xy != 0:
                    for f_m, c_fm in f_map.get(m_gen, {}).items():
                        delta_f[(x, y, f_m)] -= c_xy * c_fm

    # Filter non-zero terms
    pbw_index = {name: idx for idx, name in enumerate(basis_list)}
    sorted_keys = sorted(
        [k for k, v in delta_f.items() if v != 0],
        key=lambda k: (pbw_index[k[0]], pbw_index[k[1]], pbw_index[k[2]])
    )

    terms = []
    for x, y, z in sorted_keys:
        coeff = delta_f[(x, y, z)]
        coeff_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
        terms.append({
            "X": x,
            "Y": y,
            "Z": z,
            "coeff": coeff_str,
            "sign_rule": "graded"
        })

    return terms


def generate_schema4(n: int) -> Dict[str, Any]:
    """Generates the complete Schema 4 (Coboundary Structure) JSON dictionary."""
    basis_list, parities, brackets = load_structure_constants(n)
    basis_info = build_basis(n)
    f_map = define_canonical_odd_map(basis_info)
    coboundary_terms = compute_coboundary(basis_list, parities, brackets, f_map)

    # Format f_map for serialization
    serialized_f = {}
    for src, targets in f_map.items():
        serialized_f[src] = {tgt: str(val) for tgt, val in targets.items()}

    total_dim = len(basis_list)

    data = {
        "schema_version": "5.0",
        "layer": "4_coboundary",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n) with m=1"
            },
            "dimension": {
                "total": 2 * n**2 + 5 * n + 1,
                "even": 2 * n**2 + n + 1,
                "odd": 4 * n,
                "formulas": {
                    "even": "2n^2 + n + 1",
                    "odd": "4n",
                    "total": "2n^2 + 5n + 1"
                }
            }
        },
        "basis": basis_info,
        "parity": parities,
        "odd_linear_map_f": {
            "description": "Canonical odd linear map f: g -> g reversing parity (p(f(X)) = 1 - p(X))",
            "matrix_dimension": [total_dim, total_dim],
            "mapping": serialized_f
        },
        "coboundary_structure": {
            "description": "Coboundary (delta f)(X, Y) = (-1)^pX [X, f(Y)] - (-1)^((pX+1)pY) [Y, f(X)] - f([X, Y])",
            "ordering_convention": "PBW: κ < [odd] < [even]",
            "num_canonical_terms": len(coboundary_terms),
            "terms": coboundary_terms
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": "2026-10-05",
            "references": [
                "docs/math/C_coboundary_definition.md",
                "handover/notation.md"
            ]
        }
    }
    return data


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema4 = generate_schema4(n)
        filename = os.path.join("data", f"C_{n}_coboundary.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(schema4, f, indent=2)
        print(f"Generated {filename}: {len(schema4['coboundary_structure']['terms'])} canonical coboundary terms")


if __name__ == "__main__":
    main()
