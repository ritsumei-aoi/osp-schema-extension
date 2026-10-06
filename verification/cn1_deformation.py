"""
Exact verification engine for the inhomogeneous (gb) deformation of
C(n+1) = osp(2|2n) realised by oscillators inside U(A).

Conventions (docs/math/*.md):
  * A = V + C K + C kappa, K = 1 (even central), kappa odd central, kappa^2 = 0.
  * {a^-, a^+} = 1, (a^+)^2 = (a^-)^2 = 0, [b_k^-, b_l^+] = delta_kl.
  * Deformation:  [b_j^s, a^sigma] = - gb[sigma, j, s] * kappa.
  * Deformed bracket on g:  [X, Y]_gb = [X, Y]_0 + kappa * gamma(X, Y).
  * Coboundary of an odd f: g -> g:
      (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X, Y]).

All arithmetic on the oscillator side is exact (fractions.Fraction).
Words are normal ordered as  kappa < a^+ < a^- < b_1^+ < b_1^- < ... < b_n^-.

Usage:  python3 verification/cn1_deformation.py        (writes verification/artifacts/*.json)
"""

from fractions import Fraction as Fr
import itertools
import json
import os
import random

import numpy as np
import sympy

SIGNS = ("+", "-")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")


# ---------------------------------------------------------------------------
# Oscillator superalgebra U(A_gb) with kappa^2 = 0
# ---------------------------------------------------------------------------

class OscillatorAlgebra:
    KAPPA, AP, AM = 0, 1, 2

    def __init__(self, n, gb=None):
        self.n = n
        self.gb = {k: Fr(v) for k, v in (gb or {}).items() if v != 0}
        self.names = ["kappa", "a+", "a-"]
        self.par = [1, 1, 1]
        for j in range(1, n + 1):
            self.names += [f"b{j}+", f"b{j}-"]
            self.par += [0, 0]
        self._cache = {}

    def b(self, j, s):
        return 3 + 2 * (j - 1) + (0 if s == "+" else 1)

    def b_label(self, idx):
        j = (idx - 3) // 2 + 1
        s = "+" if (idx - 3) % 2 == 0 else "-"
        return j, s

    def a_sign(self, idx):
        return "+" if idx == self.AP else "-"

    def gen_scomm(self, x, y):
        """Supercommutator [x, y] of generators with x > y, as a polynomial."""
        if y == self.KAPPA:
            return {}
        if x == self.AM and y == self.AP:
            return {(): Fr(1)}
        if x >= 3 and y in (self.AP, self.AM):
            j, s = self.b_label(x)
            g = self.gb.get((self.a_sign(y), j, s), 0)
            return {(self.KAPPA,): -g} if g else {}
        if x >= 3 and y >= 3:
            jx, sx = self.b_label(x)
            jy, sy = self.b_label(y)
            if jx == jy and sx == "-" and sy == "+":
                return {(): Fr(1)}
            return {}
        raise ValueError((x, y))

    def normal(self, word):
        word = tuple(word)
        if word in self._cache:
            return self._cache[word]
        res = None
        if sum(1 for w in word if w == self.KAPPA) >= 2:
            res = {}
        else:
            for i in range(len(word) - 1):
                x, y = word[i], word[i + 1]
                if x == y and self.par[x] == 1:
                    res = {}
                    break
                if x > y:
                    res = {}
                    sign = -1 if self.par[x] * self.par[y] else 1
                    _add(res, self.normal(word[:i] + (y, x) + word[i + 2:]), sign)
                    for w, c in self.gen_scomm(x, y).items():
                        _add(res, self.normal(word[:i] + w + word[i + 2:]), c)
                    break
            if res is None:
                res = {word: Fr(1)}
        self._cache[word] = res
        return res

    def mul(self, P, Q):
        res = {}
        for w1, c1 in P.items():
            for w2, c2 in Q.items():
                _add(res, self.normal(w1 + w2), c1 * c2)
        return res

    def parity(self, P):
        ps = {sum(self.par[g] for g in w) % 2 for w in P}
        assert len(ps) <= 1, P
        return ps.pop() if ps else 0

    def scomm(self, P, Q):
        sgn = -1 if self.parity(P) * self.parity(Q) else 1
        res = self.mul(P, Q)
        _add(res, self.mul(Q, P), -sgn)
        return res

    def poly_str(self, P):
        return [[[self.names[g] for g in w], str(c)] for w, c in sorted(P.items())]


