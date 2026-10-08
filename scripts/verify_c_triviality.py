#!/usr/bin/env python3
"""Computational verification for triviality of inhomogeneous gb-deformations
of C(n+1) = osp(2|2n).  See docs/issues/mathematical_proof.md for the theory.

Pipeline
1. Oscillator realisation.  Generators: kappa (odd, super-central, kappa^2 = 0),
   a+, a- (odd, {a-, a+} = 1), b_j+, b_j- (even, [b_j-, b_j+] = 1), plus the
   deformed exchange relation  [b_j^s, a^sigma] = -gb_{sigma,j,s} * kappa.
2. Normal ordering in the resulting Weyl-Clifford superalgebra.  kappa is a
   generator with kappa^2 = 0, so the kappa-linear truncation is automatic.
3. g = span of quadratic normal-ordered monomials, taken modulo the central
   constant 1 (dim = 2n^2+5n+1).  mu0 = undeformed bracket; gamma_u = the
   kappa-coefficient of the bracket for the unit parameter gb_u = 1.
4. Checks: super-Jacobi for mu0; linear-kappa super-Jacobi for mu0 + kappa*gamma;
   delta(ad Z) = 0 for odd Z (sign-convention sanity check).
5. Triviality: is gamma_u in im(delta) on odd 1-cochains f?  Linear algebra
   over all parity-reversing f.  Since im(delta) is a vector subspace, the
   "up to scalar" reading gives the same answer as the exact reading.

Output: artifacts/c_triviality_n{n}.json (structured data for reuse).
Usage:  python3 scripts/verify_c_triviality.py 1 2 3
"""
import json
import os
import sys
from functools import lru_cache

import numpy as np

sys.setrecursionlimit(10000)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART_DIR = os.path.join(ROOT, "artifacts")


def oscillator_data(n):
    names = ["kappa", "a+", "a-"]
    for j in range(1, n + 1):
        names += [f"b{j}+", f"b{j}-"]
    par = [1 if nm in ("kappa", "a+", "a-") else 0 for nm in names]
    return names, par


def gb_params(n):
    """gb_{sigma,j,s}: sigma labels a^sigma, s labels b_j^s."""
    return [(sg, j, s) for sg in "+-" for j in range(1, n + 1) for s in "+-"]


def make_bracket_table(n, unit):
    """B(p,q) = [x_p, x_q] = kK * 1 + kk * kappa, returned as (kK, kk).

    unit = gb parameter set to 1 (None: all gb = 0).
    """
    names, par = oscillator_data(n)
    idx = {nm: i for i, nm in enumerate(names)}
    table = {(idx["a-"], idx["a+"]): (1, 0), (idx["a+"], idx["a-"]): (1, 0)}
    for j in range(1, n + 1):
        table[(idx[f"b{j}-"], idx[f"b{j}+"])] = (1, 0)
        table[(idx[f"b{j}+"], idx[f"b{j}-"])] = (-1, 0)
    for sg, j, s in gb_params(n):
        e = 1 if unit == (sg, j, s) else 0
        b, a = idx[f"b{j}{s}"], idx[f"a{sg}"]
        table[(b, a)] = (0, -e)  # [b, a] = -gb kappa
        table[(a, b)] = (0, e)   # [a, b] = -(-1)^0 [b, a] = +gb kappa

    def B(p, q):
        if (p, q) in table:
            return table[(p, q)]
        if (q, p) in table:  # super-skew: [x_p,x_q] = -(-1)^{|p||q|} [x_q,x_p]
            kv, kk = table[(q, p)]
            sgn = -1 if (par[p] and par[q]) else 1
            return (-sgn * kv, -sgn * kk)
        return (0, 0)

    return par, B


