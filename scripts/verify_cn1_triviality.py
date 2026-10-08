#!/usr/bin/env python3
"""Verify triviality of gb-deformations of C(n+1) = osp(2|2n).

Model (see docs/issues/mathematical_proof.md, Section 2):
  V = C^{2n|2}. Even basis e_0..e_{2n-1}: bosonic modes b_j^s,
  index k = j-1 (s=+) or k = n+j-1 (s=-). Odd basis e_{2n}, e_{2n+1}:
  fermionic modes a_1^+, a_1^- (sigma = 0, 1).
  Undeformed super-skew form B = diag(Omega, I_2), Omega symplectic (sp(2n)),
  I_2 symmetric (so(2)). osp(B) = {X : X^T B + D_{p(X)} B X = 0}, D_q = diag((-1)^{q p_i}).
  Deformation: B_kappa = B + kappa*G, G the mixed block built from gb[sigma][k].
  Coboundary of the form: F.B := F^T B + D_1 B F for odd F.
  Triviality: G = F.B for some odd F (checked as an exact linear system in F).

Outputs: artifacts/cn1_triviality.json
"""
import json
import random
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "artifacts" / "cn1_triviality.json"


def basis_parity(n):
    return [0] * (2 * n) + [1] * 2


def D(par, q):
    return sp.diag(*[(-1) ** (q * p) for p in par])


def undeformed_form(n):
    N = 2 * n + 2
    B = sp.zeros(N, N)
    for j in range(n):
        B[j, n + j] = 1
        B[n + j, j] = -1
    B[2 * n, 2 * n] = 1
    B[2 * n + 1, 2 * n + 1] = 1
    return B


def mixed_form(n, gb):
    N = 2 * n + 2
    G = sp.zeros(N, N)
    for sigma in range(2):
        for k in range(2 * n):
            G[k, 2 * n + sigma] = gb[sigma][k]
            G[2 * n + sigma, k] = -gb[sigma][k]
    return G


def is_super_skew(M, par):
    N = M.shape[0]
    return all(
        sp.expand(M[i, j] + (-1) ** (par[i] * par[j]) * M[j, i]) == 0
        for i in range(N)
        for j in range(N)
    )


def action(X, B, par, q):
    """Infinitesimal action of a homogeneous matrix X (parity q) on a form B."""
    return X.T * B + D(par, q) * B * X


def homog_matrix(par, q, name):
    N = len(par)
    M = sp.zeros(N, N)
    syms = []
    for i in range(N):
        for k in range(N):
            if par[k] == (par[i] + q) % 2:
                s = sp.Symbol(f"{name}_{k}_{i}")
                M[k, i] = s
                syms.append(s)
    return M, syms


def osp_basis(B, par, q):
    M, syms = homog_matrix(par, q, "x")
    eqs = [e for e in action(M, B, par, q) if sp.expand(e) != 0]
    if not eqs:
        A = sp.zeros(0, len(syms))
    else:
        A, _ = sp.linear_eq_to_matrix(eqs, syms)
    return [M.subs(dict(zip(syms, v))) for v in A.nullspace()]


def first_order_residuals(F, B, G, par, basis):
    """For X in osp(B) (parity q), Z = [F,X]. Return which sign s makes
    action(Z,B) + s*action(X,G) vanish for all X in basis."""
    results = {}
    for s in (+1, -1):
        ok = True
        for X, q in basis:
            Z = F * X - (-1) ** q * X * F
            R = action(Z, B, par, (q + 1) % 2) + s * action(X, G, par, q)
            if any(sp.expand(e) != 0 for e in R):
                ok = False
                break
        results[s] = ok
    return results


