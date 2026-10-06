"""
basis.py
========
Basis of g = C(n+1) = osp(2|2n) as quadratic oscillator monomials.

Even (parity 0), dim = 2n^2+n+1:
  h            = a1^+ a1^-                       (so(2))              1
  Mpp[(j,k)]   = b_j^+ b_k^+   (j<=k)            sp(2n) sym           n(n+1)/2
  Mmm[(j,k)]   = b_j^- b_k^-   (j<=k)            sp(2n) sym           n(n+1)/2
  Mpm[(j,k)]   = b_j^+ b_k^-   (all j,k)         gl(n)                n^2
Odd (parity 1), dim = 4n:
  F[(sigma,s,j)] = a1^sigma b_j^s               osp odd roots        4n
"""

def build_basis(n):
    """Returns (basis, parity, names) where basis is list of elements
       (dict (kpow,tokens)->coeff), parity list, names list."""
    basis = []
    parity = []
    names = []

    def elt(tokens):
        return {(0, tuple(tokens)): 1}

    # ---- even ----
    basis.append(elt([('a', '+'), ('a', '-')])); parity.append(0); names.append('h')

    for j in range(1, n + 1):
        for k in range(j, n + 1):
            basis.append(elt([('b', '+', j), ('b', '+', k)])); parity.append(0)
            names.append(f'Mpp_{j}{k}')
    for j in range(1, n + 1):
        for k in range(j, n + 1):
            basis.append(elt([('b', '-', j), ('b', '-', k)])); parity.append(0)
            names.append(f'Mmm_{j}{k}')
    for j in range(1, n + 1):
        for k in range(1, n + 1):
            basis.append(elt([('b', '+', j), ('b', '-', k)])); parity.append(0)
            names.append(f'Mpm_{j}{k}')

    # ---- odd ----
    for sigma in ('+', '-'):
        for s in ('+', '-'):
            for j in range(1, n + 1):
                basis.append(elt([('a', sigma), ('b', s, j)])); parity.append(1)
                names.append(f'F_{sigma}{s}{j}')

    return basis, parity, names


def monomial_to_index(n, names):
    """Map a normal-ordered degree-2 *g-monomial* token tuple -> basis index.
       Returns dict tokens_tuple -> index. (Only pure g generators; central
       scalars / degree != 2 are not included.)"""
    basis, parity, nm = build_basis(n)
    idx = {}
    for i, b in enumerate(basis):
        (key, coeff), = b.items()
        kp, toks = key
        assert kp == 0 and coeff == 1
        idx[toks] = i
    return idx
