#!/usr/bin/env python3
"""Triviality analysis of the first-order inhomogeneous (gb) deformation of C(n+1) = osp(2|2n).

Conventions (taken from docs/math/*.md):
  fermions  a^+ (index 0), a^- (index 1)           parity 1
  bosons    b_k^+ (index 2k), b_k^- (index 2k+1)   parity 0, k = 1..n
  {a^-, a^+} = 1,  (a^+)^2 = (a^-)^2 = 0,  [b_k^-, b_l^+] = delta_kl, other boson pairs commute
  [b_j^s, a^sigma] = -gb[sigma, j, s] * kappa,  kappa odd, super-central, kappa^2 = 0 (first order)
  Normal order: fermions before bosons, bosons by increasing index.

L = span{normal-ordered quadratic monomials} + C*1 ;  dim L = dim g + 1,  dim g = 2n^2+5n+1.
g = L / C*1 is the adjoint picture; C*1 is the central scalar that appears in the oscillator realisation.

gamma(X,Y) = kappa-coefficient of the deformed bracket [X,Y]_gb.
(delta F)(X,Y) = (-1)^{p(X)} [X,F(Y)] - (-1)^{(p(X)+1)p(Y)} [Y,F(X)] - F([X,Y]),   F odd linear.

Two readings of "up to scalar" are computed:
  'quotient' (I) : everything is taken in g = L/C*1 (scalar component discarded).
  'central'  (II): everything is taken in L (scalar component kept; F may send to C*1).
Both sides are linear in (gb, F), so the trivial parameters form a linear subspace T of C^{4n}:
  T = { gb : gamma(gb) in im(delta) },   dim T = 4n + rank(Delta) - rank([Delta | Gamma]).

Usage:  python3 scripts/c_n1_triviality.py n [n ...]
Writes docs/issues/artifacts/triviality_n{n}.json
"""
import json
import os
import sys
from fractions import Fraction

import numpy as np

P = 1000003  # prime for exact rank checks


def par(mono):
    """Parity of a normal-ordered monomial (number of fermionic factors mod 2)."""
    return sum(1 for i in mono if i < 2) % 2


def elem_parity(A):
    for (k, m) in A:
        return (k + par(m)) % 2
    return 0


def normal_order(word, G, k=0):
    """Normal form of kappa^k * word.  Returns {(kpow, mono): Fraction}.  kappa^2 = 0."""
    for i in range(len(word) - 1):
        x, y = word[i], word[i + 1]
        if x < y or (x == y and x >= 2):
            continue
        break
    else:
        return {(k, word): Fraction(1)}
    pre, suf = word[:i], word[i + 2:]
    out = {}

    def acc(d, c):
        for key, v in d.items():
            out[key] = out.get(key, 0) + c * v

    if x < 2 and y < 2:  # two fermions out of order (x = a^-, y = a^+) or equal
        if x == y:
            return {}
        acc(normal_order(pre + suf, G, k), 1)            # a^- a^+ = 1 - a^+ a^-
        acc(normal_order(pre + (0, 1) + suf, G, k), -1)
    elif x >= 2 and y < 2:  # boson before fermion:  b a = a b + [b,a] = a b - G kappa
        acc(normal_order(pre + (y, x) + suf, G, k), 1)
        g = G.get((y, x), 0)
        if k == 0 and g:
            # move kappa to the front of  pre * kappa * suf  (kappa odd): sign (-1)^{p(pre)}
            acc(normal_order(pre + suf, G, 1), -g * (-1) ** par(pre))
    else:  # two bosons out of order
        if x == y + 1 and x % 2 == 1:                    # b_k^- b_k^+ = b_k^+ b_k^- + 1
            acc(normal_order(pre + suf, G, k), 1)
        acc(normal_order(pre + (y, x) + suf, G, k), 1)
    return out


def mul(A, B, G):
    out = {}
    for (k1, m1), c1 in A.items():
        for (k2, m2), c2 in B.items():
            if k1 + k2 >= 2:
                continue
            sign = (-1) ** (k2 * par(m1))  # kappa^{k2} moved past m1
            for key, v in normal_order(m1 + m2, G, k1 + k2).items():
                out[key] = out.get(key, 0) + c1 * c2 * sign * v
    return {k: v for k, v in out.items() if v != 0}


def bracket(A, B, G):
    pA, pB = elem_parity(A), elem_parity(B)
    s = (-1) ** (pA * pB)
    res = dict(mul(A, B, G))
    for key, v in mul(B, A, G).items():
        res[key] = res.get(key, 0) - s * v
    return {k: v for k, v in res.items() if v != 0}


