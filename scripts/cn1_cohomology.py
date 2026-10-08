#!/usr/bin/env python3
"""
Independent linear-algebra verification of the triviality of the gb-deformation
of C(n+1), using ONLY the structure constants and the gamma tensors stored in
artifacts/Cn1_n{n}_verification.json (it never looks at the explicit f).

Computations (exact arithmetic over the prime field GF(p), p = 2^31-1; all the
data are rationals with small denominators, so the ranks coincide with the
ranks over Q with overwhelming probability, and the existence statements are
in any case backed by the exact rational f of cn1_deformation.py):

 1. Solvability of   gamma_ad = delta(phi)   for an odd phi: g -> g
    (per unit gb parameter, and for a random gb vector), plus the dimension of
    the affine solution space (= dim of the odd 1-cocycles).
 2. Non-solvability of the *literal* equation gamma = delta(phi) in g (+) C1
    with phi: g -> g (scalar-free), and solvability once phi: g -> g (+) C1.
 3. H^1_odd(g,g) and H^2_odd(g,g) via the weight-zero subcomplex (and, for
    n = 1, 2, via the full complex as a cross-check).  The 2-cocycle condition
    is written as the order-kappa part of the super-Jacobi identity on
    L = g (+) kappa g, which is exactly the condition for the deformed bracket
    to define a Lie superalgebra.

Usage:  python3 scripts/cn1_cohomology.py 1 2 3
Writes  artifacts/Cn1_n{n}_cohomology.json
"""
from fractions import Fraction
import itertools
import json
import os
import random
import sys

P = 2 ** 31 - 1


def fr(x):
    """rational string -> element of GF(p)"""
    f = Fraction(x)
    return (f.numerator % P) * pow(f.denominator % P, P - 2, P) % P


class SparseEchelon:
    """incremental row echelon form over GF(p); rows are dict col -> value"""

    def __init__(self):
        self.pivots = {}  # col -> row (normalised, pivot value 1)

    def reduce(self, row):
        row = {c: v % P for c, v in row.items() if v % P}
        while row:
            c = min(row)
            if c not in self.pivots:
                return row
            f = row[c]
            prow = self.pivots[c]
            for cc, vv in prow.items():
                nv = (row.get(cc, 0) - f * vv) % P
                if nv:
                    row[cc] = nv
                else:
                    row.pop(cc, None)
        return row

    def add(self, row):
        row = self.reduce(row)
        if not row:
            return False
        c = min(row)
        inv = pow(row[c], P - 2, P)
        row = {cc: vv * inv % P for cc, vv in row.items()}
        # keep fully reduced: eliminate c from existing pivot rows
        for pc, prow in self.pivots.items():
            if c in prow:
                f = prow[c]
                for cc, vv in row.items():
                    nv = (prow.get(cc, 0) - f * vv) % P
                    if nv:
                        prow[cc] = nv
                    else:
                        prow.pop(cc, None)
        self.pivots[c] = row
        return True

    @property
    def rank(self):
        return len(self.pivots)


def rank_of(rows):
    E = SparseEchelon()
    for r in rows:
        E.add(r)
    return E.rank


def load(n, artdir):
    with open(os.path.join(artdir, 'Cn1_n%d_verification.json' % n)) as fh:
        return json.load(fh)


