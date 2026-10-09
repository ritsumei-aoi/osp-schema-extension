"""
Triviality condition search for C(n+1) = osp(2|2n).

Determines when the inhomogeneous deformation gamma is a coboundary delta f,
by setting up and solving the linear system gamma = delta f.
"""

import json
import os
import sys
from fractions import Fraction
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import build_basis, get_parity


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load_json(path):
    with open(path) as f:
        return json.load(f)


def build_gamma_vector(n, gb_assignment=None):
    """Build the evaluated gamma as a vector indexed by (X, Y, Z) triples."""
    gamma_data = load_json(os.path.join(DATA_DIR, f"C_{n}_gamma.json"))
    structure = load_json(os.path.join(DATA_DIR, f"C_{n}_structure.json"))
    all_labels = structure["basis"]["odd"] + structure["basis"]["even"]
    label_to_idx = {l: i for i, l in enumerate(all_labels)}
    dim = len(all_labels)

    if gb_assignment is None:
        gb_assignment = {}
        for p in gamma_data["gb_matrix"]["parameters"]:
            gb_assignment[p["label"]] = 1

    pair_results = {}
    for entry in gamma_data["gamma_coefficients"]:
        x, y = entry["X"], entry["Y"]
        gb_param = entry["gb_parameter"]
        gb_val = gb_assignment.get(gb_param, 0)
        if gb_val == 0:
            continue

        key = (x, y)
        if key not in pair_results:
            pair_results[key] = {}
        for term in entry["result"]:
            z = term["Z"]
            c = Fraction(term["coeff"]) * gb_val
            pair_results[key][z] = pair_results[key].get(z, Fraction(0)) + c

    gamma_vec = {}
    for (x, y), results in pair_results.items():
        for z, c in results.items():
            if c != 0:
                gamma_vec[(x, y, z)] = c

    return gamma_vec, all_labels


def build_coboundary_matrix(n):
    """Build matrix A where gamma = A * phi represents the coboundary system.

    Each column corresponds to a phi parameter.
    Each row corresponds to a (X, Y, Z) triple.
    """
    cob_data = load_json(os.path.join(DATA_DIR, f"C_{n}_coboundary.json"))
    structure = load_json(os.path.join(DATA_DIR, f"C_{n}_structure.json"))
    all_labels = structure["basis"]["odd"] + structure["basis"]["even"]

    phi_params = set()
    for entry in cob_data["coboundary_coefficients"]:
        phi_params.add(entry["phi_parameter"])
    phi_params = sorted(phi_params)
    phi_to_col = {p: i for i, p in enumerate(phi_params)}

    xyz_triples = set()
    for entry in cob_data["coboundary_coefficients"]:
        x, y = entry["X"], entry["Y"]
        for term in entry["result"]:
            xyz_triples.add((x, y, term["Z"]))

    xyz_list = sorted(xyz_triples)
    xyz_to_row = {t: i for i, t in enumerate(xyz_list)}

    nrows = len(xyz_list)
    ncols = len(phi_params)

    A = np.zeros((nrows, ncols), dtype=np.float64)

    for entry in cob_data["coboundary_coefficients"]:
        x, y = entry["X"], entry["Y"]
        phi = entry["phi_parameter"]
        col = phi_to_col[phi]
        for term in entry["result"]:
            z = term["Z"]
            row = xyz_to_row[(x, y, z)]
            A[row, col] += float(Fraction(term["coeff"]))

    return A, xyz_list, xyz_to_row, phi_params, phi_to_col


def build_gamma_rhs(gamma_vec, xyz_to_row):
    """Build the right-hand side vector b from gamma."""
    b = np.zeros(len(xyz_to_row), dtype=np.float64)
    for (x, y, z), c in gamma_vec.items():
        key = (x, y, z)
        if key in xyz_to_row:
            b[xyz_to_row[key]] += float(c)
    return b