def make_normal_ordering(par, B):
    """Normal ordering with x_p x_q = (-1)^{|p||q|} x_q x_p + [x_p, x_q] (p > q).

    Words are sorted tuples of generator indices; kappa has index 0 and is
    therefore always placed leftmost.  Returns dict {word: int coefficient}.
    """

    @lru_cache(maxsize=None)
    def NF(word):
        for i in range(len(word) - 1):
            p, q = word[i], word[i + 1]
            if p == q:
                if par[p]:  # x^2 = [x,x]/2 = 0 for every odd generator here
                    return {}
                continue
            if p > q:
                rest = word[:i] + word[i + 2:]
                sgn = -1 if (par[p] and par[q]) else 1
                res = {}
                for w, c in NF(word[:i] + (q, p) + word[i + 2:]).items():
                    res[w] = res.get(w, 0) + sgn * c
                kv, kk = B(p, q)
                if kv:
                    for w, c in NF(rest).items():
                        res[w] = res.get(w, 0) + kv * c
                if kk:
                    # kappa sits between prefix and suffix; move it to the front
                    # (kappa odd, super-central): sign (-1)^{parity of prefix}.
                    pref = (-1) ** sum(par[x] for x in word[:i])
                    for w, c in NF((0,) + rest).items():
                        res[w] = res.get(w, 0) + pref * kk * c
                return {w: c for w, c in res.items() if c}
        return {word: 1}

    return NF


def quad_basis(par):
    """Basis of g: sorted pairs (p, q) with 1 <= p <= q, excluding odd p == q."""
    N = len(par)
    return [(p, q) for p in range(1, N) for q in range(p, N)
            if not (p == q and par[p])]


def decompose(NF, par, u, v):
    """Return (quad, kap, dropped) for the commutator [u, v] of two basis words.

    quad:    {(p,q): c}  quadratic part (kappa-free), basis coordinates
    kap:     {(p,q): c}  coefficient of kappa * x_p x_q
    dropped: constant terms (K-part and kappa*1), removed in the quotient by 1
    """
    s = -1 if ((par[u[0]] + par[u[1]]) % 2 and (par[v[0]] + par[v[1]]) % 2) else 1
    comm = dict(NF(u + v))
    for w, c in NF(v + u).items():
        comm[w] = comm.get(w, 0) - s * c
    quad, kap, dropped = {}, {}, {}
    for w, c in comm.items():
        if c == 0:
            continue
        if len(w) == 2 and w[0] != 0:
            quad[w] = quad.get(w, 0) + c
        elif len(w) == 3 and w[0] == 0:
            kap[(w[1], w[2])] = kap.get((w[1], w[2]), 0) + c
        elif len(w) == 0 or w == (0,):
            dropped[w] = dropped.get(w, 0) + c
        else:
            raise ValueError(f"unexpected word {w} in commutator")
    return ({k: v for k, v in quad.items() if v},
            {k: v for k, v in kap.items() if v},
            {k: v for k, v in dropped.items() if v})


def build_structure(n):
    names, par = oscillator_data(n)
    basis = quad_basis(par)
    D = len(basis)
    bindex = {b: i for i, b in enumerate(basis)}
    pv = [(par[p] + par[q]) % 2 for p, q in basis]

    _, B0 = make_bracket_table(n, None)
    NF0 = make_normal_ordering(par, B0)
    mu0 = np.zeros((D, D, D))
    k0 = np.zeros((D, D))  # undeformed central constant (coefficient of 1)
    dropped_undeformed = set()
    for i, u in enumerate(basis):
        for j, v in enumerate(basis):
            quad, kap, dropped = decompose(NF0, par, u, v)
            assert not kap, "kappa term without gb"
            for w, c in quad.items():
                mu0[i, j, bindex[w]] += c
            k0[i, j] = dropped.get((), 0)
            dropped_undeformed.update(w for w in dropped if w != ())

    gammas = {}
    kconst = {}  # kappa * 1 coefficient c_u(i,j), in the un-lifted quotient basis
    for u in gb_params(n):
        _, Bu = make_bracket_table(n, u)
        NFu = make_normal_ordering(par, Bu)
        gam = np.zeros((D, D, D))
        kc = np.zeros((D, D))
        for i, a in enumerate(basis):
            for j, b in enumerate(basis):
                quad, kap, dropped = decompose(NFu, par, a, b)
                for w, c in kap.items():
                    gam[i, j, bindex[w]] += c
                kc[i, j] = dropped.get((0,), 0)
        gammas[u] = gam
        kconst[u] = kc
    return dict(names=names, par=par, basis=basis, pv=pv, mu0=mu0, k0=k0,
                gammas=gammas, kconst=kconst,
                dropped_undeformed=sorted(dropped_undeformed))


