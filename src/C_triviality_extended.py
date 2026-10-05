"""
Extended triviality analysis for C(n+1).
Tests multiple gb profiles and analyzes the obstruction.
"""

import json
import os
import sys
import numpy as np
from fractions import Fraction
from itertools import product as iter_product

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import build_basis, get_parity


def load_data(n):
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    files = {}
    for name in ["structure", "gamma", "coboundary"]:
        with open(os.path.join(data_dir, f"C_{n}_{name}.json")) as f:
            files[name] = json.load(f)
    return files


def evaluate_gamma_with_profile(gamma_data, gb_values):
    """Evaluate gamma coefficients with a specific gb profile."""
    result = {}
    for gc in gamma_data["gamma_coefficients"]:
        key = (gc["X"], gc["Y"], gc["gamma_Z"])
        gb = gc["gb_param"]
        coeff = float(Fraction(gc["coeff"]))
        val = gb_values.get(gb, 0.0)
        result[key] = result.get(key, 0.0) + coeff * val
    return {k: v for k, v in result.items() if abs(v) > 1e-15}


def build_coboundary_matrix(n, coboundary, all_keys):
    """Build the coboundary matrix A."""
    cb_data = {}
    phi_set = set()
    for cb in coboundary["coboundary_coefficients"]:
        key = (cb["X"], cb["Y"], cb["delta_f_Z"])
        phi = cb["phi_param"]
        coeff = float(Fraction(cb["coeff"]))
        cb_data.setdefault(key, {})[phi] = cb_data.get(key, {}).get(phi, 0.0) + coeff
        phi_set.add(phi)

    phi_params = sorted(phi_set)
    phi_idx = {p: i for i, p in enumerate(phi_params)}

    A = np.zeros((len(all_keys), len(phi_params)), dtype=np.float64)
    for i, key in enumerate(all_keys):
        if key in cb_data:
            for phi, coeff in cb_data[key].items():
                A[i, phi_idx[phi]] += coeff

    return A, phi_params


def test_profile(n, gb_values, A, all_keys, gamma_data, phi_params, label):
    """Test a specific gb profile for triviality."""
    gamma_map = evaluate_gamma_with_profile(gamma_data, gb_values)

    b = np.zeros(len(all_keys), dtype=np.float64)
    for i, key in enumerate(all_keys):
        b[i] = gamma_map.get(key, 0.0)

    if np.max(np.abs(b)) < 1e-15:
        return True, 0.0, "zero_gamma"

    rank_A = np.linalg.matrix_rank(A, tol=1e-10)
    Ab = np.column_stack([A, b])
    rank_Ab = np.linalg.matrix_rank(Ab, tol=1e-10)

    if rank_A == rank_Ab:
        phi_sol, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
        residual = np.max(np.abs(A @ phi_sol - b))
        return True, residual, "solvable"
    else:
        phi_sol, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
        residual = np.max(np.abs(A @ phi_sol - b))
        return False, residual, "inconsistent"


def main():
    for n in [1, 2, 3]:
        print(f"\n{'='*60}")
        print(f"  Extended Triviality Analysis for C({n+1}), n={n}")
        print(f"{'='*60}")

        files = load_data(n)
        gamma_data = files["gamma"]
        coboundary = files["coboundary"]

        gb_params = sorted(set(gc["gb_param"] for gc in gamma_data["gamma_coefficients"]))
        print(f"  gb parameters ({len(gb_params)}): {gb_params}")

        all_gamma_keys = set()
        for gc in gamma_data["gamma_coefficients"]:
            all_gamma_keys.add((gc["X"], gc["Y"], gc["gamma_Z"]))
        for cb in coboundary["coboundary_coefficients"]:
            all_gamma_keys.add((cb["X"], cb["Y"], cb["delta_f_Z"]))
        all_keys = sorted(all_gamma_keys)

        A, phi_params = build_coboundary_matrix(n, coboundary, all_keys)
        print(f"  Coboundary matrix: {A.shape[0]} x {A.shape[1]}")
        print(f"  Rank of A: {np.linalg.matrix_rank(A, tol=1e-10)}")

        if n <= 2:
            print(f"\n  Testing all {2**(len(gb_params))} sign profiles...")
            trivial_profiles = []
            nontrivial_count = 0

            for signs in iter_product([1, -1], repeat=len(gb_params)):
                gb_vals = {gb_params[i]: float(signs[i]) for i in range(len(gb_params))}
                solvable, residual, reason = test_profile(
                    n, gb_vals, A, all_keys, gamma_data, phi_params, "")

                if solvable and reason != "zero_gamma":
                    profile_str = "".join("+" if s == 1 else "-" for s in signs)
                    trivial_profiles.append((profile_str, residual))
                elif not solvable:
                    nontrivial_count += 1

            print(f"  Trivial profiles: {len(trivial_profiles)}")
            print(f"  Non-trivial profiles: {nontrivial_count}")
            if trivial_profiles:
                for p, r in trivial_profiles[:5]:
                    print(f"    Profile {p}: residual = {r:.2e}")
            else:
                print(f"  No trivial profile found among all sign combinations.")
        else:
            print(f"\n  n=3: too many sign profiles ({2**len(gb_params)}), testing representative ones...")
            profiles_to_test = [
                ("all_plus", {gb: 1.0 for gb in gb_params}),
                ("all_minus", {gb: -1.0 for gb in gb_params}),
                ("alternating", {gb: (1.0 if i % 2 == 0 else -1.0) for i, gb in enumerate(gb_params)}),
            ]
            for label, gb_vals in profiles_to_test:
                solvable, residual, reason = test_profile(
                    n, gb_vals, A, all_keys, gamma_data, phi_params, label)
                status = "TRIVIAL" if solvable else "NON-TRIVIAL"
                print(f"    {label}: {status} (residual = {residual:.2e})")

        print(f"\n  Analyzing obstruction structure...")
        gb_all_plus = {gb: 1.0 for gb in gb_params}
        gamma_map = evaluate_gamma_with_profile(gamma_data, gb_all_plus)
        b = np.zeros(len(all_keys), dtype=np.float64)
        for i, key in enumerate(all_keys):
            b[i] = gamma_map.get(key, 0.0)

        U, s, Vt = np.linalg.svd(A, full_matrices=True)
        rank_A = np.sum(s > 1e-10)
        null_components = U[:, rank_A:].T @ b
        print(f"  Null space components of b: {null_components[:5]}")
        print(f"  Norm of null-space projection of b: {np.linalg.norm(null_components):.6f}")

    print()


if __name__ == "__main__":
    main()