def solve_triviality(n, gb_assignment=None):
    """Solve gamma = A * phi for the given gb assignment.

    Returns: (is_trivial, phi_solution_or_None, residual_norm, details)
    """
    gamma_vec, all_labels = build_gamma_vector(n, gb_assignment)

    if not gamma_vec:
        return True, None, 0.0, "Gamma is zero (trivially a coboundary)"

    A, xyz_list, xyz_to_row, phi_params, phi_to_col = build_coboundary_matrix(n)

    gamma_triples = set(gamma_vec.keys())
    cob_triples = set(xyz_to_row.keys())
    missing = gamma_triples - cob_triples
    if missing:
        return False, None, float('inf'), f"Gamma has {len(missing)} triples not in coboundary image"

    b = build_gamma_rhs(gamma_vec, xyz_to_row)

    phi_solution, residuals, rank, sv = np.linalg.lstsq(A, b, rcond=None)

    residual = A @ phi_solution - b
    residual_norm = np.linalg.norm(residual)

    is_trivial = residual_norm < 1e-10

    details = {
        "matrix_shape": A.shape,
        "rank": int(rank),
        "residual_norm": residual_norm,
        "gamma_triples": len(gamma_vec),
        "phi_params": len(phi_params),
        "nonzero_phi": int(np.sum(np.abs(phi_solution) > 1e-10)),
    }

    return is_trivial, phi_solution if is_trivial else None, residual_norm, details


def analyze_triviality_all_profiles(n):
    """Analyze triviality for multiple gb profiles."""
    gamma_data = load_json(os.path.join(DATA_DIR, f"C_{n}_gamma.json"))
    gb_params = [p["label"] for p in gamma_data["gb_matrix"]["parameters"]]

    profiles = {}

    assignment = {p: 1 for p in gb_params}
    profiles["all_plus"] = dict(assignment)

    assignment = {p: (-1 if i % 2 else 1) for i, p in enumerate(gb_params)}
    profiles["alternating"] = dict(assignment)

    for idx, p in enumerate(gb_params):
        single = {q: 0 for q in gb_params}
        single[p] = 1
        profiles[f"single_{p}"] = single

    results = {}
    for name, assignment in profiles.items():
        is_trivial, phi, resid, details = solve_triviality(n, assignment)
        results[name] = {
            "is_trivial": is_trivial,
            "residual_norm": resid,
            "details": details,
        }

    return results


def find_triviality_conditions(n):
    """Determine the general conditions on gb for triviality.

    Method: Set up the system symbolically. For each gb parameter,
    the gamma is linear in gb. The triviality condition is that
    for each (X, Y, Z), the gb-weighted gamma equals a coboundary.
    This gives a linear system in (gb, phi) jointly.
    """
    gamma_data = load_json(os.path.join(DATA_DIR, f"C_{n}_gamma.json"))
    cob_data = load_json(os.path.join(DATA_DIR, f"C_{n}_coboundary.json"))
    structure = load_json(os.path.join(DATA_DIR, f"C_{n}_structure.json"))

    all_labels = structure["basis"]["odd"] + structure["basis"]["even"]
    gb_params = [p["label"] for p in gamma_data["gb_matrix"]["parameters"]]
    gb_to_idx = {p: i for i, p in enumerate(gb_params)}

    phi_params = set()
    for entry in cob_data["coboundary_coefficients"]:
        phi_params.add(entry["phi_parameter"])
    phi_params = sorted(phi_params)
    phi_to_idx = {p: i for i, p in enumerate(phi_params)}

    xyz_set = set()
    for entry in gamma_data["gamma_coefficients"]:
        x, y = entry["X"], entry["Y"]
        for term in entry["result"]:
            xyz_set.add((x, y, term["Z"]))
    for entry in cob_data["coboundary_coefficients"]:
        x, y = entry["X"], entry["Y"]
        for term in entry["result"]:
            xyz_set.add((x, y, term["Z"]))

    xyz_list = sorted(xyz_set)
    xyz_to_row = {t: i for i, t in enumerate(xyz_list)}

    n_rows = len(xyz_list)
    n_gb = len(gb_params)
    n_phi = len(phi_params)

    M = np.zeros((n_rows, n_gb + n_phi), dtype=np.float64)

    for entry in gamma_data["gamma_coefficients"]:
        x, y = entry["X"], entry["Y"]
        gb = entry["gb_parameter"]
        gb_col = gb_to_idx[gb]
        for term in entry["result"]:
            z = term["Z"]
            row = xyz_to_row[(x, y, z)]
            M[row, gb_col] += float(Fraction(term["coeff"]))

    for entry in cob_data["coboundary_coefficients"]:
        x, y = entry["X"], entry["Y"]
        phi = entry["phi_parameter"]
        phi_col = n_gb + phi_to_idx[phi]
        for term in entry["result"]:
            z = term["Z"]
            row = xyz_to_row[(x, y, z)]
            M[row, phi_col] -= float(Fraction(term["coeff"]))

    rank = np.linalg.matrix_rank(M, tol=1e-10)
    U, S, Vh = np.linalg.svd(M, full_matrices=True)
    tol = 1e-10
    null_dim = np.sum(S < tol) + max(0, Vh.shape[0] - len(S))

    gb_constraints = []
    for i in range(n_rows):
        row = M[i]
        gb_part = row[:n_gb]
        phi_part = row[n_gb:]
        if np.all(np.abs(phi_part) < 1e-10) and np.any(np.abs(gb_part) > 1e-10):
            nonzero = [(gb_params[j], gb_part[j]) for j in range(n_gb) if abs(gb_part[j]) > 1e-10]
            gb_constraints.append(nonzero)

    return {
        "matrix_shape": M.shape,
        "rank": int(rank),
        "null_space_dim": null_dim,
        "gb_constraints_count": len(gb_constraints),
        "gb_constraints": gb_constraints[:20],
        "n_gb": n_gb,
        "n_phi": n_phi,
    }


