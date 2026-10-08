"""Triviality analysis for the C(n+1) inhomogeneous deformation (Issue I08).

Setting (docs/math/C_coboundary_definition.md, Section 3):
    gamma(gb) is trivial  <=>  there is an odd linear map f with gamma(gb) = delta f.
Both sides are linear: gamma is linear in gb (Schema 2), delta f is linear in the
phi parameters of f (Schema 4). Scalars are absorbed into f, since
lambda * delta f = delta(lambda f), so "up to scalar" is the same as exact equality.

Writing the equations as  A phi = B gb  (A: coefficients of delta f in phi,
B: coefficients of gamma in gb, one row per (X, Y, Z) with X <= Y), the set of
trivial gb is
    T = { gb : B gb lies in the column space of A } = proj_gb( null([A | -B]) ).

Usage: python3 src/C_triviality.py [--exact-rank-max N]
  Exact (sympy) computation is used for n <= exact-rank-max (default 1); the
  numerical (SVD) computation is used for larger n.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import sympy

sys.path.insert(0, str(Path(__file__).resolve().parent))

from C_evaluate import profiles  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_equations(n, data_dir=DATA_DIR):
    g2 = json.loads((Path(data_dir) / f"C_{n}_gamma.json").read_text())["inhomogeneous_deformation"]
    c4 = json.loads((Path(data_dir) / f"C_{n}_coboundary.json").read_text())
    gb_syms = [sympy.Symbol(s) for s in g2["gb_parameters"]]
    phi_syms = [sympy.Symbol(p["symbol"]) for p in c4["map"]["parameters"]]
    gamma = {(e["X"], e["Y"], e["Z"]): sympy.sympify(e["coeff"]) for e in g2["gamma"]}
    delta = {(e["X"], e["Y"], e["Z"]): sympy.sympify(e["coeff"]) for e in c4["coboundary"]["entries"]}
    keys = sorted(set(gamma) | set(delta))
    phi_idx = {p: c for c, p in enumerate(phi_syms)}
    gb_idx = {g: c for c, g in enumerate(gb_syms)}
    A = np.zeros((len(keys), len(phi_syms)))
    B = np.zeros((len(keys), len(gb_syms)))
    for r, k in enumerate(keys):
        if k in delta:
            for sym, c in delta[k].as_coefficients_dict().items():
                if sym in phi_idx:
                    A[r, phi_idx[sym]] = float(c)
        if k in gamma:
            for sym, c in gamma[k].as_coefficients_dict().items():
                if sym in gb_idx:
                    B[r, gb_idx[sym]] = float(c)
    return keys, gb_syms, phi_syms, A, B, gamma, delta


def trivial_subspace_numeric(A, B, tol=1e-9):
    """Basis (rows) of T = {gb : B gb in col(A)} via SVD."""
    if A.shape[1] == 0:
        return np.eye(B.shape[1])
    U, S, _ = np.linalg.svd(A, full_matrices=False)
    r = int(np.sum(S > tol * max(1.0, S.max() if S.size else 1.0)))
    Q = U[:, :r]
    C = B - Q @ (Q.T @ B)  # projection onto the complement of col(A)
    _, SC, Vt = np.linalg.svd(C, full_matrices=True)
    rc = int(np.sum(SC > tol * max(1.0, SC.max() if SC.size else 1.0)))
    return Vt[rc:]


def trivial_subspace_exact(keys, gb_syms, phi_syms, gamma, delta):
    """Exact basis of T for small n (sympy)."""
    A = sympy.Matrix([[delta[k].coeff(p) if k in delta else 0 for p in phi_syms] for k in keys])
    B = sympy.Matrix([[gamma[k].coeff(g) if k in gamma else 0 for g in gb_syms] for k in keys])
    M = A.row_join(-B)
    null = M.nullspace()
    gb_parts = sympy.Matrix([list(v[len(phi_syms):]) for v in null]) if null else sympy.zeros(0, len(gb_syms))
    if gb_parts.rows == 0:
        return [], sympy.zeros(0, len(gb_syms))
    rref, _ = gb_parts.rref()
    basis = [list(rref.row(i)) for i in range(rref.rows) if any(x != 0 for x in rref.row(i))]
    return basis, gb_parts


def profile_test(n, keys, gb_syms, phi_syms, A, B, data_dir=DATA_DIR):
    """Test each named profile: is gamma(profile) = delta f for some phi?"""
    out = {}
    names = [str(g) for g in gb_syms]
    for pname, values in profiles(n).items():
        g = np.array([float(values[name]) for name in names])
        rhs = B @ g
        phi, *_ = np.linalg.lstsq(A, rhs, rcond=None)
        resid = A @ phi - rhs
        bad = np.where(np.abs(resid) > 1e-9)[0]
        out[pname] = {
            "trivial": bool(bad.size == 0),
            "residual_norm": float(np.linalg.norm(resid)),
            "unmatched_rows": [list(keys[i]) for i in bad[:20]],
            "unmatched_count": int(bad.size),
        }
    return out


def k_row_constraints(keys, gb_syms, B):
    """Rows whose Z is K: gamma's central component. delta f never produces K."""
    rows = [i for i, k in enumerate(keys) if k[2] == "K"]
    return {
        "count": len(rows),
        "all_zero_gb_forced": bool(rows and np.linalg.matrix_rank(B[rows]) == len(gb_syms)),
        "rank_of_K_constraints": int(np.linalg.matrix_rank(B[rows])) if rows else 0,
    }


def analyse(n, exact=False, data_dir=DATA_DIR):
    keys, gb_syms, phi_syms, A, B, gamma, delta = load_equations(n, data_dir)
    result = {
        "n": n,
        "gb_parameters": len(gb_syms),
        "phi_parameters": len(phi_syms),
        "equations": len(keys),
        "rank_A": int(np.linalg.matrix_rank(A)),
        "k_row_constraints": k_row_constraints(keys, gb_syms, B),
        "profiles": profile_test(n, keys, gb_syms, phi_syms, A, B, data_dir),
    }
    if exact:
        basis, _ = trivial_subspace_exact(keys, gb_syms, phi_syms, gamma, delta)
        result["trivial_subspace_dim"] = len(basis)
        result["trivial_subspace_basis_exact"] = [[str(x) for x in row] for row in basis]
        result["method"] = "exact (sympy nullspace)"
    else:
        Tn = trivial_subspace_numeric(A, B)
        result["trivial_subspace_dim"] = int(Tn.shape[0])
        result["method"] = "numerical (SVD, tol 1e-9)"
    result["gb_coordinates"] = [str(g) for g in gb_syms]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--exact-rank-max", type=int, default=1)
    args = parser.parse_args(argv)
    for n in (1, 2, 3):
        res = analyse(n, exact=(n <= args.exact_rank_max))
        path = DATA_DIR / f"C_{n}_triviality.json"
        path.write_text(json.dumps(res, indent=2) + "\n")
        print(f"n={n}: equations={res['equations']} rank_A={res['rank_A']} "
              f"trivial_dim={res['trivial_subspace_dim']} method={res['method']}")
        print("   K-constraints:", res["k_row_constraints"])
        for name, p in res["profiles"].items():
            print(f"   {name}: trivial={p['trivial']} residual={p['residual_norm']:.3g} "
                  f"unmatched={p['unmatched_count']}")


if __name__ == "__main__":
    main()
