"""
Driver: triviality analysis of the inhomogeneous (gb) deformation of
C(n+1) = osp(2|2n) for n = 1, 2, 3.

For each n it
  1. builds the oscillator realisation inside U(A_gb) and extracts
       - the undeformed structure constants  C^c_ab
       - the kappa-part  gamma_gb(Z_a, Z_b) = sum_c G^c_ab(gb) Z_c + G0_ab(gb) * 1
  2. checks the super-Jacobi identity for the undeformed bracket and the
     2-cocycle identity for gamma (super-Jacobi on L = g (+) kappa g, random gb)
  3. verifies *symbolically* (exact, all gb simultaneously) that
       gamma_gb = delta f_gb         with the explicit odd map f_gb (see cn1.explicit_f)
     both for the g-part and for the scalar part
  4. independent linear algebra (no knowledge of f_gb used):
       - rank of  gb -> gamma_gb  (injectivity of the deformation)
       - rank / kernel of delta on odd 1-cochains  g -> g
       - image test  gamma_gb  in  Im(delta)   via rank([M | Gamma]) == rank(M)
       - rank of  gb -> scalar part of gamma  (obstruction for the strict reading)
  5. writes a JSON artifact  artifacts/C{n+1}_osp(2|2n).json
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from cn1 import CN1, coef_to_str  # noqa: E402
from osc_algebra import ONE  # noqa: E402

P = 2_147_483_647  # prime for modular rank computations


def frac_mod(q: Fraction) -> int:
    return (q.numerator % P) * pow(q.denominator % P, P - 2, P) % P


def rank_mod_p(rows: list[dict]) -> int:
    """Rank mod P of a sparse matrix given as list of {col: int} rows."""
    pivots: dict[int, dict] = {}
    rank = 0
    for row in rows:
        r = {c: v % P for c, v in row.items() if v % P}
        while r:
            c = min(r)
            if c in pivots:
                prow = pivots[c]
                f = r[c]
                for cc, vv in prow.items():
                    nv = (r.get(cc, 0) - f * vv) % P
                    if nv:
                        r[cc] = nv
                    else:
                        r.pop(cc, None)
            else:
                inv = pow(r[c], P - 2, P)
                r = {cc: vv * inv % P for cc, vv in r.items()}
                pivots[c] = r
                rank += 1
                break
    return rank


def jacobi_check(g: CN1, trials: int = 3) -> dict:
    """Super-Jacobi for the undeformed bracket (exact) and for the deformed
    bracket on L = g (+) kappa g with random rational gb (exact Fractions)."""
    import numpy as np

    d = g.dim
    par = g.parity
    # undeformed structure constants as dense float array (entries are small rationals)
    C = np.zeros((d, d, d))
    for a in range(d):
        for b in range(d):
            for c, q in g.C[a][b].items():
                C[a, b, c] = float(q)
    max_res_0 = 0.0
    # Jacobi: [a,[b,c]] = [[a,b],c] + (-1)^{p_a p_b} [b,[a,c]]
    sgn_ab = np.array([[(-1) ** (par[a] * par[b]) for b in range(d)] for a in range(d)], dtype=float)
    lhs = np.einsum("bcx,axy->abcy", C, C)
    rhs1 = np.einsum("abx,xcy->abcy", C, C)
    rhs2 = np.einsum("acx,bxy->abcy", C, C) * sgn_ab[:, :, None, None]
    max_res_0 = float(np.abs(lhs - rhs1 - rhs2).max())

    # deformed bracket on L: basis Z_a (parity p_a) and kappa Z_a (parity p_a+1)
    max_res_L = 0.0
    gbn = 4 * g.n
    for _ in range(trials):
        gbv = [random.randint(-5, 5) for _ in range(gbn)]
        Gm = np.zeros((d, d, d))
        for a in range(d):
            for b in range(d):
                for c, poly in g.G[a][b].items():
                    Gm[a, b, c] = sum(float(q) * gbv[k[0]] for k, q in poly.items())
        D = 2 * d
        T = np.zeros((D, D, D))
        parL = par + [1 - p for p in par]
        T[:d, :d, :d] = C
        T[:d, :d, d:] = Gm
        for a in range(d):
            for b in range(d):
                for c, q in g.C[a][b].items():
                    T[a, d + b, d + c] = (-1) ** par[a] * float(q)   # [Z_a, kappa Z_b] = (-1)^{p_a} kappa [Z_a,Z_b]
                    T[d + a, b, d + c] = float(q)                   # [kappa Z_a, Z_b] = kappa [Z_a,Z_b]
        sgn = np.array([[(-1) ** (parL[a] * parL[b]) for b in range(D)] for a in range(D)], dtype=float)
        lhs = np.einsum("bcx,axy->abcy", T, T)
        rhs1 = np.einsum("abx,xcy->abcy", T, T)
        rhs2 = np.einsum("acx,bxy->abcy", T, T) * sgn[:, :, None, None]
        max_res_L = max(max_res_L, float(np.abs(lhs - rhs1 - rhs2).max()))
    return {"undeformed_jacobi_max_residual": max_res_0,
            "deformed_L_jacobi_max_residual": max_res_L,
            "random_trials": trials}


def change_of_variables_check(g: CN1) -> dict:
    """Inside U(A_gb) define  a~^sig = a^sig + kappa C^sig  with
       C^sig = sum_j ( gb[a^sig,b_j^-] b_j^+ - gb[a^sig,b_j^+] b_j^- ).
    Verify exactly (as polynomials in gb) that a~, b, kappa satisfy the
    *undeformed* relations."""
    from osc_algebra import c_const, c_gb, e_add, e_scale_coef
    A = g.A
    kappa = A.word(0)
    at = {}
    for sig, idx in (("+", 1), ("-", 2)):
        C = {}
        for j in range(1, g.n + 1):
            C = e_add(C, e_scale_coef(A.word(A.bp(j)), c_gb(A.gb_flat(sig, j, "-"), 1)))
            C = e_add(C, e_scale_coef(A.word(A.bm(j)), c_gb(A.gb_flat(sig, j, "+"), -1)))
        at[sig] = e_add(A.word(idx), A.mul(kappa, C))
    one = {(): c_const(1)}
    out = {}
    out["[a~-, a~+] == 1"] = e_add(A.bracket(at["-"], at["+"]), e_scale_coef(one, c_const(-1))) == {}
    out["[a~+, a~+] == 0"] = A.bracket(at["+"], at["+"]) == {}
    out["[a~-, a~-] == 0"] = A.bracket(at["-"], at["-"]) == {}
    ok = True
    for j in range(1, g.n + 1):
        for b in (A.bp(j), A.bm(j)):
            for sig in "+-":
                ok &= A.bracket(A.word(b), at[sig]) == {}
    out["[b_j^s, a~^sig] == 0 for all j,s,sig"] = ok
    out["[kappa, a~^sig] == 0"] = all(A.bracket(kappa, at[sig]) == {} for sig in "+-")
    return out


def analyse(n: int, outdir: str) -> dict:
    t0 = time.time()
    g = CN1(n)
    d, par = g.dim, g.parity
    gbn = 4 * n
    gb_names = g.A.gb_names
    res: dict = {"n": n, "algebra": f"C({n+1}) = osp(2|{2*n})", "dim": d,
                 "dim_even": d - sum(par), "dim_odd": sum(par), "num_gb_parameters": gbn}

    # --- 1. sanity: structure constants close exactly inside g (no scalar part)
    res["undeformed_bracket_has_scalar_part"] = any(g.C0[a][b] != 0 for a in range(d) for b in range(d))
    res.update(jacobi_check(g))

    # --- 2. symbolic verification  gamma = delta f  (exact in Q[gb])
    phi, phi0 = g.explicit_f()
    D, D0 = g.delta(phi, phi0)
    ok_g = all(D[a][b][c] == g.G[a][b].get(c, {}) for a in range(d) for b in range(d) for c in range(d))
    ok_s = all(D0[a][b] == g.G0[a][b] for a in range(d) for b in range(d))
    res["symbolic_identity_gamma_equals_delta_f"] = {"g_part": ok_g, "scalar_part": ok_s}
    # delta of the g-part of f alone (f_bar : g -> g) has zero scalar part
    Dbar, D0bar = g.delta(phi, None)
    res["delta_fbar_scalar_part_is_zero"] = all(not D0bar[a][b] for a in range(d) for b in range(d))
    res["delta_fbar_equals_gamma_g_part"] = all(
        Dbar[a][b][c] == g.G[a][b].get(c, {}) for a in range(d) for b in range(d) for c in range(d))

    # --- 2b. exact check of the change of variables  a~ = a + kappa C  in U(A_gb)
    res["change_of_variables_check"] = change_of_variables_check(g)
    # --- 2c. odd inner derivations ad(W), W in g_1, lie in ker(delta)  (exact)
    inner_ok = True
    for w in range(d):
        if par[w] != 1:
            continue
        phi_w = [[({ONE: g.C[w][j][i]} if i in g.C[w][j] else {}) for j in range(d)] for i in range(d)]
        Dw, _ = g.delta(phi_w, None)
        inner_ok &= all(not Dw[a][b][c] for a in range(d) for b in range(d) for c in range(d))
    res["odd_inner_derivations_in_kernel_of_delta"] = inner_ok

    # --- 3. independent linear algebra ----------------------------------
    # odd 1-cochain unknowns phi_ij with p_i != p_j
    odd_idx = [(i, j) for j in range(d) for i in range(d) if par[i] != par[j]]
    col = {ij: k for k, ij in enumerate(odd_idx)}
    nphi = len(odd_idx)
    # matrix of delta: rows indexed by (a<=b, c); columns phi_ij ; computed from the
    # formula with unit cochains (linear), using exact Fractions
    # Build by linearity: delta(e_ij) where e_ij(Z_j) = Z_i.
    rows_M: dict[tuple, dict] = {}
    for (i, j), k in col.items():
        phi_u = [[{} for _ in range(d)] for _ in range(d)]
        phi_u[i][j] = {ONE: Fraction(1)}
        # only pairs (a,b) with a == j or b == j or C^j_ab != 0 contribute; do it directly
        for a in range(d):
            for b in range(a, d):
                pa, pb = par[a], par[b]
                vec = {}
                if b == j:  # (-1)^{p_a} [Z_a, Z_i]
                    s = -1 if pa else 1
                    for c, q in g.C[a][i].items():
                        vec[c] = vec.get(c, Fraction(0)) + s * q
                if a == j:  # -(-1)^{(p_a+1)p_b} [Z_b, Z_i]
                    s = -(-1 if ((pa + 1) * pb) % 2 else 1)
                    for c, q in g.C[b][i].items():
                        vec[c] = vec.get(c, Fraction(0)) + s * q
                if j in g.C[a][b]:  # - C^j_ab Z_i
                    vec[i] = vec.get(i, Fraction(0)) - g.C[a][b][j]
                for c, q in vec.items():
                    if q != 0:
                        rows_M.setdefault((a, b, c), {})[k] = q
    # Gamma columns: gb_k -> gamma coefficient  (g-part) ; scalar part separately
    rows_G: dict[tuple, dict] = {}
    rows_G0: dict[tuple, dict] = {}
    for a in range(d):
        for b in range(a, d):
            for c, poly in g.G[a][b].items():
                for key, q in poly.items():
                    rows_G.setdefault((a, b, c), {})[key[0]] = q
            for key, q in g.G0[a][b].items():
                rows_G0.setdefault((a, b), {})[key[0]] = q
    all_rows = set(rows_M) | set(rows_G)
    M_rows = [{k: frac_mod(v) for k, v in rows_M.get(r, {}).items()} for r in all_rows]
    MG_rows = [{**{k: frac_mod(v) for k, v in rows_M.get(r, {}).items()},
                **{nphi + k: frac_mod(v) for k, v in rows_G.get(r, {}).items()}} for r in all_rows]
    G_rows = [{k: frac_mod(v) for k, v in rows_G.get(r, {}).items()} for r in all_rows]
    G0_rows = [{k: frac_mod(v) for k, v in rows_G0[r].items()} for r in rows_G0]
    rk_M = rank_mod_p(M_rows)
    rk_MG = rank_mod_p(MG_rows)
    rk_G = rank_mod_p(G_rows)
    rk_G0 = rank_mod_p(G0_rows)
    # strict reading: [M | G] where G includes scalar rows which M cannot reach
    rows_strict = []
    for r in all_rows:
        rows_strict.append({**{k: frac_mod(v) for k, v in rows_M.get(r, {}).items()},
                            **{nphi + k: frac_mod(v) for k, v in rows_G.get(r, {}).items()}})
    for r in rows_G0:
        rows_strict.append({nphi + k: frac_mod(v) for k, v in rows_G0[r].items()})
    rk_strict = rank_mod_p(rows_strict)
    res["linear_algebra_mod_p"] = {
        "prime": P,
        "num_odd_phi_unknowns": nphi,
        "rank_delta_on_odd_1cochains": rk_M,
        "dim_ker_delta_odd": nphi - rk_M,
        "dim_odd_inner_derivations": sum(par),
        "dim_H1_odd_adjoint_upper_bound": nphi - rk_M - sum(par),
        "rank_gb_to_gamma_g_part": rk_G,
        "rank_gb_to_gamma_scalar_part": rk_G0,
        "rank_[delta | gamma]_g_part": rk_MG,
        "gamma_g_part_in_image_of_delta_for_all_gb": rk_MG == rk_M,
        "dim_trivial_gb_subspace_modulo_scalars": gbn - (rk_MG - rk_M),
        "rank_[delta | gamma]_strict_with_scalars": rk_strict,
        "dim_trivial_gb_subspace_strict": gbn - (rk_strict - rk_M),
    }

    # --- 4. artifact ------------------------------------------------------
    def poly_json(poly):
        return {gb_names[k[0]] if k else "1": str(v) for k, v in poly.items()}

    art = {
        "algebra": res["algebra"], "n": n, "dim": d,
        "basis": g.labels, "parity": par, "gb_parameters": gb_names,
        "conventions": {
            "bracket": "[X,Y] = XY - (-1)^{p(X)p(Y)} YX in U(A_gb), K = 1",
            "deformation": "[b_j^s, a^sigma] = - gb[a^sigma,b_j^s] * kappa ; kappa odd, central, kappa^2 = 0",
            "decomposition": "[Z_a, Z_b] = sum_c C[a][b][c] Z_c  +  kappa * ( sum_c gamma[a][b][c] Z_c + gamma_scalar[a][b] * 1 )",
            "coboundary": "(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
            "f": "f(Z_j) = sum_i phi[i][j] Z_i + phi_scalar[j] * 1 ; phi, phi_scalar are linear forms in gb",
            "indexing": "0-based indices into 'basis'",
        },
        "structure_constants": [[a, b, c, str(q)] for a in range(d) for b in range(d) for c, q in g.C[a][b].items()],
        "gamma": [[a, b, c, poly_json(p)] for a in range(d) for b in range(d) for c, p in g.G[a][b].items()],
        "gamma_scalar": [[a, b, poly_json(g.G0[a][b])] for a in range(d) for b in range(d) if g.G0[a][b]],
        "explicit_f_phi": [[i, j, poly_json(phi[i][j])] for j in range(d) for i in range(d) if phi[i][j]],
        "explicit_f_phi_scalar": [[j, poly_json(phi0[j])] for j in range(d) if phi0[j]],
        "verification": res,
    }
    os.makedirs(outdir, exist_ok=True)
    fn = os.path.join(outdir, f"C{n+1}_osp2_{2*n}.json")
    with open(fn, "w") as fh:
        json.dump(art, fh, indent=1)
    res["artifact"] = os.path.relpath(fn, os.path.dirname(outdir))
    res["seconds"] = round(time.time() - t0, 2)
    return res, g, phi, phi0


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(os.path.dirname(here), "artifacts")
    random.seed(20261008)
    summary = {}
    for n in (1, 2, 3):
        res, g, phi, phi0 = analyse(n, outdir)
        summary[f"n={n}"] = res
        print(json.dumps(res, indent=1))
        if n == 1:
            print("explicit f for n=1:")
            for j in range(g.dim):
                terms = [f"{coef_to_str(phi[i][j], g.A.gb_names)} * {g.labels[i]}" for i in range(g.dim) if phi[i][j]]
                if phi0[j]:
                    terms.append(f"{coef_to_str(phi0[j], g.A.gb_names)} * 1")
                print(f"  f({g.labels[j]}) = " + (" + ".join(terms) if terms else "0"))
    with open(os.path.join(outdir, "verification_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
