"""C(n+1) = osp(2|2n) Inhomogeneous Deformation (Gamma Structure, Schema 2) Generator.

This script constructs the symbolic gb matrix (size 2 x 2n) and computes the
gamma 2-cocycle coefficients for the inhomogeneous deformation:
    [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)
for n = 1, 2, 3, outputting Schema 2 JSON files in data/.
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, Dict, List, Tuple

from src.C_generators import (
    build_basis,
    build_generator_realizations,
    get_oscillator_order,
    osc_parity,
    solve_exact_linear
)


def build_gb_matrix(n: int) -> Dict[str, Any]:
    """Build the 2 x 2n gb matrix definition."""
    row_labels = ["a_1_p", "a_1_m"]
    col_labels = []
    for j in range(1, n + 1):
        col_labels.extend([f"b_{j}_p", f"b_{j}_m"])
        
    matrix = []
    for r in row_labels:
        sigma = r.split('_')[2]
        row = []
        for c in col_labels:
            j = c.split('_')[1]
            s = c.split('_')[2]
            row.append(f"gb_a_1_{sigma}_b_{j}_{s}")
        matrix.append(row)
        
    return {
        "dimensions": [2, 2 * n],
        "row_labels": row_labels,
        "col_labels": col_labels,
        "matrix": matrix
    }

def normal_order_deformed(word: List[str], coeff: Fraction, osc_rank: Dict[str, int], param: str = None) -> List[Tuple[Tuple[str, ...], Fraction, str]]:
    """Normal-order an oscillator word with deformed exchange relations [b, a] = -gb * kappa."""
    for i in range(len(word) - 1):
        u, v = word[i], word[i + 1]
        if u == v and osc_parity(u) == 1:
            return []
        if osc_rank[u] > osc_rank[v]:
            p_uv = osc_parity(u) * osc_parity(v)
            sign = -1 if p_uv == 1 else 1
            comm = 0
            gb_term = None
            if u == 'a_1_m' and v == 'a_1_p':
                comm = 1
            elif u.startswith('b_') and v.startswith('b_'):
                uj, us = u.split('_')[1], u.split('_')[2]
                vj, vs = v.split('_')[1], v.split('_')[2]
                if uj == vj and us == 'm' and vs == 'p':
                    comm = 1
            elif u.startswith('b_') and v.startswith('a_1_'):
                sigma = v.split('_')[2]
                j = u.split('_')[1]
                s = u.split('_')[2]
                gb_term = (f"gb_a_1_{sigma}_b_{j}_{s}", -1)

            res = []
            w1 = word[:i] + [v, u] + word[i + 2:]
            res.extend(normal_order_deformed(w1, coeff * sign, osc_rank, param))
            if comm != 0:
                w2 = word[:i] + word[i + 2:]
                res.extend(normal_order_deformed(w2, coeff * comm, osc_rank, param))
            if gb_term is not None and param is None:
                p_name, p_sign = gb_term
                w3 = word[:i] + word[i + 2:]
                res.extend(normal_order_deformed(w3, coeff * p_sign, osc_rank, p_name))
            return res

    for i in range(len(word) - 1):
        if word[i] == word[i + 1] and osc_parity(word[i]) == 1:
            return []
    return [(tuple(word), coeff, param)]

def deformed_bracket(x: str, y: str, polys: Dict[str, Dict[Tuple[str, ...], Fraction]],
                     parities: Dict[str, int], osc_rank: Dict[str, int]) -> Dict[str, Dict[Tuple[str, ...], Fraction]]:
    """Compute deformed bracket terms grouped by gb parameter."""
    px, py = parities[x], parities[y]
    sign_yx = - (-1) ** (px * py)
    terms: Dict[str, Dict[Tuple[str, ...], Fraction]] = defaultdict(lambda: defaultdict(Fraction))
    
    for w1, c1 in polys[x].items():
        for w2, c2 in polys[y].items():
            w = list(w1 + w2)
            for nw, c, p in normal_order_deformed(w, c1 * c2, osc_rank):
                terms[p][nw] += c
                
    for w2, c2 in polys[y].items():
        for w1, c1 in polys[x].items():
            w = list(w2 + w1)
            for nw, c, p in normal_order_deformed(w, c2 * c1 * sign_yx, osc_rank):
                terms[p][nw] += c
                
    return {p: {nw: c for nw, c in wdict.items() if c != 0}
            for p, wdict in terms.items() if any(c != 0 for c in wdict.values())}

def compute_gamma_structure(n: int) -> Dict[str, Any]:
    """Compute Schema 2 gamma structure for rank n."""
    osc_order = get_oscillator_order(n)
    osc_rank = {name: i for i, name in enumerate(osc_order)}
    even_basis, odd_basis = build_basis(n)
    total_basis = even_basis + odd_basis
    polys, parities, _ = build_generator_realizations(n)

    # In adjoint representation, generators correspond to degree-2 oscillator expressions
    all_words = sorted(list({w for poly in polys.values() for w in poly.keys() if len(w) == 2}))
    word_to_idx = {w: i for i, w in enumerate(all_words)}

    A = [[Fraction(0)] * len(total_basis) for _ in all_words]
    for col_idx, gen_name in enumerate(total_basis):
        for w, c in polys[gen_name].items():
            if len(w) == 2:
                A[word_to_idx[w]][col_idx] = c

    gb_info = build_gb_matrix(n)
    gamma_entries = []

    for x in total_basis:
        for y in total_basis:
            br = deformed_bracket(x, y, polys, parities, osc_rank)
            for param, wdict in br.items():
                if param is None:
                    continue
                b = [Fraction(0)] * len(all_words)
                for nw, c in wdict.items():
                    if len(nw) == 2:
                        b[word_to_idx[nw]] = c
                sol = solve_exact_linear(A, b)
                for z_idx, c in enumerate(sol):
                    if c != 0:
                        gamma_entries.append({
                            "X": x,
                            "Y": y,
                            "Z": total_basis[z_idx],
                            "gb_param": param,
                            "coeff": str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"
                        })

    schema_2 = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})"
            },
            "dimension": {
                "total": 2 * n**2 + 5 * n + 1,
                "even": 2 * n**2 + n + 1,
                "odd": 4 * n
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis
        },
        "parity": parities,
        "gb_matrix": gb_info,
        "inhomogeneous_deformation": {
            "description": "Symbolic gamma coefficients gamma(X, Y) = sum_Z gamma_{XY}^Z Z in [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)",
            "sign_rule": "graded",
            "total_entries": len(gamma_entries),
            "gamma_coefficients": gamma_entries
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": "2026-10-05"
        }
    }

    return schema_2

def generate_all_schema_2(output_dir: str = "data"):
    """Generate C_1_gamma.json, C_2_gamma.json, and C_3_gamma.json."""
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        schema_2 = compute_gamma_structure(n)
        filepath = os.path.join(output_dir, f"C_{n}_gamma.json")
        with open(filepath, "w") as f:
            json.dump(schema_2, f, indent=2)
        print(f"Generated {filepath}: {len(schema_2['gb_matrix']['matrix'][0]) * 2} gb parameters, {schema_2['inhomogeneous_deformation']['total_entries']} gamma coefficients")

if __name__ == "__main__":
    generate_all_schema_2()