def _add(acc, P, c=1):
    for w, v in P.items():
        nv = acc.get(w, 0) + c * v
        if nv:
            acc[w] = nv
        else:
            acc.pop(w, None)


# ---------------------------------------------------------------------------
# Basis of g = C(n+1) (super-symmetrised / Weyl-ordered quadratics)
# ---------------------------------------------------------------------------

class CBasis:
    def __init__(self, n):
        self.n = n
        alg = OscillatorAlgebra(n)
        self.alg0 = alg
        bidx = [alg.b(j, s) for j in range(1, n + 1) for s in SIGNS]
        self.labels, self.parity, self.lifts, self.roots = [], [], [], []
        # even part: sp(2n)
        for p, q in itertools.combinations_with_replacement(bidx, 2):
            P = {}
            _add(P, alg.normal((p, q)), Fr(1, 2))
            _add(P, alg.normal((q, p)), Fr(1, 2))
            (jp, sp_), (jq, sq) = alg.b_label(p), alg.b_label(q)
            self._push(f"S(b{jp}{sp_},b{jq}{sq})", 0, P,
                       _root(0, {jp: _sg(sp_)}, {jq: _sg(sq)}, n))
        # even part: so(2)
        P = {}
        _add(P, alg.normal((alg.AP, alg.AM)), Fr(1, 2))
        _add(P, alg.normal((alg.AM, alg.AP)), Fr(-1, 2))
        self._push("J", 0, P, _root(0, {}, {}, n))
        # odd part
        for a in (alg.AP, alg.AM):
            for p in bidx:
                jp, sp_ = alg.b_label(p)
                self._push(f"O(a{alg.a_sign(a)},b{jp}{sp_})", 1, alg.normal((a, p)),
                           _root(_sg(alg.a_sign(a)), {jp: _sg(sp_)}, {}, n))
        self.dim = len(self.labels)
        self.even = [i for i in range(self.dim) if self.parity[i] == 0]
        self.odd = [i for i in range(self.dim) if self.parity[i] == 1]
        # leading monomial -> (basis index, scalar offset)
        self._lead = {}
        for i, P in enumerate(self.lifts):
            lead = [w for w in P if len(w) == 2]
            assert len(lead) == 1 and P[lead[0]] == 1
            self._lead[lead[0]] = (i, P.get((), Fr(0)))

    def _push(self, label, par, P, root):
        self.labels.append(label)
        self.parity.append(par)
        self.lifts.append(P)
        self.roots.append(root)

    def decompose(self, P):
        """kappa-free normal-ordered P (degree <= 2) -> ({basis idx: coef}, scalar)."""
        vec, scalar = {}, P.get((), Fr(0))
        for w, c in P.items():
            if w == ():
                continue
            if w not in self._lead:
                raise ValueError(f"monomial outside g + C: {w}")
            i, off = self._lead[w]
            vec[i] = vec.get(i, 0) + c
            scalar -= c * off
        return {i: c for i, c in vec.items() if c}, scalar


def _sg(s):
    return 1 if s == "+" else -1


def _root(eps, d1, d2, n):
    delta = [0] * n
    for d in (d1, d2):
        for j, v in d.items():
            delta[j - 1] += v
    return {"eps": eps, "delta": delta}


def split_kappa(P):
    free, kap = {}, {}
    for w, c in P.items():
        if w and w[0] == OscillatorAlgebra.KAPPA:
            assert OscillatorAlgebra.KAPPA not in w[1:]
            kap[w[1:]] = c
        else:
            assert OscillatorAlgebra.KAPPA not in w
            free[w] = c
    return free, kap


# ---------------------------------------------------------------------------
# Deformed brackets: structure constants and gamma
# ---------------------------------------------------------------------------

