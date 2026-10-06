#!/usr/bin/env python3
"""Triviality of the inhomogeneous (gb) deformation of C(n+1)=osp(2|2n).

Model (docs/math/*.md): U(A) with oscillators a^+,a^- (odd), b_k^+,b_k^- (even),
central odd kappa (kappa^2 = 0), relations
  [b^-_k,b^+_l]=delta_kl, {a^-,a^+}=1, [b_j^s,a^sigma] = -gb[sigma,j,s]*kappa.
g = span of supersymmetrised quadratics Z=(1/2)(uv+(-1)^{p(u)p(v)}vu) (in U(A)).
[Z_i,Z_j] = sum_k c_ij^k Z_k + kappa*(sum_k gamma_ij^k Z_k + s_ij*1).
gamma is linear in gb.  Then solve  gamma_gb = delta f  (f odd) by exact linear algebra.

Usage: python3 verify_triviality.py [n ...]   -> writes artifacts/cn1_n{n}.json
"""
import itertools, json, os, sys
from fractions import Fraction as Fr
import numpy as np
import sympy
from sympy.polys.matrices import DomainMatrix
from sympy import QQ

# ---------------------------------------------------------------- algebra U(A)
# generator labels: ('a','+'),('a','-'),('b',k,'+'),('b',k,'-'),('K',)  (K = kappa)
def gens(n):
    g = [('a', '+'), ('a', '-')]
    for k in range(1, n + 1):
        g += [('b', k, '+'), ('b', k, '-')]
    g.append(('K',))
    return g

class Alg:
    def __init__(self, n, gb):
        """gb: dict {(sigma,j,s): number}; missing keys = 0."""
        self.n, self.gb = n, gb
        self.G = gens(n)
        self.idx = {g: i for i, g in enumerate(self.G)}
        self.par = [1 if g[0] in ('a', 'K') else 0 for g in self.G]
        self.memo = {}

    def sc(self, i, j):
        """supercommutator [x_i,x_j] as dict {monomial tuple: coeff}."""
        gi, gj = self.G[i], self.G[j]
        K = self.idx[('K',)]
        if gi[0] == 'K' or gj[0] == 'K':
            return {}
        if gi[0] == 'a' and gj[0] == 'a':
            return {(): Fr(1)} if gi[1] != gj[1] else {}
        if gi[0] == 'b' and gj[0] == 'b':
            if gi[1] != gj[1] or gi[2] == gj[2]:
                return {}
            return {(): Fr(1) if gi[2] == '-' else Fr(-1)}
        if gi[0] == 'b':   # [b_j^s, a^sigma] = -gb kappa
            c = -Fr(self.gb.get((gj[1], gi[1], gi[2]), 0))
        else:              # [a^sigma, b_j^s] = +gb kappa
            c = Fr(self.gb.get((gi[1], gj[1], gj[2]), 0))
        return {(K,): c} if c else {}

    def normal(self, mono):
        """normal order a word (tuple of gen indices) -> dict."""
        if mono in self.memo:
            return self.memo[mono]
        for p in range(len(mono) - 1):
            i, j = mono[p], mono[p + 1]
            if i > j or (i == j and self.par[i] == 1):
                res = {}
                def add(m, c):
                    for mm, cc in self.normal(m).items():
                        res[mm] = res.get(mm, 0) + c * cc
                if i == j:   # odd: x^2 = 1/2 [x,x]
                    for m, c in self.sc(i, i).items():
                        add(mono[:p] + m + mono[p + 2:], c / 2)
                else:
                    s = -1 if (self.par[i] and self.par[j]) else 1
                    add(mono[:p] + (j, i) + mono[p + 2:], Fr(s))
                    for m, c in self.sc(i, j).items():
                        add(mono[:p] + m + mono[p + 2:], c)
                res = {m: c for m, c in res.items() if c != 0}
                self.memo[mono] = res
                return res
        self.memo[mono] = {mono: Fr(1)}
        return self.memo[mono]

    def mul(self, X, Y):
        res = {}
        for m1, c1 in X.items():
            for m2, c2 in Y.items():
                for m, c in self.normal(m1 + m2).items():
                    res[m] = res.get(m, 0) + c1 * c2 * c
        return {m: c for m, c in res.items() if c != 0}

    @staticmethod
    def lin(*terms):
        res = {}
        for c, X in terms:
            for m, v in X.items():
                res[m] = res.get(m, 0) + c * v
        return {m: c for m, c in res.items() if c != 0}

    def gen(self, g):
        return {(self.idx[g],): Fr(1)}

    def sbracket(self, X, p, Y, q):
        return self.lin((1, self.mul(X, Y)), (-(-1) ** (p * q), self.mul(Y, X)))

