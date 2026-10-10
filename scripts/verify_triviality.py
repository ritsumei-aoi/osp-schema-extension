#!/usr/bin/env python3
"""
verify_triviality.py
====================

Computational verification for the triviality analysis of the inhomogeneous
(gb) deformations of C(n+1) = osp(2|2n), for n = 1, 2, 3.

Everything is computed with EXACT rational arithmetic (fractions.Fraction);
no external libraries are used.

Mathematical setting (see docs/math/*.md):

  * Oscillators: one standard fermionic pair a^+, a^- with {a^-, a^+} = 1,
    (a^+)^2 = (a^-)^2 = 0, and n bosonic pairs b_k^+, b_k^- with
    [b_k^-, b_l^+] = delta_{kl}.

  * The inhomogeneous deformation is defined by
        [b_j^s, a^sigma] = - gb_{sigma,j,s} * kappa ,
    kappa an odd central element.  Parity consistency of this relation forces
    the gb's to be ordinary (even) scalars: p([b,a]) = 1 = p(gb) + p(kappa)
    requires p(gb) = 0.  (The "Parity Note" of the source document, which
    assigns parity 1 to gb, is addressed in the report: with Grassmann-odd gb
    the same linear algebra applies verbatim, so the conclusion is unchanged.)
    We absorb kappa into the parameter by setting
        ghat_{sigma,j,s} := gb_{sigma,j,s} * kappa ,
    which is an ODD, CENTRAL, NILPOTENT tag: it anticommutes with the
    fermionic oscillators, commutes with the bosonic ones, and all products
    of two ghat's vanish because kappa^2 = 0.  The deformed exchange relation
    used by the engine is therefore

        b_j^s a^sigma = a^sigma b_j^s - ghat_{sigma,j,s} .

  * g = C(n+1) is realized by the quadratics in U(A), *modulo scalars*
    (= modulo the center C*1; this is the "adjoint representation / up to
    scalar" prescription of docs/math/C_coboundary_definition.md).

  * Basis of g:
        even:  N = a^+ a^-                        (the so(2) generator)
               P_kl = b_k^+ b_l^+  (k<=l)
               Q_kl = b_k^+ b_l^-  (all k,l)       } sp(2n)
               M_kl = b_k^- b_l^-  (k<=l)
        odd :  F_{sigma,j,s} = a^sigma b_j^s       (4n root vectors e_{sigma*eps + s*delta_j})

  * Deformed bracket on g:  [X,Y]_def = [X,Y]_0 + sum_alpha ghat_alpha * C_alpha(X,Y)
    (+ central scalar terms, which are recorded separately and quotiented out).
    Since gb is an even scalar commuting with kappa, kappa*gamma(X,Y)
    = sum_alpha ghat_alpha C_alpha(X,Y) gives exactly
        gamma_gb = sum_alpha gb_alpha * C_alpha .
    Triviality of gamma_gb is therefore equivalent to
    sum_alpha gb_alpha [C_alpha] = 0 in H^2; we show each [C_alpha] = 0.

  * Coboundary operator (docs/math/C_coboundary_definition.md), f odd linear:
        (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)]
                         - (-1)^{(p(X)+1) p(Y)} [Y, f(X)]
                         - f([X,Y])

What the script verifies, for n = 1, 2, 3:

  (V1) The quadratics close (mod scalars) and the structure constants satisfy
       the super-Jacobi identity exactly  -> g is the expected Lie superalgebra
       of dimension (2n^2+n+1 | 4n).
  (V2) The deformed bracket satisfies super-Jacobi to first order in ghat
       -> every C_alpha is a genuine (odd) 2-cocycle in the adjoint module.
  (V3) Each C_alpha is homogeneous of ad(N)-degree -sigma(alpha) != 0
       (the grading fact behind the theoretical proof).
  (V4) MAIN RESULT: for each alpha an explicit odd map f_alpha with
       delta f_alpha = C_alpha is CONSTRUCTED (Cartan homotopy: f_alpha is
       proportional to C_alpha(N, .)) and the identity delta f_alpha = C_alpha
       is verified exactly on every pair of basis elements.
       => by linearity, gamma_gb is a coboundary for EVERY value of gb.
  (V5) Independent cross-check (n=1,2): the linear system delta f = C_alpha is
       solved from scratch by Gaussian elimination over Q, confirming (V4) and
       reporting the dimension of the solution space.
  (V6) The residual CENTRAL (scalar) parts of gamma are computed, and the
       script determines whether the triviality survives at the level of the
       central extension ghat' = g + C*1 (i.e. WITHOUT the "up to scalar"
       quotient), for n = 1, 2.

Artifacts written (JSON, exact rationals as strings):
    artifacts/structure_constants_n{N}.json
    artifacts/gamma_components_n{N}.json
    artifacts/triviality_certificate_n{N}.json
"""