def compute_brackets(B, gb):
    """Return (C, C_scalar, G, G_scalar) as dicts keyed by (i, j)."""
    alg = OscillatorAlgebra(B.n, gb)
    C, Cs, G, Gs = {}, {}, {}, {}
    for i in range(B.dim):
        for j in range(B.dim):
            free, kap = split_kappa(alg.scomm(B.lifts[i], B.lifts[j]))
            C[i, j], Cs[i, j] = B.decompose(free)
            G[i, j], Gs[i, j] = B.decompose(kap)
    return C, Cs, G, Gs


def gb_params(n):
    return [(sig, j, s) for sig in SIGNS for j in range(1, n + 1) for s in SIGNS]


def gb_name(k):
    return f"gb[a{k[0]},b{k[1]}{k[2]}]"


# ---------------------------------------------------------------------------
# Explicit trivialising map (Theorem):  f = -F,
#   F(S) = 0,  F(O(a^sig, b)) = L_sig b,  F(J) = a^- L_+ - a^+ L_-,
#   L_sig = sum_j ( gb[sig,j,-] b_j^+ - gb[sig,j,+] b_j^- ).
# ---------------------------------------------------------------------------

def L_poly(alg, gb, sig):
    P = {}
    for j in range(1, alg.n + 1):
        _add(P, {(alg.b(j, "+"),): Fr(1)}, Fr(gb.get((sig, j, "-"), 0)))
        _add(P, {(alg.b(j, "-"),): Fr(1)}, -Fr(gb.get((sig, j, "+"), 0)))
    return P


def explicit_F(B, gb):
    """F(Z_j) as ({i: coef}, scalar) for each basis index j."""
    alg = B.alg0
    Lp, Lm = L_poly(alg, gb, "+"), L_poly(alg, gb, "-")
    F = {}
    for j, lab in enumerate(B.labels):
        if lab.startswith("S("):
            F[j] = ({}, Fr(0))
        elif lab == "J":
            P = alg.mul({(alg.AM,): Fr(1)}, Lp)
            _add(P, alg.mul({(alg.AP,): Fr(1)}, Lm), -1)
            F[j] = B.decompose(P)
        else:
            sig = lab[3]
            w = [m for m in B.lifts[j]][0]
            P = alg.mul(Lp if sig == "+" else Lm, {(w[1],): Fr(1)})
            F[j] = B.decompose(P)
    return F


def F_by_substitution(B, gb):
    """Independent derivation: X(a + kappa L, b) = X(a, b) + kappa F(X) in U(A_gb)."""
    alg = OscillatorAlgebra(B.n, gb)
    sub = {alg.AP: {(alg.AP,): Fr(1)}, alg.AM: {(alg.AM,): Fr(1)}}
    for a, sig in ((alg.AP, "+"), (alg.AM, "-")):
        for w, c in L_poly(alg, gb, sig).items():
            sub[a][(alg.KAPPA,) + w] = c
    F = {}
    for j, P in enumerate(B.lifts):
        Q = {}
        for w, c in P.items():
            term = {(): Fr(1)}
            for g in w:
                term = alg.mul(term, sub.get(g, {(g,): Fr(1)}))
            _add(Q, term, c)
        free, kap = split_kappa(Q)
        _add(free, P, -1)
        assert not free
        F[j] = B.decompose(kap)
    return F


def delta_f(B, C, f, with_scalar=False):
    """(delta f)(Z_a, Z_b) for f given as {j: ({i: coef}, scalar)}."""
    def br(x, vec):  # [Z_x, v]
        out = {}
        for i, c in vec.items():
            for k, v in C[x, i].items():
                out[k] = out.get(k, 0) + c * v
        return out

    def fvec(vec):
        out, sc = {}, Fr(0)
        for i, c in vec.items():
            vi, si = f[i]
            for k, v in vi.items():
                out[k] = out.get(k, 0) + c * v
            sc += c * si
        return out, sc

    res = {}
    for a in range(B.dim):
        for b in range(B.dim):
            pa, pb = B.parity[a], B.parity[b]
            out = {}
            for k, v in br(a, f[b][0]).items():
                out[k] = out.get(k, 0) + (-1) ** pa * v
            for k, v in br(b, f[a][0]).items():
                out[k] = out.get(k, 0) - (-1) ** ((pa + 1) * pb) * v
            fv, fs = fvec(C[a, b])
            for k, v in fv.items():
                out[k] = out.get(k, 0) - v
            res[a, b] = ({k: v for k, v in out.items() if v}, -fs if with_scalar else Fr(0))
    return res


