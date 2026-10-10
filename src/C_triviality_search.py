"""
Triviality condition search for C(n+1) = osp(2|2n).

Compares Layer 3 (evaluated gamma) and Layer 4 (coboundary) to determine
conditions under which the inhomogeneous deformation is trivial:
  γ(X, Y) = (δf)(X, Y) for all X, Y ∈ g

This amounts to solving a linear system in the phi parameters of f.
"""

import json
import os
import sys
from fractions import Fraction
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import build_basis, get_parity


def load_json(data_dir, filename):
    with open(os.path.join(data_dir, filename)) as f:
        return json.load(f)


def build_triviality_system(n, evaluated_data, coboundary_data, structure_data):
    """Build the linear system γ = δf.

    For each (X, Y, Z) triple, the equation is:
      evaluated_gamma[X,Y,Z] = Σ_phi coboundary_coeff[X,Y,Z,phi] * phi

    Returns: A (matrix), b (rhs vector), phi_labels (column labels), equation_labels
    """
    even, odd = build_basis(n)
    all_gens = odd + even
    parity = {g: get_parity(g) for g in all_gens}

    phi_labels = []
    for e_gen in even:
        for o_gen in odd:
            phi_labels.append(f"phi_{o_gen}_{e_gen}")
    for o_gen in odd:
        for e_gen in even:
            phi_labels.append(f"phi_{e_gen}_{o_gen}")
    phi_index = {label: i for i, label in enumerate(phi_labels)}
    n_phi = len(phi_labels)

    gamma_dict = {}
    for entry in evaluated_data["evaluated_gamma_coefficients"]:
        x, y = entry["X"], entry["Y"]
        for term in entry["result"]:
            z = term["Z"]
            c = Fraction(term["coeff"])
            gamma_dict[(x, y, z)] = gamma_dict.get((x, y, z), Fraction(0)) + c

    coboundary_dict = {}
    for entry in coboundary_data["coboundary_coefficients"]:
        x, y = entry["X"], entry["Y"]
        for term in entry["result"]:
            z = term["Z"]
            phi = term["phi_param"]
            c = Fraction(term["coeff"])
            key = (x, y, z)
            if key not in coboundary_dict:
                coboundary_dict[key] = {}
            coboundary_dict[key][phi] = coboundary_dict[key].get(phi, Fraction(0)) + c

    all_xyz = set()
    all_xyz.update(gamma_dict.keys())
    all_xyz.update(coboundary_dict.keys())
    all_xyz = sorted(all_xyz)

    n_eq = len(all_xyz)
    A = np.zeros((n_eq, n_phi), dtype=float)
    b = np.zeros(n_eq, dtype=float)
    equation_labels = []

    for eq_idx, (x, y, z) in enumerate(all_xyz):
        equation_labels.append(f"[{x}, {y}] -> {z}")
        b[eq_idx] = float(gamma_dict.get((x, y, z), Fraction(0)))

        if (x, y, z) in coboundary_dict:
            for phi, c in coboundary_dict[(x, y, z)].items():
                if phi in phi_index:
                    A[eq_idx, phi_index[phi]] += float(c)

    return A, b, phi_labels, equation_labels