def lifted_constants(mu0, k0, gam, kc):
    """Constant (kappa*1) part of the deformation in a splitting basis.

    The lift Q~_a = Q_a + lam_a * 1 is chosen so that the undeformed bracket closes
    without constants: k0_{ij} = sum_c mu0[i,j,c] lam_c.  Brackets of lifts equal
    brackets of the unlifted elements (1 is central), but the kappa-quadratic
    part gam_{ij}^c Q_c = gam_{ij}^c (Q~_c - lam_c 1) shifts the constant term.
    Returns (lam, residual of the closure system, c_lift).
    """
    D = mu0.shape[0]
    A = mu0.reshape(D * D, D)
    lam, *_ = np.linalg.lstsq(A, k0.reshape(-1), rcond=None)
    closure_res = float(np.linalg.norm(A @ lam - k0.reshape(-1)))
    c_lift = kc - np.einsum("ijc,c->ij", gam, lam)
    return lam, closure_res, c_lift


def super_jacobi_residual(mu0, gam, pv):
    """Max |residual| of the super-Jacobi identity, kappa-free and kappa-linear.

    Convention: element = a0 + kappa*a1 with kappa odd and super-central.
      mu(X, kappa W) = (-1)^{|X|} kappa mu0(X, W),   mu(kappa W, Y) = kappa mu0(W, Y).
    Super-Jacobi: [X,[Y,Z]] = [[X,Y],Z] + (-1)^{|X||Y|} [Y,[X,Z]].
    """
    # Vectorised over all triples: index order (x, y, z, w) with X=e_x, Y=e_y, Z=e_z.
    pv = np.asarray(pv)
    sx = (-1.0) ** pv[:, None, None, None]
    sy = (-1.0) ** pv[None, :, None, None]
    sxy = (-1.0) ** (pv[:, None] * pv[None, :])[:, :, None, None]

    # kappa-free: m0(X,m0(Y,Z)) - m0(m0(X,Y),Z) - s_xy m0(Y,m0(X,Z))
    J0 = (np.einsum("xkw,yzk->xyzw", mu0, mu0)
          - np.einsum("xyk,kzw->xyzw", mu0, mu0)
          - sxy * np.einsum("xzk,ykw->xyzw", mu0, mu0))
    # kappa-linear: A - Bt - s_xy C, with
    #   A  = g(X,m0(Y,Z)) + (-1)^{|X|} m0(X,g(Y,Z))
    #   Bt = g(m0(X,Y),Z) + m0(g(X,Y),Z)
    #   C  = g(Y,m0(X,Z)) + (-1)^{|Y|} m0(Y,g(X,Z))
    A = (np.einsum("xkw,yzk->xyzw", gam, mu0)
         + sx * np.einsum("xkw,yzk->xyzw", mu0, gam))
    Bt = (np.einsum("xyk,kzw->xyzw", mu0, gam)
          + np.einsum("xyk,kzw->xyzw", gam, mu0))
    C = (np.einsum("xzk,ykw->xyzw", mu0, gam)
         + sy * np.einsum("xzk,ykw->xyzw", gam, mu0))
    J1 = A - Bt - sxy * C
    return float(np.max(np.abs(J0))), float(np.max(np.abs(J1)))


