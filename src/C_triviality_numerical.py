"""
Numerical triviality check: substitute gb=all_plus, solve Aφ=b numerically.
"""
import json
import os
import numpy as np
from fractions import Fraction
from C_generators import build_basis, build_parity_map


def check_triviality_numerical(n, data_dir="data"):
    with open(os.path.join(data_dir, f"C_{n}_gamma.json")) as f:
        gamma = json.load(f)
    with open(os.path.join(data_dir, f"C_{n}_coboundary.json")) as f:
        coboundary = json.load(f)

    # Evaluate gamma with all gb = 1
    gamma_eval = {}
    for entry in gamma["gamma_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        gamma_eval[key] = gamma_eval.get(key, Fraction(0)) + Fraction(entry["coeff"])

    # Build coboundary coefficient matrix
    coboundary_table = {}
    all_phi = set()
    for entry in coboundary["coboundary_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        if key not in coboundary_table:
            coboundary_table[key] = {}
        phi = entry["phi_param"]
        all_phi.add(phi)
        coboundary_table[key][phi] = coboundary_table[key].get(phi, Fraction(0)) + Fraction(entry["coeff"])

    all_triples = sorted(set(gamma_eval.keys()) | set(coboundary_table.keys()))
    all_phi = sorted(all_phi)
    phi_idx = {p: i for i, p in enumerate(all_phi)}

    num_eqs = len(all_triples)
    num_phi = len(all_phi)

    A = np.zeros((num_eqs, num_phi))
    b = np.zeros(num_eqs)

    for i, triple in enumerate(all_triples):
        if triple in coboundary_table:
            for phi, coeff in coboundary_table[triple].items():
                j = phi_idx[phi]
                A[i, j] = float(coeff)
        if triple in gamma_eval:
            b[i] = float(gamma_eval[triple])

    rank_A = np.linalg.matrix_rank(A, tol=1e-10)
    Ab = np.column_stack([A, b])
    rank_Ab = np.linalg.matrix_rank(Ab, tol=1e-10)

    print(f"\nC({n+1}) numerical check (gb=all_plus):")
    print(f"  Equations: {num_eqs}, Variables: {num_phi}")
    print(f"  rank(A) = {rank_A}, rank([A|b]) = {rank_Ab}")
    print(f"  Consistent: {rank_A == rank_Ab}")

    if rank_A == rank_Ab:
        phi_sol, residuals, _, _ = np.linalg.lstsq(A, b, rcond=None)
        max_residual = np.max(np.abs(A @ phi_sol - b))
        print(f"  Max residual: {max_residual:.2e}")
        print(f"  => TRIVIAL for gb=all_plus")
    else:
        # Find the residual of least-squares
        phi_sol, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
        residual = A @ phi_sol - b
        max_res_idx = np.argmax(np.abs(residual))
        max_res = residual[max_res_idx]
        triple = all_triples[max_res_idx]
        print(f"  Max residual: {max_res:.6f} at triple {triple}")
        print(f"  => NOT TRIVIAL for gb=all_plus")

        # Find obstruction: which triples are impossible?
        print(f"\n  Obstruction analysis:")
        nonzero_residuals = [(i, residual[i]) for i in range(len(residual)) if abs(residual[i]) > 1e-8]
        nonzero_residuals.sort(key=lambda x: -abs(x[1]))
        for idx, res in nonzero_residuals[:10]:
            print(f"    {all_triples[idx]}: residual = {res:.6f}")

    # Also check gb=0 (should always be trivial)
    b_zero = np.zeros(num_eqs)
    rank_Ab0 = np.linalg.matrix_rank(np.column_stack([A, b_zero]), tol=1e-10)
    print(f"\n  Sanity check (gb=0): rank(A)={rank_A}, rank([A|0])={rank_Ab0}, consistent={rank_A==rank_Ab0}")

    return rank_A == rank_Ab


if __name__ == "__main__":
    for n in [1, 2, 3]:
        check_triviality_numerical(n)