def neg(f):
    return {j: ({i: -c for i, c in v.items()}, -s) for j, (v, s) in f.items()}


# ---------------------------------------------------------------------------
# Linear-algebra checks (coboundary matrix)
# ---------------------------------------------------------------------------

def coboundary_matrix(B, C):
    """Matrix of f -> delta f restricted to odd f, rows (a<=b, c), floats."""
    unk = [(i, j) for j in range(B.dim) for i in range(B.dim) if B.parity[i] != B.parity[j]]
    col = {u: k for k, u in enumerate(unk)}
    rows = [(a, b, c) for a in range(B.dim) for b in range(a, B.dim) for c in range(B.dim)
            if B.parity[c] == (B.parity[a] + B.parity[b] + 1) % 2]
    rix = {r: k for k, r in enumerate(rows)}
    M = np.zeros((len(rows), len(unk)))
    for a in range(B.dim):
        for b in range(a, B.dim):
            pa, pb = B.parity[a], B.parity[b]
            # (-1)^pa [Z_a, f(Z_b)] : f(Z_b) = sum_i phi_{i b} Z_i
            for i in range(B.dim):
                if B.parity[i] == pb:
                    continue
                for c, v in C[a, i].items():
                    M[rix[a, b, c], col[i, b]] += (-1) ** pa * float(v)
            # -(-1)^{(pa+1)pb} [Z_b, f(Z_a)]
            for i in range(B.dim):
                if B.parity[i] == pa:
                    continue
                for c, v in C[b, i].items():
                    M[rix[a, b, c], col[i, a]] -= (-1) ** ((pa + 1) * pb) * float(v)
            for k, v in C[a, b].items():
                for c in range(B.dim):
                    if B.parity[c] != B.parity[k]:
                        M[rix[a, b, c], col[c, k]] -= float(v)
    return M, rows, unk


def cochain_vector(B, rows, G):
    return np.array([float(G[a, b].get(c, 0)) for (a, b, c) in rows])


def check_jacobi_deformed(B, C, G):
    """First-order super-Jacobi of [X,Y]_0 + kappa*gamma on L = g + kappa g (mod kappa^2).

    kappa-component of  [X,[Y,Z]] - [[X,Y],Z] - (-1)^{pXpY} [Y,[X,Z]]  must vanish.
    With [U, kappa W] = (-1)^{pU} kappa [U, W] and [kappa W, U] = kappa [W, U].
    """
    def br(x, vec):
        out = {}
        for i, c in vec.items():
            for k, v in C[x, i].items():
                out[k] = out.get(k, 0) + c * v
        return out

    def brl(vec, z):
        out = {}
        for i, c in vec.items():
            for k, v in C[i, z].items():
                out[k] = out.get(k, 0) + c * v
        return out

    def gam(x, vec):
        out = {}
        for i, c in vec.items():
            for k, v in G[x, i].items():
                out[k] = out.get(k, 0) + c * v
        return out

    def gaml(vec, z):
        out = {}
        for i, c in vec.items():
            for k, v in G[i, z].items():
                out[k] = out.get(k, 0) + c * v
        return out

    bad = 0
    for x, y, z in itertools.product(range(B.dim), repeat=3):
        px, py = B.parity[x], B.parity[y]
        tot = {}

        def acc(d, s):
            for k, v in d.items():
                tot[k] = tot.get(k, 0) + s * v
        # [X,[Y,Z]_g]: gamma(X, [Y,Z]_0) + (-1)^pX [X, gamma(Y,Z)]_0
        acc(gam(x, C[y, z]), 1)
        acc(br(x, G[y, z]), (-1) ** px)
        # [[X,Y]_g, Z]: gamma([X,Y]_0, Z) + [gamma(X,Y), Z]_0
        acc(gaml(C[x, y], z), -1)
        acc(brl(G[x, y], z), -1)
        # (-1)^{pXpY} [Y,[X,Z]_g]
        s = (-1) ** (px * py)
        acc(gam(y, C[x, z]), -s)
        acc(br(y, G[x, z]), -s * (-1) ** py)
        if any(v != 0 for v in tot.values()):
            bad += 1
    return bad


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def sparse3(D):
    return [[a, b, k, str(v)] for (a, b), vec in sorted(D.items()) for k, v in sorted(vec.items())]