def delta_matrix(mu0, pv):
    """Linear map F -> delta f, F[g,b] = coefficient of Z_g in f(Z_b).

    (delta f)(X,Y) = (-1)^{|X|} [X, fY] - (-1)^{(|X|+1)|Y|} [Y, fX] - f([X,Y]).
    Unknowns: parity-reversing F (|g| != |b|).  Returns (M, unknowns) with
    M of shape (D*D*D, #unknowns).
    """
    D = len(pv)
    U = [(g, b) for g in range(D) for b in range(D) if pv[g] != pv[b]]
    M = np.zeros((D, D, D, len(U)))
    for k, (g, b) in enumerate(U):
        # term 1: f(Z_b) = Z_g  -> contributes at (alpha, beta=b)
        for a in range(D):
            M[a, b, :, k] += (-1) ** pv[a] * mu0[a, g, :]
        # term 2: f(Z_alpha) = Z_g with alpha = b, any beta
        for be in range(D):
            M[b, be, :, k] += -((-1) ** ((pv[b] + 1) * pv[be])) * mu0[be, g, :]
        # term 3: -f([Z_a, Z_be]) with [Z_a,Z_be] having Z_b component
        M[:, :, g, k] += -mu0[:, :, b]
    return M.reshape(D * D * D, len(U)), U


def in_image(Q, t, tol=1e-9):
    res = t - Q @ (Q.T @ t)
    return float(np.linalg.norm(res)), bool(np.linalg.norm(res) < tol * max(1.0, np.linalg.norm(t)))