def build(n):
    bos = list(range(2, 2 * n + 2))
    quad = [(0, 1)] + [(f, b) for f in (0, 1) for b in bos] + \
           [(b1, b2) for i, b1 in enumerate(bos) for b2 in bos[i:]]
    basis = quad + [()]
    return bos, quad, basis


def mono_name(m):
    if not m:
        return "1"
    names = {0: "a+", 1: "a-"}
    for idx in range(2, 2 * 99):
        names.setdefault(idx, f"b{idx // 2}{'+' if idx % 2 == 0 else '-'}")
    return "*".join(names[i] for i in m)


def to_vec(d, index, N):
    v = np.zeros(N, dtype=np.int64)
    for (k, m), c in d.items():
        assert k == 0 or True
        assert c.denominator == 1, c
        v[index[m]] += int(c)
    return v


def rank_mod_p(M):
    A = np.array(M, dtype=np.int64) % P
    if A.size == 0:
        return 0
    A = A[np.any(A != 0, axis=1)]
    rows, cols = A.shape
    r = 0
    for c in range(cols):
        if r == rows:
            break
        nz = np.nonzero(A[r:, c])[0]
        if nz.size == 0:
            continue
        piv = r + nz[0]
        A[[r, piv]] = A[[piv, r]]
        inv = pow(int(A[r, c]), P - 2, P)
        A[r] = (A[r] * inv) % P
        col = A[:, c].copy()
        col[r] = 0
        A = (A - np.outer(col, A[r])) % P
        r += 1
    return r


def system_matrices(br, gam, par_b, gb_keys, S):
    """Linear system  Gamma gb = Delta phi  on the index set S.

    Rows are (a, b, o) (cochain value at (e_a, e_b), component e_o); columns of Gamma are the
    gb parameters; columns of Delta are the unknowns F(e_d) = e_c for pairs (c, d) of opposite parity.
    """
    m_ = len(S)
    pS = [par_b[s] for s in S]
    brS = [[br[S[a]][S[b]][S] for b in range(m_)] for a in range(m_)]
    gS = [[[gam[key][S[a]][S[b]][S] for b in range(m_)] for a in range(m_)] for key in gb_keys]
    unknowns = [(c, d) for c in range(m_) for d in range(m_) if pS[c] != pS[d]]
    R = m_ * m_ * m_
    Gam = np.zeros((R, len(gb_keys)), dtype=np.int64)
    Del = np.zeros((R, len(unknowns)), dtype=np.int64)
    for mi in range(len(gb_keys)):
        Gam[:, mi] = np.array([gS[mi][a][b][o] for a in range(m_) for b in range(m_) for o in range(m_)])
    for ui, (c, d) in enumerate(unknowns):
        col = np.zeros((m_, m_, m_), dtype=np.int64)
        for a in range(m_):
            for b in range(m_):
                v = np.zeros(m_, dtype=np.int64)
                if b == d:   # (-1)^{p(X)} [X, F(Y)],  X = e_a, Y = e_b, F(e_b) = e_c
                    v += (-1) ** pS[a] * brS[a][c]
                if a == d:   # -(-1)^{(p(X)+1)p(Y)} [Y, F(X)],  F(e_a) = e_c
                    v -= (-1) ** ((pS[a] + 1) * pS[b]) * brS[b][c]
                v[c] -= brS[a][b][d]  # -F([X,Y]),  F(e_d) = e_c
                col[a, b, :] = v
        Del[:, ui] = col.reshape(-1)
    return Gam, Del, unknowns


