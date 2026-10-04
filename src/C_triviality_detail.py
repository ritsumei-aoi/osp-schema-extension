"""Detailed triviality constraint analysis for C(n+1)."""
import json
import sys
sys.path.insert(0, "src")
from fractions import Fraction
from C_triviality import load_coboundary


def find_triviality_constraints(n):
    fname = f"data/C_{n}_gamma.json"
    with open(fname) as f:
        d = json.load(f)

    gb_params = d["gb_matrix"]["parameters"]
    gb_idx = {p: i for i, p in enumerate(gb_params)}
    n_gb = len(gb_params)

    gamma_by_key = {}
    for entry in d["gamma_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        gb_lbl = entry["gb_param"]
        coeff = Fraction(entry["numeric_coeff"])
        if key not in gamma_by_key:
            gamma_by_key[key] = {}
        gamma_by_key[key][gb_lbl] = gamma_by_key[key].get(gb_lbl, Fraction(0)) + coeff

    gamma_keys = list(gamma_by_key.keys())
    coboundary = load_coboundary(n)

    all_phi = set()
    for key in gamma_keys:
        if key in coboundary:
            all_phi.update(coboundary[key].keys())
    all_phi = sorted(all_phi)
    phi_idx = {p: i for i, p in enumerate(all_phi)}
    n_phi = len(all_phi)

    n_rows = len(gamma_keys)
    aug = []
    for key in gamma_keys:
        row = [Fraction(0)] * (n_phi + n_gb)
        if key in coboundary:
            for phi_lbl, coeff in coboundary[key].items():
                if phi_lbl in phi_idx:
                    row[phi_idx[phi_lbl]] += coeff
        for gb_lbl, coeff in gamma_by_key[key].items():
            row[n_phi + gb_idx[gb_lbl]] += coeff
        aug.append(row)

    pivot_row = 0
    for col in range(n_phi):
        pivot = None
        for row in range(pivot_row, n_rows):
            if aug[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        aug[pivot_row], aug[pivot] = aug[pivot], aug[pivot_row]
        pv = aug[pivot_row][col]
        for row in range(n_rows):
            if row != pivot_row and aug[row][col] != 0:
                fac = aug[row][col] / pv
                for j in range(n_phi + n_gb):
                    aug[row][j] -= fac * aug[pivot_row][j]
        pivot_row += 1

    rank = pivot_row
    print(f"C({n+1}) (n={n}): {n_rows} gamma constraints, {n_phi} relevant phi params")
    print(f"  Rank of coboundary (gamma-restricted): {rank}")

    constraints_on_gb = []
    for row in range(pivot_row, n_rows):
        m_row = aug[row][n_phi:]
        if any(c != 0 for c in m_row):
            constraints_on_gb.append(m_row)

    print(f"  Triviality constraints on gb: {len(constraints_on_gb)}")
    for c in constraints_on_gb:
        terms = []
        for j, val in enumerate(c):
            if val != 0:
                terms.append(f"({val})*{gb_params[j]}")
        print(f"    " + " + ".join(terms) + " = 0")


if __name__ == "__main__":
    for n in [1, 2, 3]:
        find_triviality_constraints(n)
        print()
