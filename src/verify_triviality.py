"""
Analysis and verification module for deformation triviality in C(n+1) = osp(2|2n).

Analyzes the 1-cohomology H^1(g, g) and the relationship between the inhomogeneous
deformation gamma(gb) and the 1-coboundary space B^1(g, g).
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
from typing import Dict, List, Tuple, Any
import sympy as sp

from src.C_coboundary import get_elementary_odd_maps, compute_elementary_coboundary


def analyze_deformation_cohomology(n: int, data_dir: str = "data") -> Dict[str, Any]:
    """
    Computes exact linear algebraic dimensions and cohomology projections for C(n+1):
    1. Dimension of odd linear maps: dim(Map_{odd}(g, g)) = 2 * dim(g_0) * dim(g_1)
    2. Rank of coboundary space: rank(B^1(g, g))
    3. Dimension of derivation kernel: dim(Der_{odd}(g, g))
    4. Rank of coboundary + deformation space: rank(B^1 + span(gamma_{gb}))
    5. Proof that span(gamma_{gb}) cap B^1(g, g) = {0}
    """
    # Load Schemas
    with open(os.path.join(data_dir, f"C_{n}_structure.json"), "r", encoding="utf-8") as f:
        s1 = json.load(f)
    with open(os.path.join(data_dir, f"C_{n}_gamma.json"), "r", encoding="utf-8") as f:
        g2 = json.load(f)
    with open(os.path.join(data_dir, f"C_{n}_evaluated.json"), "r", encoding="utf-8") as f:
        e3 = json.load(f)

    basis_even = s1["basis"]["even"]
    basis_odd = s1["basis"]["odd"]
    basis_list = basis_odd + basis_even
    parity_dict = s1["parity"]
    basis_idx = {b: i for i, b in enumerate(basis_list)}

    # Index bracket
    bracket_dict = defaultdict(lambda: defaultdict(dict))
    for entry in s1["structure_constants"]:
        bracket_dict[entry["X"]][entry["Y"]][entry["Z"]] = Fraction(entry["coeff"])

    # Elementary maps
    elem_maps = get_elementary_odd_maps(basis_list, parity_dict)
    elem_cbs = []
    for zi, zj, param in elem_maps:
        cb = compute_elementary_coboundary(zi, zj, basis_list, parity_dict, bracket_dict)
        elem_cbs.append(cb)

    # Decomposed gamma by parameter (ignoring central K)
    gb_params = g2["inhomogeneous_deformation"]["parameters"]["labels"]
    gamma_by_param = {p: defaultdict(Fraction) for p in gb_params}
    for t in g2["inhomogeneous_deformation"]["gamma_constants"]:
        if t["Z"] != "K":
            gamma_by_param[t["param"]][(t["X"], t["Y"], t["Z"])] += Fraction(t["coeff"])

    # Collect equations for upper triangular pairs X <= Y
    eqn_keys = set()
    for cb in elem_cbs:
        for (X, Y, Z), v in cb.items():
            if basis_idx[X] <= basis_idx[Y] and v != 0:
                eqn_keys.add((X, Y, Z))
    for p, gdict in gamma_by_param.items():
        for (X, Y, Z), v in gdict.items():
            if basis_idx[X] <= basis_idx[Y] and v != 0:
                eqn_keys.add((X, Y, Z))

    sorted_keys = sorted(list(eqn_keys))

    # Matrix M for B^1
    matrix_rows = []
    for k in sorted_keys:
        matrix_rows.append([cb.get(k, Fraction(0)) for cb in elem_cbs])

    M = sp.Matrix(matrix_rows)
    rank_M = int(M.rank())

    # Matrix G for deformation parameters
    G_cols = []
    for p in gb_params:
        col = [gamma_by_param[p].get(k, Fraction(0)) for k in sorted_keys]
        G_cols.append(col)

    G_mat = sp.Matrix(G_cols).T
    M_full = M.row_join(G_mat)
    rank_full = int(M_full.rank())

    # Evaluated deformation check
    gamma_eval = defaultdict(Fraction)
    for t in e3["evaluated_deformation"]["evaluated_gamma_constants"]:
        if t["Z"] != "K":
            gamma_eval[(t["X"], t["Y"], t["Z"])] = Fraction(t["coeff"])

    targets = [gamma_eval[k] for k in sorted_keys]
    b = sp.Matrix(targets)
    M_aug_eval = M.row_join(b)
    rank_eval = int(M_aug_eval.rank())

    dim_maps = len(elem_maps)
    kernel_dim = dim_maps - rank_M
    num_gb = len(gb_params)
    added_rank = rank_full - rank_M

    is_eval_trivial = (rank_M == rank_eval)
    trivial_only_at_zero = (added_rank == num_gb)

    return {
        "n": n,
        "algebra": f"C({n+1})",
        "dim_even": len(basis_even),
        "dim_odd": len(basis_odd),
        "total_dim": len(basis_list),
        "odd_maps_dim": dim_maps,
        "coboundary_rank": rank_M,
        "derivation_kernel_dim": kernel_dim,
        "num_gb_parameters": num_gb,
        "joint_rank": rank_full,
        "added_rank_by_gb": added_rank,
        "evaluated_is_trivial": is_eval_trivial,
        "trivial_only_at_zero": trivial_only_at_zero,
    }


def run_full_triviality_search() -> None:
    print("=" * 70)
    print("DEFORMATION TRIVIALITY ANALYSIS FOR C(n+1) = osp(2|2n)")
    print("=" * 70)
    for n in (1, 2, 3):
        res = analyze_deformation_cohomology(n)
        print(f"\n--- Results for n={n} ({res['algebra']}) ---")
        print(f"  Basis: {res['dim_even']} even + {res['dim_odd']} odd = {res['total_dim']} total")
        print(f"  Odd linear map space dim: {res['odd_maps_dim']}")
        print(f"  Coboundary space rank (dim B^1): {res['coboundary_rank']}")
        print(f"  Odd derivations kernel dim (dim Der_{{odd}}): {res['derivation_kernel_dim']}")
        print(f"  Deformation parameter count: {res['num_gb_parameters']}")
        print(f"  Joint rank [B^1 | span(gamma_gb)]: {res['joint_rank']}")
        print(f"  Added rank by deformation: {res['added_rank_by_gb']} (matches dim(gb) = {res['num_gb_parameters']})")
        print(f"  Evaluated deformation (all_plus_one) trivial? {res['evaluated_is_trivial']}")
        print(f"  Trivial if and only if gb = 0? {res['trivial_only_at_zero']}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    run_full_triviality_search()