def exact_certificate(br, gam, par_b, gb_keys, S):
    """Exact rational certificate: for each gb basis direction e_m find odd F with delta F = gamma(e_m).

    Row-reduces [Delta | Gamma] over Q.  Returns the rational rank data and, for each direction,
    the explicit F as {(c, d): value} meaning F(e_d) = sum value * e_c, verified in exact arithmetic.
    """
    from sympy import QQ
    from sympy.polys.matrices import DomainMatrix

    Gam, Del, unknowns = system_matrices(br, gam, par_b, gb_keys, S)
    A = np.hstack([Del, Gam])
    A = np.unique(A[np.any(A != 0, axis=1)], axis=0)
    nphi = Del.shape[1]
    dm = DomainMatrix([[QQ(int(x)) for x in row] for row in A.tolist()], (A.shape[0], A.shape[1]), QQ)
    rref, pivots = dm.rref()
    rref_list = rref.to_list()
    rank_DG = len(pivots)
    rank_D = sum(1 for p_ in pivots if p_ < nphi)
    dimT = len(gb_keys) + rank_D - rank_DG
    certificate = {}
    for mi, key in enumerate(gb_keys):
        phi = [Fraction(0)] * nphi
        for r_idx, pc in enumerate(pivots):
            if pc < nphi:
                q = QQ.to_sympy(rref_list[r_idx][nphi + mi])
                phi[pc] = Fraction(int(q.p), int(q.q))
        # exact check  Delta phi == Gamma e_m  (integer/rational arithmetic)
        for row in range(Del.shape[0]):
            lhs = sum(Fraction(int(Del[row, k])) * phi[k] for k in range(nphi) if Del[row, k] and phi[k])
            assert lhs == Fraction(int(Gam[row, mi])), "exact certificate failed"
        certificate[f"{key[0]}|{key[1]}"] = {
            (f"{unknowns[k][0]},{unknowns[k][1]}"): str(phi[k])
            for k in range(nphi) if phi[k] != 0
        }
    return {
        "exact_rank_Delta": rank_D,
        "exact_rank_Delta_Gamma": rank_DG,
        "exact_dim_T": dimT,
        "certificate_F_entries_by_gb_direction": certificate,
    }