from fractions import Fraction
import itertools
import json
import os
import sys

# ----------------------------------------------------------------------------
# 1. Normal-ordering engine for the deformed oscillator algebra
# ----------------------------------------------------------------------------
# A monomial is a tuple of "letters":
#   ('g', (sigma, j, s))  : the central even nilpotent parameter ghat_{sigma,j,s}
#   ('a', sigma)          : fermionic oscillator a^sigma, sigma in {+1,-1}
#   ('b', j, s)           : bosonic oscillator b_j^s, j in 1..n, s in {+1,-1}
# An element of the algebra is a dict {monomial: Fraction}.
# Normal order: ghat first (at most one), then a^+ then a^-, then all b^+
# (sorted by index), then all b^- (sorted by index).

def letter_key(letter):
    if letter[0] == 'g':
        return (0,)
    if letter[0] == 'a':
        return (1, 0 if letter[1] == 1 else 1)
    _, j, s = letter
    return (2, 0 if s == 1 else 1, j)


def normalize(terms):
    """Normal-order a list of (coeff, word) pairs; return dict word->coeff."""
    out = {}
    stack = list(terms)
    while stack:
        coeff, word = stack.pop()
        if coeff == 0:
            continue
        rule = None
        idx = None
        for i in range(len(word) - 1):
            x, y = word[i], word[i + 1]
            if x[0] == 'g' and y[0] == 'g':
                rule, idx = 'kill', i          # ghat*ghat = 0 (first order)
                break
            if x[0] != 'g' and y[0] == 'g':
                # ghat = gb*kappa is ODD central: it anticommutes with the
                # fermionic oscillators and commutes with the bosonic ones.
                rule, idx = ('gswap_sign' if x[0] == 'a' else 'swap'), i
                break
            if x[0] == 'a' and y[0] == 'a':
                if x[1] == y[1]:
                    rule, idx = 'kill', i      # (a^+)^2 = (a^-)^2 = 0
                    break
                if x[1] == -1 and y[1] == 1:
                    rule, idx = 'CAR', i       # a^- a^+ = 1 - a^+ a^-
                    break
                continue
            if x[0] == 'b' and y[0] == 'a':
                rule, idx = 'MIX', i           # b a = a b - ghat   (deformation!)
                break
            if x[0] == 'b' and y[0] == 'b':
                if letter_key(x) > letter_key(y):
                    if x[2] == -1 and y[2] == 1:
                        rule, idx = 'CCR', i   # b_k^- b_l^+ = b_l^+ b_k^- + d_kl
                    else:
                        rule, idx = 'swap', i  # same-sign b's commute
                    break
                continue
            # remaining ordered cases: 'a' before 'b', 'g' first
        if rule is None:
            out[word] = out.get(word, Fraction(0)) + coeff
            continue
        pre, post = word[:idx], word[idx + 2:]
        x, y = word[idx], word[idx + 1]
        if rule == 'kill':
            continue
        elif rule == 'swap':
            stack.append((coeff, pre + (y, x) + post))
        elif rule == 'gswap_sign':
            stack.append((-coeff, pre + (y, x) + post))
        elif rule == 'CAR':
            stack.append((coeff, pre + post))
            stack.append((-coeff, pre + (y, x) + post))
        elif rule == 'CCR':
            stack.append((coeff, pre + (y, x) + post))
            if x[1] == y[1]:
                stack.append((coeff, pre + post))
        elif rule == 'MIX':
            # b_j^s a^sigma = a^sigma b_j^s - ghat_{sigma, j, s}
            stack.append((coeff, pre + (y, x) + post))
            stack.append((-coeff, pre + (('g', (y[1], x[1], x[2])),) + post))
    return {w: c for w, c in out.items() if c != 0}


def mul(X, Y):
    terms = []
    for w1, c1 in X.items():
        for w2, c2 in Y.items():
            terms.append((c1 * c2, w1 + w2))
    return normalize(terms)


