#!/usr/bin/env python3
"""
osp_deform.py -- exact computational model for the inhomogeneous (gb) deformation
of C(n+1) = osp(2|2n) and its triviality analysis.

Everything is computed over Q[gb] with exact rational arithmetic (fractions.Fraction);
no floating point is used for any statement that enters the proof.  Modular / float
ranks are used only as *independent* cross-checks of the exact results.

Conventions (all taken from docs/math/*.md):
  * Oscillators: standard fermionic pair a^+, a^- with {a^-, a^+} = K,
    bosonic b_j^+, b_j^- (j = 1..n) with [b_j^-, b_l^+] = delta_{jl} K.
    We work in the quotient K = 1 (this is what makes the quadratic elements of
    docs/math/Cn1_definition.md close into osp(2|2n)).
  * kappa is an odd central element with kappa^2 = 0 (it is odd and central,
    hence [kappa,kappa] = 2 kappa^2 = 0).
  * Deformation (docs/math/C_inhomogeneous_definition.md):
        [b_j^s, a^sigma] = - gb_{sigma,j,s} kappa ,   sigma,s in {+,-}.
    The 4n parameters gb_{sigma,j,s} are ordinary (even) scalars; the resulting
    2-cochain gamma is odd (it is the coefficient of the odd central kappa).
  * Coboundary (docs/math/C_coboundary_definition.md):
        (df)(X,Y) = (-1)^{p(X)} [X,f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y,f(X)] - f([X,Y]).

Elements of the (deformed) universal enveloping algebra are stored as
    dict{ word : poly }      word = tuple of generator labels (normal ordered)
                              poly = dict{ monomial-in-gb : Fraction }
Generator labels:  ('k',)  kappa ;  ('a','+'), ('a','-') ;  ('b', j, '+'), ('b', j, '-').
Normal order:  kappa < a^+ < a^- < b_1^+ < b_1^- < b_2^+ < ... .
"""
from fractions import Fraction
from itertools import product
import json

KAPPA = ('k',)


# --------------------------------------------------------------------------------------
# coefficient ring Q[gb]  (polynomials as dict monomial(tuple of sorted names) -> Fraction)
# --------------------------------------------------------------------------------------
def P_const(c):
    c = Fraction(c)
    return {(): c} if c != 0 else {}


def P_var(name):
    return {(name,): Fraction(1)}


def P_add(p, q):
    r = dict(p)
    for m, c in q.items():
        v = r.get(m, Fraction(0)) + c
        if v == 0:
            r.pop(m, None)
        else:
            r[m] = v
    return r


def P_mul(p, q):
    r = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = tuple(sorted(m1 + m2))
            v = r.get(m, Fraction(0)) + c1 * c2
            if v == 0:
                r.pop(m, None)
            else:
                r[m] = v
    return r


def P_scale(p, s):
    s = Fraction(s)
    return {m: c * s for m, c in p.items()} if s != 0 else {}


def P_str(p):
    if not p:
        return "0"
    terms = []
    for m, c in sorted(p.items()):
        mono = "*".join(m) if m else "1"
        terms.append(f"({c})*{mono}" if m else f"({c})")
    return " + ".join(terms)


# --------------------------------------------------------------------------------------
# generators
# --------------------------------------------------------------------------------------
def key(g):
    if g == KAPPA:
        return 0
    if g[0] == 'a':
        return 1 if g[1] == '+' else 2
    j, s = g[1], g[2]
    return 3 + 2 * (j - 1) + (0 if s == '+' else 1)


def parity(g):
    return 0 if g[0] == 'b' else 1


def gb_name(sigma, j, s):
    """name of the parameter gb_{sigma, j, s} = gb_{a_1^sigma, b_j^s}"""
    return f"gb[{sigma}][{j}][{s}]"


def gb_names(n):
    return [gb_name(sg, j, s) for sg in '+-' for j in range(1, n + 1) for s in '+-']