# ---------------------------------------------------------------- basis of g
def basis(n):
    """list of (name, parity, (u,v)) ; quadratic oscillator monomials spanning osp(2|2n)."""
    A = [('a', '+'), ('a', '-')]
    B = [('b', k, s) for k in range(1, n + 1) for s in '+-']
    out = []
    out.append(('a+a-', 0, (A[0], A[1])))
    for u, v in itertools.combinations_with_replacement(B, 2):
        out.append((f'b{u[1]}{u[2]}b{v[1]}{v[2]}', 0, (u, v)))
    for u in A:
        for v in B:
            out.append((f'a{u[1]}b{v[1]}{v[2]}', 1, (u, v)))
    return out

def Zelt(alg, b):
    _, _, (u, v) = b
    pu = 1 if u[0] == 'a' else 0
    pv = 1 if v[0] == 'a' else 0
    U, V = alg.gen(u), alg.gen(v)
    return alg.lin((Fr(1, 2), alg.mul(U, V)), (Fr(1, 2) * (-1) ** (pu * pv), alg.mul(V, U)))

def split_kappa(alg, X):
    K = alg.idx[('K',)]
    X0 = {m: c for m, c in X.items() if K not in m}
    X1 = {tuple(x for x in m if x != K): c for m, c in X.items() if K in m}
    return X0, X1

def solve_in_basis(rows, cols):
    """express each dict in `cols`' span; returns solver using exact rational lstsq."""
    mons = sorted({m for c in cols for m in c} | {m for r in rows for m in r})
    mi = {m: i for i, m in enumerate(mons)}
    M = sympy.zeros(len(mons), len(cols))
    for j, c in enumerate(cols):
        for m, v in c.items():
            M[mi[m], j] = sympy.Rational(v.numerator, v.denominator)
    return mons, mi, M

def structure(n, gb):
    """returns (basis, parity, c[(i,j)] -> {k:val}, gamma[(i,j)] -> {k:val}, scalar[(i,j)])."""
    alg = Alg(n, gb)
    alg0 = Alg(n, {})
    bs = basis(n)
    d = len(bs)
    par = [b[1] for b in bs]
    Z = [Zelt(alg, b) for b in bs]
    Z0 = [split_kappa(alg, z)[0] for z in Z]          # kappa-free parts
    # exact projection: monomial dict (kappa-free) -> coefficients on Z0, plus constant
    mons = sorted({m for z in Z0 for m in z} | {()})
    mi = {m: i for i, m in enumerate(mons)}
    cols = Z0 + [{(): Fr(1)}]
    M = sympy.zeros(len(mons), d + 1)
    for j, c in enumerate(cols):
        for m, v in c.items():
            M[mi[m], j] = sympy.Rational(v.numerator, v.denominator)
    Mdm = DomainMatrix.from_Matrix(M).convert_to(QQ)
    # left-inverse via normal equations (columns independent)
    MtM = (Mdm.transpose() * Mdm)
    MtMinv = MtM.inv()
    P = MtMinv * Mdm.transpose()

    def project(X):
        v = sympy.zeros(len(mons), 1)
        for m, c in X.items():
            if m not in mi:
                raise ValueError(f'monomial {m} outside span of g (+1)')
            v[mi[m], 0] = sympy.Rational(c.numerator, c.denominator)
        coef = (P * DomainMatrix.from_Matrix(v).convert_to(QQ)).to_Matrix()
        # residual check
        res = Mdm.to_Matrix() * coef - v
        assert all(r == 0 for r in res), 'element not in span(g,1)'
        return [Fr(int(sympy.Rational(x).p), int(sympy.Rational(x).q)) for x in coef]

    C, G, S = {}, {}, {}
    for i in range(d):
        for j in range(d):
            R = alg.sbracket(Z[i], par[i], Z[j], par[j])
            R0, R1 = split_kappa(alg, R)
            # kappa-free part -> c (and constant must vanish)
            c = project(R0)
            assert c[-1] == 0, 'constant in undeformed bracket'
            # subtract sum c_k Z_k (full, including kappa pieces) and read the kappa part
            rem = alg.lin((1, R), *[(-c[k], Z[k]) for k in range(d) if c[k] != 0])
            r0, r1 = split_kappa(alg, rem)
            assert not r0, 'kappa-free remainder'
            # kappa*Q : monomials in r1 are the Q monomials
            g = project(r1) if r1 else [Fr(0)] * (d + 1)
            ci = {k: c[k] for k in range(d) if c[k] != 0}
            if ci:
                C[(i, j)] = ci
            gi = {k: g[k] for k in range(d) if g[k] != 0}
            if gi:
                G[(i, j)] = gi
            if g[-1] != 0:
                S[(i, j)] = g[-1]
    return bs, par, C, G, S

