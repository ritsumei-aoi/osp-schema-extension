#!/usr/bin/env python3
"""Independent check of the four (kappa-sign, K) combinations for C(n+1).

Written from scratch from the definition documents (no Worker or subagent code):
  - oscillators: a+ a- odd (CAR {a-,a+}=1, a+^2=a-^2=0); b_k+ b_k- even (CCR [b_k-,b_l+]=delta)
  - undeformed: a and b (anti)commute trivially, i.e. b a = a b
  - deformed:   [b_j^s, a^sigma] = -gb_{sigma,j,s} kappa, i.e. b a = a b - gb kappa
  - kappa odd, kappa^2 = 0. SIGN=True: kappa supercommutes (x kappa = (-1)^p(x) kappa x),
    moved to the left; SIGN=False: kappa commutes with everything.
  - [X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y); gamma expanded in the basis of g plus K (=1).
  - delta f(X,Y) = (-1)^p(X) [X,f(Y)] - (-1)^((p(X)+1)p(Y)) [Y,f(X)] - f([X,Y]), f odd, g -> g.
  - KEEP_K=True: the K component of gamma must also match (delta f has none);
    KEEP_K=False: K components are dropped ("up to scalar").
Triviality of all gb directions <=> rank[A|G] == rank A.
"""
import itertools
import sys
from fractions import Fraction as F

n = int(sys.argv[1])
A_P, A_M = ("a", "+"), ("a", "-")
def bp(k): return ("b%d" % k, "+")
def bm(k): return ("b%d" % k, "-")
def is_ferm(x): return x[0] == "a"

# ---------- oscillator words: dict (word tuple, kappa flag) -> Fraction ----------
def okey(x):
    """Canonical order: all fermions (a) left of all bosons (b); within each
    species creators left of annihilators. With this order every generator
    realization (a^s b^t, a+ a-, b b) is written in canonical form, so the
    deformation b a = a b - gb kappa is applied consistently both in products
    and in the realizations themselves. (An earlier version put creators of
    both species first; then a- b+ realizations were normal-ordered without
    the deformation, which flipped the sign of some K components.)"""
    name, s = x
    return (0 if name == "a" else 1, 0 if s == "+" else 1, 0 if name == "a" else int(name[1:]))

def normal(word, deformed, sign, gbval, kappa=False, coef=F(1), out=None):
    """Normal-order coef * (kappa?) * word into out."""
    if out is None:
        out = {}
    w = list(word)
    for i in range(len(w) - 1):
        x, y = w[i], w[i + 1]
        if okey(x) <= okey(y):
            if x == y and is_ferm(x):
                return out  # a+^2 = a-^2 = 0
            continue
        pre, suf = tuple(w[:i]), tuple(w[i + 2:])
        # swap with graded sign
        s = -1 if (is_ferm(x) and is_ferm(y)) else 1
        normal(pre + (y, x) + suf, deformed, sign, gbval, kappa, coef * s, out)
        # contractions
        if x == A_M and y == A_P:            # a- a+ = 1 - a+ a-
            normal(pre + suf, deformed, sign, gbval, kappa, coef, out)
        if x[0].startswith("b") and y[0].startswith("b") and x[0] == y[0] and x[1] == "-" and y[1] == "+":
            normal(pre + suf, deformed, sign, gbval, kappa, coef, out)   # b- b+ = b+ b- + 1
        if deformed and not kappa and ((x[0].startswith("b") and is_ferm(y)) or (is_ferm(x) and y[0].startswith("b"))):
            # [b,a] = b a - a b = -gb kappa:  b a = a b - gb kappa,  a b = b a + gb kappa
            if is_ferm(y):
                g, c = gbval(y, x), -1
            else:
                g, c = gbval(x, y), 1
            if g:
                c = c * g * coef
                if sign and sum(is_ferm(z) for z in pre) % 2:
                    c = -c                    # move kappa left past the fermions in pre
                normal(pre + suf, deformed, sign, gbval, True, c, out)
        return out
    key = (tuple(w), kappa)
    out[key] = out.get(key, 0) + coef
    if out[key] == 0:
        del out[key]
    return out

def poly_mul(P, Q, deformed, sign, gbval):
    out = {}
    for (w1, k1), c1 in P.items():
        for (w2, k2), c2 in Q.items():
            if k1 and k2:
                continue
            c = c1 * c2
            if k2 and not k1 and sign and sum(is_ferm(z) for z in w1) % 2:
                c = -c                        # move kappa of Q left past w1
            normal(w1 + w2, deformed, sign, gbval, k1 or k2, c, out)
    return out

# ---------- generators (Cn1_definition.md, normalization 1/2 for long roots) ----------
gens, parity = {}, {}
def P(*terms):  # terms: (coef, word)
    d = {}
    for c, w in terms:
        d[(tuple(w), False)] = d.get((tuple(w), False), 0) + F(c)
    return d
gens["H1"] = P((1, [A_P, A_M]), (1, [bp(1), bm(1)]))
for k in range(2, n + 1):
    gens["H%d" % k] = P((1, [bp(k - 1), bm(k - 1)]), (-1, [bp(k), bm(k)]))
gens["H%d" % (n + 1)] = P((-1, [bp(n), bm(n)]), (F(-1, 2), []))
for k in range(1, n + 1):
    gens["E2d%d+" % k] = P((F(1, 2), [bp(k), bp(k)]))
    gens["E2d%d-" % k] = P((F(1, 2), [bm(k), bm(k)]))
