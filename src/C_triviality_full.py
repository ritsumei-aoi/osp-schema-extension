"""
Full triviality constraint analysis using the complete coboundary matrix.
For the system A*phi = M*gb (all constraints), find the constraints on gb
that make the system consistent.
"""
import json
import sys
sys.path.insert(0, "src")
from fractions import Fraction
from C_triviality import load_coboundary


def full_triviality_analysis(n):
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

    coboundary = load_coboundary(n)

    all_phi = sorted(set(p for pd in coboundary.values() for p in pd.keys()))
    phi_idx = {p: i for i, p in enumerate(all_phi)}
    n_phi = len(all_phi)

    all_keys = sorted(set(list(gamma_by_key.keys()) + list(coboundary.keys())))
    n_rows = len(all_keys)

    aug = []
    for key in all_keys:
        row = [Fraction(0)] * (n_phi + n_gb)
        if key in coboundary:
            for phi_lbl, coeff in coboundary[key].items():
                row[phi_idx[phi_lbl]] += coeff
        if key in gamma_by_key:
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
    print(f"C({n+1}) (n={n}): {n_rows} total constraints, {n_phi} phi params, {n_gb} gb params")
    print(f"  Rank of full coboundary A: {rank}")

    constraints_on_gb = []
    for row in range(pivot_row, n_rows):
        m_row = aug[row][n_phi:]
        if any(c != 0 for c in m_row):
            constraints_on_gb.append(m_row)

    # Compute true rank via Gaussian elimination on the constraint rows
    gb_mat = [list(row) for row in constraints_on_gb]
    gb_rows = len(gb_mat)
    pivot_col = 0
    independent = []
    for col in range(n_gb):
        pivot = None
        for row in range(pivot_col, gb_rows):
            if gb_mat[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        gb_mat[pivot_col], gb_mat[pivot] = gb_mat[pivot], gb_mat[pivot_col]
        pv = gb_mat[pivot_col][col]
        for row in range(gb_rows):
            if row != pivot_col and gb_mat[row][col] != 0:
                fac = gb_mat[row][col] / pv
                for j in range(n_gb):
                    gb_mat[row][j] -= fac * gb_mat[pivot_col][j]
        independent.append(gb_mat[pivot_col])
        pivot_col += 1

    print(f"  Independent triviality constraints on gb: {len(independent)}")
    for c in independent:
        terms = []
        for j, val in enumerate(c):
            if val != 0:
                terms.append(f"({val})*{gb_params[j]}")
        print(f"    " + " + ".join(terms) + " = 0")


if __name__ == "__main__":
    for n in [1, 2, 3]:
        full_triviality_analysis(n)
        print()