# ---------------------------------------------------------------- linear algebra
def delta_f_matrix(d, par, C):
    """rows indexed by (i,j,k); columns by phi_{m,l} (f(Z_l)=sum_m phi_{ml} Z_m), parity-odd only."""
    cols = [(m, l) for l in range(d) for m in range(d) if par[m] != par[l]]
    ci = {c: t for t, c in enumerate(cols)}
    entries = {}   # (i,j,k) -> {col: val}
    def add(row, col, v):
        r = entries.setdefault(row, {})
        r[col] = r.get(col, 0) + v
    # bracket table by first index for speed
    for i in range(d):
        for j in range(d):
            pi, pj = par[i], par[j]
            # term1: (-1)^{p(X)} [X, f(Y)] = (-1)^{pi} sum_m phi_{m j} [Z_i, Z_m]
            for m in range(d):
                if par[m] == pj ^ 1:
                    for k, c in C.get((i, m), {}).items():
                        add((i, j, k), ci[(m, j)], (-1) ** pi * c)
            # term2: -(-1)^{(pi+1)pj} [Y, f(X)] = ... sum_m phi_{m i} [Z_j, Z_m]
            for m in range(d):
                if par[m] == pi ^ 1:
                    for k, c in C.get((j, m), {}).items():
                        add((i, j, k), ci[(m, i)], -(-1) ** ((pi + 1) * pj) * c)
            # term3: - f([X,Y]) = - sum_l c_ij^l sum_m phi_{m l} Z_m
            for l, c in C.get((i, j), {}).items():
                for m in range(d):
                    if par[m] != par[l]:
                        add((i, j, m), ci[(m, l)], -c)
    return cols, entries