# --------------------------------------------------------------------------------------
# normal ordering in U(A') (deformed=True) or U(A) (deformed=False)
# --------------------------------------------------------------------------------------
def _violation(word):
    for i in range(len(word) - 1):
        kx, ky = key(word[i]), key(word[i + 1])
        if kx > ky:
            return i
        if kx == ky and parity(word[i]) == 1:   # fermionic square = 0
            return i
    return None


def _rewrite(x, y, deformed):
    """x*y with key(x) >= key(y) (out of order) -> list of (word, poly)"""
    if x == y:                      # fermionic square (bosonic equal pairs are never violations)
        return []
    if y == KAPPA:                  # x kappa = (-1)^{p(x)} kappa x
        return [((y, x), P_const((-1) ** parity(x)))]
    if x[0] == 'a' and y[0] == 'a':  # a^- a^+ = 1 - a^+ a^-
        return [((), P_const(1)), ((y, x), P_const(-1))]
    if x[0] == 'b' and y[0] == 'a':  # b a = a b - gb kappa
        out = [((y, x), P_const(1))]
        if deformed:
            out.append(((KAPPA,), P_scale(P_var(gb_name(y[1], x[1], x[2])), -1)))
        return out
    if x[0] == 'b' and y[0] == 'b':
        if x[1] == y[1] and x[2] == '-' and y[2] == '+':   # b_j^- b_j^+ = b_j^+ b_j^- + 1
            return [((y, x), P_const(1)), ((), P_const(1))]
        return [((y, x), P_const(1))]
    raise RuntimeError(f"unexpected pair {x} {y}")


def normalize(elem, deformed=True):
    out = {}
    stack = list(elem.items())
    while stack:
        word, coef = stack.pop()
        if not coef:
            continue
        i = _violation(word)
        if i is None:
            out[word] = P_add(out.get(word, {}), coef)
            continue
        pre, post = word[:i], word[i + 2:]
        for neww, c in _rewrite(word[i], word[i + 1], deformed):
            stack.append((pre + neww + post, P_mul(coef, c)))
    return {w: c for w, c in out.items() if c}


def E_add(X, Y):
    r = dict(X)
    for w, c in Y.items():
        v = P_add(r.get(w, {}), c)
        if v:
            r[w] = v
        else:
            r.pop(w, None)
    return r


def E_scale(X, s):
    return {w: P_scale(c, s) for w, c in X.items()} if s != 0 else {}


def E_mul(X, Y, deformed=True):
    prod = {}
    for w1, c1 in X.items():
        for w2, c2 in Y.items():
            prod[w1 + w2] = P_add(prod.get(w1 + w2, {}), P_mul(c1, c2))
    return normalize(prod, deformed)


def E_parity(X):
    ps = {sum(parity(g) for g in w) % 2 for w in X}
    if len(ps) > 1:
        raise ValueError("inhomogeneous element")
    return ps.pop() if ps else 0


def E_bracket(X, Y, deformed=True):
    """super-commutator [X,Y] = XY - (-1)^{p(X)p(Y)} YX"""
    pX, pY = E_parity(X), E_parity(Y)
    return E_add(E_mul(X, Y, deformed), E_scale(E_mul(Y, X, deformed), -((-1) ** (pX * pY))))


def word(*gens):
    return {tuple(gens): P_const(1)}


def a(s):
    return ('a', s)


def b(j, s):
    return ('b', j, s)