def run(n, exact=False):
    bos, quad, basis = build(n)
    N = len(basis)
    dg = len(quad)
    index = {m: i for i, m in enumerate(basis)}
    par_b = [par(m) for m in basis]
    gb_keys = [(f, b) for f in (0, 1) for b in bos]  # parameters gb[sigma, j, s], 4n of them
    one = Fraction(1)
    elems = [{(0, m): one} for m in basis]

    # ---- undeformed bracket (kappa^0 part) and gamma^{(m)} (kappa^1 part) -------------
    br = [[None] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            d = bracket(elems[i], elems[j], {})
            assert all(k == 0 for (k, _) in d), "kappa appeared in undeformed bracket"
            assert all(m in index for (_, m) in d), "monomial outside basis (undeformed)"
            br[i][j] = to_vec({(0, m): c for (_, m), c in d.items()}, index, N)

    gam = {}
    for key in gb_keys:
        G = {key: one}
        tab = [[None] * N for _ in range(N)]
        for i in range(N):
            for j in range(N):
                d = bracket(elems[i], elems[j], G)
                kap = {(0, m): c for (k, m), c in d.items() if k == 1}
                assert all(m in index for (_, m) in kap), "quartic/unknown term in gamma"
                tab[i][j] = to_vec(kap, index, N)
        gam[key] = tab

    # ---- Jacobi check (first order, with random generic gb) ------------------------
    rng = np.random.default_rng(1)
    Grand = {key: Fraction(int(rng.integers(-3, 4))) for key in gb_keys}
    jac_fail = 0
    jac_checked = 0
    for G in ({}, Grand):
        for i in range(N):
            for j in range(N):
                for k in range(N):
                    X, Y, Z = elems[i], elems[j], elems[k]
                    lhs = bracket(X, bracket(Y, Z, G), G)
                    s = (-1) ** (elem_parity(X) * elem_parity(Y))
                    rhs = dict(bracket(bracket(X, Y, G), Z, G))
                    for key, v in bracket(Y, bracket(X, Z, G), G).items():
                        rhs[key] = rhs.get(key, 0) + s * v
                    diff = {kk: lhs.get(kk, 0) - rhs.get(kk, 0) for kk in set(lhs) | set(rhs)}
                    jac_checked += 1
                    if any(v != 0 for v in diff.values()):
                        jac_fail += 1
    # ---- linear algebra for the two readings --------------------------------------
    results = {}
    for name, S in (("quotient", list(range(dg))), ("central", list(range(N)))):
        Gam, Del, unknowns = system_matrices(br, gam, par_b, gb_keys, S)
        R = Gam.shape[0]
        rG = rank_mod_p(Gam)
        rD = rank_mod_p(Del) if Del.size else 0
        rGD = rank_mod_p(np.hstack([Del, Gam])) if Del.size else rG
        dimT_mod = len(gb_keys) + rD - rGD
        Gf = Gam.astype(float)
        Df = Del.astype(float)
        rDf = np.linalg.matrix_rank(Df) if Df.size else 0
        rGDf = np.linalg.matrix_rank(np.hstack([Df, Gf])) if Df.size else np.linalg.matrix_rank(Gf)
        dimT_float = len(gb_keys) + rDf - rGDf
        # explicit trivial directions (float nullspace projected onto gb coordinates)
        M = np.hstack([Gf, -Df])
        _, sv, Vt = np.linalg.svd(M)
        nullity = M.shape[1] - np.sum(sv > 1e-9)
        null_vecs = Vt[len(sv) - nullity:] if nullity else np.zeros((0, M.shape[1]))
        proj = null_vecs[:, :len(gb_keys)]
        if proj.size and np.linalg.matrix_rank(proj, tol=1e-9) > 0:
            u, s2, vt2 = np.linalg.svd(proj)
            r2 = int(np.sum(s2 > 1e-9))
            T_basis = [list(np.round(vt2[i], 6)) for i in range(r2)]
        else:
            T_basis = []
        results[name] = {}
        if exact:
            results[name].update(exact_certificate(br, gam, par_b, gb_keys, S))
        results[name].update({
            "num_unknowns_F": len(unknowns),
            "num_equations": int(R),
            "rank_Gamma_mod_p": rG,
            "rank_Delta_mod_p": rD,
            "rank_Delta_Gamma_mod_p": rGD,
            "dim_T_mod_p": dimT_mod,
            "rank_Delta_float": int(rDf),
            "rank_Delta_Gamma_float": int(rGDf),
            "dim_T_float": int(dimT_float),
            "trivial_gb_basis_float": T_basis,
            "trivial_gb_is_zero": dimT_mod == 0,
        })

    # single-parameter deformations: is gamma(e_m) a coboundary on its own?
    # (covered by T, recorded for convenience)
    nonzero_gamma = {
        f"gb[{'a+' if f == 0 else 'a-'},b{b // 2}{'+' if b % 2 == 0 else '-'}]": {
            "gamma_nonzero_entries": [
                {"pair": [mono_name(basis[i]), mono_name(basis[j])],
                 "value": {mono_name(basis[o]): int(gam[(f, b)][i][j][o])
                           for o in range(N) if gam[(f, b)][i][j][o] != 0}}
                for i in range(N) for j in range(N) if np.any(gam[(f, b)][i][j] != 0)
            ]
        }
        for (f, b) in gb_keys
    }

    out = {
        "n": n,
        "dim_g": dg,
        "dim_L": N,
        "parity_quotient_basis": [("odd" if p else "even") for p in par_b[:dg]],
        "basis": [mono_name(m) for m in basis],
        "undeformed_bracket_nonzero": [
            {"pair": [mono_name(basis[i]), mono_name(basis[j])],
             "value": {mono_name(basis[o]): int(br[i][j][o]) for o in range(N) if br[i][j][o] != 0}}
            for i in range(N) for j in range(i, N) if np.any(br[i][j] != 0)
        ],
        "gamma_per_parameter": nonzero_gamma,
        "jacobi_check": {"triples_checked": jac_checked, "failures": jac_fail},
        "triviality": results,
    }
    return out


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(here, "..", "docs", "issues", "artifacts")
    os.makedirs(outdir, exist_ok=True)
    summary = {}
    for arg in argv:
        n = int(arg)
        res = run(n, exact=(n <= 2))  # exact rational row-reduction is run for n = 1, 2
        path = os.path.join(outdir, f"triviality_n{n}.json")
        with open(path, "w") as fh:
            json.dump(res, fh, indent=1, ensure_ascii=False)
        summary[f"n={n}"] = {
            "dim_g": res["dim_g"],
            "jacobi_failures": res["jacobi_check"]["failures"],
            "jacobi_triples_checked": res["jacobi_check"]["triples_checked"],
            "exact_over_Q": n <= 2,
            **{v: {"dim_T": r["dim_T_mod_p"], "dim_T_float": r["dim_T_float"],
                   "rank_Delta": r["rank_Delta_mod_p"], "rank_Delta_Gamma": r["rank_Delta_Gamma_mod_p"],
                   "unknowns_F": r["num_unknowns_F"]}
               for v, r in res["triviality"].items()},
        }
        print(f"n={n}: dim g={res['dim_g']}, jacobi failures={res['jacobi_check']['failures']}"
              f"/{res['jacobi_check']['triples_checked']}")
        for name, r in res["triviality"].items():
            print(f"  [{name}] unknowns={r['num_unknowns_F']} rank Gamma={r['rank_Gamma_mod_p']} "
                  f"rank Delta={r['rank_Delta_mod_p']} rank [D|G]={r['rank_Delta_Gamma_mod_p']} "
                  f"dim T={r['dim_T_mod_p']} (float {r['dim_T_float']})")
        print("  wrote", os.path.relpath(path))
    with open(os.path.join(outdir, "triviality_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    print("  wrote", os.path.relpath(os.path.join(outdir, "triviality_summary.json")))


if __name__ == "__main__":
    main(sys.argv[1:] or ["1"])