def find_gb_triviality_space(n):
    """Find the subspace of gb parameter space where gamma is a coboundary.

    Method: gamma = M_gamma * gb must lie in col(M_cob).
    Condition: P_perp * M_gamma * gb = 0 where P_perp projects
    onto the orthogonal complement of col(M_cob).
    """
    gamma_data = load_json(os.path.join(DATA_DIR, f"C_{n}_gamma.json"))
    cob_data = load_json(os.path.join(DATA_DIR, f"C_{n}_coboundary.json"))
    structure = load_json(os.path.join(DATA_DIR, f"C_{n}_structure.json"))

    gb_params = [p["label"] for p in gamma_data["gb_matrix"]["parameters"]]
    gb_to_col = {p: i for i, p in enumerate(gb_params)}

    phi_params = set()
    for entry in cob_data["coboundary_coefficients"]:
        phi_params.add(entry["phi_parameter"])
    phi_params = sorted(phi_params)
    phi_to_col = {p: i for i, p in enumerate(phi_params)}

    all_xyz = set()
    for entry in gamma_data["gamma_coefficients"]:
        for term in entry["result"]:
            all_xyz.add((entry["X"], entry["Y"], term["Z"]))
    for entry in cob_data["coboundary_coefficients"]:
        for term in entry["result"]:
            all_xyz.add((entry["X"], entry["Y"], term["Z"]))
    xyz_list = sorted(all_xyz)
    xyz_to_row = {t: i for i, t in enumerate(xyz_list)}

    n_rows = len(xyz_list)
    n_gb = len(gb_params)
    n_phi = len(phi_params)

    M_gamma = np.zeros((n_rows, n_gb), dtype=np.float64)
    for entry in gamma_data["gamma_coefficients"]:
        x, y = entry["X"], entry["Y"]
        gb = entry["gb_parameter"]
        gb_col = gb_to_col[gb]
        for term in entry["result"]:
            z = term["Z"]
            row = xyz_to_row[(x, y, z)]
            M_gamma[row, gb_col] += float(Fraction(term["coeff"]))

    M_cob = np.zeros((n_rows, n_phi), dtype=np.float64)
    for entry in cob_data["coboundary_coefficients"]:
        x, y = entry["X"], entry["Y"]
        phi = entry["phi_parameter"]
        phi_col = phi_to_col[phi]
        for term in entry["result"]:
            z = term["Z"]
            row = xyz_to_row[(x, y, z)]
            M_cob[row, phi_col] += float(Fraction(term["coeff"]))

    U, S, Vh = np.linalg.svd(M_cob, full_matrices=True)
    tol = 1e-10
    r = np.sum(S > tol)
    U_perp = U[:, r:]

    C = U_perp.T @ M_gamma

    gb_constraints_rank = np.linalg.matrix_rank(C, tol=tol)

    _, S_c, Vh_c = np.linalg.svd(C, full_matrices=True)
    trivial_gb_dim = n_gb - np.sum(S_c > tol)

    trivial_gb_basis = []
    if trivial_gb_dim > 0:
        null_indices = np.where(S_c < tol)[0]
        if len(null_indices) > 0:
            start = min(len(S_c), Vh_c.shape[0])
            for idx in range(start, Vh_c.shape[0]):
                vec = Vh_c[idx]
                trivial_gb_basis.append(vec)
            for idx in null_indices:
                if idx < Vh_c.shape[0]:
                    vec = Vh_c[idx]
                    trivial_gb_basis.append(vec)

    return {
        "n_gb": n_gb,
        "n_phi": n_phi,
        "cob_rank": r,
        "constraint_matrix_shape": C.shape,
        "constraint_rank": gb_constraints_rank,
        "trivial_gb_dim": trivial_gb_dim,
        "trivial_gb_basis": trivial_gb_basis,
        "gb_params": gb_params,
    }


