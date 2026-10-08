#!/usr/bin/env python3
"""Triviality analysis of inhomogeneous (gb) deformations of C(n+1) = osp(2|2n).

Model (see docs/issues/mathematical_proof.md, Section 2):

* Oscillators (index -> operator):
    0 = a_1^+ (odd),  1 = a_1^- (odd),  {a_1^-, a_1^+} = 1, a_1^{+2} = a_1^{-2} = 0
    2 + 2j = b_{j+1}^+ (even),  3 + 2j = b_{j+1}^- (even),  [b_j^-, b_k^+] = delta_jk
* Deformation (first order in kappa, kappa odd, kappa central, kappa^2 = 0):
    [b_j^s, a_1^sigma] = - gb_{sigma,j,s} * kappa
  Each gb parameter is selected one at a time (one-hot), so the cochain is linear in gb.
* g basis: canonically ordered quadratic monomials x_i x_j (i <= j) with a^+a^+ = a^-a^- = 0.
  Count: 2n^2 + 5n + 1 (= dim osp(2|2n)).
* gamma_gb(X, Y) := coefficient of kappa in [X, Y]_{U(A)}, expressed in the g basis.
* delta f: exactly the formula of docs/math/C_coboundary_definition.md, using the
  undeformed bracket; f ranges over odd linear maps.
* Triviality: gamma_gb = delta f.  Since delta is linear in f, "gamma = lambda * delta f"
  for a scalar lambda is equivalent to "gamma = delta(lambda f)"; the scalar is absorbed.

The linear system  delta(phi) - sum_g c_g gamma_g = 0  is solved exactly over Q.
The set of c for which a solution phi exists is the trivial subspace.
Each solution is verified by direct evaluation of delta f (independent of the solver).

Usage:  python3 analysis/cn1_triviality.py [--n 1 2 3] [--out artifacts]
"""

import argparse
import json
import random
from fractions import Fraction
from functools import lru_cache
from itertools import product
from pathlib import Path


# ---------------------------------------------------------------------------
# Oscillator algebra with first-order kappa
# ---------------------------------------------------------------------------

def parity_of_osc(i):
    return 1 if i < 2 else 0


def mono_parity(mono):
    return sum(parity_of_osc(i) for i in mono) % 2


def rel(x, y, sel):
    """Relation for the ordered pair (x, y):  x*y = s*y*x + c0 + kappa*c1.

    sel = (f, bidx) selects the single nonzero gb parameter (or None for kappa = 0).
    Returns (s, c0, c1) with c0, c1 scalars.
    """
    fx, fy = x < 2, y < 2
    if fx and fy:
        # {a^-, a^+} = 1, {a^+, a^+} = {a^-, a^-} = 0 ; x y = -y x + {x, y}
        c0 = 1 if sorted((x, y)) == [0, 1] else 0
        return -1, c0, 0
    if fx != fy:
        if fx:
            # [a^sigma, b] = +gb kappa
            c1 = 1 if sel == (x, y) else 0
        else:
            # [b, a^sigma] = -gb kappa
            c1 = -1 if sel == (y, x) else 0
        return 1, 0, c1
    # both bosonic: [b_j^-, b_j^+] = 1, all others zero
    c0 = 0
    if x != y and (x - 2) // 2 == (y - 2) // 2:
        if x % 2 == 1 and y % 2 == 0:
            c0 = 1
        elif x % 2 == 0 and y % 2 == 1:
            c0 = -1
    return 1, c0, 0