def sbracket(X, pX, Y, pY):
    """Super-bracket [X,Y] = XY - (-1)^{pX pY} YX in the associative algebra."""
    sign = -1 if (pX and pY) else 1
    A = mul(X, Y)
    B = mul(Y, X)
    out = dict(A)
    for w, c in B.items():
        out[w] = out.get(w, Fraction(0)) - sign * c
    return {w: c for w, c in out.items() if c != 0}


# ----------------------------------------------------------------------------
# 2. Basis of g = C(n+1) (quadratics, mod scalars)
# ----------------------------------------------------------------------------

def build_basis(n):
    """Return list of (name, word, parity, adN_degree)."""
    basis = [('N', (('a', 1), ('a', -1)), 0, 0)]
    for k in range(1, n + 1):
        for l in range(k, n + 1):
            basis.append((f'P_{k}_{l}', (('b', k, 1), ('b', l, 1)), 0, 0))
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            basis.append((f'Q_{k}_{l}', (('b', k, 1), ('b', l, -1)), 0, 0))
    for k in range(1, n + 1):
        for l in range(k, n + 1):
            basis.append((f'M_{k}_{l}', (('b', k, -1), ('b', l, -1)), 0, 0))
    for sigma in (1, -1):
        for j in range(1, n + 1):
            for s in (1, -1):
                nm = f'F_{"p" if sigma == 1 else "m"}_{j}_{"p" if s == 1 else "m"}'
                basis.append((nm, (('a', sigma), ('b', j, s)), 1, sigma))
    return basis


def param_name(alpha):
    sigma, j, s = alpha
    return f'gb({"+" if sigma == 1 else "-"},{j},{"+" if s == 1 else "-"})'


# ----------------------------------------------------------------------------
# 3. Decomposition of bracket results onto the basis (+ scalar + ghat parts)
# ----------------------------------------------------------------------------

def decompose(el, wordindex):
    """el -> (vec {k:coeff}, scalar, gvec {alpha:{k:coeff}}, gscal {alpha:coeff})."""
    vec, scal, gvec, gscal = {}, Fraction(0), {}, {}
    for w, c in el.items():
        if w and w[0][0] == 'g':
            alpha, rest = w[0][1], w[1:]
            if rest == ():
                gscal[alpha] = gscal.get(alpha, Fraction(0)) + c
            else:
                k = wordindex[rest]  # KeyError => bracket does not close: bug
                d = gvec.setdefault(alpha, {})
                d[k] = d.get(k, Fraction(0)) + c
        else:
            if w == ():
                scal += c
            else:
                vec[w and wordindex[w]] = vec.get(wordindex[w], Fraction(0)) + c
    clean = lambda d: {k: v for k, v in d.items() if v != 0}
    return (clean(vec), scal,
            {a: clean(v) for a, v in gvec.items() if clean(v)},
            {a: v for a, v in gscal.items() if v != 0})


# small sparse-vector helpers ------------------------------------------------

def vadd(acc, vec, coeff=Fraction(1)):
    for k, v in vec.items():
        acc[k] = acc.get(k, Fraction(0)) + coeff * v


def vclean(vec):
    return {k: v for k, v in vec.items() if v != 0}


# ----------------------------------------------------------------------------
# 4. Main computation per n
# ----------------------------------------------------------------------------

def compute_algebra(n):
    basis = build_basis(n)
    dim = len(basis)
    words = {b[1]: i for i, b in enumerate(basis)}
    par = [b[2] for b in basis]
    deg = [b[3] for b in basis]
    elems = [{b[1]: Fraction(1)} for b in basis]

    c = {}      # (i,j) -> {k: coeff}      undeformed structure constants mod scalars
    s = {}      # (i,j) -> Fraction        central-extension 2-cocycle (scalar part)
    G = {}      # alpha -> {(i,j): {k: coeff}}   gamma components C_alpha
    GS = {}     # alpha -> {(i,j): Fraction}     scalar parts of gamma

    for i in range(dim):
        for j in range(dim):
            br = sbracket(elems[i], par[i], elems[j], par[j])
            vec, scal, gvec, gscal = decompose(br, words)
            c[(i, j)] = vec
            s[(i, j)] = scal
            for a, v in gvec.items():
                G.setdefault(a, {})[(i, j)] = v
            for a, v in gscal.items():
                GS.setdefault(a, {})[(i, j)] = v
    params = [(sigma, j, sg) for sigma in (1, -1)
              for j in range(1, n + 1) for sg in (1, -1)]
    for a in params:
        G.setdefault(a, {})
        GS.setdefault(a, {})
    return basis, par, deg, c, s, G, GS, params