def main():
    print("=" * 70)
    print("TRIVIALITY CONDITION SEARCH FOR C(n+1)")
    print("=" * 70)

    for n in [1, 2, 3]:
        print(f"\n{'='*70}")
        print(f"C({n+1}) = osp(2|{2*n}), n={n}")
        print(f"{'='*70}")

        print("\n--- Profile analysis ---")
        results = analyze_triviality_all_profiles(n)
        for name, res in sorted(results.items()):
            if not name.startswith("single_"):
                trivial_str = "TRIVIAL" if res["is_trivial"] else "NON-TRIVIAL"
                print(f"  {name}: {trivial_str} (residual={res['residual_norm']:.2e})")

        single_results = {k: v for k, v in results.items() if k.startswith("single_")}
        trivial_singles = [k for k, v in single_results.items() if v["is_trivial"]]
        nontrivial_singles = [k for k, v in single_results.items() if not v["is_trivial"]]
        print(f"  Single gb profiles: {len(trivial_singles)} trivial, {len(nontrivial_singles)} non-trivial")

        print("\n--- General triviality conditions ---")
        conditions = find_triviality_conditions(n)
        print(f"  Joint matrix (gb+phi): {conditions['matrix_shape']}")
        print(f"  Rank: {conditions['rank']}")
        print(f"  Null space dimension: {conditions['null_space_dim']}")

        print("\n--- gb triviality subspace ---")
        gb_info = find_gb_triviality_space(n)
        print(f"  Coboundary matrix rank: {gb_info['cob_rank']} / {gb_info['n_phi']}")
        print(f"  Constraint matrix on gb: {gb_info['constraint_matrix_shape']}")
        print(f"  Constraint rank: {gb_info['constraint_rank']} / {gb_info['n_gb']}")
        print(f"  Trivial gb subspace dimension: {gb_info['trivial_gb_dim']} / {gb_info['n_gb']}")

        if gb_info['trivial_gb_dim'] == 0:
            print("  => Only gb=0 gives a trivial (coboundary) deformation")
            print("  => ALL non-zero deformations of C(%d) are NON-TRIVIAL" % (n+1))
        elif gb_info['trivial_gb_dim'] == gb_info['n_gb']:
            print("  => ALL deformations are trivial (coboundaries)")
        else:
            print(f"  => {gb_info['trivial_gb_dim']}-dimensional subspace of gb gives trivial deformations")
            if gb_info['trivial_gb_basis']:
                print("  Basis vectors of trivial gb subspace:")
                for i, vec in enumerate(gb_info['trivial_gb_basis']):
                    components = []
                    for j, v in enumerate(vec):
                        if abs(v) > 1e-10:
                            components.append(f"{v:.4f}*{gb_info['gb_params'][j]}")
                    print(f"    v{i}: {' + '.join(components)}")

    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE")


if __name__ == "__main__":
    main()