@lru_cache(maxsize=None)
def reduce_mono(mono, sel):
    """Normal-order a monomial (tuple of oscillator indices).

    Returns {(canonical_monomial, kpow): coeff}, kpow in {0, 1}; kappa is kept in front.
    Terms with kappa^2 are dropped (first order).
    """
    for i in range(len(mono) - 1):
        x, y = mono[i], mono[i + 1]
        if x == y:
            if x < 2:
                return {}
            continue
        if x < y:
            continue
        s, c0, c1 = rel(x, y, sel)
        out = {}
        swapped = mono[:i] + (y, x) + mono[i + 2:]
        for key, c in reduce_mono(swapped, sel).items():
            out[key] = out.get(key, 0) + s * c
        rest = mono[:i] + mono[i + 2:]
        if c0:
            for key, c in reduce_mono(rest, sel).items():
                out[key] = out.get(key, 0) + c0 * c
        if c1:
            # move kappa to the front past the prefix (kappa is odd)
            sign = -1 if mono_parity(mono[:i]) else 1
            for (m, k), c in reduce_mono(rest, sel).items():
                if k == 0:
                    out[(m, 1)] = out.get((m, 1), 0) + sign * c1 * c
        return {k: v for k, v in out.items() if v != 0}
    return {(mono, 0): 1}


def mul(A, B, sel):
    """Product of elements given as {(monomial, kpow): coeff}."""
    out = {}
    for (m1, k1), c1 in A.items():
        for (m2, k2), c2 in B.items():
            if k1 + k2 > 1:
                continue
            sign = -1 if (k2 and mono_parity(m1)) else 1
            for (m, k), c in reduce_mono(m1 + m2, sel).items():
                if k1 + k2 + k > 1:
                    continue
                key = (m, k1 + k2 + k)
                out[key] = out.get(key, 0) + sign * c1 * c2 * c
    return {k: v for k, v in out.items() if v != 0}


def bracket(X, Y, sel, pX, pY):
    """Super-commutator [X, Y] = XY - (-1)^{pX pY} YX."""
    sgn = -1 if (pX * pY) % 2 else 1
    out = dict(mul(X, Y, sel))
    for key, c in mul(Y, X, sel).items():
        out[key] = out.get(key, 0) - sgn * c
    return {k: v for k, v in out.items() if v != 0}


# ---------------------------------------------------------------------------
# Lie superalgebra g = osp(2|2n) (canonical quadratic monomial basis)
# ---------------------------------------------------------------------------

def basis_monomials(n):
    N = 2 + 2 * n
    out = []
    for i in range(N):
        for j in range(i, N):
            if i == j and i < 2:
                continue
            out.append((i, j))
    return out


def osc_label(i):
    if i == 0:
        return "a+"
    if i == 1:
        return "a-"
    j = (i - 2) // 2 + 1
    return f"b{j}{'+' if i % 2 == 0 else '-'}"


def mono_label(m):
    return "*".join(osc_label(i) for i in m)


def gb_label(g):
    f, b = g
    sigma = "+" if f == 0 else "-"
    j = (b - 2) // 2 + 1
    s = "+" if b % 2 == 0 else "-"
    return f"gb[sigma={sigma},j={j},s={s}]"


def split(elem, k):
    return {m: c for (m, kk), c in elem.items() if kk == k}


def apply(M, u, v):
    """Bilinear map M = {(a, b): vec} evaluated on vectors u, v (dict index -> coeff)."""
    out = {}
    for a, ca in u.items():
        for b, cb in v.items():
            for k, c in M.get((a, b), {}).items():
                out[k] = out.get(k, 0) + ca * cb * c
    return {k: v for k, v in out.items() if v != 0}


def delta(mu0, par, fmap):
    """Coboundary of an odd linear map f, following docs/math/C_coboundary_definition.md:

    (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X, Y]).

    fmap: {d: vector} giving f(X_d).
    """
    D = len(par)

    def f_of(v):
        out = {}
        for d, cd in v.items():
            for k, c in fmap.get(d, {}).items():
                out[k] = out.get(k, 0) + cd * c
        return {k: v for k, v in out.items() if v != 0}

    res = {}
    for a in range(D):
        for b in range(D):
            pa, pb = par[a], par[b]
            t = {}
            t1 = apply(mu0, {a: Fraction(1)}, f_of({b: Fraction(1)}))
            t2 = apply(mu0, {b: Fraction(1)}, f_of({a: Fraction(1)}))
            t3 = f_of(mu0.get((a, b), {}))
            for k, c in t1.items():
                t[k] = t.get(k, 0) + ((-1) ** pa) * c
            for k, c in t2.items():
                t[k] = t.get(k, 0) - ((-1) ** ((pa + 1) * pb)) * c
            for k, c in t3.items():
                t[k] = t.get(k, 0) - c
            t = {k: v for k, v in t.items() if v != 0}
            if t:
                res[(a, b)] = t
    return res