# --------------------------------------------------------------------------------------
# the Lie superalgebra  g = C(n+1) = osp(2|2n)  realized by quadratic elements
# (docs/math/Cn1_definition.md); ghat = g + C.1 is the span of all quadratics.
# --------------------------------------------------------------------------------------
def basis(n):
    """returns list of (name, element, parity, root_label)"""
    B = []
    # Cartan
    B.append(("H1", E_add(word(a('+'), a('-')), word(b(1, '+'), b(1, '-'))), 0, "0"))
    for k in range(2, n + 1):
        B.append((f"H{k}", E_add(word(b(k - 1, '+'), b(k - 1, '-')), E_scale(word(b(k, '+'), b(k, '-')), -1)), 0, "0"))
    B.append((f"H{n + 1}", E_add(E_scale(word(b(n, '+'), b(n, '-')), -1), E_scale(word(), Fraction(-1, 2))), 0, "0"))
    # even roots
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            B.append((f"E[d{k}+d{l}]", word(b(k, '+'), b(l, '+')), 0, f"d{k}+d{l}"))
            B.append((f"E[-d{k}-d{l}]", word(b(k, '-'), b(l, '-')), 0, f"-d{k}-d{l}"))
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k != l:
                B.append((f"E[d{k}-d{l}]", word(b(k, '+'), b(l, '-')), 0, f"d{k}-d{l}"))
    for k in range(1, n + 1):
        B.append((f"E[2d{k}]", word(b(k, '+'), b(k, '+')), 0, f"2d{k}"))
        B.append((f"E[-2d{k}]", word(b(k, '-'), b(k, '-')), 0, f"-2d{k}"))
    # odd roots
    for l in range(1, n + 1):
        B.append((f"E[e+d{l}]", word(a('+'), b(l, '+')), 1, f"e+d{l}"))
        B.append((f"E[e-d{l}]", word(a('+'), b(l, '-')), 1, f"e-d{l}"))
        B.append((f"E[-e+d{l}]", word(a('-'), b(l, '+')), 1, f"-e+d{l}"))
        B.append((f"E[-e-d{l}]", word(a('-'), b(l, '-')), 1, f"-e-d{l}"))
    out = []
    for name, X, p, r in B:
        X2 = normalize(X, deformed=False)   # only reorders commuting bosonic factors (b_k^+ b_l^-, k > l)
        assert E_parity(X2) == p, name
        out.append((name, X2, p, r))
    return out


# --------------------------------------------------------------------------------------
# exact linear algebra over Q
# --------------------------------------------------------------------------------------
def inverse(M):
    """inverse of a square matrix (list of lists of Fraction) by Gauss-Jordan"""
    m = len(M)
    A = [list(row) + [Fraction(int(i == j)) for j in range(m)] for i, row in enumerate(M)]
    for c in range(m):
        piv = next(r for r in range(c, m) if A[r][c] != 0)
        A[c], A[piv] = A[piv], A[c]
        inv = 1 / A[c][c]
        A[c] = [v * inv for v in A[c]]
        for r in range(m):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [vr - f * vc for vr, vc in zip(A[r], A[c])]
    return [row[m:] for row in A]


class Decomposer:
    """expresses elements of ghat (quadratic span, kappa-degree <= 1) in the basis of ghat = g + C.1"""

    def __init__(self, B):
        self.B = B
        self.dim = len(B)               # dim g
        words = sorted({w for _, X, _, _ in B for w in X} | {()}, key=lambda w: [key(g) for g in w])
        self.words = words
        self.widx = {w: i for i, w in enumerate(words)}
        assert len(words) == self.dim + 1, (len(words), self.dim)
        # column j = basis element j (j < dim), column dim = unit
        M = [[Fraction(0)] * (self.dim + 1) for _ in words]
        for j, (_, X, _, _) in enumerate(B):
            for w, c in X.items():
                M[self.widx[w]][j] = c[()]
        M[self.widx[()]][self.dim] = Fraction(1)
        self.Minv = inverse(M)

    def __call__(self, X):
        """X -> dict{ (kappa_degree, gb_monomial) : coordinate vector of length dim+1 }"""
        comps = {}
        for w, poly in X.items():
            kdeg = 1 if (w and w[0] == KAPPA) else 0
            w0 = w[1:] if kdeg else w
            if w0 not in self.widx:
                raise ValueError(f"word {w0} not in the quadratic span")
            for mono, c in poly.items():
                v = comps.setdefault((kdeg, mono), [Fraction(0)] * (self.dim + 1))
                for i in range(self.dim + 1):
                    v[i] += self.Minv[i][self.widx[w0]] * c
        return {k: v for k, v in comps.items() if any(v)}