def analyse(n, verbose=True):
    # gb parameter list
    params = [(s, j, t) for s in '+-' for j in range(1, n + 1) for t in '+-']
    gb_struct = {}
    bs, par, C, _, _ = structure(n, {})
    d = len(bs)
    Gs = {}
    Ss = {}
    for p in params:
        _, _, _, G, S = structure(n, {p: 1})
        Gs[p], Ss[p] = G, S
        if verbose:
            print(f'  n={n} gb{p}: gamma nonzero entries {sum(len(v) for v in G.values())}, scalar entries {len(S)}')
    cols, ent = delta_f_matrix(d, par, C)
    nf, npar = len(cols), len(params)
    rowkeys = set(ent)
    for p in params:
        rowkeys |= {(i, j, k) for (i, j), v in Gs[p].items() for k in v}
    rowkeys = sorted(rowkeys)
    ri = {r: t for t, r in enumerate(rowkeys)}
    # matrix  [D | -Gamma]  acting on (phi, t) : delta f - gamma_t = 0
    M = np.zeros((len(rowkeys), nf + npar))
    for r, dct in ent.items():
        for c, v in dct.items():
            M[ri[r], c] += float(v)
    for q, p in enumerate(params):
        for (i, j), v in Gs[p].items():
            for k, val in v.items():
                M[ri[(i, j, k)], nf + q] -= float(val)
    # exact nullspace through the Gram matrix
    Gram = M.T @ M
    GramQ = sympy.Matrix(np.rint(Gram * 4).astype(int).tolist())  # entries are multiples of 1/4 at most -> exact after scaling
    assert np.allclose(Gram * 4, np.rint(Gram * 4)), 'non-dyadic entries; use float rank only'
    dm = DomainMatrix.from_Matrix(GramQ).convert_to(QQ)
    ns = dm.nullspace().to_Matrix()          # rows = nullspace basis vectors
    tproj = [[ns[r, nf + q] for q in range(npar)] for r in range(ns.rows)]
    Tmat = sympy.Matrix(tproj) if tproj else sympy.zeros(0, npar)
    T_rank = Tmat.rank() if Tmat.rows else 0
    # also: dimension of the space of coboundaries delta f (rank of D), and of gamma-span
    D = M[:, :nf]
    rank_D = np.linalg.matrix_rank(D)
    rank_all = np.linalg.matrix_rank(M)
    gam = M[:, nf:]
    rank_gam = np.linalg.matrix_rank(gam)
    out = dict(
        n=n, dim_g=[sum(1 for x in par if x == 0), sum(1 for x in par if x == 1)],
        n_gb_params=npar, n_f_unknowns=nf, rows=len(rowkeys),
        rank_delta=int(rank_D), rank_gamma_span=int(rank_gam),
        rank_joint=int(rank_all),
        dim_trivial_gb_subspace=int(T_rank),
        trivial_gb_basis=[[str(x) for x in Tmat.row(r)] for r in range(Tmat.rows)] if T_rank else [],
        gb_param_order=[f'gb[{p[0]},{p[1]},{p[2]}]' for p in params],
        scalar_parts_nonzero={f'gb[{p[0]},{p[1]},{p[2]}]': len(Ss[p]) for p in params},
    )
    # sanity: gamma is a cocycle in the adjoint module? (automatic from associativity; check delta gamma=0 numerically skipped)
    # export
    os.makedirs('artifacts', exist_ok=True)
    art = dict(
        meta=dict(n=n, description='osp(2|2n) in oscillator basis; c = undeformed structure constants, '
                  'gamma[param] = kappa-coefficient of [Z_i,Z_j] for gb[param]=1 (others 0); '
                  'entries "i,j" -> {"k": value}', gb_param_order=out['gb_param_order']),
        basis=[dict(index=i, name=b[0], parity=b[1]) for i, b in enumerate(bs)],
        c={f'{i},{j}': {str(k): str(v) for k, v in dd.items()} for (i, j), dd in C.items()},
        gamma={f'gb[{p[0]},{p[1]},{p[2]}]': {f'{i},{j}': {str(k): str(v) for k, v in dd.items()}
                                           for (i, j), dd in Gs[p].items()} for p in params},
        gamma_scalar_part={f'gb[{p[0]},{p[1]},{p[2]}]': {f'{i},{j}': str(v) for (i, j), v in Ss[p].items()}
                           for p in params},
        result=out)
    with open(f'artifacts/cn1_n{n}.json', 'w') as fh:
        json.dump(art, fh)
    return out

if __name__ == '__main__':
    ns = [int(x) for x in sys.argv[1:]] or [1, 2, 3]
    allres = {}
    for n in ns:
        print(f'== n={n}')
        r = analyse(n)
        allres[n] = r
        print({k: v for k, v in r.items() if k not in ('trivial_gb_basis', 'gb_param_order')})
        print('trivial gb subspace basis:', r['trivial_gb_basis'])
    with open('artifacts/summary.json', 'w') as fh:
        json.dump(allres, fh, indent=1)