def verify(n):
    par = basis_parity(n)
    N = len(par)
    B = undeformed_form(n)
    assert is_super_skew(B, par), "undeformed form not super-skew"

    gb_syms = [[sp.Symbol(f"gb_{s}_{k}") for k in range(2 * n)] for s in range(2)]
    flat_gb = [x for row in gb_syms for x in row]
    G = mixed_form(n, gb_syms)
    assert is_super_skew(G, par), "mixed deformation not super-skew"

    even = osp_basis(B, par, 0)
    odd = osp_basis(B, par, 1)
    dims = {
        "osp_even": len(even),
        "osp_odd": len(odd),
        "osp_total": len(even) + len(odd),
        "expected_even": 2 * n * n + n + 1,
        "expected_odd": 4 * n,
        "expected_total": 2 * n * n + 5 * n + 1,
    }
    assert dims["osp_even"] == dims["expected_even"]
    assert dims["osp_odd"] == dims["expected_odd"]

    # Trivialization system: F.B = G, unknowns = entries of odd F.
    F, fsyms = homog_matrix(par, 1, "f")
    Phi = action(F, B, par, 1)
    nonmixed_identically_zero = all(
        sp.expand(Phi[i, j]) == 0 for i in range(N) for j in range(N) if par[i] == par[j]
    )
    eqs = [sp.expand(Phi[i, j] - G[i, j]) for i in range(N) for j in range(N)]
    eqs = [e for e in eqs if e != 0]
    A, b = sp.linear_eq_to_matrix(eqs, fsyms)  # A f = b(gb)
    rank_A = A.rank()

    # Exact obstruction: y^T A = 0  =>  y^T b(gb) = 0 is a condition on gb.
    constraints = []
    for y in A.T.nullspace():
        c = sp.expand((y.T * b)[0, 0])
        if c != 0:
            constraints.append(c)
    constraint_matrix = sp.Matrix([[sp.diff(c, g) for g in flat_gb] for c in constraints]) if constraints else sp.zeros(0, len(flat_gb))
    constraint_rank = constraint_matrix.rank() if constraints else 0

    sol, params = A.gauss_jordan_solve(b)
    F_sol = F.subs(dict(zip(fsyms, sol.subs({p: 0 for p in params}))))
    F_sol = F_sol.applyfunc(sp.expand)
    particular_ok = all(sp.expand(e) == 0 for e in (action(F_sol, B, par, 1) - G))

    # Closed-form trivializer: F(b_k) = sum_sigma gb[sigma][k] a^sigma, F(a) = 0.
    F_closed = sp.zeros(N, N)
    for sigma in range(2):
        for k in range(2 * n):
            F_closed[2 * n + sigma, k] = gb_syms[sigma][k]
    closed_ok = all(sp.expand(e) == 0 for e in (action(F_closed, B, par, 1) - G))

    basis = [(X, 0) for X in even] + [(X, 1) for X in odd]
    fo = first_order_residuals(F_sol, B, G, par, basis)

    # Numerical spot checks with random integer gb.
    rng = random.Random(1000 + n)
    random_checks = []
    for trial in range(3):
        vals = {g: rng.randint(-5, 5) for g in flat_gb}
        Gn = G.subs(vals)
        Fn = F_sol.subs(vals)
        ok_form = all(sp.expand(e) == 0 for e in (action(Fn, B, par, 1) - Gn))
        fo_n = first_order_residuals(Fn, B, Gn, par, [(X, q) for X, q in basis])
        random_checks.append(
            {
                "gb": {f"gb_{s}_{k}": int(vals[gb_syms[s][k]]) for s in range(2) for k in range(2 * n)},
                "F_dot_B_equals_G": ok_form,
                "first_order_sign_plus_ok": fo_n[+1],
                "first_order_sign_minus_ok": fo_n[-1],
            }
        )

    nonzero_F = {str(k): str(v) for k, v in zip(fsyms, sol.subs({p: 0 for p in params})) if v != 0}

    return {
        "n": n,
        "parity": par,
        "undeformed_form_B": [[int(B[i, j]) for j in range(N)] for i in range(N)],
        "dimensions": dims,
        "nonmixed_part_of_F_dot_B_identically_zero": nonmixed_identically_zero,
        "linear_system": {
            "unknowns_odd_F": len(fsyms),
            "rank_A": int(rank_A),
            "free_parameters_in_F": len(fsyms) - int(rank_A),
            "expected_free_parameters_4n": 4 * n,
            "obstruction_constraints_on_gb": [str(c) for c in constraints],
            "obstruction_rank": int(constraint_rank),
        },
        "triviality": {
            "gb_space_dimension": 4 * n,
            "trivial_locus_dimension": 4 * n - int(constraint_rank),
            "all_gb_trivial": constraint_rank == 0,
            "particular_solution_verified_symbolically": particular_ok,
            "particular_solution_nonzero_entries": nonzero_F,
            "closed_form_F_b_k_to_sum_sigma_gb_a_sigma_verified": closed_ok,
        },
        "first_order_invariance_check": {
            "sign_plus_all_X_ok": fo[+1],
            "sign_minus_all_X_ok": fo[-1],
            "number_of_X_checked": len(basis),
        },
        "random_numeric_checks": random_checks,
    }


def main():
    artifact = {
        "description": "Triviality of gb (fermion-boson mixed) form deformations of osp(2|2n) = C(n+1)",
        "conventions": {
            "gb_index": "gb[sigma][k]; sigma=0 <-> a_1^+, sigma=1 <-> a_1^-; k=j-1 <-> b_j^+, k=n+j-1 <-> b_j^-",
            "form": "super-skew: B(x,y) = -(-1)^{p(x)p(y)} B(y,x); even block symplectic, odd block symmetric",
            "osp_condition": "X^T B + D_{p(X)} B X = 0, D_q = diag((-1)^{q p_i})",
            "coboundary": "F.B = F^T B + D_1 B F for odd F; G = F.B is the triviality condition",
            "up_to_scalar": "B is even, so cB has no odd part; scalar rescaling cannot affect odd gb",
        },
        "results": {},
    }
    for n in (1, 2, 3):
        artifact["results"][f"n={n}"] = verify(n)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2) + "\n")
    for key, r in artifact["results"].items():
        print(
            key,
            "dims", r["dimensions"]["osp_total"], "/", r["dimensions"]["expected_total"],
            "| all gb trivial:", r["triviality"]["all_gb_trivial"],
            "| particular verified:", r["triviality"]["particular_solution_verified_symbolically"],
            "| first-order +/-:", r["first_order_invariance_check"]["sign_plus_all_X_ok"],
            r["first_order_invariance_check"]["sign_minus_all_X_ok"],
        )
    print("wrote", OUT)


if __name__ == "__main__":
    main()