def analyze_triviality(n):
    """Analyze triviality for C(n+1) with bosonic rank n."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), "data")

    structure = load_json(data_dir, f"C_{n}_structure.json")
    evaluated = load_json(data_dir, f"C_{n}_evaluated.json")
    coboundary = load_json(data_dir, f"C_{n}_coboundary.json")

    print(f"\n{'='*70}")
    print(f"Triviality analysis for C({n+1}) = osp(2|{2*n}), n={n}")
    print(f"{'='*70}")

    A, b, phi_labels, eq_labels = build_triviality_system(n, evaluated, coboundary, structure)

    print(f"\nSystem size: {A.shape[0]} equations x {A.shape[1]} unknowns (phi params)")
    print(f"Non-zero RHS entries (gamma): {np.count_nonzero(b)}")
    print(f"Non-zero matrix entries: {np.count_nonzero(A)}")

    rank_A = np.linalg.matrix_rank(A)
    Ab = np.column_stack([A, b.reshape(-1, 1)])
    rank_Ab = np.linalg.matrix_rank(Ab)

    print(f"\nRank of A: {rank_A}")
    print(f"Rank of [A|b]: {rank_Ab}")

    if rank_A == rank_Ab:
        print(f"\n>>> RESULT: System is CONSISTENT.")
        print(f"    The deformation γ IS a coboundary (trivial) for this gb assignment.")
        print(f"    Solution space dimension: {len(phi_labels) - rank_A}")

        phi_solution, residuals, _, _ = np.linalg.lstsq(A, b, rcond=None)
        residual_norm = np.linalg.norm(A @ phi_solution - b)
        print(f"    Least-squares residual: {residual_norm:.2e}")

        nonzero_phi = [(phi_labels[i], phi_solution[i])
                       for i in range(len(phi_labels))
                       if abs(phi_solution[i]) > 1e-10]
        print(f"    Non-zero phi in particular solution: {len(nonzero_phi)}")
        for label, val in nonzero_phi[:20]:
            print(f"      {label} = {val:.6f}")
        if len(nonzero_phi) > 20:
            print(f"      ... ({len(nonzero_phi) - 20} more)")
    else:
        print(f"\n>>> RESULT: System is INCONSISTENT.")
        print(f"    The deformation γ is NOT a coboundary (non-trivial) for this gb assignment.")
        print(f"    Rank deficiency: rank(A)={rank_A} < rank([A|b])={rank_Ab}")

        residual = A @ np.linalg.lstsq(A, b, rcond=None)[0] - b
        inconsistent_eqs = [(eq_labels[i], abs(residual[i]))
                            for i in range(len(eq_labels))
                            if abs(residual[i]) > 1e-10]
        inconsistent_eqs.sort(key=lambda x: -x[1])
        print(f"\n    Inconsistent equations ({len(inconsistent_eqs)} total):")
        for label, res in inconsistent_eqs[:10]:
            print(f"      {label}: residual = {res:.6f}")

    return rank_A, rank_Ab, A, b, phi_labels, eq_labels


def analyze_symbolic_triviality(n):
    """Analyze triviality symbolically for general gb parameters.

    Instead of fixing gb to specific values, express gamma as a function of
    gb parameters and check which gb assignments make the system consistent.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), "data")

    structure = load_json(data_dir, f"C_{n}_structure.json")
    gamma_data = load_json(data_dir, f"C_{n}_gamma.json")
    coboundary_data = load_json(data_dir, f"C_{n}_coboundary.json")

    even, odd = build_basis(n)
    all_gens = odd + even

    from C_gamma import get_gb_parameters
    gb_params = get_gb_parameters(n)
    gb_labels = [p["label"] for p in gb_params]
    n_gb = len(gb_labels)

    phi_labels = []
    for e_gen in even:
        for o_gen in odd:
            phi_labels.append(f"phi_{o_gen}_{e_gen}")
    for o_gen in odd:
        for e_gen in even:
            phi_labels.append(f"phi_{e_gen}_{o_gen}")
    phi_index = {label: i for i, label in enumerate(phi_labels)}
    n_phi = len(phi_labels)

    gamma_symbolic = {}
    for entry in gamma_data["gamma_coefficients"]:
        x, y = entry["X"], entry["Y"]
        for term in entry["result"]:
            z = term["Z"]
            gb = term["gb_param"]
            c = Fraction(term["coeff"])
            key = (x, y, z)
            if key not in gamma_symbolic:
                gamma_symbolic[key] = {}
            gamma_symbolic[key][gb] = gamma_symbolic[key].get(gb, Fraction(0)) + c

    coboundary_dict = {}
    for entry in coboundary_data["coboundary_coefficients"]:
        x, y = entry["X"], entry["Y"]
        for term in entry["result"]:
            z = term["Z"]
            phi = term["phi_param"]
            c = Fraction(term["coeff"])
            key = (x, y, z)
            if key not in coboundary_dict:
                coboundary_dict[key] = {}
            coboundary_dict[key][phi] = coboundary_dict[key].get(phi, Fraction(0)) + c

    all_xyz = set()
    all_xyz.update(gamma_symbolic.keys())
    all_xyz.update(coboundary_dict.keys())
    all_xyz = sorted(all_xyz)

    print(f"\n--- Symbolic analysis for C({n+1}), n={n} ---")
    print(f"Equations: {len(all_xyz)}")
    print(f"Phi unknowns: {n_phi}")
    print(f"GB parameters: {n_gb}")

    n_eq = len(all_xyz)

    A = np.zeros((n_eq, n_phi), dtype=float)

    for eq_idx, (x, y, z) in enumerate(all_xyz):
        if (x, y, z) in coboundary_dict:
            for phi, c in coboundary_dict[(x, y, z)].items():
                if phi in phi_index:
                    A[eq_idx, phi_index[phi]] += float(c)

    rank_A = np.linalg.matrix_rank(A)
    print(f"Rank of coboundary matrix A: {rank_A}")
    print(f"Image dimension of δ: {rank_A}")
    print(f"Kernel dimension of δ (null space): {n_phi - rank_A}")

    from C_gamma import gb_label as make_gb_label
    from C_evaluated import default_gb_assignment, evaluate_gamma

    test_profiles = []

    all_plus = {gl: "+1" for gl in gb_labels}
    test_profiles.append(("all +1", all_plus))

    all_minus = {gl: "-1" for gl in gb_labels}
    test_profiles.append(("all -1", all_minus))

    if n >= 1:
        mixed = {}
        for gl in gb_labels:
            if "a1p" in gl:
                mixed[gl] = "+1"
            else:
                mixed[gl] = "-1"
        test_profiles.append(("a1p=+1, a1m=-1", mixed))

    print(f"\n--- Testing specific gb profiles ---")
    trivial_profiles = []
    nontrivial_profiles = []

    for profile_name, gb_assign in test_profiles:
        b_vec = np.zeros(n_eq)
        for eq_idx, (x, y, z) in enumerate(all_xyz):
            if (x, y, z) in gamma_symbolic:
                val = Fraction(0)
                for gb, c in gamma_symbolic[(x, y, z)].items():
                    val += c * Fraction(gb_assign[gb])
                b_vec[eq_idx] = float(val)

        Ab = np.column_stack([A, b_vec.reshape(-1, 1)])
        rank_Ab = np.linalg.matrix_rank(Ab)

        if rank_A == rank_Ab:
            trivial_profiles.append(profile_name)
            residual = np.linalg.norm(A @ np.linalg.lstsq(A, b_vec, rcond=None)[0] - b_vec)
            print(f"  {profile_name}: TRIVIAL (rank [A|b]={rank_Ab}, residual={residual:.2e})")
        else:
            nontrivial_profiles.append(profile_name)
            print(f"  {profile_name}: NON-TRIVIAL (rank A={rank_A}, rank [A|b]={rank_Ab})")

    return trivial_profiles, nontrivial_profiles


def main():
    all_results = {}

    for n in [1, 2, 3]:
        rank_A, rank_Ab, A, b, phi_labels, eq_labels = analyze_triviality(n)
        trivial, nontrivial = analyze_symbolic_triviality(n)
        all_results[n] = {
            "rank_A": rank_A,
            "rank_Ab": rank_Ab,
            "consistent": rank_A == rank_Ab,
            "trivial_profiles": trivial,
            "nontrivial_profiles": nontrivial
        }

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    for n in [1, 2, 3]:
        r = all_results[n]
        status = "TRIVIAL" if r["consistent"] else "NON-TRIVIAL"
        print(f"\nC({n+1}) [gb=all +1]: {status}")
        print(f"  Trivial profiles: {r['trivial_profiles']}")
        print(f"  Non-trivial profiles: {r['nontrivial_profiles']}")


if __name__ == "__main__":
    main()