# --------------------------------------------------------------------------------------
# structure constants of g and the cocycle gamma_gb
# --------------------------------------------------------------------------------------
def compute_structure(n):
    B = basis(n)
    dec = Decomposer(B)
    dim = dec.dim
    names = gb_names(n)
    c = {}       # c[(a,b)] = vector over ghat (undeformed bracket); scalar part must vanish
    gamma = {}   # gamma[(a,b)] = dict{ gb_name : vector over ghat }
    for i, (_, X, _, _) in enumerate(B):
        for j, (_, Y, _, _) in enumerate(B):
            comps = dec(E_bracket(X, Y, deformed=True))
            cv = comps.get((0, ()), [Fraction(0)] * (dim + 1))
            for k in comps:
                if k[0] == 0:
                    assert k[1] == (), "kappa^0 part depends on gb ?!"
                else:
                    assert len(k[1]) == 1, "kappa^1 part not linear in gb ?!"
            assert cv[dim] == 0, f"[g,g] not inside g: scalar term in [{B[i][0]},{B[j][0]}]"
            c[(i, j)] = cv
            gamma[(i, j)] = {k[1][0]: v for k, v in comps.items() if k[0] == 1}
    return B, dec, c, gamma, names


def bracket_vec(c, dim, i, v):
    """[Z_i, v] for v a vector over ghat (scalar component is central -> ignored)"""
    out = [Fraction(0)] * (dim + 1)
    for j in range(dim):
        if v[j] != 0:
            cv = c[(i, j)]
            for k in range(dim + 1):
                if cv[k] != 0:
                    out[k] += v[j] * cv[k]
    return out


def coboundary(B, c, f, names):
    """f: dict{ j : dict{gb_name : vector over ghat} }  (odd linear map g -> ghat, gb-linear)
       returns df as dict{(a,b): dict{gb_name: vector over ghat}} using the formula of
       docs/math/C_coboundary_definition.md"""
    dim = len(B)
    par = [p for _, _, p, _ in B]
    zero = [Fraction(0)] * (dim + 1)
    df = {}
    for i in range(dim):
        for j in range(dim):
            res = {}
            for nm in names:
                fj = f.get(j, {}).get(nm, zero)
                fi = f.get(i, {}).get(nm, zero)
                t1 = bracket_vec(c, dim, i, fj)
                t2 = bracket_vec(c, dim, j, fi)
                s1 = (-1) ** par[i]
                s2 = -((-1) ** ((par[i] + 1) * par[j]))
                v = [s1 * x + s2 * y for x, y in zip(t1, t2)]
                cij = c[(i, j)]
                for k in range(dim):
                    if cij[k] != 0:
                        fk = f.get(k, {}).get(nm, zero)
                        for q in range(dim + 1):
                            v[q] -= cij[k] * fk[q]
                if any(v):
                    res[nm] = v
            df[(i, j)] = res
    return df


# --------------------------------------------------------------------------------------
# the explicit splitting map  Phi: a^sigma -> a^sigma + kappa u^sigma,  u^sigma = sum c_{sigma,j,s} b_j^s
#      c_{sigma,j,+} = - gb_{sigma,j,-},   c_{sigma,j,-} = + gb_{sigma,j,+}
# f_gb(Z) := kappa-coefficient of Phi(Z)   (computed in the UNDEFORMED algebra U(A))
# --------------------------------------------------------------------------------------
def phi_of_generator(g, n):
    if g[0] == 'b':
        return word(g)
    sigma = g[1]
    X = word(g)
    for j in range(1, n + 1):
        X = E_add(X, {(KAPPA, b(j, '+')): P_scale(P_var(gb_name(sigma, j, '-')), -1)})
        X = E_add(X, {(KAPPA, b(j, '-')): P_var(gb_name(sigma, j, '+'))})
    return X