def check_jacobi(dim, par, c, G=None, params=None):
    """Super-Jacobi: [Xi,[Xj,Xk]] = [[Xi,Xj],Xk] + (-1)^{pi pj} [Xj,[Xi,Xk]].
    If G/params given, also check the first-order ghat terms (cocycle cond.)."""
    def comp(bracket_outer, inner):
        acc = {}
        for m, cm in inner.items():
            vadd(acc, bracket_outer(m), cm)
        return vclean(acc)

    n_checked = 0
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                sg = -1 if (par[i] and par[j]) else 1
                # order-0 part
                t1 = comp(lambda m: c[(i, m)], c[(j, k)])
                t2 = comp(lambda m: c[(m, k)], c[(i, j)])
                t3 = comp(lambda m: c[(j, m)], c[(i, k)])
                acc = dict(t1)
                vadd(acc, t2, Fraction(-1))
                vadd(acc, t3, Fraction(-sg))
                if vclean(acc):
                    raise AssertionError(f'Jacobi fails (order 0) at {(i, j, k)}')
                if G is not None:
                    # First order in ghat.  ghat is ODD central, so moving it
                    # out of an inner bracket past an outer odd element costs
                    # a sign:  [X_i, ghat*W] = (-1)^{p_i} ghat [X_i, W], while
                    # [ghat*W, X_k] = ghat [W, X_k].
                    sgn_i = Fraction(-1) if par[i] else Fraction(1)
                    sgn_j = Fraction(-1) if par[j] else Fraction(1)
                    for a in params:
                        Ga = G[a]
                        u1 = comp(lambda m: Ga.get((i, m), {}), c[(j, k)])
                        vadd(u1, comp(lambda m: c[(i, m)], Ga.get((j, k), {})),
                             sgn_i)
                        u2 = comp(lambda m: Ga.get((m, k), {}), c[(i, j)])
                        vadd(u2, comp(lambda m: c[(m, k)], Ga.get((i, j), {})))
                        u3 = comp(lambda m: Ga.get((j, m), {}), c[(i, k)])
                        vadd(u3, comp(lambda m: c[(j, m)], Ga.get((i, k), {})),
                             sgn_j)
                        acc = dict(u1)
                        vadd(acc, u2, Fraction(-1))
                        vadd(acc, u3, Fraction(-sg))
                        if vclean(acc):
                            raise AssertionError(
                                f'Jacobi fails (order 1, {a}) at {(i, j, k)}')
                n_checked += 1
    return n_checked


def delta_f(f, dim, par, c):
    """(delta f)(Xi,Xj) = (-1)^{pi}[Xi,f(Xj)] - (-1)^{(pi+1)pj}[Xj,f(Xi)] - f([Xi,Xj]).
    f: dict i -> {k: coeff}.  Returns dict (i,j) -> {k: coeff} (mod scalars)."""
    out = {}
    for i in range(dim):
        for j in range(dim):
            acc = {}
            s1 = Fraction(-1) if par[i] else Fraction(1)
            for k, fk in f.get(j, {}).items():
                vadd(acc, c[(i, k)], s1 * fk)
            s2 = Fraction(-1) if ((par[i] + 1) * par[j]) % 2 else Fraction(1)
            for k, fk in f.get(i, {}).items():
                vadd(acc, c[(j, k)], -s2 * fk)
            for m, cm in c[(i, j)].items():
                vadd(acc, f.get(m, {}), -cm)
            acc = vclean(acc)
            if acc:
                out[(i, j)] = acc
    return out


def cochain_eq(A, B):
    keys = set(A) | set(B)
    for k in keys:
        if vclean({m: A.get(k, {}).get(m, Fraction(0)) - B.get(k, {}).get(m, Fraction(0))
                   for m in set(A.get(k, {})) | set(B.get(k, {}))}):
            return False
    return True


