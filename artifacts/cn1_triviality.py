"""Verification of triviality of the inhomogeneous (gb) deformation of C(n+1)=osp(2|2n).

Model: Weyl-symbol (graded-commutative) realization. Symmetrized quadratic
elements of the oscillator algebra close exactly under the super Poisson bracket
induced by the form on generators (K=1), so there are no ordering constants.
Generators: b_j^+, b_j^- (even), a^+, a^- (odd), kappa (odd, central, kappa^2=0).

Usage: python3 artifacts/cn1_triviality.py   -> writes artifacts/results.json
"""
import itertools
import json
from fractions import Fraction as Fr

import numpy as np


def build(n):
    # generator indices: 0=kappa, 1=a+, 2=a-, then b_j^+, b_j^-
    names = ['k', 'a+', 'a-']
    par = [1, 1, 1]
    for j in range(1, n + 1):
        names += ['b%d+' % j, 'b%d-' % j]
        par += [0, 0]
    return names, par


def mono_mul(m1, m2, par):
    """Product of sorted monomials in a graded-commutative algebra -> (sign, mono) or None."""
    lst = list(m1) + list(m2)
    sign = 1
    for i in range(1, len(lst)):
        j = i
        while j > 0 and lst[j - 1] > lst[j]:
            if par[lst[j - 1]] and par[lst[j]]:
                sign = -sign
            lst[j - 1], lst[j] = lst[j], lst[j - 1]
            j -= 1
    for i in range(len(lst) - 1):
        if lst[i] == lst[i + 1] and par[lst[i]]:
            return None
    return sign, tuple(lst)


class Alg:
    def __init__(self, n, gb):
        """gb: dict (sigma, j, s) -> value, sigma, s in '+-'.  [b_j^s, a^sigma] = -gb*kappa."""
        self.n = n
        self.names, self.par = build(n)
        self.gen = {}
        L = len(self.names)
        for i in range(1, L):
            for j in range(1, L):
                v = {}
                ni, nj = self.names[i], self.names[j]
                if ni[0] == 'a' and nj[0] == 'a':
                    if ni != nj:
                        v[()] = 1                                  # {a+,a-}=1
                elif ni[0] == 'b' and nj[0] == 'b':
                    if ni[:-1] == nj[:-1] and ni[-1] != nj[-1]:    # [b-,b+]=1
                        v[()] = 1 if ni[-1] == '-' else -1
                elif ni[0] == 'b' and nj[0] == 'a':                # [b_j^s,a^sig] = -gb kappa
                    c = gb.get((nj[-1], int(ni[1:-1]), ni[-1]), 0)
                    if c != 0:
                        v[(0,)] = -c
                else:                                              # [a,b] = -[b,a] = +gb kappa
                    c = gb.get((ni[-1], int(nj[1:-1]), nj[-1]), 0)
                    if c != 0:
                        v[(0,)] = c
                self.gen[(i, j)] = v

    def pmul(self, p, q):
        r = {}
        for m1, c1 in p.items():
            for m2, c2 in q.items():
                t = mono_mul(m1, m2, self.par)
                if t is None:
                    continue
                r[t[1]] = r.get(t[1], 0) + t[0] * c1 * c2
        return {m: c for m, c in r.items() if c != 0}

    def padd(self, p, q, s=1):
        r = dict(p)
        for m, c in q.items():
            r[m] = r.get(m, 0) + s * c
        return {m: c for m, c in r.items() if c != 0}

    def mpar(self, m):
        return sum(self.par[i] for i in m) % 2

    def br_gen_mono(self, x, m):
        """{x_i, monomial}: x acts as a graded derivation."""
        res = {}
        for t in range(len(m)):
            before, y, after = m[:t], m[t], m[t + 1:]
            sgn = -1 if (self.par[x] and self.mpar(before)) else 1
            if y == 0:
                continue
            g = self.gen[(x, y)]
            if not g:
                continue
            term = self.pmul(self.pmul({before: 1}, g), {after: 1})
            res = self.padd(res, term, sgn)
        return res

    def br_mono(self, m, z):
        if len(m) == 0:
            return {}
        x, rest = m[0], m[1:]
        if x == 0:
            return {}
        r1 = self.pmul({(x,): 1}, self.br_mono(rest, z)) if rest else {}
        sgn = -1 if (self.mpar(rest) and self.mpar(z)) else 1
        r2 = self.pmul(self.br_gen_mono(x, z), {rest: 1})
        return self.padd(r1, r2, sgn)

    def br(self, X, Y):
        r = {}
        for m, c in X.items():
            for z, d in Y.items():
                for mm, e in self.br_mono(m, z).items():
                    r[mm] = r.get(mm, 0) + c * d * e
        return {m: c for m, c in r.items() if c != 0}