def phi(X, n):
    out = {}
    for w, coef in X.items():
        prod = {(): coef}
        for g in w:
            prod = E_mul(prod, phi_of_generator(g, n), deformed=False)
        out = E_add(out, prod)
    return out


def explicit_f(B, dec, n):
    dim = len(B)
    f = {}
    for j, (_, X, _, _) in enumerate(B):
        comps = dec(phi(X, n))
        # kappa^0 part must be X itself
        v0 = comps.get((0, ()), [Fraction(0)] * (dim + 1))
        assert v0 == [Fraction(int(i == j)) for i in range(dim + 1)], B[j][0]
        f[j] = {k[1][0]: v for k, v in comps.items() if k[0] == 1}
    return f


def check_phi_relations(n):
    """Phi preserves the defining relations:  [Phi(b), Phi(a)] = -gb kappa, {Phi(a^-),Phi(a^+)} = 1, ..."""
    ok = True
    gens = [a('+'), a('-')] + [b(j, s) for j in range(1, n + 1) for s in '+-']
    for x in gens:
        for y in gens:
            lhs = E_bracket(phi(word(x), n), phi(word(y), n), deformed=False)
            rhs = E_bracket(word(x), word(y), deformed=True)
            if lhs != rhs:
                ok = False
    return ok


# --------------------------------------------------------------------------------------
# cocycle (super-Jacobi) check for an odd 2-cochain  gamma  with values in ghat/C = g
#   L = g + kappa g,  [X+kU, Y+kV] = [X,Y] + kappa( gamma(X,Y) + (-1)^{p(X)}[X,V] + [U,Y] )
# --------------------------------------------------------------------------------------
def jacobi_defect(B, c, gamma_vec):
    """gamma_vec[(a,b)] = vector over g (length dim; scalar part dropped).
       returns the number of (x,y,z) triples where super-Jacobi of L fails."""
    dim = len(B)
    par = [p for _, _, p, _ in B]

    def br(X, Y):
        # X, Y : (vector over g, vector over g) = X0 + kappa X1 ; homogeneous w.r.t. parity info passed separately
        raise NotImplementedError

    # Linear version:  for basis triples (x,y,z) check the kappa^1 part of
    #   [x,[y,z]] - [[x,y],z] - (-1)^{p(x)p(y)} [y,[x,z]]  = 0
    def ad(i, v):   # [Z_i, v], v over g
        out = [Fraction(0)] * dim
        for j in range(dim):
            if v[j] != 0:
                cv = c[(i, j)]
                for k in range(dim):
                    out[k] += v[j] * cv[k]
        return out

    def gam(i, v):  # gamma(Z_i, v) linear in v
        out = [Fraction(0)] * dim
        for j in range(dim):
            if v[j] != 0:
                gv = gamma_vec[(i, j)]
                for k in range(dim):
                    out[k] += v[j] * gv[k]
        return out

    def gam_right(v, k):  # gamma(v, Z_k)
        out = [Fraction(0)] * dim
        for j in range(dim):
            if v[j] != 0:
                gv = gamma_vec[(j, k)]
                for q in range(dim):
                    out[q] += v[j] * gv[q]
        return out

    bad = 0
    for x in range(dim):
        for y in range(dim):
            for z in range(dim):
                cyz = c[(y, z)][:dim]
                cxy = c[(x, y)][:dim]
                cxz = c[(x, z)][:dim]
                # kappa part of [x,[y,z]'] ' :  gamma(x,[y,z]) + (-1)^{p(x)} [x, gamma(y,z)]
                t1 = gam(x, cyz)
                t1b = ad(x, gamma_vec[(y, z)])
                sx = (-1) ** par[x]
                # kappa part of [[x,y]',z]' :  gamma([x,y],z) + [gamma(x,y), z]
                t2 = gam_right(cxy, z)
                t2b = [-((-1) ** ((par[x] + par[y] + 1) * par[z])) * v for v in ad(z, gamma_vec[(x, y)])]
                # kappa part of [y,[x,z]']' : gamma(y,[x,z]) + (-1)^{p(y)} [y, gamma(x,z)]
                t3 = gam(y, cxz)
                t3b = ad(y, gamma_vec[(x, z)])
                sy = (-1) ** par[y]
                sxy = (-1) ** (par[x] * par[y])
                tot = [t1[k] + sx * t1b[k] - t2[k] - t2b[k] - sxy * (t3[k] + sy * t3b[k]) for k in range(dim)]
                if any(tot):
                    bad += 1
    return bad


