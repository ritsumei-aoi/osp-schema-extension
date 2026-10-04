"""
C_triviality_analysis.py: Compares Layer 3 (evaluated deformation) and Layer 4 (coboundary)
to determine the necessary and sufficient triviality conditions on gb parameters for C(n+1).
"""

import json
import os
import sys
from fractions import Fraction
from collections import defaultdict
import sympy as sp

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def analyze_triviality(n, data_dir="data"):
    with open(os.path.join(data_dir, f"C_{n}_structure.json")) as f:
        struct_data = json.load(f)
    with open(os.path.join(data_dir, f"C_{n}_gamma.json")) as f:
        gamma_data = json.load(f)
    with open(os.path.join(data_dir, f"C_{n}_coboundary.json")) as f:
        cob_data = json.load(f)

    # All distinct equation slots (X, Y, Z)
    slots = set()
    for entry in cob_data["coboundary_coefficients"]:
        slots.add((entry["X"], entry["Y"], entry["Z"]))
    for entry in gamma_data["gamma_coefficients"]:
        if entry["Z"] != "K":
            slots.add((entry["X"], entry["Y"], entry["Z"]))
    slots = sorted(list(slots))

    phi_list = [m["id"] for m in cob_data["odd_map_basis"]]
    phi_idx = {p: i for i, p in enumerate(phi_list)}

    M = sp.zeros(len(slots), len(phi_list))
    for entry in cob_data["coboundary_coefficients"]:
        r = slots.index((entry["X"], entry["Y"], entry["Z"]))
        c = phi_idx[entry["phi_id"]]
        M[r, c] = sp.Rational(entry["coeff"])

    gb_list = gamma_data["gb_matrix"]["parameters"]
    gb_symbols = [sp.Symbol(p) for p in gb_list]
    gamma_vecs = {p: sp.zeros(len(slots), 1) for p in gb_list}

    for entry in gamma_data["gamma_coefficients"]:
        if entry["Z"] == "K":
            continue
        r = slots.index((entry["X"], entry["Y"], entry["Z"]))
        p = entry["gb_param"]
        gamma_vecs[p][r, 0] = sp.Rational(entry["coeff"])

    total_gamma = sp.zeros(len(slots), 1)
    for p, sym in zip(gb_list, gb_symbols):
        total_gamma += sym * gamma_vecs[p]

    null_left = M.T.nullspace()

    constraints = []
    for v in null_left:
        c = (v.T * total_gamma)[0, 0]
        c_sim = sp.simplify(c)
        if c_sim != 0:
            constraints.append(c_sim)

    indep_constraints = []
    if constraints:
        C_mat = sp.Matrix([[c.coeff(sym) for sym in gb_symbols] for c in constraints])
        rref_C, pivots = C_mat.rref()
        indep_constraints = [sum(rref_C[i, j] * gb_symbols[j] for j in range(len(gb_symbols))) for i in range(len(pivots))]

    # Check baseline all_plus_one assignment
    v_all1 = sp.zeros(len(slots), 1)
    for p in gb_list:
        v_all1 += gamma_vecs[p]
    
    # Check if solvable: M * x = v_all1
    # Solvable iff v.T * v_all1 == 0 for all v in null_left
    residuals_all1 = [(slots[i], (M * x_sol - v_all1)[i, 0]) if False else None for i in range(1)]
    fails_all1 = []
    for v in null_left:
        val = (v.T * v_all1)[0, 0]
        if val != 0:
            fails_all1.append(val)

    return {
        "n": n,
        "cartan_type": struct_data["algebra"]["cartan_type"],
        "slots_count": len(slots),
        "phi_count": len(phi_list),
        "matrix_rank": M.rank(),
        "left_nullspace_dim": len(null_left),
        "independent_constraints": indep_constraints,
        "all_plus_one_solvable": len(fails_all1) == 0,
        "all_plus_one_obstructions": len(fails_all1)
    }


def run_all_analysis():
    results = {}
    for n in [1, 2, 3]:
        res = analyze_triviality(n)
        results[n] = res
        print(f"--- Analysis for C({n+1}) (n={n}) ---")
        print(f"Slots: {res['slots_count']}, Map params: {res['phi_count']}, Rank: {res['matrix_rank']}")
        print(f"Independent triviality constraints ({len(res['independent_constraints'])}):")
        for ic in res['independent_constraints']:
            print(f"  {ic} = 0")
        print(f"all_plus_one assignment trivial? {res['all_plus_one_solvable']} (obstructions: {res['all_plus_one_obstructions']})")
    return results


if __name__ == "__main__":
    run_all_analysis()
