"""
C_gamma.py: Computation of the inhomogeneous deformation (Schema 2, gamma structure)
for C(n+1) = osp(2|2n) across n=1, 2, 3.
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
import sys
from typing import Dict, List, Tuple, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sympy as sp
from src.C_generators import (
    build_basis,
    build_oscillator_realizations,
    op_key
)


def get_gb_matrix_info(n: int) -> Dict[str, Any]:
    """Generates the gb_matrix specification for C(n+1) (size 2 x 2n)."""
    rows = ["a_1_p", "a_1_m"]
    columns = []
    for k in range(1, n + 1):
        columns.extend([f"b_{k}_p", f"b_{k}_m"])

    parameters = []
    matrix = []
    for f in rows:
        row_params = []
        for b in columns:
            param_name = f"gb_{f}_{b}"
            parameters.append(param_name)
            row_params.append(param_name)
        matrix.append(row_params)

    return {
        "rows": rows,
        "columns": columns,
        "shape": [2, 2 * n],
        "total_parameters": 4 * n,
        "parameters": parameters,
        "matrix": matrix
    }


def reduce_deformed_word(word: List[str], coeff: Fraction = Fraction(1)) -> Tuple[Dict[Tuple[str, ...], Fraction], Dict[Tuple[str, Tuple[str, ...]], Fraction]]:
    """
    Evaluates deformed word reduction under:
    [b_j^s, a_1^sigma] = - gb_{a_1^sigma, b_j^s} * kappa.
    Returns:
    - order0: dict of word -> Fraction
    - order1: dict of (param, word) -> Fraction
    """
    items = [(list(word), coeff, None)]
    final_order0 = defaultdict(Fraction)
    final_order1 = defaultdict(Fraction)

    while items:
        w, c, param = items.pop()
        if c == 0:
            continue
        nilpotent = False
        for i in range(len(w) - 1):
            if w[i] == w[i + 1] and w[i].startswith("a_1"):
                nilpotent = True
                break
        if nilpotent:
            continue

        inv_idx = -1
        for i in range(len(w) - 1):
            if op_key(w[i]) > op_key(w[i + 1]):
                inv_idx = i
                break

        if inv_idx == -1:
            if param is None:
                final_order0[tuple(w)] += c
            else:
                final_order1[(param, tuple(w))] += c
        else:
            u, v = w[inv_idx], w[inv_idx + 1]
            pre = w[:inv_idx]
            post = w[inv_idx + 2 :]

            if u.startswith("a_1") and v.startswith("a_1"):
                items.append((pre + [v, u] + post, -c, param))
                items.append((pre + post, c, param))
            elif u.startswith("b_") and v.startswith("b_"):
                parts_u = u.split("_")
                parts_v = v.split("_")
                if parts_u[1] == parts_v[1] and parts_u[2] == "m" and parts_v[2] == "p":
                    items.append((pre + [v, u] + post, c, param))
                    items.append((pre + post, c, param))
                else:
                    items.append((pre + [v, u] + post, c, param))
            elif u.startswith("b_") and v.startswith("a_1"):
                # u is boson, v is fermion
                # u * v = v * u - gb_{v, u} * kappa
                items.append((pre + [v, u] + post, c, param))
                if param is None:
                    gb_name = f"gb_{v}_{u}"
                    items.append((pre + post, -c, gb_name))
            else:
                raise ValueError(f"Unhandled pair: {u}, {v}")

    f0 = {k: v for k, v in final_order0.items() if v != 0}
    f1 = {k: v for k, v in final_order1.items() if v != 0}
    return f0, f1


def project_mod_K(elem: Dict[Tuple[str, ...], Fraction],
                   basis_list: List[str],
                   gens: Dict[str, Dict[Tuple[str, ...], Fraction]]) -> Dict[str, Fraction]:
    """Projects an element of the oscillator algebra onto g modulo central identity K."""
    if not elem:
        return {}
    all_words = set(elem.keys())
    for name in basis_list:
        all_words.update(gens[name].keys())
    all_words.add(())
    word_list = sorted(list(all_words), key=lambda w: (len(w), [op_key(x) for x in w]))

    M = []
    b = []
    for w in word_list:
        row = [gens[name].get(w, Fraction(0)) for name in basis_list]
        row.append(Fraction(1) if w == () else Fraction(0))
        M.append(row)
        b.append(elem.get(w, Fraction(0)))

    sp_M = sp.Matrix(M)
    sp_b = sp.Matrix(b)
    sol = sp_M.gauss_jordan_solve(sp_b)[0]
    res = sp_M * sol - sp_b
    if any(r != 0 for r in res):
        raise ValueError(f"Expression {elem} could not be projected mod K!")

    coeffs = {}
    for i, name in enumerate(basis_list):
        if sol[i] != 0:
            coeffs[name] = Fraction(int(sol[i].p), int(sol[i].q))
    return coeffs


def compute_gamma_structure(n: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Computes all non-zero canonical gamma terms for X <= Y in PBW order."""
    basis_info = build_basis(n)
    total_pbw = basis_info["odd"] + basis_info["even"]
    gens, parities, _ = build_oscillator_realizations(n)
    gb_info = get_gb_matrix_info(n)

    gamma_terms = []
    for i, x in enumerate(total_pbw):
        for j in range(i, len(total_pbw)):
            y = total_pbw[j]
            p_x = parities[x]
            p_y = parities[y]
            sign = -1 if (p_x * p_y % 2 == 1) else 1

            gamma_xy = defaultdict(lambda: defaultdict(Fraction))
            for w1, c1 in gens[x].items():
                for w2, c2 in gens[y].items():
                    _, o1 = reduce_deformed_word(list(w1) + list(w2), c1 * c2)
                    for (param, w), c in o1.items():
                        gamma_xy[param][w] += c

            for w2, c2 in gens[y].items():
                for w1, c1 in gens[x].items():
                    _, o1 = reduce_deformed_word(list(w2) + list(w1), c2 * c1)
                    for (param, w), c in o1.items():
                        gamma_xy[param][w] -= sign * c

            for param in sorted(gamma_xy.keys()):
                elem = {k: v for k, v in gamma_xy[param].items() if v != 0}
                if elem:
                    decomp = project_mod_K(elem, total_pbw, gens)
                    for z, coeff in decomp.items():
                        coeff_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                        gamma_terms.append({
                            "X": x,
                            "Y": y,
                            "Z": z,
                            "param": param,
                            "coeff": coeff_str,
                            "sign_rule": "graded"
                        })

    return gamma_terms, gb_info


def generate_schema2(n: int) -> Dict[str, Any]:
    """Generates the complete Schema 2 (gamma structure) JSON dictionary."""
    basis_info = build_basis(n)
    total_pbw = basis_info["odd"] + basis_info["even"]
    gens, parities, _ = build_oscillator_realizations(n)
    gamma_terms, gb_info = compute_gamma_structure(n)

    data = {
        "schema_version": "5.0",
        "layer": "2_gamma",
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
        "gb_matrix": gb_info,
        "basis": basis_info,
        "parity": {gen: parities[gen] for gen in total_pbw},
        "inhomogeneous_deformation": {
            "description": "2-cocycle gamma for inhomogeneous deformation [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)",
            "ordering_convention": "PBW: κ < [odd] < [even]",
            "num_terms": len(gamma_terms),
            "gamma_terms": gamma_terms
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": "2026-10-05",
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "handover/notation.md"
            ]
        }
    }
    return data


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema = generate_schema2(n)
        filename = os.path.join("data", f"C_{n}_gamma.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated {filename}: {schema['gb_matrix']['total_parameters']} gb parameters, "
              f"{len(schema['inhomogeneous_deformation']['gamma_terms'])} canonical gamma terms")


if __name__ == "__main__":
    main()