def jacobi_first_order(mu0, mu1, par):
    """Count violations of the super Jacobi identity at order t^0 (mu0) and t^1 (mu1).

    Jacobi: [X,[Y,Z]] - [[X,Y],Z] - (-1)^{pX pY} [Y,[X,Z]] = 0, with mu = mu0 + t mu1.
    Returns (violations_order0, violations_order1).
    """
    D = len(par)
    bad0 = bad1 = 0
    for a, b, c in product(range(D), repeat=3):
        X, Y, Z = {a: Fraction(1)}, {b: Fraction(1)}, {c: Fraction(1)}
        s = -1 if (par[a] * par[b]) % 2 else 1
        r0 = {}
        r1 = {}

        def acc(dst, v, sc):
            for k, val in v.items():
                dst[k] = dst.get(k, 0) + sc * val

        # order t^0
        acc(r0, apply(mu0, X, apply(mu0, Y, Z)), 1)
        acc(r0, apply(mu0, apply(mu0, X, Y), Z), -1)
        acc(r0, apply(mu0, Y, apply(mu0, X, Z)), -s)
        # order kappa^1, with kappa odd: [X, kappa W] = (-1)^{pX} kappa [X, W]
        # and [kappa W, Z] = kappa [W, Z]
        sX = -1 if par[a] else 1
        sY = -1 if par[b] else 1
        acc(r1, apply(mu1, X, apply(mu0, Y, Z)), 1)
        acc(r1, apply(mu0, X, apply(mu1, Y, Z)), sX)
        acc(r1, apply(mu1, apply(mu0, X, Y), Z), -1)
        acc(r1, apply(mu0, apply(mu1, X, Y), Z), -1)
        acc(r1, apply(mu1, Y, apply(mu0, X, Z)), -s)
        acc(r1, apply(mu0, Y, apply(mu1, X, Z)), -s * sY)
        bad0 += any(v != 0 for v in r0.values())
        bad1 += any(v != 0 for v in r1.values())
    return bad0, bad1


# ---------------------------------------------------------------------------
# Structure constants
# ---------------------------------------------------------------------------

def sym_element(i, j):
    """Weyl super-symmetrised quadratic 1/2 (x_i x_j + s x_j x_i) at kappa = 0,
    with s = -1 for two fermionic oscillators and +1 otherwise.
    Written in the canonical PBW basis: it equals the canonical monomial x_i x_j plus a constant."""
    s = -1 if (i < 2 and j < 2) else 1
    X = {((i,), 0): Fraction(1)}
    Y = {((j,), 0): Fraction(1)}
    P = split(mul(X, Y, None), 0)
    Q = split(mul(Y, X, None), 0)
    E = {}
    for m, c in P.items():
        E[m] = E.get(m, 0) + Fraction(1, 2) * c
    for m, c in Q.items():
        E[m] = E.get(m, 0) + Fraction(s, 2) * c
    E = {m: c for m, c in E.items() if c != 0}
    assert E.get((i, j)) == 1, "canonical monomial must appear with coefficient 1"
    assert all(m == (i, j) or m == () for m in E), "symmetrised element must be quadratic + constant"
    return E