def run(n, artdir):
    art = load(n, artdir)
    names = [b['name'] for b in art['basis']]
    N = len(names)
    idx = {nm: i for i, nm in enumerate(names)}
    par = [b['parity'] for b in art['basis']]
    wt = [tuple(b['weight']) for b in art['basis']]
    C = [[{} for _ in range(N)] for _ in range(N)]
    for a, row in art['structure_constants_C[i][j][k]'].items():
        for b, col in row.items():
            for c, v in col.items():
                C[idx[a]][idx[b]][idx[c]] = fr(v)
    keys = art['gb_parameters']
    gam = {}
    gam0 = {}
    for key in keys:
        T = [[{} for _ in range(N)] for _ in range(N)]
        for a, row in art['gamma_ad_per_gb'][key].items():
            for b, col in row.items():
                for c, v in col.items():
                    T[idx[a]][idx[b]][idx[c]] = fr(v)
        gam[key] = T
        S = [[0] * N for _ in range(N)]
        for a, row in art['gamma_scalar_per_gb'][key].items():
            for b, v in row.items():
                S[idx[a]][idx[b]] = fr(v)
        gam0[key] = S

    sgn = lambda e: P - 1 if e % 2 else 1

    # ---------------- odd 1-cochains and delta^1 ----------------------------
    # unknowns: phi[i][j] with par[i] != par[j]  (f(Z_j) = sum_i phi[i][j] Z_i),
    # plus (optionally) scalar unknowns c[j] with par[j] == 1 (f(Z_j) has +c[j]*1)
    phi_vars = [(i, j) for i in range(N) for j in range(N) if par[i] != par[j]]
    phi_idx = {v: k for k, v in enumerate(phi_vars)}
    c_vars = [j for j in range(N) if par[j] == 1]
    c_idx = {j: len(phi_vars) + k for k, j in enumerate(c_vars)}
    nphi = len(phi_vars)

    def delta1_rows(with_scalar):
        """rows of the matrix of delta on 1-cochains, indexed by (i,j,k) for the
        adjoint component and ('s',i,j) for the scalar component."""
        rows = {}
        for i in range(N):
            for j in range(N):
                s1 = sgn(par[i])
                s2 = sgn((par[i] + 1) * par[j])
                acc = {}  # (k, var) -> coeff

                def put(k, var, v):
                    acc[(k, var)] = (acc.get((k, var), 0) + v) % P

                # (-1)^{p_i} [Z_i, f(Z_j)] = sum_m phi[m][j] C[i][m][k]
                for m in range(N):
                    if (m, j) in phi_idx:
                        for k, v in C[i][m].items():
                            put(k, phi_idx[(m, j)], s1 * v)
                # - (-1)^{(p_i+1)p_j} [Z_j, f(Z_i)]
                for m in range(N):
                    if (m, i) in phi_idx:
                        for k, v in C[j][m].items():
                            put(k, phi_idx[(m, i)], (P - s2) * v)
                # - f([Z_i,Z_j])
                for m, v in C[i][j].items():
                    for k in range(N):
                        if (k, m) in phi_idx:
                            put(k, phi_idx[(k, m)], (P - v))
                    if with_scalar and m in c_idx:
                        put('s', c_idx[m], (P - v))
                for (k, var), v in acc.items():
                    if v:
                        rows.setdefault((i, j, k), {})[var] = v
        return rows

    D_rows = delta1_rows(with_scalar=True)
    # matrix without scalar unknowns = same rows restricted to phi columns
    rows_ad = [{v: c for v, c in r.items() if v < nphi} for (i, j, k), r in D_rows.items() if k != 's']
    E_ad = SparseEchelon()
    for r in rows_ad:
        E_ad.add(r)
    rank_delta1 = E_ad.rank
    dim_Z1_odd = nphi - rank_delta1
    inner_odd = sum(par)  # dim g_1 = dim of inner odd derivations (ad is injective: g simple)
    H1_odd = dim_Z1_odd - inner_odd

    def rhs_ad(key):
        return {(i, j, k): v for i in range(N) for j in range(N) for k, v in gam[key][i][j].items()}

    def rhs_scalar(key):
        return {(i, j): gam0[key][i][j] for i in range(N) for j in range(N) if gam0[key][i][j]}

    def solvable(rows_by_label, rhs, ncols):
        """is A x = b solvable?  (labels of rows_by_label are equation labels; rhs maps label -> value)"""
        E = SparseEchelon()
        for r in rows_by_label.values():
            E.add(dict(r))
        r0 = E.rank
        labels = set(rows_by_label) | set(rhs)
        E2 = SparseEchelon()
        for lab in labels:
            r = dict(rows_by_label.get(lab, {}))
            if rhs.get(lab, 0):
                r[ncols] = rhs[lab]
            E2.add(r)
        return E2.rank == r0, r0

    results = {'n': n, 'dim_g': N, 'dim_g_even': N - sum(par), 'dim_g_odd': sum(par), 'prime': P,
               'num_odd_1_cochains_phi': nphi,
               'rank_delta1_on_phi': rank_delta1,
               'dim_Z1_odd(=odd derivations)': dim_Z1_odd,
               'dim_inner_odd_derivations(=dim g_odd)': inner_odd,
               'H1_odd(g,g)': H1_odd}

    # (1) gamma_ad = delta(phi), phi: g -> g
    ad_rows = {(i, j, k): {v: c for v, c in r.items() if v < nphi} for (i, j, k), r in D_rows.items() if k != 's'}
    per_key = {}
    for key in keys:
        ok, _ = solvable(ad_rows, rhs_ad(key), nphi)
        per_key[key] = ok
    random.seed(12345)
    coeffs = {key: random.randrange(1, P) for key in keys}
    rhs_rand = {}
    for key in keys:
        for lab, v in rhs_ad(key).items():
            rhs_rand[lab] = (rhs_rand.get(lab, 0) + coeffs[key] * v) % P
    ok_rand, _ = solvable(ad_rows, rhs_rand, nphi)
    results['adjoint_equation_gamma_ad=delta_phi'] = {
        'solvable_per_gb': per_key, 'solvable_for_random_gb': ok_rand,
        'affine_solution_space_dimension': dim_Z1_odd,
        'random_gb_coefficients_mod_p': coeffs}

    # (2) literal equation in g (+) C1
    full_rows_nos = {}
    for (i, j, k), r in D_rows.items():
        full_rows_nos[(i, j, k)] = {v: c for v, c in r.items() if v < nphi}
    lit = {}
    ext = {}
    ncols_ext = nphi + len(c_vars)
    for key in keys:
        rhs = rhs_ad(key)
        rhs.update({(i, j, 's'): v for (i, j), v in rhs_scalar(key).items()})
        ok_lit, _ = solvable(full_rows_nos, rhs, nphi)
        ok_ext, _ = solvable(D_rows, rhs, ncols_ext)
        lit[key] = ok_lit
        ext[key] = ok_ext
    results['literal_equation_gamma=delta_phi_with_scalars'] = {
        'phi_maps_g_to_g_(no_scalar_part)': lit,
        'phi_maps_g_to_g_plus_C1': ext,
        'scalar_part_of_gamma_nonzero': {key: bool(rhs_scalar(key)) for key in keys}}

    # (3) H^2_odd via Jacobi on L = g (+) kappa g ---------------------------
    # unknowns: gamma[a][b][k] for a<b, or a==b odd ; super-skew extension
    def uvars(weight_zero):
        vars_ = {}
        for a in range(N):
            for b in range(a, N):
                if a == b and par[a] == 0:
                    continue
                for k in range(N):
                    if (par[a] + par[b] + 1) % 2 != par[k]:
                        continue
                    if weight_zero and tuple(x + y for x, y in zip(wt[a], wt[b])) != wt[k]:
                        continue
                    vars_[(a, b, k)] = len(vars_)
        return vars_

    def gvar(vars_, a, b, k):
        """(index, sign) of gamma[a][b][k] or None"""
        if a <= b:
            v = vars_.get((a, b, k))
            return (v, 1) if v is not None else None
        v = vars_.get((b, a, k))
        if v is None:
            return None
        return (v, P - sgn(par[a] * par[b]))  # gamma_ab = -(-1)^{p_a p_b} gamma_ba

    def jacobi_rows(vars_, weight_zero):
        rows = []
        for i in range(N):
            for j in range(i, N):
                for k in range(j, N):
                    for l in range(N):
                        if (par[i] + par[j] + par[k] + 1) % 2 != par[l]:
                            continue
                        if weight_zero and tuple(x + y + z for x, y, z in zip(wt[i], wt[j], wt[k])) != wt[l]:
                            continue
                        row = {}

                        def put(gv, coef):
                            if gv is None or coef % P == 0:
                                return
                            v, s = gv
                            row[v] = (row.get(v, 0) + s * coef) % P

                        # [Z_i,[Z_j,Z_k]]:  sum_m C_jk^m gamma_im^l + (-1)^{p_i} gamma_jk^m C_im^l
                        for m, c in C[j][k].items():
                            put(gvar(vars_, i, m, l), c)
                        for m in range(N):
                            c = C[i][m].get(l)
                            if c:
                                put(gvar(vars_, j, k, m), sgn(par[i]) * c)
                        # -[[Z_i,Z_j],Z_k]: -(sum_m C_ij^m gamma_mk^l + gamma_ij^m C_mk^l)
                        for m, c in C[i][j].items():
                            put(gvar(vars_, m, k, l), P - c)
                        for m in range(N):
                            c = C[m][k].get(l)
                            if c:
                                put(gvar(vars_, i, j, m), P - c)
                        # -(-1)^{p_i p_j}[Z_j,[Z_i,Z_k]]
                        s = sgn(par[i] * par[j])
                        for m, c in C[i][k].items():
                            put(gvar(vars_, j, m, l), (P - s) * c % P)
                        for m in range(N):
                            c = C[j][m].get(l)
                            if c:
                                put(gvar(vars_, i, k, m), (P - s) * sgn(par[j]) * c % P)
                        row = {v: c for v, c in row.items() if c}
                        if row:
                            rows.append(row)
        return rows

    def gamma_vector(vars_, T):
        vec = {}
        for (a, b, k), v in vars_.items():
            x = T[a][b].get(k, 0)
            if x:
                vec[v] = x
        return vec

    def delta_phi_vector(vars_, phi):
        """delta(phi) as a vector in the gamma-unknowns (adjoint part)"""
        vec = {}
        for (a, b, k), v in vars_.items():
            s1 = sgn(par[a])
            s2 = sgn((par[a] + 1) * par[b])
            acc = 0
            for m in range(N):
                if (m, b) in phi:
                    acc += s1 * phi[(m, b)] * C[a][m].get(k, 0)
                if (m, a) in phi:
                    acc -= s2 * phi[(m, a)] * C[b][m].get(k, 0)
            for m, c in C[a][b].items():
                if (k, m) in phi:
                    acc -= c * phi[(k, m)]
            acc %= P
            if acc:
                vec[v] = acc
        return vec

    def check_in_kernel(rows, vec):
        for r in rows:
            s = sum(c * vec.get(v, 0) for v, c in r.items()) % P
            if s:
                return False
        return True

    def coboundary_rows(vars_):
        """images delta(e) of the unit odd 1-cochains e = E_{ij}, as vectors in the gamma unknowns"""
        out = []
        for (i, j) in phi_vars:
            out.append(delta_phi_vector(vars_, {(i, j): 1}))
        return out

    coh = {}
    modes = [('weight_zero', True)] + ([('full', False)] if (n <= 2 or FULL_COMPLEX) else [])
    for label, wz in modes:
        vars_ = uvars(wz)
        rows = jacobi_rows(vars_, wz)
        # every gamma_ad(gb) must be a cocycle
        gam_in_Z = {key: check_in_kernel(rows, gamma_vector(vars_, gam[key])) for key in keys}
        # a random coboundary must be a cocycle
        random.seed(7)
        phi_rand = {v: random.randrange(P) for v in phi_vars}
        cob_in_Z = check_in_kernel(rows, delta_phi_vector(vars_, phi_rand))
        rank_jac = rank_of(rows)
        dim_Z2 = len(vars_) - rank_jac
        B_rows = coboundary_rows(vars_)
        dim_B2 = rank_of(B_rows)
        coh[label] = {'num_gamma_unknowns': len(vars_), 'num_jacobi_equations': len(rows),
                      'rank_jacobi': rank_jac, 'dim_Z2_odd': dim_Z2, 'dim_B2_odd': dim_B2,
                      'H2_odd(g,g)': dim_Z2 - dim_B2,
                      'gamma_ad_is_cocycle_per_gb': gam_in_Z,
                      'random_coboundary_is_cocycle': cob_in_Z}
        assert all(gam_in_Z.values()) and cob_in_Z
    results['cohomology'] = coh

    path = os.path.join(artdir, 'Cn1_n%d_cohomology.json' % n)
    with open(path, 'w') as fh:
        json.dump(results, fh, indent=1)
    print('n=%d: dim g=%d; Z1_odd=%d, inner=%d -> H1_odd=%d' % (n, N, dim_Z1_odd, inner_odd, H1_odd))
    print('   gamma_ad = delta(phi) solvable per gb: %s ; random gb: %s' % (all(per_key.values()), ok_rand))
    print('   literal gamma = delta(phi) (phi: g->g, scalars included): %s' % lit)
    print('   extended (phi: g -> g+C1): %s' % all(ext.values()))
    for label, c in coh.items():
        print('   [%s] unknowns=%d eqs=%d Z2=%d B2=%d H2_odd=%d' % (label, c['num_gamma_unknowns'], c['num_jacobi_equations'], c['dim_Z2_odd'], c['dim_B2_odd'], c['H2_odd(g,g)']))
    print('   -> %s' % path)
    return results


FULL_COMPLEX = False

if __name__ == '__main__':
    args = sys.argv[1:]
    if '--full' in args:
        FULL_COMPLEX = True  # also run the full (non weight-restricted) complex for n = 3
        args.remove('--full')
    ns = [int(x) for x in args] or [1, 2, 3]
    here = os.path.dirname(os.path.abspath(__file__))
    artdir = os.path.join(os.path.dirname(here), 'artifacts')
    for n in ns:
        run(n, artdir)