# --------------------------------------------------------------------------------------
# rank computations (independent cross-checks): exact modular rank with chunked elimination
# --------------------------------------------------------------------------------------
def rank_mod_p(row_iter, ncols, p=1000003, chunk=2000):
    import numpy as np
    pivots = []          # list of (col, row ndarray)   (insertion order)
    buf = []

    def flush(buf):
        if not buf:
            return
        M = np.array(buf, dtype=np.int64) % p
        for col, row in pivots:
            f = M[:, col].copy()
            nz = f != 0
            if nz.any():
                M[nz] = (M[nz] - np.outer(f[nz], row)) % p
        # eliminate inside the chunk
        r = 0
        nrows = M.shape[0]
        for col in range(ncols):
            if r >= nrows:
                break
            nzr = np.nonzero(M[r:, col])[0]
            if nzr.size == 0:
                continue
            pr = r + nzr[0]
            M[[r, pr]] = M[[pr, r]]
            inv = pow(int(M[r, col]), p - 2, p)
            M[r] = (M[r] * inv) % p
            f = M[:, col].copy()
            f[r] = 0
            nz = f != 0
            if nz.any():
                M[nz] = (M[nz] - np.outer(f[nz], M[r])) % p
            pivots.append((col, M[r].copy()))
            r += 1

    for row in row_iter:
        buf.append(row)
        if len(buf) >= chunk:
            flush(buf)
            buf = []
    flush(buf)
    return len(pivots)


def to_int_rows(rows, ncols=None):
    """rows (dense lists of Fractions, or sparse dicts col->Fraction) -> dense integer rows
       (common denominator per row); a generator."""
    from math import lcm
    for r in rows:
        if isinstance(r, dict):
            d = 1
            for v in r.values():
                d = lcm(d, Fraction(v).denominator)
            row = [0] * ncols
            for t, v in r.items():
                row[t] = int(Fraction(v) * d)
            yield row
        else:
            d = 1
            for v in r:
                d = lcm(d, Fraction(v).denominator)
            yield [int(Fraction(v) * d) for v in r]