def to_basis(part, basis, consts):
    """Express a kappa^0 or kappa^1 part (canonical PBW monomials) in the basis
    E_a = m_a + consts[a].  Returns (vec over basis indices, central residual)."""
    vec = {}
    rest = dict(part)
    for a, m in enumerate(basis):
        c = rest.pop(m, 0)
        if c != 0:
            vec[a] = c
    const_part = rest.pop((), 0)
    if rest:
        raise ValueError(f"monomials {sorted(rest)} lie outside the g basis (closure failure)")
    resid = const_part - sum(c * consts[a] for a, c in vec.items())
    return vec, resid


def build_structure(n):
    pairs = basis_monomials(n)
    par = [mono_parity(m) for m in pairs]
    syms = [sym_element(i, j) for (i, j) in pairs]
    elems = [{(m, 0): c for m, c in e.items()} for e in syms]
    basis = pairs  # canonical monomial m_a; E_a = m_a + consts[a]
    consts = [e.get((), Fraction(0)) for e in syms]
    D = len(basis)
    G = [(f, b) for f in (0, 1) for b in range(2, 2 + 2 * n)]

    mu0 = {}
    gam = {g: {} for g in G}
    for a in range(D):
        for b in range(D):
            br0 = bracket(elems[a], elems[b], None, par[a], par[b])
            assert not split(br0, 1), "kappa term without deformation parameter"
            v0, r0 = to_basis(split(br0, 0), basis, consts)
            assert r0 == 0, "g is not closed under the undeformed bracket"
            if v0:
                mu0[(a, b)] = v0
                assert all((par[a] + par[b] - par[k]) % 2 == 0 for k in v0), "parity of [X,Y]_0"
            for g in G:
                br = bracket(elems[a], elems[b], g, par[a], par[b])
                v0g, r0g = to_basis(split(br, 0), basis, consts)
                assert v0g == v0 and r0g == 0, "kappa^0 part depends on gb"
                vg, rg = to_basis(split(br, 1), basis, consts)
                # The central constant (identity) is the extra coordinate index D
                if rg != 0:
                    vg[D] = rg
                if vg:
                    gam[g][(a, b)] = vg
                    assert all((par[a] + par[b] + 1 - par[k]) % 2 == 0 for k in vg
                               if k < D), "parity of gamma(X,Y)"
    idx = {m: a for a, m in enumerate(basis)}
    return basis, idx, par, G, mu0, gam


# ---------------------------------------------------------------------------
# Linear algebra (exact, sparse echelon form)
# ---------------------------------------------------------------------------

class Echelon:
    """Row echelon form keyed by leading (smallest) column; rows normalised to lead 1."""

    def __init__(self):
        self.rows = {}

    def insert(self, row):
        row = {k: Fraction(v) for k, v in row.items() if v != 0}
        while row:
            lead = min(row)
            if lead in self.rows:
                f = row[lead]
                for k, v in self.rows[lead].items():
                    nv = row.get(k, 0) - f * v
                    if nv:
                        row[k] = nv
                    else:
                        row.pop(k, None)
            else:
                f = row[lead]
                self.rows[lead] = {k: v / f for k, v in row.items()}
                return


def nullspace(rows, ncols):
    """Basis of {x in Q^ncols : rows . x = 0}; rows is a list of dict col -> value."""
    M = [[Fraction(r.get(c, 0)) for c in range(ncols)] for r in rows]
    piv = []
    r = 0
    for c in range(ncols):
        if r >= len(M):
            break
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [x - f * y for x, y in zip(M[i], M[r])]
        piv.append(c)
        r += 1
    free = [c for c in range(ncols) if c not in piv]
    basis = []
    for fc in free:
        v = [Fraction(0)] * ncols
        v[fc] = Fraction(1)
        for i, pc in enumerate(piv):
            v[pc] = -M[i][fc]
        basis.append(v)
    return basis


