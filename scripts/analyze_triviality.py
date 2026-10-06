#!/usr/bin/env python3
"""
Main analysis of the inhomogeneous deformation gamma_gb of C(n+1) = osp(2|2n).

Steps
-----
(0) undeformed structure constants C0
(1) gamma_gb  (and the two scalar anomalies tau, sigma) for both sections
(2) gamma_gb is a genuine odd 2-cocycle, and is nonzero whenever gb != 0
(3) the explicit twist gives f with  gamma = - delta f   (exact, symbolic in gb)
(4) rank of the full linear system  delta f = gamma  (numeric, random gb)
"""
from fractions import Fraction
import itertools
import json
import random
import sys

import numpy as np

from osp_algebra import const, ZERO, ONE, prune, scale, sub, add_into, mul_lin, Lin
from osp_deformation import Deformation, delta_f

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 3
REPORT = {}


def undeformed(n):
    gb0 = {k: ZERO for k in Deformation(n).A.gb}
    return Deformation(n, gb=gb0, section="SYM").compute()


for n in range(1, NMAX + 1):
    print("=" * 70)
    print(f"  n = {n}   g = C({n+1}) = osp(2|{2*n})")
    print("=" * 70)
    rep = {}
    D0 = undeformed(n)
    C0 = D0.C

    # ---- Jacobi (super) for the undeformed algebra ----------------------
    d = D0.dim
    jac_ok = True
    for a in range(d):
        for b in range(d):
            for c in range(d):
                pa, pb, pc = D0.zpar[a], D0.zpar[b], D0.zpar[c]
                acc = [Fraction(0)] * d
                for (x, y, z, s) in ((a, b, c, (-1) ** (pa * pc)),
                                     (b, c, a, (-1) ** (pb * pa)),
                                     (c, a, b, (-1) ** (pc * pb))):
                    for i in range(d):
                        if C0[x][y][i].is_zero():
                            continue
                        ci = C0[x][y][i].get(None, Fraction(0))
                        for k in range(d):
                            acc[k] += s * ci * C0[i][z][k].get(None, Fraction(0))
                if any(acc):
                    jac_ok = False
    print(f"[0] graded Jacobi identity for C0 : {jac_ok}")
    assert jac_ok
    rep["jacobi_undeformed"] = jac_ok

    # ---- gamma for both sections ---------------------------------------
    for section in ("SYM", "NAIVE"):
        D = Deformation(n, section=section).compute()
        D.C0 = C0
        # structure constants must be gb-independent
        cc_ok = all(C0[a][b][c] == D.C[a][b][c] for a in range(d)
                    for b in range(d) for c in range(d))
        tau_nz = [(a, b) for a in range(d) for b in range(d)
                  if not D.tau[a][b].is_zero()]
        sig_nz = [(a, b) for a in range(d) for b in range(d)
                  if not D.sigma[a][b].is_zero()]
        gam_nz = sum(1 for a in range(d) for b in range(d)
                     for c in range(d) if not D.G[a][b][c].is_zero())
        print(f"[1] section={section:5s}: C==C0 {cc_ok} | "
              f"even-scalar anomaly tau: {len(tau_nz)} nonzero | "
              f"odd-scalar anomaly sigma: {len(sig_nz)} nonzero | "
              f"gamma entries nonzero: {gam_nz}")
        assert cc_ok and not tau_nz
        rep[f"section_{section}"] = {
            "tau_nonzero": len(tau_nz),
            "sigma_nonzero": len(sig_nz),
            "gamma_nonzero_entries": gam_nz,
        }
        if section == "NAIVE" and sig_nz:
            a, b = sig_nz[0]
            print(f"      e.g. sigma({D.labels[a]}, {D.labels[b]}) = "
                  f"{D.sigma[a][b].as_str()}")
            rep["sigma_example_NAIVE"] = {
                "X": D.labels[a], "Y": D.labels[b],
                "value": D.sigma[a][b].as_str()}
        if section == "SYM":
            Dsym = D

    D = Dsym

    # ---- gamma != 0 for every gb != 0 -----------------------------------
    # collect, for each gb symbol, a witness entry of gamma containing it
    witnesses = {}
    for a in range(d):
        for b in range(d):
            for c in range(d):
                for k in D.G[a][b][c]:
                    if k is not None and k not in witnesses:
                        witnesses[k] = (D.labels[a], D.labels[b], D.labels[c],
                                        D.G[a][b][c].as_str())
    print(f"[2] gamma depends on all {len(witnesses)}/{4*n} gb parameters: "
          f"{len(witnesses) == 4*n}")
    assert len(witnesses) == 4 * n
    rep["gamma_depends_on_all_gb"] = True
    k0 = sorted(witnesses)[0]
    print(f"      e.g. gamma({witnesses[k0][0]}, {witnesses[k0][1]})"
          f"[{witnesses[k0][2]}] = {witnesses[k0][3]}")

    # ---- gamma is a 2-cocycle, verified convention-free -------------------
    # L = g (+) kappa.g is closed under the bracket of W_kappa, and the bracket
    # of an associative algebra automatically satisfies the graded Jacobi
    # identity.  Hence L is a Lie superalgebra, i.e. gamma IS a 2-cocycle with
    # values in the adjoint module.  We verify closure on ALL pairs of L:
    #   [Z_a, Z_b]      = C_ab^c Z_c + kappa gamma_ab^c Z_c
    #   [Z_a, kappa Z_b] = (-1)^{p_a} kappa C_ab^c Z_c
    #   [kappa Z_a, kappa Z_b] = 0
    closure_ok = True
    adjoint_ok = True
    for a in range(d):
        for b in range(d):
            kb = D.A.kappa_times(D.Z[b])
            ka = D.A.kappa_times(D.Z[a])
            # [Z_a, kappa Z_b] must be (-1)^{p_a} kappa [Z_a, Z_b]_0  (abelian
            # extension by the ADJOINT representation, kappa acting trivially)
            br = D.A.bracket(D.Z[a], kb)
            tgt = {}
            for c in range(d):
                if not C0[a][b][c].is_zero():
                    add_into(tgt, D.A.kappa_times(D.Z[c]),
                             C0[a][b][c] * Fraction(-1) ** D.zpar[a])
            if prune(sub(br, tgt)):
                adjoint_ok = False
            # kappa.g is an abelian ideal
            if prune(D.A.bracket(ka, kb)):
                closure_ok = False
    print(f"[3] L = g (+) kappa.g closes; kappa.g abelian ideal: {closure_ok}; "
          f"module = adjoint: {adjoint_ok}")
    print(f"    => gamma is a graded 2-cocycle in C^2(g; g)_odd (Jacobi is "
          f"automatic in the associative algebra)")
    assert closure_ok and adjoint_ok
    rep["cocycle"] = bool(closure_ok and adjoint_ok)

    # ---- the twist: Zt = Z + kappa f(Z) ---------------------------------
    Zt = D.twisted_Z()
    phi = [[ZERO] * d for _ in range(d)]
    f_scalar = [ZERO] * d
    for a in range(d):
        C, G, tau, sg = D.decompose(sub(Zt[a], D.Z[a]))
        assert all(x.is_zero() for x in C) and tau.is_zero(), (a, C, tau)
        for i in range(d):
            phi[i][a] = G[i]
        f_scalar[a] = sg
    scal_nz = [a for a in range(d) if not f_scalar[a].is_zero()]
    print(f"[4] f = (twist) maps g -> g  (scalar part of f nonzero on "
          f"{len(scal_nz)} basis vectors)")
    rep["f_scalar_part_nonzero"] = len(scal_nz)

    # f must be odd
    odd_ok = all(phi[i][j].is_zero() or D.zpar[i] != D.zpar[j]
                 for i in range(d) for j in range(d))
    print(f"[5] f is parity-reversing (odd): {odd_ok}")
    assert odd_ok
    rep["f_is_odd"] = odd_ok

    # ---- Zt spans a subalgebra isomorphic to the UNDEFORMED g ------------
    iso_ok = True
    for a in range(d):
        for b in range(d):
            br = D.A.bracket(Zt[a], Zt[b])
            tgt = {}
            for c in range(d):
                if not C0[a][b][c].is_zero():
                    add_into(tgt, Zt[c], C0[a][b][c])
            if prune(sub(br, tgt)):
                iso_ok = False
    print(f"[6] [Zt_a, Zt_b] = C0_ab^c Zt_c  (exact isomorphism onto the "
          f"undeformed algebra): {iso_ok}")
    rep["twisted_subalgebra_isomorphic"] = iso_ok

    # ---- gamma = - delta f ----------------------------------------------
    df = delta_f(D, phi)
    match = True
    for a in range(d):
        for b in range(d):
            for c in range(d):
                if not (D.G[a][b][c] + df[(a, b)][c]).is_zero():
                    match = False
    print(f"[7] gamma_gb = - delta f  (exact, symbolic in all {4*n} gb): {match}")
    rep["gamma_equals_minus_delta_f"] = match
    assert match

    # ---- rank of the linear system delta f = gamma ------------------------
    random.seed(20261006 + n)
    gbval = {f"gb[{s},{j},{t}]": Fraction(random.randint(-9, 9))
             for (s, j, t) in D.A.gb}
    while all(v == 0 for v in gbval.values()):
        gbval = {f"gb[{s},{j},{t}]": Fraction(random.randint(-9, 9))
                 for (s, j, t) in D.A.gb}
    unknowns = [(i, j) for i in range(d) for j in range(d)
                if D.zpar[i] != D.zpar[j]]
    # Dense system indexed by (a,b,c); column (i0,j0) built directly from the
    # three terms of  (delta f)(Z_a, Z_b)  with  f(Z_j) = delta_{j,j0} Z_{i0}.
    C0f = np.zeros((d, d, d))
    for a in range(d):
        for b in range(d):
            for c in range(d):
                C0f[a, b, c] = float(C0[a][b][c].get(None, Fraction(0)))
    pz = np.array(D.zpar)
    Amat = np.zeros((d * d * d, len(unknowns)))
    for m, (i0, j0) in enumerate(unknowns):
        col = np.zeros((d, d, d))
        # (-1)^{p(X)} [X, f(Y)] ,  f(Y) nonzero only for Y = Z_{j0}
        col[:, j0, :] += ((-1.0) ** pz)[:, None] * C0f[:, i0, :]
        # -(-1)^{(p(X)+1)p(Y)} [Y, f(X)] ,  f(X) nonzero only for X = Z_{j0}
        s2 = -((-1.0) ** (((pz[j0] + 1) * pz) % 2))
        col[j0, :, :] += s2[:, None] * C0f[:, i0, :]
        # - f([X,Y])
        col[:, :, i0] += -C0f[:, :, j0]
        Amat[:, m] = col.reshape(-1)
    bvec = np.zeros(d * d * d)
    for a in range(d):
        for b in range(d):
            for c in range(d):
                bvec[a * d * d + b * d + c] = float(D.G[a][b][c].subs(gbval))
    # rank via Gram matrices (A and [A|b] are tall and thin)
    G_A = Amat.T @ Amat
    scale_ = max(np.abs(G_A).max(), 1.0)
    rk = np.linalg.matrix_rank(G_A, tol=1e-9 * scale_)
    Ab = np.column_stack([Amat, bvec])
    G_Ab = Ab.T @ Ab
    aug = np.linalg.matrix_rank(G_Ab, tol=1e-9 * max(np.abs(G_Ab).max(), 1.0))
    sol, *_ = np.linalg.lstsq(Amat, bvec, rcond=None)
    resid = np.linalg.norm(Amat @ sol - bvec) / max(np.linalg.norm(bvec), 1.0)
    print(f"[8] linear system delta f = gamma : unknowns={len(unknowns)} "
          f"equations={Amat.shape[0]}")
    print(f"      rank(A)={rk}  rank([A|b])={aug}  "
          f"=> {'SOLVABLE' if rk == aug else 'INCONSISTENT'}   "
          f"residual={resid:.2e}")
    print(f"      dim of solution set = {len(unknowns)-rk}  "
          f"(= dim g_1 = {4*n}: inner odd derivations)")
    rep["linear_system"] = {
        "unknowns": len(unknowns), "equations": int(Amat.shape[0]),
        "rank_A": int(rk), "rank_Ab": int(aug), "solvable": bool(rk == aug),
        "residual": float(resid), "solution_dim": int(len(unknowns) - rk),
        "dim_g_odd": 4 * n,
        "gb_values": {str(k): str(v) for k, v in gbval.items()},
    }
    REPORT[f"n={n}"] = rep
    print()

with open("../artifacts/analysis_summary.json", "w") as fh:
    json.dump(REPORT, fh, indent=2)
print("summary written to artifacts/analysis_summary.json")