def homotopy_solution(Ga, iN, dim, par, c):
    """Try f(X) = lam * C_alpha(N, X) (and sign variants); return f with
    delta f = C_alpha exactly, or None."""
    candidates = []
    u1 = {j: v for (i, j), v in Ga.items() if i == iN}
    u2 = {j: {k: (-cv if par[j] else cv) for k, cv in v.items()}
          for j, v in u1.items()}
    u3 = {i: v for (i, j), v in Ga.items() if j == iN}
    candidates = [u1, u2, u3]
    for u in candidates:
        u = {j: vclean(v) for j, v in u.items() if vclean(v)}
        if not u:
            continue
        w = delta_f(u, dim, par, c)
        # find ratio r with w = r * Ga
        r = None
        ok = True
        keys = set(w) | set(Ga)
        for key in keys:
            wv, gv = w.get(key, {}), Ga.get(key, {})
            for m in set(wv) | set(gv):
                a, b = wv.get(m, Fraction(0)), gv.get(m, Fraction(0))
                if b == 0:
                    if a != 0:
                        ok = False
                    continue
                rr = Fraction(a, 1) / b
                if r is None:
                    r = rr
                elif rr != r:
                    ok = False
            if not ok:
                break
        if ok and r not in (None, 0):
            f = {j: {k: cv / r for k, cv in v.items()} for j, v in u.items()}
            if cochain_eq(delta_f(f, dim, par, c), Ga):
                return f, r
    return None, None


def closed_form_f(alpha, basis, names):
    """The closed-form odd map claimed in the report, for alpha=(sigma,j,s):
         f_alpha(N) = 0
         f_alpha(B) = - (dB/db_j^s) * a^{-sigma}          for B in sp(2n)
         f_alpha(F_beta) = delta_{alpha,beta} * sigma * N  (mod scalars)
       Returns dict i -> {k: coeff}."""
    sigma, j, s = alpha
    idx = {b[0]: i for i, b in enumerate(basis)}
    f = {}
    for i, (nm, word, par_i, _) in enumerate(basis):
        if par_i == 0 and nm != 'N':
            # word = (('b',k,t), ('b',l,u)); formal derivative w.r.t. b_j^s
            vec = {}
            for pos in (0, 1):
                if word[pos][1] == j and word[pos][2] == s:
                    other = word[1 - pos]
                    tgt = (f'F_{"p" if -sigma == 1 else "m"}_{other[1]}'
                           f'_{"p" if other[2] == 1 else "m"}')
                    vec[idx[tgt]] = vec.get(idx[tgt], Fraction(0)) - 1
            if vec:
                f[i] = vec
        elif par_i == 1:
            if word == (('a', sigma), ('b', j, s)):
                f[i] = {idx['N']: Fraction(sigma)}
    return f


# ----------------------------------------------------------------------------
# 5. Independent linear solve (Gaussian elimination over Q)
# ----------------------------------------------------------------------------

def solve_linear_system(rows, rhs, nvars):
    """Solve rows * x = rhs over Q. rows: list of dict col->coeff.
    Returns (solution dict or None, nullity)."""
    aug = [dict(r, **{'rhs': v}) for r, v in zip(rows, rhs)]
    pivots = {}
    for col in range(nvars):
        piv = None
        for ridx, r in enumerate(aug):
            if ridx in pivots.values():
                continue
            if r.get(col, Fraction(0)) != 0:
                piv = ridx
                break
        if piv is None:
            continue
        pr = aug[piv]
        pc = pr[col]
        for k in list(pr):
            pr[k] = pr[k] / pc
        for ridx, r in enumerate(aug):
            if ridx == piv:
                continue
            factor = r.get(col, Fraction(0))
            if factor:
                for k, v in pr.items():
                    r[k] = r.get(k, Fraction(0)) - factor * v
                    if r[k] == 0:
                        del r[k]
        pivots[col] = piv
    # consistency
    for ridx, r in enumerate(aug):
        if ridx in pivots.values():
            continue
        if r.get('rhs', Fraction(0)) != 0 and not any(
                k != 'rhs' and v != 0 for k, v in r.items()):
            return None, None
        if r.get('rhs', Fraction(0)) != 0 and all(
                (k == 'rhs' or v == 0) for k, v in r.items()):
            return None, None
    sol = {col: aug[piv].get('rhs', Fraction(0)) for col, piv in pivots.items()}
    nullity = nvars - len(pivots)
    return sol, nullity