def fstr(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


# ---------------------------------------------------------------------------
# Main analysis for one n
# ---------------------------------------------------------------------------

def analyse(n, mode="strict", seed=12345):
    """mode = 'strict':   gamma must equal delta f exactly, including the central
                          (constant) component, which delta f cannot produce.
    mode = 'quotient': the constant component is projected out (gamma taken mod CZ)."""
    assert mode in ("strict", "quotient", "extended")
    basis, idx, par, G, mu0, gam = build_structure(n)
    D = len(basis)
    Zk = D  # index of the central constant in gamma
    if mode == "quotient":
        for g in G:
            for key in list(gam[g]):
                gam[g][key] = {k: v for k, v in gam[g][key].items() if k != Zk}
                if not gam[g][key]:
                    del gam[g][key]
    U = [(c, e) for c in range(D) for e in range(D) if par[c] != par[e]]  # f odd
    if mode == "extended":
        # f may also have a central component f(X_e) ∋ lambda_e * Z; Z is even, so this is
        # allowed only when X_e is odd (keeps f odd).
        U += [(Zk, e) for e in range(D) if par[e] == 1]
    Un = len(U)
    Gn = len(G)
    checks = {}
    checks["central_component_present"] = any(
        Zk in v for g in G for v in gam[g].values())

    # --- Jacobi sanity checks -------------------------------------------------
    rng = random.Random(seed)
    cvec = [Fraction(rng.randint(-3, 3)) for _ in G]
    mu1_rand = {}
    for (a, b) in set(k for g in G for k in gam[g]):
        vec = {}
        for gi, g in enumerate(G):
            for k, v in gam[g].get((a, b), {}).items():
                vec[k] = vec.get(k, 0) + cvec[gi] * v
        vec = {k: v for k, v in vec.items() if v != 0}
        if vec:
            mu1_rand[(a, b)] = vec
    j0, j1 = jacobi_first_order(mu0, mu1_rand, par)
    checks["jacobi_order0_violations (g_0)"] = j0
    checks["jacobi_order1_violations (random gamma)"] = j1

    fr = {}
    for ui, (c, e) in enumerate(U):
        fr.setdefault(e, {})
        fr[e][c] = fr[e].get(c, 0) + Fraction(rng.randint(-2, 2))
    dF_rand = delta(mu0, par, fr)
    jd0, jd1 = jacobi_first_order(mu0, dF_rand, par)
    checks["jacobi_order1_violations (random delta f; tests coboundary sign convention)"] = jd1

    # --- Linear system  delta(phi) - sum_g c_g gamma_g = 0 -------------------
    # columns: phi_u (u in U) first, then c_g
    ech = Echelon()
    rows = {}
    for ui, (c, e) in enumerate(U):
        dF = delta(mu0, par, {e: {c: Fraction(1)}})
        for (a, b), vec in dF.items():
            for k, val in vec.items():
                rows.setdefault((a, b, k), {})[ui] = val
    for gi, g in enumerate(G):
        for (a, b), vec in gam[g].items():
            for k, val in vec.items():
                rows.setdefault((a, b, k), {})[Un + gi] = -val
    for key in sorted(rows):
        ech.insert(rows[key])

    constraints = [ech.rows[l] for l in sorted(ech.rows) if l >= Un]
    cons_dense = [{l - Un: v for l, v in row.items()} for row in constraints]
    T = nullspace(cons_dense, Gn)

    # --- Witness phi for each trivial direction, verified independently -------
    witnesses = []
    for tvec in T:
        vals = {Un + gi: tvec[gi] for gi in range(Gn)}
        for lead in sorted((l for l in ech.rows if l < Un), reverse=True):
            row = ech.rows[lead]
            s = sum(coef * vals.get(k, 0) for k, coef in row.items() if k != lead)
            vals[lead] = -s
        fmap = {}
        for ui, (c, e) in enumerate(U):
            v = vals.get(ui, 0)
            if v:
                fmap.setdefault(e, {})[c] = Fraction(v)
        lhs = delta(mu0, par, fmap)
        ok = True
        for (a, b) in set(lhs) | set(k for g in G for k in gam[g]):
            rhs = {}
            for gi, g in enumerate(G):
                for k, v in gam[g].get((a, b), {}).items():
                    rhs[k] = rhs.get(k, 0) + tvec[gi] * v
            diff = dict(lhs.get((a, b), {}))
            for k, v in rhs.items():
                diff[k] = diff.get(k, 0) - v
            if any(v != 0 for v in diff.values()):
                ok = False
                break
        witnesses.append({
            "c": [fstr(x) for x in tvec],
            "phi_nonzero": {f"{basis_label(basis, c)} <- {basis_label(basis, e)}": fstr(v)
                            for (c, e), v in ((U[ui], vals.get(ui, 0)) for ui in range(Un))
                            if v},
            "verified_delta_f_equals_gamma": ok,
        })
        assert ok, "witness verification failed"

    # Each gb parameter on its own: e_gi lies in T iff every constraint vanishes on it
    single = {}
    for gi, g in enumerate(G):
        triv = all(row.get(gi, 0) == 0 for row in cons_dense)
        single[gb_label(g)] = {"trivial_alone": bool(triv)}

    def res_label(k):
        return mono_label(basis[k]) if k < D else "Z (central, = identity)"

    result = {
        "n": n,
        "mode": mode,
        "dim_g": D,
        "dim_even": sum(1 for p in par if p == 0),
        "dim_odd": sum(1 for p in par if p == 1),
        "num_gb_parameters": Gn,
        "num_odd_f_unknowns": Un,
        "g_basis": [{"index": i, "monomial": mono_label(m), "parity": par[i]}
                    for i, m in enumerate(basis)],
        "gb_parameters": [{"index": gi, "label": gb_label(g), "fermion_osc": osc_label(g[0]),
                           "boson_osc": osc_label(g[1])} for gi, g in enumerate(G)],
        "structure_constants_mu0": [
            {"a": mono_label(basis[a]), "b": mono_label(basis[b]),
             "result": {res_label(k): fstr(v) for k, v in vec.items()}}
            for (a, b), vec in sorted(mu0.items())],
        "gamma": {gb_label(g): [
            {"a": mono_label(basis[a]), "b": mono_label(basis[b]),
             "result": {res_label(k): fstr(v) for k, v in vec.items()}}
            for (a, b), vec in sorted(gam[g].items())] for g in G},
        "checks": checks,
        "triviality_constraints_on_gb": [
            " + ".join(f"({fstr(v)})*{gb_label(G[j])}" for j, v in sorted(row.items()) if v != 0) + " = 0"
            for row in cons_dense],
        "trivial_subspace_dimension": len(T),
        "trivial_subspace_basis": [{gb_label(G[j]): fstr(v) for j, v in enumerate(t) if v != 0}
                                   for t in T],
        "single_parameter_triviality": single,
        "witnesses": witnesses,
        "conclusion": (
            "only gb = 0 is trivial" if len(T) == 0 else
            f"trivial subspace of dimension {len(T)} in gb-space"),
    }
    return result


def basis_label(basis, i):
    return mono_label(basis[i]) if i < len(basis) else "Z"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "artifacts"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    summary = {}
    for n in args.n:
        for mode in ("strict", "quotient", "extended"):
            res = analyse(n, mode)
            path = out / f"cn1_triviality_n{n}_{mode}.json"
            path.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            summary[f"n={n},mode={mode}"] = {
                "dim_g": res["dim_g"],
                "num_gb_parameters": res["num_gb_parameters"],
                "trivial_subspace_dimension": res["trivial_subspace_dimension"],
                "conclusion": res["conclusion"],
                "checks": res["checks"],
                "single_parameter_triviality": res["single_parameter_triviality"],
            }
            print(f"n={n} mode={mode}: dim g={res['dim_g']}, gb params={res['num_gb_parameters']}, "
                  f"dim trivial subspace={res['trivial_subspace_dimension']}")
            print(f"  checks: {res['checks']}")
            print(f"  {res['conclusion']}")
    (out / "cn1_triviality_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "cn1_triviality_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