def run(n):
    S = build_structure(n)
    names, par, basis, pv = S["names"], S["par"], S["basis"], S["pv"]
    mu0, gammas = S["mu0"], S["gammas"]
    D = len(basis)

    # Super-Jacobi checks
    jac_undeformed, _ = super_jacobi_residual(mu0, np.zeros_like(mu0), pv)
    jac_k = {}
    for u, gam in gammas.items():
        _, r1 = super_jacobi_residual(mu0, gam, pv)
        jac_k[str(u)] = r1

    # Coboundary image
    M, U = delta_matrix(mu0, pv)
    Uu, sv, _ = np.linalg.svd(M, full_matrices=False)
    rank = int(np.sum(sv > 1e-9 * sv[0]))
    Q = Uu[:, :rank]

    # Sanity: delta(ad Z) = 0 for odd Z
    ad_check = []
    for z in range(D):
        if pv[z] == 1:
            F = np.zeros(len(U))
            for k, (g, b) in enumerate(U):
                F[k] = mu0[z, b, g]
            ad_check.append(float(np.max(np.abs(M @ F))))
    ad_ok = max(ad_check) if ad_check else 0.0

    # Membership of each gamma_u in im(delta), and the joint solution space
    per_unit, residual_cols = {}, []
    for u, gam in gammas.items():
        t = gam.reshape(-1)
        rnorm, inside = in_image(Q, t)
        per_unit[str(u)] = dict(residual_norm=rnorm, is_trivial=inside,
                                gamma_norm=float(np.linalg.norm(t)))
        residual_cols.append(t - Q @ (Q.T @ t))
    R_adj = np.array(residual_cols).T  # columns: gamma_u mod im(delta)
    trivial_units = [u for u, info in per_unit.items() if info["is_trivial"]]

    # Trivial-module block (kappa*1 part), in the splitting basis.
    # Coboundaries of odd functionals h: g -> C are (delta h)_{ij} = -sum_c h_c mu0[i,j,c].
    k0, kconst = S["k0"], S["kconst"]
    odd_idx = [c for c in range(D) if pv[c] == 1]
    T = np.array([(-mu0[:, :, c]).reshape(-1) for c in odd_idx]).T
    Ut, st, _ = np.linalg.svd(T, full_matrices=False)
    QT = Ut[:, :int(np.sum(st > 1e-9 * max(st[0], 1e-300)))]
    lam, closure_res, _ = lifted_constants(mu0, k0, gammas[gb_params(n)[0]], kconst[gb_params(n)[0]])
    per_unit_const, const_cols, parity_violation = {}, [], 0.0
    for u, gam in gammas.items():
        _, _, cl = lifted_constants(mu0, k0, gam, kconst[u])
        # kappa*1 must only sit on pairs of mixed parity (kappa is odd)
        parity_violation = max(parity_violation, float(np.max(np.abs(cl[np.add.outer(np.array(pv), np.array(pv)) % 2 == 0]))))
        t = cl.reshape(-1)
        res_vec = t - QT @ (QT.T @ t)
        per_unit_const[str(u)] = dict(residual_norm=float(np.linalg.norm(res_vec)),
                                      is_trivial=bool(np.linalg.norm(res_vec) < 1e-9 * max(1.0, np.linalg.norm(t))),
                                      c_norm=float(np.linalg.norm(t)))
        const_cols.append(res_vec)
    R_const = np.array(const_cols).T

    # Explicit witnesses: f (adjoint block) with delta f = gamma_u, and h (trivial
    # block) with delta h = c_u, both found by least squares.
    adj_wit, const_wit = {}, {}
    for u, gam in gammas.items():
        sol, *_ = np.linalg.lstsq(M, gam.reshape(-1), rcond=None)
        F = {}
        for k, (g, b) in enumerate(U):
            if abs(sol[k]) > 1e-10:
                F[f"Z{g}<-Z{b}"] = float(round(sol[k], 12))
        adj_wit[str(u)] = dict(f_nonzero=F,
                               residual=float(np.linalg.norm(M @ sol - gam.reshape(-1))))
        _, _, cl = lifted_constants(mu0, k0, gam, kconst[u])
        hsol, *_ = np.linalg.lstsq(T, cl.reshape(-1), rcond=None)
        h = {f"Z{c}": float(round(hsol[i], 12)) for i, c in enumerate(odd_idx) if abs(hsol[i]) > 1e-10}
        const_wit[str(u)] = dict(h_nonzero=h,
                                 residual=float(np.linalg.norm(T @ hsol - cl.reshape(-1))))

    # Controls: random cochains of the right shape must NOT be coboundaries.
    rng = np.random.default_rng(12345)
    ctrl_adj = rng.standard_normal((D, D, D))
    ctrl_adj *= np.array([[[1.0 if (pv[i] + pv[j] + pv[k]) % 2 == 1 else 0.0
                            for k in range(D)] for j in range(D)] for i in range(D)])
    ctrl_const = rng.standard_normal((D, D))
    ctrl_const *= np.add.outer(np.array(pv), np.array(pv)) % 2
    control = dict(
        adjoint_random_residual=float(np.linalg.norm(ctrl_adj.reshape(-1) - Q @ (Q.T @ ctrl_adj.reshape(-1)))),
        trivial_random_residual=float(np.linalg.norm(ctrl_const.reshape(-1) - QT @ (QT.T @ ctrl_const.reshape(-1)))),
    )
    # Joint trivial subspace: both blocks must vanish on the combination
    R_all = np.vstack([R_adj, R_const])
    rk_all = int(np.linalg.matrix_rank(R_all, tol=1e-9)) if np.linalg.norm(R_all) > 0 else 0
    dim_W = len(gammas) - rk_all
    rk_adj = int(np.linalg.matrix_rank(R_adj, tol=1e-9)) if np.linalg.norm(R_adj) > 0 else 0
    rk_const = int(np.linalg.matrix_rank(R_const, tol=1e-9)) if np.linalg.norm(R_const) > 0 else 0

    # Structured artifact
    mu0_nz = [[int(i), int(j), int(k), float(mu0[i, j, k])]
              for i, j, k in zip(*np.nonzero(mu0))]
    gam_nz = {str(u): [[int(i), int(j), int(k), float(g[i, j, k])]
                       for i, j, k in zip(*np.nonzero(g))]
              for u, g in gammas.items()}
    result = dict(
        n=n,
        dim_g=D,
        dim_expected=2 * n * n + 5 * n + 1,
        dim_even=sum(1 for p in pv if p == 0),
        dim_odd=sum(1 for p in pv if p == 1),
        basis=[dict(index=i, pair=[int(p), int(q)],
                    label=f"{names[p]}*{names[q]}", parity=pv[i])
               for i, (p, q) in enumerate(basis)],
        oscillator_names=names,
        structure_constants_mu0_nonzero=mu0_nz,
        gamma_nonzero=gam_nz,
        gb_parameters=[str(u) for u in gb_params(n)],
        checks=dict(
            super_jacobi_undeformed_max_residual=jac_undeformed,
            super_jacobi_kappa_linear_max_residual=jac_k,
            delta_ad_Z_max_abs=ad_ok,
            undeformed_constant_closure_residual=closure_res,
            kappa_constant_parity_violation=parity_violation,
            lifted_constants_lambda=[float(x) for x in lam],
        ),
        adjoint_block=dict(
            unknowns_odd_maps=len(U),
            rank_delta=rank,
            per_unit=per_unit,
            trivial_units=trivial_units,
            rank_joint=rk_adj,
            witnesses=adj_wit,
        ),
        trivial_module_block=dict(
            unknowns_odd_functionals=len(odd_idx),
            rank_delta_triv=int(QT.shape[1]),
            per_unit=per_unit_const,
            rank_joint=rk_const,
            witnesses=const_wit,
        ),
        controls_random_cochains_residual=control,
        joint=dict(
            dim_trivial_subspace_W=dim_W,
            trivial_gb_basis_rank=rk_all,
        ),
        conclusion=("only gb = 0 gives trivial deformation" if dim_W == 0 else
                    f"trivial subspace of dimension {dim_W} in gb-space"),
    )
    return result