def coboundary_system(B, c, gamma, names, include_scalar_rows, allow_scalar_in_f):
    """Build A (coboundary matrix on odd maps) and G (columns = gamma_{gb = e_k}).
       Unknowns: phi[(i, j)] with f(Z_j) = sum_i phi[i,j] Z_i,  p(i) != p(j)  (i over g, optionally also the unit).
       Rows: (a, b, k) with k over g (and over the unit if include_scalar_rows).
       Rows are returned sparse: dict column -> Fraction."""
    dim = len(B)
    par = [p for _, _, p, _ in B] + [0]     # unit is even
    unknowns = [(i, j) for j in range(dim) for i in range(dim + (1 if allow_scalar_in_f else 0)) if par[i] != par[j]]
    uidx = {u: t for t, u in enumerate(unknowns)}
    ncomp = dim + (1 if include_scalar_rows else 0)
    rows_A, rows_G = [], []
    nA = len(unknowns)
    zero = [Fraction(0)] * (dim + 1)
    for a_ in range(dim):
        for b_ in range(dim):
            s1 = (-1) ** par[a_]
            s2 = -((-1) ** ((par[a_] + 1) * par[b_]))
            # df(a,b)[k] = s1 * sum_i phi[i,b] c[(a,i)][k] + s2 * sum_i phi[i,a] c[(b,i)][k] - sum_m c[(a,b)][m] phi[k,m]
            rowsk = [dict() for _ in range(ncomp)]
            for i in range(dim):
                if (i, b_) in uidx:
                    cv = c[(a_, i)]
                    for k in range(ncomp):
                        if cv[k] != 0:
                            d = rowsk[k]
                            d[uidx[(i, b_)]] = d.get(uidx[(i, b_)], Fraction(0)) + s1 * cv[k]
                if (i, a_) in uidx:
                    cv = c[(b_, i)]
                    for k in range(ncomp):
                        if cv[k] != 0:
                            d = rowsk[k]
                            d[uidx[(i, a_)]] = d.get(uidx[(i, a_)], Fraction(0)) + s2 * cv[k]
            cab = c[(a_, b_)]
            for m in range(dim):
                if cab[m] != 0:
                    for k in range(ncomp):
                        if (k, m) in uidx:
                            d = rowsk[k]
                            d[uidx[(k, m)]] = d.get(uidx[(k, m)], Fraction(0)) - cab[m]
            gab = gamma[(a_, b_)]
            for k in range(ncomp):
                rowA = {t: v for t, v in rowsk[k].items() if v != 0}
                rowG = {t: gab.get(nm, zero)[k] for t, nm in enumerate(names) if gab.get(nm, zero)[k] != 0}
                if rowA or rowG:
                    rows_A.append(rowA)
                    rows_G.append(rowG)
    return unknowns, rows_A, rows_G