def independent_solve(Ga, dim, par, c, include_center=False, s=None):
    """Solve delta f = C_alpha from scratch.  Unknowns: phi_{k,i} for all
    parity-reversing pairs (p_k != p_i).  If include_center, work in the
    central extension g + C*I: add unknowns theta_i (I-component of f(X_i),
    only for odd i) and match the scalar parts too (s = extension cocycle,
    GSa = scalar part of gamma passed inside Ga as key 'scal')."""
    Ga_vec, Ga_scal = Ga
    varindex = {}
    for k in range(dim):
        for i in range(dim):
            if par[k] != par[i]:
                varindex[('phi', k, i)] = len(varindex)
    if include_center:
        for i in range(dim):
            if par[i] == 1:
                varindex[('theta', i)] = len(varindex)
    rows, rhs = [], []
    for i in range(dim):
        for j in range(dim):
            s1 = Fraction(-1) if par[i] else Fraction(1)
            s2 = Fraction(-1) if ((par[i] + 1) * par[j]) % 2 else Fraction(1)
            # g-components
            comp = {}
            # (-1)^{pi} [Xi, f(Xj)] : sum_k phi_{k,j} c[(i,k)]
            for k in range(dim):
                if par[k] == par[j]:
                    continue
                for m, cv in c[(i, k)].items():
                    d = comp.setdefault(m, {})
                    d[('phi', k, j)] = d.get(('phi', k, j), Fraction(0)) + s1 * cv
            for k in range(dim):
                if par[k] == par[i]:
                    continue
                for m, cv in c[(j, k)].items():
                    d = comp.setdefault(m, {})
                    d[('phi', k, i)] = d.get(('phi', k, i), Fraction(0)) - s2 * cv
            for m, cv in c[(i, j)].items():
                for k in range(dim):
                    if par[k] == par[m]:
                        continue
                    d = comp.setdefault(k, {})
                    d[('phi', k, m)] = d.get(('phi', k, m), Fraction(0)) - cv
            target = Ga_vec.get((i, j), {})
            for m in set(comp) | set(target):
                row = {varindex[v]: cv for v, cv in comp.get(m, {}).items() if cv != 0}
                rows.append(row)
                rhs.append(target.get(m, Fraction(0)))
            if include_center:
                # scalar component of delta f:
                #  s1 * sum_k phi_{k,j} s[(i,k)] - s2 * sum_k phi_{k,i} s[(j,k)]
                #  - sum_m c[(i,j)][m] theta_m        (theta only for odd m)
                row = {}
                for k in range(dim):
                    if par[k] != par[j] and s[(i, k)] != 0:
                        row[varindex[('phi', k, j)]] = \
                            row.get(varindex[('phi', k, j)], Fraction(0)) + s1 * s[(i, k)]
                for k in range(dim):
                    if par[k] != par[i] and s[(j, k)] != 0:
                        row[varindex[('phi', k, i)]] = \
                            row.get(varindex[('phi', k, i)], Fraction(0)) - s2 * s[(j, k)]
                for m, cv in c[(i, j)].items():
                    if par[m] == 1:
                        row[varindex[('theta', m)]] = \
                            row.get(varindex[('theta', m)], Fraction(0)) - cv
                row = {k: v for k, v in row.items() if v != 0}
                rows.append(row)
                rhs.append(Ga_scal.get((i, j), Fraction(0)))
    sol, nullity = solve_linear_system(rows, rhs, len(varindex))
    return sol, nullity, varindex


# ----------------------------------------------------------------------------
# 6. JSON serialization helpers
# ----------------------------------------------------------------------------

def frs(x):
    return str(x)


def vec_json(vec, names):
    return {names[k]: frs(v) for k, v in sorted(vec.items())}