def main(argv):
    ns = [int(a) for a in argv] or [1, 2, 3]
    os.makedirs(ART_DIR, exist_ok=True)
    for n in ns:
        res = run(n)
        path = os.path.join(ART_DIR, f"c_triviality_n{n}.json")
        with open(path, "w") as fh:
            json.dump(res, fh, indent=1)
        print(f"n={n}: dim g={res['dim_g']} (expected {res['dim_expected']}), "
              f"even/odd={res['dim_even']}/{res['dim_odd']}")
        print(f"  super-Jacobi undeformed={res['checks']['super_jacobi_undeformed_max_residual']:.2e}, "
              f"kappa-linear={max(res['checks']['super_jacobi_kappa_linear_max_residual'].values()):.2e}")
        print(f"  delta(ad Z) max={res['checks']['delta_ad_Z_max_abs']:.2e}; "
              f"closure residual={res['checks']['undeformed_constant_closure_residual']:.2e}; "
              f"kappa*1 parity violation={res['checks']['kappa_constant_parity_violation']:.2e}")
        a = res["adjoint_block"]
        print(f"  adjoint block: odd maps={a['unknowns_odd_maps']}, rank(delta)={a['rank_delta']}, "
              f"trivial gamma_u={len(a['trivial_units'])}/{len(a['per_unit'])}")
        t = res["trivial_module_block"]
        for u, info in t["per_unit"].items():
            print(f"  kappa*1 part {u}: |c|={info['c_norm']:.3f} "
                  f"residual_mod_im(delta_triv)={info['residual_norm']:.3e} trivial={info['is_trivial']}")
        print(f"  joint dim of trivial gb-subspace W = {res['joint']['dim_trivial_subspace_W']}  -> {res['conclusion']}")
        print(f"  wrote {path}")


if __name__ == "__main__":
    main(sys.argv[1:])