for i in range(1, n + 1):
    for j in range(i + 1, n + 1):
        for si, bi in (("+", bp), ("-", bm)):
            for sj, bj in (("+", bp), ("-", bm)):
                gens["E%d%s%d%s" % (i, si, j, sj)] = P((1, [bi(i), bj(j)]))
even = list(gens)
for k in range(1, n + 1):
    for se, a in (("+", A_P), ("-", A_M)):
        for sd, b in (("+", bp), ("-", bm)):
            gens["F%s%d%s" % (se, k, sd)] = P((1, [a, b(k)]))
odd = [g for g in gens if g not in even]
basis = even + odd
for g in even: parity[g] = 0
for g in odd: parity[g] = 1
assert len(even) == 2 * n * n + n + 1 and len(odd) == 4 * n

def normalize(Pd):
    out = {}
    for (w, k), c in Pd.items():
        normal(w, False, False, None, k, c, out)
    return out

GEN = {}
for g in basis:
    GEN[g] = gens[g]
GEN = {g: normalize(GEN[g]) for g in basis}
COLS = [GEN[g] for g in basis] + [{((), False): F(1)}]
LABELS = basis + ["K"]

def solve_coords(target):
    """Return coords (dict label->Fraction) with sum c_i COLS_i = target, or raise."""
    monos = sorted({w for c in COLS for (w, _k) in c} | {w for (w, _k) in target})
    # Gaussian elimination on augmented system
    M = [[c.get((m, False), F(0)) for c in COLS] + [target.get((m, False), F(0))] for m in monos]
    ncol = len(COLS)
    piv_cols, r = [], 0
    for c in range(ncol):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        inv = 1 / M[r][c]
        M[r] = [v * inv for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        piv_cols.append(c); r += 1
    for i in range(r, len(M)):
        if M[i][-1] != 0:
            raise ValueError("not in span of basis + K")
    return {LABELS[c]: M[i][-1] for i, c in enumerate(piv_cols) if M[i][-1] != 0}

def graded_bracket(X, Y, deformed, sign, gbval):
    PX, PY = GEN[X], GEN[Y]
    s = -1 if parity[X] * parity[Y] else 1
    out = poly_mul(PX, PY, deformed, sign, gbval)
    for k, v in poly_mul(PY, PX, deformed, sign, gbval).items():
        out[k] = out.get(k, 0) - s * v
        if out[k] == 0:
            del out[k]
    return out

# undeformed structure constants
SC = {}
for X in basis:
    for Y in basis:
        br = graded_bracket(X, Y, False, False, None)
        co = solve_coords(br)
        assert "K" not in co or co["K"] == 0, (X, Y, co)  # undeformed closes in g
        SC[(X, Y)] = {z: c for z, c in co.items() if z != "K"}

gb_params = [(sg, k, sb) for sg in "+-" for k in range(1, n + 1) for sb in "+-"]

def gamma_for(param, sign):
    def gbval(a, b):
        return F(1) if (a[1], int(b[0][1:]), b[1]) == param else F(0)
    G = {}
    for X in basis:
        for Y in basis:
            br = graded_bracket(X, Y, True, sign, gbval)
            kap = {(w, False): c for (w, k), c in br.items() if k}
            for z, c in solve_coords(kap).items():
                G[(X, Y, z)] = c
    return G

# delta f matrix: columns phi_(t <- s) with p(t) != p(s)
phis = [(t, s) for s in basis for t in basis if parity[t] != parity[s]]
def br_g(x, y):
    return SC[(x, y)]
Dcols = {}
for X in basis:
    for Y in basis:
        row = {}
        for (t, s) in phis:
            if s == Y:
                for z, c in br_g(X, t).items():
                    row[(z, (t, s))] = row.get((z, (t, s)), 0) + (-1) ** parity[X] * c
            if s == X:
                for z, c in br_g(Y, t).items():
                    row[(z, (t, s))] = row.get((z, (t, s)), 0) - (-1) ** ((parity[X] + 1) * parity[Y]) * c
        for w, c in br_g(X, Y).items():
            for (t, s) in phis:
                if s == w:
                    row[(t, (t, s))] = row.get((t, (t, s)), 0) - c
        for (z, ph), c in row.items():
            if c:
                Dcols.setdefault(ph, {})[(X, Y, z)] = Dcols.get(ph, {}).get((X, Y, z), 0) + c

def rank(columns):
    """Exact rank of a list of sparse column vectors (dict row->Fraction)."""
    pivots = {}   # pivot row -> reduced column
    r = 0
    for col in columns:
        v = {k: x for k, x in col.items() if x}
        while v:
            pr = min(v)
            if pr in pivots:
                pv = pivots[pr]
                f = v[pr] / pv[pr]
                for k, x in pv.items():
                    nv = v.get(k, 0) - f * x
                    if nv:
                        v[k] = nv
                    else:
                        v.pop(k, None)
            else:
                pivots[pr] = v
                r += 1
                break
    return r

A = list(Dcols.values())
rA = rank(A)
for sign in (True, False):
    Gs = [gamma_for(p, sign) for p in gb_params]
    for keep_k in (True, False):
        cols = []
        for G in Gs:
            cols.append({k: v for k, v in G.items() if keep_k or k[2] != "K"})
        rAG = rank(A + cols)
        rG = rank(cols)
        print(f"n={n} sign={'super' if sign else 'none ':5} K={'keep' if keep_k else 'drop'}: "
              f"rank A={rA} rank[A|G]={rAG} rank G={rG} -> "
              f"{'all gb trivial' if rAG == rA else 'only gb=0 trivial' if rAG - rA == len(gb_params) else 'partial'}")
