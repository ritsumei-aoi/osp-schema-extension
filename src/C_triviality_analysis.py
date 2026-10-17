"""
C_triviality_analysis.py: Comprehensive triviality analysis for C(n+1) = osp(2|2n).
Compares Layer 3 (evaluated deformation) and Layer 4 (coboundary structure),
and computes the exact cohomology dimension and linear independence.
"""

import json
import os
import sys
from fractions import Fraction
from collections import defaultdict
import sympy as sp

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_triviality_analysis(n, data_dir="data"):
    eval_path = os.path.join(data_dir, f"C_{n}_evaluated.json")
    cob_path = os.path.join(data_dir, f"C_{n}_coboundary.json")
    struct_path = os.path.join(data_dir, f"C_{n}_structure.json")
    gamma_path = os.path.join(data_dir, f"C_{n}_gamma.json")

    with open(eval_path) as f: s3 = json.load(f)
    with open(cob_path) as f: s4 = json.load(f)
    with open(struct_path) as f: s1 = json.load(f)
    with open(gamma_path) as f: s2 = json.load(f)

    basis = s1["basis"]["odd"] + s1["basis"]["even"]
    parity = s1["parity"]
    dim = len(basis)
    name_to_idx = {name: i for i, name in enumerate(basis)}

    # 1. Compare Layer 3 and Layer 4 data directly
    gamma_table = defaultdict(dict)
    for e in s3["evaluated_gamma_structure_constants"]:
        gamma_table[(e["X"], e["Y"])][e["Z"]] = Fraction(e["coeff"])

    cob_table = defaultdict(dict)
    for e in s4["coboundary_structure_constants"]:
        cob_table[(e["X"], e["Y"])][e["Z"]] = Fraction(e["coeff"])

    all_pairs = sorted(list(set(gamma_table.keys()) | set(cob_table.keys())))
    coinciding_pairs = []
    differing_pairs = []
    gamma_only_pairs = []
    cob_only_pairs = []

    for pair in all_pairs:
        in_g = pair in gamma_table
        in_c = pair in cob_table
        if in_g and not in_c:
            gamma_only_pairs.append(pair)
        elif in_c and not in_g:
            cob_only_pairs.append(pair)
        else:
            if gamma_table[pair] == cob_table[pair]:
                coinciding_pairs.append(pair)
            else:
                differing_pairs.append(pair)

    # 2. Algebraic Cohomology / Linear System Analysis across ALL odd maps f
    c_0 = defaultdict(Fraction)
    for e in s1["structure_constants"]:
        c_0[(name_to_idx[e["X"]], name_to_idx[e["Y"]], name_to_idx[e["Z"]])] = Fraction(e["coeff"])

    param_names = [p for row in s2["inhomogeneous_deformation"]["gb_matrix"]["parameter_names"] for p in row]
    param_to_idx = {p: i for i, p in enumerate(param_names)}
    num_params = len(param_names)

    symm_gamma_table = defaultdict(dict)
    for e in s2["gamma_structure_constants"]:
        x = name_to_idx[e["X"]]
        y = name_to_idx[e["Y"]]
        z = name_to_idx[e["Z"]]
        p = param_to_idx[e["param"]]
        symm_gamma_table[(x, y, z)][p] = Fraction(e["coeff"])

    f_vars = []
    for j in range(dim):
        for i in range(dim):
            if parity[basis[i]] != parity[basis[j]]:
                f_vars.append((i, j))
    num_f_vars = len(f_vars)
    f_var_to_col = {v: c for c, v in enumerate(f_vars)}

    eq_rows_coboundary = []
    eq_rows_gamma = []

    for j in range(dim):
        pX = parity[basis[j]]
        for k in range(j, dim):
            pY = parity[basis[k]]
            for m in range(dim):
                if parity[basis[m]] != (pX + pY + 1) % 2:
                    continue

                row_f = [Fraction(0)] * num_f_vars
                row_g = [Fraction(0)] * num_params

                sign1 = -1 if pX == 1 else 1
                for i in range(dim):
                    if (i, k) in f_var_to_col:
                        c_ji_m = c_0.get((j, i, m), 0)
                        if c_ji_m != 0:
                            row_f[f_var_to_col[(i, k)]] += sign1 * c_ji_m

                sign2 = -1 if ((pX + 1) * pY) % 2 == 1 else 1
                for i in range(dim):
                    if (i, j) in f_var_to_col:
                        c_ki_m = c_0.get((k, i, m), 0)
                        if c_ki_m != 0:
                            row_f[f_var_to_col[(i, j)]] -= sign2 * c_ki_m

                for l in range(dim):
                    if (m, l) in f_var_to_col:
                        c_jk_l = c_0.get((j, k, l), 0)
                        if c_jk_l != 0:
                            row_f[f_var_to_col[(m, l)]] -= c_jk_l

                if (j, k, m) in symm_gamma_table:
                    for p_idx, c_val in symm_gamma_table[(j, k, m)].items():
                        row_g[p_idx] = c_val

                if any(x != 0 for x in row_f) or any(x != 0 for x in row_g):
                    eq_rows_coboundary.append(row_f)
                    eq_rows_gamma.append(row_g)

    M_cob = sp.Matrix([[sp.Rational(x.numerator, x.denominator) for x in row] for row in eq_rows_coboundary])
    M_gam = sp.Matrix([[sp.Rational(x.numerator, x.denominator) for x in row] for row in eq_rows_gamma])

    rank_cob = M_cob.rank()
    dim_der = num_f_vars - rank_cob
    M_aug = sp.Matrix.hstack(M_cob, M_gam)
    rank_aug = M_aug.rank()
    diff = rank_aug - rank_cob

    return {
        "n": n,
        "cartan_type": s1["algebra"]["cartan_type"],
        "dim_g": dim,
        "dim_Hom_1": num_f_vars,
        "num_params": num_params,
        "total_pairs": len(all_pairs),
        "coinciding_pairs": coinciding_pairs,
        "differing_pairs": differing_pairs,
        "gamma_only_pairs": gamma_only_pairs,
        "cob_only_pairs": cob_only_pairs,
        "sample_gamma": {str(p): {k: str(v) for k, v in gamma_table[p].items()} for p in differing_pairs[:3]},
        "sample_cob": {str(p): {k: str(v) for k, v in cob_table[p].items()} for p in differing_pairs[:3]},
        "rank_cob": rank_cob,
        "dim_der": dim_der,
        "rank_aug": rank_aug,
        "diff": diff,
        "is_trivial_for_all": diff == 0,
        "is_trivial_only_at_zero": diff == num_params
    }


def main():
    for n in [1, 2, 3]:
        res = run_triviality_analysis(n)
        print(f"\n=================== C({n+1}) Triviality Summary ===================")
        print(f"Algebra: {res['cartan_type']} (dim = {res['dim_g']})")
        print(f"Layer 3 vs Layer 4 Direct Comparison:")
        print(f"  Coinciding pairs: {len(res['coinciding_pairs'])}")
        print(f"  Differing pairs:  {len(res['differing_pairs'])}")
        print(f"  Gamma-only pairs: {len(res['gamma_only_pairs'])}")
        print(f"  Cob-only pairs:   {len(res['cob_only_pairs'])}")
        print(f"Cohomology Linear Algebra:")
        print(f"  dim(B^2_1) = {res['rank_cob']}")
        print(f"  dim(Der_1) = {res['dim_der']}")
        print(f"  rank([delta | gamma]) = {res['rank_aug']}")
        print(f"  Obstruction dimension (diff) = {res['diff']} / {res['num_params']}")
        print(f"  Trivial only at zero: {res['is_trivial_only_at_zero']}")


if __name__ == "__main__":
    main()