def basis(n):
    names, _ = build(n)
    ev = list(range(3, len(names)))
    B = [((i, j), 0) for i, j in itertools.combinations_with_replacement(ev, 2)]
    B.append(((1, 2), 0))  # so(2) generator a+a-
    for x in (1, 2):
        for y in ev:
            B.append(((x, y), 1))
    return B


def setup(n):
    names, par = build(n)
    B = basis(n)
    N = len(B)
    mons, signs = [], []
    for t, _ in B:
        s, m = mono_mul((t[0],), (t[1],), par)
        mons.append(m)
        signs.append(s)
    index = {m: i for i, m in enumerate(mons)}
    bpar = [p for _, p in B]
    elems = [{mons[i]: signs[i]} for i in range(N)]
    return B, N, mons, signs, index, bpar, elems


def decompose(poly, kappa, N, index, signs):
    c = [Fr(0)] * N
    for m, v in poly.items():
        if kappa:
            assert m[0] == 0, 'non-kappa term'
            m = m[1:]
        else:
            assert 0 not in m
        assert m in index, 'outside g: %s' % (m,)
        c[index[m]] += Fr(v) * signs[index[m]]
    return c


def structure(n):
    B, N, mons, signs, index, bpar, elems = setup(n)
    alg0 = Alg(n, {})
    sc = {}
    for i in range(N):
        for j in range(N):
            sc[(i, j)] = decompose(alg0.br(elems[i], elems[j]), False, N, index, signs)
    return B, N, bpar, sc


def gamma_for(n, gbdict, B, N, signs, index, elems, sc):
    """Return dict (i,j)->vector gamma(Z_i,Z_j), with [X,Y]_gamma = [X,Y]_0 + kappa*gamma."""
    alg = Alg(n, gbdict)
    alg0 = Alg(n, {})
    G = {}
    for i in range(N):
        for j in range(N):
            r = alg.br(elems[i], elems[j])
            assert {m: c for m, c in r.items() if 0 not in m} == alg0.br(elems[i], elems[j])
            kap = {m: c for m, c in r.items() if 0 in m}
            v = decompose(kap, True, N, index, signs)
            if any(v):
                G[(i, j)] = v
    return G


def delta_f_matrix(N, bpar, sc):
    """Dense D: (delta f)(Z_i,Z_j)_c = sum D[(i,j,c),(p,q)] phi_pq, f(Z_q)=sum_p phi_pq Z_p (p(p)!=p(q))."""
    var = [(p, q) for p in range(N) for q in range(N) if bpar[p] != bpar[q]]
    vi = {v: k for k, v in enumerate(var)}
    D = np.zeros((N ** 3, len(var)))

    def add(i, j, c, col, val):
        D[(i * N + j) * N + c, col] += val

    for i in range(N):
        for j in range(N):
            s1 = -1 if bpar[i] else 1
            s2 = -1 if ((bpar[i] + 1) * bpar[j]) % 2 else 1
            for p in range(N):
                if bpar[p] != bpar[j]:                      # (-1)^{p(X)} [X, f(Y)]
                    for c, v in enumerate(sc[(i, p)]):
                        if v:
                            add(i, j, c, vi[(p, j)], float(s1 * v))
                if bpar[p] != bpar[i]:                      # - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
                    for c, v in enumerate(sc[(j, p)]):
                        if v:
                            add(i, j, c, vi[(p, i)], float(-s2 * v))
            for q, v in enumerate(sc[(i, j)]):              # - f([X,Y])
                if v:
                    for p in range(N):
                        if bpar[p] != bpar[q]:
                            add(i, j, p, vi[(p, q)], float(-v))
    return D, var