# --------------------------------------------------------------------------------------
# odd second cohomology H^2(g, Pi g)  (values in g, i.e. modulo scalars) -- context only
# --------------------------------------------------------------------------------------
def odd_H2(B, c, p=1000003):
    """dim Z^2_odd, dim B^2_odd, dim H^2_odd for odd super-skew 2-cochains g x g -> g."""
    import numpy as np
    dim = len(B)
    par = [p_ for _, _, p_, _ in B]
    # unknowns: gamma(a,b)^k for a <= b, with parity k = p_a+p_b+1 ; for a == b only if p_a == 1
    unk = []
    for a_ in range(dim):
        for b_ in range(a_, dim):
            if a_ == b_ and par[a_] == 0:
                continue
            for k in range(dim):
                if par[k] == (par[a_] + par[b_] + 1) % 2:
                    unk.append((a_, b_, k))
    uidx = {u: t for t, u in enumerate(unk)}

    def gcoef(a_, b_, k):
        """gamma(a,b)^k as (unknown index, sign) or None"""
        if a_ <= b_:
            t = uidx.get((a_, b_, k))
            return (t, 1) if t is not None else None
        t = uidx.get((b_, a_, k))
        return (t, -((-1) ** (par[a_] * par[b_]))) if t is not None else None

    def rows():
        for x in range(dim):
            for y in range(x, dim):
                for z in range(y, dim):
                    # linear form in gamma for each component k of the Jacobi kappa-part
                    forms = [dict() for _ in range(dim)]

                    def add(t, s, k):
                        if t is None:
                            return
                        forms[k][t[0]] = forms[k].get(t[0], 0) + s * t[1]

                    sx, sy = (-1) ** par[x], (-1) ** par[y]
                    sxy = (-1) ** (par[x] * par[y])
                    # gamma(x,[y,z])
                    for j in range(dim):
                        v = c[(y, z)][j]
                        if v:
                            for k in range(dim):
                                add(gcoef(x, j, k), v, k)
                    # (-1)^{p(x)} [x, gamma(y,z)]
                    for j in range(dim):
                        for k in range(dim):
                            v = c[(x, j)][k]
                            if v:
                                add(gcoef(y, z, j), sx * v, k)
                    # - gamma([x,y],z)
                    for j in range(dim):
                        v = c[(x, y)][j]
                        if v:
                            for k in range(dim):
                                add(gcoef(j, z, k), -v, k)
                    # - [gamma(x,y), z] = + (-1)^{(p(x)+p(y)+1)p(z)} [z, gamma(x,y)]
                    s = (-1) ** ((par[x] + par[y] + 1) * par[z])
                    for j in range(dim):
                        for k in range(dim):
                            v = c[(z, j)][k]
                            if v:
                                add(gcoef(x, y, j), s * v, k)
                    # - (-1)^{p(x)p(y)} gamma(y,[x,z])
                    for j in range(dim):
                        v = c[(x, z)][j]
                        if v:
                            for k in range(dim):
                                add(gcoef(y, j, k), -sxy * v, k)
                    # - (-1)^{p(x)p(y)} (-1)^{p(y)} [y, gamma(x,z)]
                    for j in range(dim):
                        for k in range(dim):
                            v = c[(y, j)][k]
                            if v:
                                add(gcoef(x, z, j), -sxy * sy * v, k)
                    for k in range(dim):
                        if forms[k]:
                            row = [0] * len(unk)
                            den = 1
                            from math import lcm
                            for t, v in forms[k].items():
                                den = lcm(den, Fraction(v).denominator)
                            for t, v in forms[k].items():
                                row[t] = int(Fraction(v) * den)
                            yield row

    rk = rank_mod_p(rows(), len(unk), p=p)
    dimZ2 = len(unk) - rk
    # B^2 : image of coboundary on odd maps g -> g (scalar rows excluded)
    unknowns = [(i, j) for j in range(dim) for i in range(dim) if par[i] != par[j]]
    uidx2 = {u: t for t, u in enumerate(unknowns)}
    # coboundary matrix in the (a<=b, k) coordinates
    def brows():
        for a_ in range(dim):
            for b_ in range(a_, dim):
                if a_ == b_ and par[a_] == 0:
                    continue
                s1 = (-1) ** par[a_]
                s2 = -((-1) ** ((par[a_] + 1) * par[b_]))
                forms = [dict() for _ in range(dim)]
                for i in range(dim):
                    if (i, b_) in uidx2:
                        for k in range(dim):
                            v = c[(a_, i)][k]
                            if v:
                                forms[k][uidx2[(i, b_)]] = forms[k].get(uidx2[(i, b_)], 0) + s1 * v
                    if (i, a_) in uidx2:
                        for k in range(dim):
                            v = c[(b_, i)][k]
                            if v:
                                forms[k][uidx2[(i, a_)]] = forms[k].get(uidx2[(i, a_)], 0) + s2 * v
                for m in range(dim):
                    v = c[(a_, b_)][m]
                    if v:
                        for k in range(dim):
                            if (k, m) in uidx2:
                                forms[k][uidx2[(k, m)]] = forms[k].get(uidx2[(k, m)], 0) - v
                for k in range(dim):
                    if forms[k]:
                        from math import lcm
                        den = 1
                        for t, v in forms[k].items():
                            den = lcm(den, Fraction(v).denominator)
                        row = [0] * len(unknowns)
                        for t, v in forms[k].items():
                            row[t] = int(Fraction(v) * den)
                        yield row
    # rank of the coboundary map = dim B^2 ; compute via the transpose trick: rank(A) = rank(A^T)
    rkB = rank_mod_p(brows(), len(unknowns), p=p)
    return {"dim_C2_odd": len(unk), "dim_Z2_odd": dimZ2, "dim_B2_odd": rkB, "dim_H2_odd": dimZ2 - rkB,
            "dim_Z1_odd": len(unknowns) - rkB}


# --------------------------------------------------------------------------------------
def vec_to_sparse(v, B):
    dim = len(B)
    return {(B[i][0] if i < dim else "1"): str(v[i]) for i in range(dim + 1) if v[i] != 0}
