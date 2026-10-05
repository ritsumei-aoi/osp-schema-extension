"""
C(n+1) = osp(2|2n) triviality analysis.

Compares Layer 3 (evaluated deformation γ) with Layer 4 (coboundary δf)
to determine conditions under which the deformation is trivial.

A deformation γ is trivial iff γ = δf for some odd linear map f,
i.e., for each (X,Y,Z):
  γ_{X,Y,Z}(gb) = Σ_φ (δf)_{X,Y,Z,φ} · φ

This is a system of linear equations in the φ variables, with the gb
parameters appearing as constants (or symbolic parameters) on the LHS.
"""

import json
import os
from fractions import Fraction
from datetime import date
from C_generators import build_basis, build_parity_map


def load_data(n, data_dir="data"):
    """Load Layer 2 (gamma), Layer 3 (evaluated), and Layer 4 (coboundary) data."""
    with open(os.path.join(data_dir, f"C_{n}_gamma.json")) as f:
        gamma = json.load(f)
    with open(os.path.join(data_dir, f"C_{n}_evaluated.json")) as f:
        evaluated = json.load(f)
    with open(os.path.join(data_dir, f"C_{n}_coboundary.json")) as f:
        coboundary = json.load(f)
    return gamma, evaluated, coboundary


def analyze_triviality_symbolic(n, data_dir="data"):
    """Analyze triviality symbolically.

    For each (X, Y, Z), the equation γ_{X,Y,Z} = (δf)_{X,Y,Z} must hold.

    γ_{X,Y,Z} is linear in gb parameters.
    (δf)_{X,Y,Z} is linear in φ parameters.

    We need: for each gb assignment, there exist φ values satisfying all equations.
    """
    gamma_data, evaluated, coboundary = load_data(n, data_dir)

    # Build gamma table: (X, Y, Z) -> {gb_param: coeff}
    gamma_table = {}
    for entry in gamma_data["gamma_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        if key not in gamma_table:
            gamma_table[key] = {}
        gb = entry["gb_param"]
        gamma_table[key][gb] = gamma_table[key].get(gb, Fraction(0)) + Fraction(entry["coeff"])

    # Build coboundary table: (X, Y, Z) -> {phi_param: coeff}
    coboundary_table = {}
    for entry in coboundary["coboundary_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        if key not in coboundary_table:
            coboundary_table[key] = {}
        phi = entry["phi_param"]
        coboundary_table[key][phi] = coboundary_table[key].get(phi, Fraction(0)) + Fraction(entry["coeff"])

    # Collect all gb and phi params
    all_gb = set()
    for gb_dict in gamma_table.values():
        all_gb.update(gb_dict.keys())
    all_phi = set()
    for phi_dict in coboundary_table.values():
        all_phi.update(phi_dict.keys())

    all_gb = sorted(all_gb)
    all_phi = sorted(all_phi)

    # All (X,Y,Z) triples where either gamma or coboundary is non-zero
    all_triples = sorted(set(gamma_table.keys()) | set(coboundary_table.keys()))

    print(f"\n=== C({n+1}) Triviality Analysis ===")
    print(f"  gb parameters: {len(all_gb)}")
    print(f"  phi parameters: {len(all_phi)}")
    print(f"  equation triples (X,Y,Z): {len(all_triples)}")

    # For each gb parameter, collect equations of the form:
    # gb_k * coeff_k = Σ_j (δf)_{XYZ,φ_j} · φ_j
    # This decouples by gb parameter since γ is linear in gb.

    # Group equations by gb parameter
    equations_by_gb = {gb: [] for gb in all_gb}

    for triple in all_triples:
        gamma_gb = gamma_table.get(triple, {})
        coboundary_phi = coboundary_table.get(triple, {})

        for gb, gb_coeff in gamma_gb.items():
            equations_by_gb[gb].append({
                "triple": triple,
                "gb_coeff": gb_coeff,
                "phi_coeffs": coboundary_phi,
            })

        # Triples where gamma is 0 but coboundary might be nonzero
        # These give homogeneous constraints on phi
        if not gamma_gb and coboundary_phi:
            for gb in all_gb:
                equations_by_gb[gb].append({
                    "triple": triple,
                    "gb_coeff": Fraction(0),
                    "phi_coeffs": coboundary_phi,
                })

    return {
        "gamma_table": gamma_table,
        "coboundary_table": coboundary_table,
        "equations_by_gb": equations_by_gb,
        "all_gb": all_gb,
        "all_phi": all_phi,
        "all_triples": all_triples,
    }


def solve_triviality(n, data_dir="data"):
    """Attempt to solve γ = δf using Gaussian elimination.

    Since γ is linear in gb and δf is linear in φ, the system γ = δf
    is: for each (X,Y,Z): Σ_k gb_k · γ_{XYZ,k} = Σ_j φ_j · (δf)_{XYZ,j}

    Rearranging: Σ_j (δf)_{XYZ,j} · φ_j = Σ_k gb_k · γ_{XYZ,k}

    This is a linear system in φ with gb on the RHS.
    Using sympy for symbolic solution.
    """
    from sympy import Matrix, symbols, Rational, solve, zeros

    analysis = analyze_triviality_symbolic(n, data_dir)

    gamma_table = analysis["gamma_table"]
    coboundary_table = analysis["coboundary_table"]
    all_gb = analysis["all_gb"]
    all_phi = analysis["all_phi"]
    all_triples = analysis["all_triples"]

    gb_syms = {gb: symbols(gb) for gb in all_gb}
    phi_syms = {phi: symbols(phi) for phi in all_phi}

    num_eqs = len(all_triples)
    num_phi = len(all_phi)

    print(f"  Setting up {num_eqs} x {num_phi} system...")

    # Build the system: A · φ = b(gb)
    # A[i,j] = coboundary coefficient for triple i, phi j
    # b[i] = gamma value for triple i (linear in gb)

    phi_list = list(all_phi)
    phi_idx = {p: i for i, p in enumerate(phi_list)}

    A = zeros(num_eqs, num_phi)
    b = zeros(num_eqs, 1)

    for eq_idx, triple in enumerate(all_triples):
        phi_coeffs = coboundary_table.get(triple, {})
        for phi, coeff in phi_coeffs.items():
            j = phi_idx[phi]
            A[eq_idx, j] = Rational(coeff.numerator, coeff.denominator)

        gamma_gb = gamma_table.get(triple, {})
        rhs = sum(
            Rational(coeff.numerator, coeff.denominator) * gb_syms[gb]
            for gb, coeff in gamma_gb.items()
        )
        b[eq_idx, 0] = rhs

    print(f"  Matrix A: {A.shape[0]} x {A.shape[1]}")
    print(f"  Rank of A: ", end="")

    rank_A = A.rank()
    print(f"{rank_A}")

    # Augmented matrix [A | b]
    Ab = A.row_join(b)
    rank_Ab = Ab.rank()
    print(f"  Rank of [A|b]: {rank_Ab}")

    if rank_A == rank_Ab:
        print(f"  => System is CONSISTENT for all gb values.")
        print(f"  => The deformation is ALWAYS TRIVIAL (for any gb assignment).")
        trivial = True
        conditions = "No conditions needed - trivial for all gb."
    else:
        print(f"  => System is INCONSISTENT for generic gb.")
        print(f"  => The deformation is NOT always trivial.")
        trivial = False

        # Find the conditions on gb for consistency
        # The inconsistency arises when rows of [A|b] give 0·φ = nonzero(gb)
        rref_A, pivots_A = A.rref()
        rref_Ab, pivots_Ab = Ab.rref()

        conditions_on_gb = []
        for i in range(A.shape[0]):
            row_A = rref_Ab[i, :num_phi]
            if row_A.is_zero_matrix or all(row_A[0, j] == 0 for j in range(num_phi)):
                rhs_val = rref_Ab[i, num_phi]
                if rhs_val != 0:
                    conditions_on_gb.append(str(rhs_val) + " = 0")

        if conditions_on_gb:
            print(f"  Conditions on gb for triviality:")
            for cond in conditions_on_gb[:20]:
                print(f"    {cond}")
        conditions = conditions_on_gb

    return {
        "n": n,
        "trivial_always": trivial,
        "rank_A": rank_A,
        "rank_Ab": rank_Ab,
        "num_equations": num_eqs,
        "num_phi": num_phi,
        "conditions": conditions,
    }


def run_analysis(data_dir="data"):
    results = {}
    for n in [1, 2, 3]:
        results[n] = solve_triviality(n, data_dir)
    return results


if __name__ == "__main__":
    results = run_analysis()

    print("\n\n=== SUMMARY ===")
    for n in [1, 2, 3]:
        r = results[n]
        print(f"\nC({n+1}) = osp(2|{2*n}):")
        print(f"  System: {r['num_equations']} eqs, {r['num_phi']} unknowns")
        print(f"  Rank A: {r['rank_A']}, Rank [A|b]: {r['rank_Ab']}")
        print(f"  Always trivial: {r['trivial_always']}")
        if not r['trivial_always']:
            print(f"  Conditions: {r['conditions'][:5]}")
