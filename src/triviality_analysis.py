"""
triviality_analysis.py: Comprehensive investigation of triviality conditions for C(n+1) deformations.
Solves the coboundary equation delta f = gamma across n=1, 2, 3 and analyzes discrepancies.
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
import sys
from typing import Dict, List, Tuple, Any
import numpy as np
import sympy as sp

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def load_all_layers(n: int):
    with open(f"data/C_{n}_structure.json") as f:
        s1 = json.load(f)
    with open(f"data/C_{n}_gamma.json") as f:
        s2 = json.load(f)
    with open(f"data/C_{n}_evaluated.json") as f:
        s3 = json.load(f)
    with open(f"data/C_{n}_coboundary.json") as f:
        s4 = json.load(f)
    return s1, s2, s3, s4


def build_coboundary_operator_matrix(s1: Dict[str, Any]):
    """
    Constructs the linear operator M_cob mapping odd linear maps phi to coboundaries delta f.
    Rows: canonical pairs (a, b) with a <= b, and target basis index c.
    Cols: odd linear map entries (i, j) with p(i) != p(j).
    """
    basis_list = s1["basis"]["odd"] + s1["basis"]["even"]
    parities = s1["parity"]
    N = len(basis_list)
    idx_map = {name: i for i, name in enumerate(basis_list)}

    C = np.zeros((N, N, N), dtype=np.float64)
    for entry in s1["structure_constants"]:
        i = idx_map[entry["X"]]
        j = idx_map[entry["Y"]]
        k = idx_map[entry["Z"]]
        c = float(Fraction(entry["coeff"]))
        C[i, j, k] = c
        if i != j:
            p_i = parities[entry["X"]]
            p_j = parities[entry["Y"]]
            sign = -1 if (p_i * p_j % 2 == 1) else 1
            C[j, i, k] = -sign * c

    odd_pairs = []
    for j in range(N):
        for i in range(N):
            if parities[basis_list[i]] != parities[basis_list[j]]:
                odd_pairs.append((i, j))

    canonical_pairs = []
    for a in range(N):
        for b in range(a, N):
            canonical_pairs.append((a, b))

    num_rows = len(canonical_pairs) * N
    num_cols = len(odd_pairs)
    M_cob = np.zeros((num_rows, num_cols), dtype=np.float64)

    for col, (i, j) in enumerate(odd_pairs):
        for row_idx, (a, b) in enumerate(canonical_pairs):
            p_a = parities[basis_list[a]]
            p_b = parities[basis_list[b]]
            sgn1 = -1.0 if (p_a % 2 == 1) else 1.0
            sgn2 = -1.0 if ((p_a + 1) * p_b % 2 == 1) else 1.0
            for k in range(N):
                row = row_idx * N + k
                val = 0.0
                if b == j:
                    val += sgn1 * C[a, i, k]
                if a == j:
                    val -= sgn2 * C[b, i, k]
                if k == i:
                    val -= C[a, b, j]
                M_cob[row, col] = val

    return basis_list, parities, canonical_pairs, odd_pairs, M_cob, idx_map


def analyze_triviality_rank(n: int) -> Dict[str, Any]:
    s1, s2, s3, s4 = load_all_layers(n)
    basis_list, parities, canonical_pairs, odd_pairs, M_cob, idx_map = build_coboundary_operator_matrix(s1)
    N = len(basis_list)
    num_rows = len(canonical_pairs) * N

    rank_cob = np.linalg.matrix_rank(M_cob)

    # 1. Compare evaluated gamma (Layer 3) with reference coboundary (Layer 4)
    l3_dict = {}
    for term in s3["evaluated_gamma"]["terms"]:
        l3_dict[(term["X"], term["Y"], term["Z"])] = float(Fraction(term["evaluated_coeff"]))

    l4_dict = {}
    for term in s4["coboundary_structure"]["terms"]:
        l4_dict[(term["X"], term["Y"], term["Z"])] = float(Fraction(term["coeff"]))

    all_triples = set(l3_dict.keys()) | set(l4_dict.keys())
    discrepancies = []
    matches = []
    for trip in all_triples:
        v3 = l3_dict.get(trip, 0.0)
        v4 = l4_dict.get(trip, 0.0)
        if abs(v3 - v4) > 1e-9:
            discrepancies.append((trip, v3, v4, v3 - v4))
        else:
            matches.append((trip, v3, v4))

    # 2. Check if evaluated gamma is in coboundary space
    gamma_eval_vec = np.zeros(num_rows)
    for (x, y, z), val in l3_dict.items():
        a = idx_map[x]
        b = idx_map[y]
        k = idx_map[z]
        row_idx = canonical_pairs.index((a, b))
        gamma_eval_vec[row_idx * N + k] = val

    rank_aug_eval = np.linalg.matrix_rank(np.hstack([M_cob, gamma_eval_vec[:, None]]))
    eval_is_coboundary = bool(rank_aug_eval == rank_cob)

    # 3. Check individual gb parameters
    gb_params = s2["gb_matrix"]["parameters"]
    Gamma_mat = np.zeros((num_rows, len(gb_params)))
    param_status = {}
    for col_p, param in enumerate(gb_params):
        vec = np.zeros(num_rows)
        for term in s2["inhomogeneous_deformation"]["gamma_terms"]:
            if term["param"] == param:
                a = idx_map[term["X"]]
                b = idx_map[term["Y"]]
                k = idx_map[term["Z"]]
                row_idx = canonical_pairs.index((a, b))
                vec[row_idx * N + k] = float(Fraction(term["coeff"]))
        Gamma_mat[:, col_p] = vec
        rank_param = np.linalg.matrix_rank(np.hstack([M_cob, vec[:, None]]))
        param_status[param] = bool(rank_param == rank_cob)

    # 4. Check rank of coboundary + entire gb parameter space
    rank_combined = np.linalg.matrix_rank(np.hstack([M_cob, Gamma_mat]))
    param_rank_increase = rank_combined - rank_cob

    return {
        "n": n,
        "dim": N,
        "even_dim": len(s1["basis"]["even"]),
        "odd_dim": len(s1["basis"]["odd"]),
        "num_odd_map_params": len(odd_pairs),
        "rank_coboundary": int(rank_cob),
        "num_gb_params": len(gb_params),
        "param_rank_increase": int(param_rank_increase),
        "eval_is_coboundary": eval_is_coboundary,
        "num_discrepancies": len(discrepancies),
        "num_matches": len(matches),
        "sample_discrepancies": discrepancies[:8],
        "sample_matches": matches[:8]
    }


def main():
    print("=" * 70)
    print("TRIVIALITY ANALYSIS FOR C(n+1) INHOMOGENEOUS DEFORMATIONS")
    print("=" * 70)

    for n in [1, 2, 3]:
        res = analyze_triviality_rank(n)
        print(f"\n--- C({n+1}) (n={n}, Total Dim={res['dim']}) ---")
        print(f"Even Dim: {res['even_dim']}, Odd Dim: {res['odd_dim']}")
        print(f"Odd linear map f space dimension: {res['num_odd_map_params']}")
        print(f"Coboundary space B^2 rank: {res['rank_coboundary']} (Kernel dim = {res['num_odd_map_params'] - res['rank_coboundary']})")
        print(f"Deformation parameters gb count: {res['num_gb_params']}")
        print(f"Rank increase from gb parameters: {res['param_rank_increase']} / {res['num_gb_params']}")
        print(f"Evaluated deformation (uniform +1) is coboundary? {res['eval_is_coboundary']}")
        print(f"Layer 3 vs Layer 4 direct comparisons: {res['num_matches']} matches, {res['num_discrepancies']} discrepancies")
        print("Sample discrepancies [(X, Y, Z), Layer3_val, Layer4_val, diff]:")
        for d in res["sample_discrepancies"][:5]:
            print(f"  {d[0]}: Layer3={d[1]}, Layer4={d[2]}, diff={d[3]}")


if __name__ == "__main__":
    main()