def run(n, outdir, do_full_jacobi=True, do_independent_solve=True,
        do_center_check=True):
    print(f'================ n = {n}  (C({n+1}) = osp(2|{2*n})) ================')
    basis, par, deg, c, s, G, GS, params = compute_algebra(n)
    dim = len(basis)
    names = [b[0] for b in basis]
    iN = names.index('N')
    n_even = sum(1 for p in par if p == 0)
    n_odd = dim - n_even
    assert n_even == 2 * n * n + n + 1 and n_odd == 4 * n, 'dimension mismatch'
    print(f'dim g = ({n_even} | {n_odd}) = {dim}   [expected ({2*n*n+n+1} | {4*n})]')

    # (V1)+(V2) Jacobi / cocycle check
    if do_full_jacobi:
        nchk = check_jacobi(dim, par, c, G, params)
        print(f'(V1) super-Jacobi (order 0) holds on all {nchk} triples: OK')
        print(f'(V2) super-Jacobi to first order in ghat holds on all triples')
        print(f'     => every C_alpha is a 2-cocycle in the adjoint module: OK')
    else:
        nchk = check_jacobi(dim, par, c)   # order 0 only
        print(f'(V1) super-Jacobi (order 0) holds on all {nchk} triples: OK')
        print('(V2) first-order cocycle condition: implied by (V4) below '
              '(coboundaries are cocycles)')

    # (V3) degree homogeneity of each C_alpha
    for a in params:
        sigma = a[0]
        for (i, j), v in G[a].items():
            for k in v:
                assert deg[k] - deg[i] - deg[j] == -sigma, \
                    f'degree inhomogeneity for {param_name(a)}'
    print('(V3) each C_alpha is ad(N)-homogeneous of degree -sigma(alpha): OK')

    # (V4) homotopy construction of f_alpha with delta f_alpha = C_alpha
    certificates = {}
    for a in params:
        if not G[a]:
            certificates[a] = ({}, None)
            continue
        f, r = homotopy_solution(G[a], iN, dim, par, c)
        assert f is not None, f'homotopy failed for {param_name(a)}'
        assert cochain_eq(delta_f(f, dim, par, c), G[a])
        certificates[a] = (f, r)
    print(f'(V4) MAIN: for each of the {len(params)} parameters gb_alpha an '
          f'explicit odd map')
    print('     f_alpha = (1/r_alpha) C_alpha(N, .) with delta f_alpha = '
          'C_alpha was found and')
    print('     verified exactly on all basis pairs.  Ratios r_alpha:')
    for a in params:
        f, r = certificates[a]
        print(f'       {param_name(a)}: r = {r}   '
              f'(sigma = {a[0]:+d}, support size |f| = {len(f)})')

    # (V7) the closed-form f of the report reproduces C_alpha exactly
    for a in params:
        fc = closed_form_f(a, basis, names)
        assert cochain_eq(delta_f(fc, dim, par, c), G[a]), \
            f'closed-form f fails for {param_name(a)}'
        # and it agrees with the homotopy construction (mod scalars)
        fh = certificates[a][0]
        assert all(vclean({k: fc.get(i, {}).get(k, Fraction(0)) -
                           fh.get(i, {}).get(k, Fraction(0))
                           for k in set(fc.get(i, {})) | set(fh.get(i, {}))}) == {}
                   for i in set(fc) | set(fh))
    print('(V7) the closed-form map  f_a(N)=0, f_a(B)=-(dB/db_j^s) a^{-sigma}, '
          'f_a(F_a)=sigma*N')
    print('     satisfies delta f_a = C_a exactly and coincides with the '
          'homotopy solution: OK')

    # (V5) independent linear solve
    if do_independent_solve:
        for a in params:
            sol, nullity, varindex = independent_solve(
                (G[a], GS[a]), dim, par, c, include_center=False)
            assert sol is not None, f'independent solve failed for {param_name(a)}'
        print(f'(V5) independent Gaussian-elimination solve of delta f = C_alpha '
              f'succeeded for all alpha')
        print(f'     (solution space affine of dim = ker(delta^1) = {nullity} '
              f'for each alpha): OK')

    # (V6) central (scalar) analysis
    center_result = None
    if do_center_check:
        nonzero_scal = {param_name(a): {f'[{names[i]},{names[j]}]': frs(v)
                                        for (i, j), v in GS[a].items()}
                        for a in params if GS[a]}
        print(f'(V6) residual scalar (central) parts of gamma: '
              f'{sum(len(v) for v in nonzero_scal.values())} nonzero entries')
        center_ok = {}
        for a in params:
            sol, nullity, varindex = independent_solve(
                (G[a], GS[a]), dim, par, c, include_center=True, s=s)
            center_ok[param_name(a)] = (sol is not None)
        if all(center_ok.values()):
            print('     delta f = gamma is solvable EVEN INCLUDING the scalar '
                  'parts (central extension level),')
            print('     when f is allowed a scalar component on odd elements: OK')
        else:
            bad = [k for k, v in center_ok.items() if not v]
            print(f'     scalar parts NOT exact for {bad} -> the "up to scalar" '
                  f'quotient is essential there')
        center_result = center_ok

    # ---------------- artifacts ----------------
    os.makedirs(outdir, exist_ok=True)
    meta = {
        'algebra': f'C({n+1}) = osp(2|{2*n})',
        'n': n,
        'dim_even': n_even, 'dim_odd': n_odd,
        'conventions': {
            'basis': 'N=a+a-, P_kl=bk+bl+ (k<=l), Q_kl=bk+bl-, M_kl=bk-bl- (k<=l), '
                     'F_{sigma}_{j}_{s}=a^sigma bj^s; p/m encode +/-',
            'deformed_relation': 'b_j^s a^sigma = a^sigma b_j^s - ghat_{sigma,j,s}, '
                                 'ghat = gb*kappa (odd central nilpotent tag; '
                                 'gb even scalar, kappa odd central, kappa^2=0)',
            'gamma': '[X,Y]_def = [X,Y]_0 + sum_alpha ghat_alpha C_alpha(X,Y) '
                     '+ central scalars; doc gamma_gb = sum_alpha gb_alpha C_alpha',
            'delta_f': '(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] '
                       '- (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])',
            'scalars': 'structure constants and cocycles are reported modulo C*1 '
                       '(adjoint representation / up-to-scalar prescription); the '
                       'central parts are reported separately',
        },
    }
    sc = dict(meta)
    sc['basis'] = [{'name': b[0], 'parity': b[2], 'adN_degree': b[3],
                    'word': [list(l) for l in b[1]]} for b in basis]
    sc['brackets'] = [
        {'i': names[i], 'j': names[j],
         'value': vec_json(c[(i, j)], names),
         'central_scalar': frs(s[(i, j)])}
        for i in range(dim) for j in range(dim)
        if c[(i, j)] or s[(i, j)] != 0]
    with open(os.path.join(outdir, f'structure_constants_n{n}.json'), 'w') as fh:
        json.dump(sc, fh, indent=1)

    gm = dict(meta)
    gm['gamma_components'] = [
        {'param': param_name(a),
         'sigma': a[0], 'j': a[1], 's': a[2],
         'adN_degree_of_cochain': -a[0],
         'entries': [{'i': names[i], 'j': names[j],
                      'value': vec_json(v, names),
                      'central_scalar': frs(GS[a].get((i, j), Fraction(0)))}
                     for (i, j), v in sorted(G[a].items())]}
        for a in params]
    with open(os.path.join(outdir, f'gamma_components_n{n}.json'), 'w') as fh:
        json.dump(gm, fh, indent=1)

    ct = dict(meta)
    ct['theorem'] = ('For EVERY value of the parameters gb the inhomogeneous '
                     'deformation gamma_gb of C(n+1) is TRIVIAL: gamma_gb = '
                     'delta f_gb with f_gb = sum_alpha gb_alpha f_alpha, '
                     'f_alpha below (f_alpha = -(1/sigma) C_alpha(N, .)). '
                     'The triviality condition on gb is vacuous.')
    ct['certificates'] = [
        {'param': param_name(a),
         'homotopy_ratio_r': frs(certificates[a][1]) if certificates[a][1] is not None else None,
         'f_alpha (delta f_alpha = C_alpha, values mod scalars)':
             {names[i]: vec_json(v, names)
              for i, v in sorted(certificates[a][0].items())}}
        for a in params]
    if center_result is not None:
        ct['central_extension_check'] = {
            'question': 'is delta f = gamma solvable INCLUDING scalar parts '
                        '(i.e. without the up-to-scalar quotient), allowing f '
                        'a scalar component on odd elements?',
            'answer_per_param': center_result}
    with open(os.path.join(outdir, f'triviality_certificate_n{n}.json'), 'w') as fh:
        json.dump(ct, fh, indent=1)
    print(f'artifacts written to {outdir}/*_n{n}.json')
    print()
    return certificates


if __name__ == '__main__':
    outdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          'artifacts')
    run(1, outdir, do_full_jacobi=True, do_independent_solve=True, do_center_check=True)
    run(2, outdir, do_full_jacobi=True, do_independent_solve=True, do_center_check=True)
    run(3, outdir, do_full_jacobi=True, do_independent_solve=False, do_center_check=False)
    print('ALL VERIFICATIONS PASSED')
    print('CONCLUSION: gamma_gb is a coboundary for every gb '
          '(triviality condition: no constraint on gb).')