def sparse2(D):
    return [[a, b, str(v)] for (a, b), v in sorted(D.items()) if v != 0]


def eq_cochain(X, Y, B, scalar=False):
    for a in range(B.dim):
        for b in range(B.dim):
            if X[a, b][0] != Y[a, b][0]:
                return False
            if scalar and X[a, b][1] != Y[a, b][1]:
                return False
    return True


def run(n, rng):
    B = CBasis(n)
    params = gb_params(n)
    C, Cs, G0, G0s = compute_brackets(B, {})
    report = {"n": n, "algebra": f"C({n + 1}) = osp(2|{2 * n})",
              "dim_even": len(B.even), "dim_odd": len(B.odd), "dim": B.dim}
    report["undeformed_closure_no_scalar"] = all(v == 0 for v in Cs.values())
    report["undeformed_gamma_zero"] = all(not v for v in G0.values()) and all(v == 0 for v in G0s.values())
    report["undeformed_jacobi_violations"] = check_jacobi_deformed(B, C, G0)

    M, rows, unk = coboundary_matrix(B, C)
    sv = np.linalg.svd(M, compute_uv=False)
    rank = int((sv > 1e-9 * sv[0]).sum())
    report["coboundary_matrix_shape"] = list(M.shape)
    report["coboundary_rank"] = rank
    report["odd_1cocycle_dim(nullity)"] = M.shape[1] - rank

    per_param, scalar_cols = {}, []
    for k in params:
        gb = {k: 1}
        _, _, G, Gs = compute_brackets(B, gb)
        Gfull = {ab: (G[ab], Gs[ab]) for ab in G}
        F_exp = explicit_F(B, gb)
        F_sub = F_by_substitution(B, gb)
        f = neg(F_exp)
        dF = delta_f(B, C, f, with_scalar=True)
        g_vec = cochain_vector(B, rows, G)
        phi, *_ = np.linalg.lstsq(M, g_vec, rcond=None)
        resid = float(np.linalg.norm(M @ phi - g_vec))
        entry = {
            "gamma_g_part": sparse3(G),
            "gamma_scalar_part": sparse2(Gs),
            "gamma_is_zero_mod_scalars": all(not v for v in G.values()),
            "jacobi_violations_mod_scalars": check_jacobi_deformed(B, C, G),
            "explicit_f": [[j, i, str(-c)] for j, (v, s) in sorted(F_exp.items()) for i, c in sorted(v.items())],
            "explicit_f_scalar_part": [[j, str(-s)] for j, (v, s) in sorted(F_exp.items()) if s != 0],
            "explicit_formula_equals_substitution": all(F_exp[j] == F_sub[j] for j in F_exp),
            "gamma_eq_delta_f_mod_scalars(exact)": eq_cochain(Gfull, dF, B),
            "gamma_eq_delta_f_with_scalar_valued_f(exact)": eq_cochain(Gfull, dF, B, scalar=True),
            "lstsq_residual": resid,
        }
        per_param[gb_name(k)] = entry
        scalar_cols.append([Gs[a, b] for a in range(B.dim) for b in range(B.dim)])

    # random rational combination: everything is linear in gb, check directly anyway
    gb_rand = {k: Fr(rng.randint(-9, 9), rng.randint(1, 5)) for k in params}
    _, _, G, Gs = compute_brackets(B, gb_rand)
    dF = delta_f(B, C, neg(explicit_F(B, gb_rand)), with_scalar=True)
    report["random_gb"] = {gb_name(k): str(v) for k, v in gb_rand.items()}
    report["random_gb_gamma_eq_delta_f_mod_scalars"] = eq_cochain({ab: (G[ab], Gs[ab]) for ab in G}, dF, B)
    report["random_gb_gamma_eq_delta_f_with_scalar"] = eq_cochain({ab: (G[ab], Gs[ab]) for ab in G}, dF, B, scalar=True)

    # negative controls: the checks must be able to fail
    k0 = params[0]
    _, _, G, Gs = compute_brackets(B, {k0: 1})
    Gfull = {ab: (G[ab], Gs[ab]) for ab in G}
    wrong_sign = delta_f(B, C, explicit_F(B, {k0: 1}))
    Gpert = {ab: dict(v) for ab, v in G.items()}
    a_, b_ = B.even[0], B.odd[0]
    Gpert[a_, b_][b_] = Gpert[a_, b_].get(b_, 0) + 1
    Gpert[b_, a_][b_] = Gpert[b_, a_].get(b_, 0) - 1
    report["negative_controls"] = {
        "wrong_sign_f_accepted": eq_cochain(Gfull, wrong_sign, B),
        "zero_f_accepted": eq_cochain(Gfull, delta_f(B, C, {j: ({}, Fr(0)) for j in range(B.dim)}), B),
        "perturbed_gamma_jacobi_violations": check_jacobi_deformed(B, C, Gpert),
    }

    # strict reading: f: g -> g (no scalar component), gamma taken with its scalar part
    S = sympy.Matrix(scalar_cols).T  # rows: pairs, cols: gb params
    report["strict_scalar_obstruction_rank"] = int(S.rank())
    report["strict_reading_only_gb_zero"] = int(S.rank()) == len(params)

    report["per_param"] = per_param
    report["all_params_trivial_mod_scalars"] = all(
        e["gamma_eq_delta_f_mod_scalars(exact)"] for e in per_param.values())
    report["all_params_nonzero_gamma"] = all(not e["gamma_is_zero_mod_scalars"] for e in per_param.values())

    data = {
        "basis": [{"index": i, "label": B.labels[i], "parity": B.parity[i], "root": B.roots[i],
                   "oscillator_lift": B.alg0.poly_str(B.lifts[i])} for i in range(B.dim)],
        "gb_parameters": [gb_name(k) for k in params],
        "structure_constants": sparse3(C),
        "conventions": {
            "bracket": "[Z_i, Z_j]_0 = sum_k c[i,j,k] Z_k; entries [i, j, k, c]",
            "gamma": "kappa-coefficient: [Z_i,Z_j]_gb = [Z_i,Z_j]_0 + kappa*gamma(Z_i,Z_j); entries [i,j,k,coef] for gb param = 1",
            "gamma_scalar_part": "component of gamma along the unit K = 1 (killed by ad); entries [i,j,coef]",
            "explicit_f": "f(Z_j) = sum_i phi[i,j] Z_i; entries [j, i, phi]; gamma = delta f",
            "deformation": "[b_j^s, a^sigma] = -gb[a^sigma, b_j^s] * kappa",
        },
    }
    data.update(report)
    return data


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rng = random.Random(20261006)
    summary = {}
    for n in (1, 2, 3):
        d = run(n, rng)
        with open(os.path.join(OUT_DIR, f"cn1_n{n}.json"), "w") as fh:
            json.dump(d, fh, indent=1)
        s = {k: v for k, v in d.items()
             if k not in ("basis", "structure_constants", "per_param", "conventions", "random_gb")}
        s["per_param_checks"] = {
            p: {k: v for k, v in e.items()
                if k not in ("gamma_g_part", "gamma_scalar_part", "explicit_f", "explicit_f_scalar_part")}
            for p, e in d["per_param"].items()}
        summary[f"n={n}"] = s
        print(json.dumps({k: v for k, v in s.items() if k != "per_param_checks"}, indent=1))
        bad = [p for p, e in s["per_param_checks"].items()
               if not (e["gamma_eq_delta_f_mod_scalars(exact)"] and e["explicit_formula_equals_substitution"]
                       and e["jacobi_violations_mod_scalars"] == 0)]
        print("per-param failures:", bad)
    with open(os.path.join(OUT_DIR, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)


if __name__ == "__main__":
    main()