def explicit_f(n, gb, B, N, index, bpar, signs):
    """Shift realization: deformed b_j^s = b0_j^s + kappa * c * a^{-sigma'}, c_{-sig',j,s} = -gb_{sig',j,s}.
    Returns dict (p,q)->coefficient phi_pq (f(Z_q) = sum_p phi_pq Z_p) obtained by substitution.
    (Computed symbolically with the same graded algebra: kappa-coefficient of X(b0+kappa*c*a, a).)"""
    names, par = build(n)
    nid = {nm: i for i, nm in enumerate(names)}
    # substitution b -> b + kappa*(sum_sigma c a^sigma)
    shift = {}
    for (sig, j, s), val in gb.items():
        # c_{-sig,j,s} = -gb_{sig,j,s}
        bi = nid['b%d%s' % (j, s)]
        ai = nid['a' + ('-' if sig == '+' else '+')]
        shift.setdefault(bi, {})
        shift[bi][ai] = shift[bi].get(ai, 0) - val
    phi = {}
    alg = Alg(n, {})
    for q in range(N):
        t, _ = B[q]
        # X = s * x y.  derivative: substitute each factor
        res = {}
        for pos in (0, 1):
            fac = t[pos]
            if fac in shift:
                rep = {(0, ai): c for ai, c in shift[fac].items()}   # kappa * c * a
                other = t[1 - pos]
                left, right = (rep, {(other,): 1}) if pos == 0 else ({(other,): 1}, rep)
                res = alg.padd(res, alg.pmul(left, right))
        res = {m: c * signs[q] for m, c in res.items()}
        v = decompose(res, True, N, index, signs) if res else [Fr(0)] * N
        for p, x in enumerate(v):
            if x:
                phi[(p, q)] = x
    return phi


def main():
    results = {}
    for n in (1, 2, 3):
        B, N, bpar, sc = structure(n)
        _, _, mons, signs, index, _, elems = setup(n)
        keys = [(sig, j, s) for sig in '+-' for j in range(1, n + 1) for s in '+-']
        gam = {k: gamma_for(n, {k: 1}, B, N, signs, index, elems, sc) for k in keys}
        D, var = delta_f_matrix(N, bpar, sc)
        Dd = D
        Gm = np.zeros((N ** 3, len(keys)))
        for k, key in enumerate(keys):
            for (i, j), v in gam[key].items():
                for c, x in enumerate(v):
                    Gm[(i * N + j) * N + c, k] = float(x)
        rankG = int(np.linalg.matrix_rank(Gm))
        rankD = int(np.linalg.matrix_rank(Dd))
        rankDG = int(np.linalg.matrix_rank(np.hstack([Dd, Gm])))
        # explicit f: check gamma = s * delta f for s = +1 or -1, with random gb
        rng = np.random.default_rng(n)
        gbr = {k: int(rng.integers(-5, 6)) or 1 for k in keys}
        gam_r = gamma_for(n, gbr, B, N, signs, index, elems, sc)
        gvec = np.zeros(N ** 3)
        for (i, j), v in gam_r.items():
            for c, x in enumerate(v):
                gvec[(i * N + j) * N + c] = float(x)
        phi = explicit_f(n, gbr, B, N, index, bpar, signs)
        pv = np.zeros(len(var))
        vi = {v: k for k, v in enumerate(var)}
        for pq, x in phi.items():
            pv[vi[pq]] = float(x)
        dfv = D @ pv
        sign_match = [int(s) for s in (1, -1) if np.allclose(gvec, s * dfv)]
        # also: sp(2n) restriction / odd-odd-coupled counts
        results['n=%d' % n] = dict(
            n=n, dim_even=bpar.count(0), dim_odd=bpar.count(1), dim=N,
            n_gb=len(keys), rank_gamma_map=rankG, rank_delta=rankD,
            rank_joint=rankDG, all_gb_trivial=(rankDG == rankD),
            gamma_injective_in_gb=(rankG == len(keys)),
            explicit_shift_f_matches_delta_f_with_sign=sign_match,
            random_gb=['%s%d%s=%d' % (k[0], k[1], k[2], v) for k, v in gbr.items()],
            nonzero_gamma_entries_per_gb={'%s,%d,%s' % k: len(gam[k]) for k in keys},
        )
        if n == 1:
            names, _ = build(n)
            results['n=1']['basis'] = [dict(idx=i, monomial=[names[t] for t in B[i][0]],
                                            sign=signs[i], parity=B[i][1]) for i in range(N)]
            results['n=1']['structure_constants_nonzero'] = {
                '%d,%d' % ij: [str(x) for x in v] for ij, v in sc.items() if any(v)}
            results['n=1']['gamma_structure'] = {
                'gb_%s_%d_%s' % k: {'%d,%d' % ij: [str(x) for x in v] for ij, v in gam[k].items()}
                for k in keys}
            results['n=1']['explicit_f_phi_for_random_gb'] = {'%d,%d' % pq: str(x) for pq, x in phi.items()}
        print(n, {k: v for k, v in results['n=%d' % n].items()
                  if k not in ('basis', 'structure_constants_nonzero', 'gamma_structure',
                               'explicit_f_phi_for_random_gb', 'nonzero_gamma_entries_per_gb')})
    with open('artifacts/results.json', 'w') as fh:
        json.dump(results, fh, indent=1)


if __name__ == '__main__':
    main()
