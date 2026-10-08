"""Oscillator realization of C(n+1) = osp(2|2n) with exact rational arithmetic.

Letters
    ('a', s)     standard fermion a_1^s,  s in {+1, -1}   (parity 1)
    ('b', k, s)  boson b_k^s, k = 1..n,   s in {+1, -1}   (parity 0)

Words are tuples of letters in canonical order (see ``_key``). The algebra is
the Weyl-Clifford algebra with the relations

    {a^-, a^+} = 1, (a^±)^2 = 0,   [b_k^-, b_l^+] = δ_kl,   others 0,

together with the deformation (inhomogeneous, linear in κ)

    [b_k^s, a^σ] = -gb_{σ,k,s} κ,    κ odd, central, κ^2 = 0.

An element is a dict ``{(g, word): Fraction}``. ``g`` is ``None`` for a κ-free
term, or a tuple ``(σ, k, s)`` meaning the term carries ``κ · gb_{σ,k,s}``.
The constant word ``()`` is the identity, identified with K.
"""

from fractions import Fraction
from functools import lru_cache


def _key(letter):
    """Canonical order: fermions before bosons; '+' before '-'; then by k."""
    if letter[0] == 'a':
        return (0, 0 if letter[1] > 0 else 1, 0)
    return (1, 0 if letter[2] > 0 else 1, letter[1])


def is_fermion(letter):
    return letter[0] == 'a'


def parity(word):
    """Parity of a word: number of fermion letters mod 2."""
    return sum(1 for letter in word if letter[0] == 'a') % 2


@lru_cache(maxsize=None)
def _reduce(word, kappa):
    """Normal-order ``word``. Returns a tuple of ``((g, word), coeff)``.

    ``kappa`` is the gb-index of a κ already present at the front (or None).
    Any second κ is dropped because κ^2 = 0.
    """
    for i in range(len(word) - 1):
        x, y = word[i], word[i + 1]
        if x == y and is_fermion(x):
            return ()                      # (a^±)^2 = 0
        if _key(x) > _key(y):
            return _swap(word, i, kappa)
    return (((kappa, word), Fraction(1)),)


def _swap(word, i, kappa):
    """Rewrite the inversion at position i (x = word[i], y = word[i+1])."""
    x, y = word[i], word[i + 1]
    pre, post = word[:i], word[i + 2:]
    out = {}

    def add(items, factor):
        for term, c in items:
            out[term] = out.get(term, 0) + factor * c

    if is_fermion(x) and is_fermion(y):
        # x y = -y x + {x, y}
        add(_reduce(pre + (y, x) + post, kappa), -1)
        if x[1] == -y[1]:
            add(_reduce(pre + post, kappa), 1)
    elif not is_fermion(x) and not is_fermion(y):
        # x = b^-_k, y = b^+_l (key order): x y = y x + δ_kl
        add(_reduce(pre + (y, x) + post, kappa), 1)
        if x[1] == y[1] and x[2] < 0 < y[2]:
            add(_reduce(pre + post, kappa), 1)
    else:
        # x boson, y fermion: x y = y x + [x, y] = y x - gb κ
        add(_reduce(pre + (y, x) + post, kappa), 1)
        if kappa is None:
            sign = (-1) ** parity(pre)     # move κ to the front past pre
            gb_index = (y[1], x[1], x[2])
            add(_reduce(pre + post, gb_index), -sign)
    return tuple((term, c) for term, c in out.items() if c != 0)


def normal_order(terms):
    """Normal-order a list of ``(coeff, raw_word)`` pairs (κ-free)."""
    out = {}
    for c, word in terms:
        for term, d in _reduce(tuple(word), None):
            out[term] = out.get(term, 0) + c * d
    return {k: v for k, v in out.items() if v != 0}


def mul(A, B):
    """Product of two elements in the deformed associative algebra."""
    out = {}
    for (ga, wa), ca in A.items():
        for (gb_, wb), cb in B.items():
            if ga is not None and gb_ is not None:
                continue                  # κ^2 = 0
            if gb_ is not None:
                sign, kap = (-1) ** parity(wa), gb_   # κ moves past wa
            else:
                sign, kap = 1, ga
            for term, c in _reduce(wa + wb, kap):
                out[term] = out.get(term, 0) + sign * ca * cb * c
    return {k: v for k, v in out.items() if v != 0}


def bracket(A, B, pA, pB):
    """Super-commutator [A, B] = AB - (-1)^{pA pB} BA."""
    s = -1 if (pA * pB) % 2 else 1
    out = dict(mul(A, B))
    for k, v in mul(B, A).items():
        out[k] = out.get(k, 0) - s * v
    return {k: v for k, v in out.items() if v != 0}


def kappa_free(elem):
    return {k: v for k, v in elem.items() if k[0] is None}


def kappa_part(elem):
    """Return {gb_index: {word: coeff}} for the κ-linear part of elem."""
    out = {}
    for (g, w), c in elem.items():
        if g is not None:
            out.setdefault(g, {})[w] = c
    return out


def letter_label(letter):
    if letter[0] == 'a':
        return 'a_1_p' if letter[1] > 0 else 'a_1_m'
    return f"b_{letter[1]}_{'p' if letter[2] > 0 else 'm'}"


def gb_label(g):
    sigma, k, s = g
    return f"gb_a1{'p' if sigma > 0 else 'm'}_b{k}{'p' if s > 0 else 'm'}"


def build_basis(n):
    """Return the PBW-ordered basis of C(n+1) as a list of dicts.

    Each dict has keys: label, parity, elem (κ-free normal-ordered element).
    Ordering (fixed in I01): odd block, then even block.
    """
    def b(k, s):
        return ('b', k, s)

    def a(s):
        return ('a', s)

    P, M = 1, -1
    entries = []
    for (s, t, code) in [(P, P, 'pp'), (P, M, 'pm'), (M, P, 'mp'), (M, M, 'mm')]:
        for k in range(1, n + 1):
            entries.append((f'E_eps1_del{k}_{code}', 1,
                            [(1, (a(s), b(k, t)))]))

    even = []
    h1 = [(1, (a(P), a(M))), (1, (b(1, P), b(1, M)))]
    even.append(('H_1', h1))
    for k in range(2, n + 1):
        even.append((f'H_{k}', [(1, (b(k - 1, P), b(k - 1, M))),
                                (-1, (b(k, P), b(k, M)))]))
    even.append((f'H_{n + 1}', [(-1, (b(n, P), b(n, M))),
                                (Fraction(-1, 2), ())]))
    for k in range(1, n + 1):
        even.append((f'E_2del{k}_p', [(1, (b(k, P), b(k, P)))]))
    for k in range(1, n + 1):
        even.append((f'E_2del{k}_m', [(1, (b(k, M), b(k, M)))]))
    for (s, t, code) in [(P, P, 'pp'), (P, M, 'pm'), (M, P, 'mp'), (M, M, 'mm')]:
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                even.append((f'E_del{i}_del{j}_{code}', [(1, (b(i, s), b(j, t)))]))

    out = []
    for label, p, spec in entries:
        out.append({'label': label, 'parity': p,
                    'elem': normal_order(spec)})
    for label, spec in even:
        out.append({'label': label, 'parity': 0,
                    'elem': normal_order(spec)})
    return out


class Decomposer:
    """Exact coordinates of κ-free elements in a fixed basis."""

    def __init__(self, basis):
        self.basis = basis
        words = sorted({w for item in basis for (_, w) in item['elem']},
                       key=lambda w: (len(w), w))
        self.words = words
        d = len(basis)
        M = [[item['elem'].get((None, w), Fraction(0)) for item in basis]
             for w in words]
        # choose d linearly independent rows
        rows, A = [], []
        for r, row in enumerate(M):
            trial = A + [row]
            if _rank(trial) == len(trial):
                A = trial
                rows.append(r)
            if len(rows) == d:
                break
        if len(rows) != d:
            raise ValueError('basis is not linearly independent')
        self.rows = rows
        self.inv = _inverse(A)  # A c = z_R  =>  c = inv z_R
        self.M = M

    def coords(self, elem):
        """Return (coeffs, residual) where residual is {word: coeff} not matched.

        The residual is empty iff elem lies in the span of the basis.
        """
        z = [elem.get((None, w), Fraction(0)) for w in self.words]
        zR = [z[r] for r in self.rows]
        d = len(self.basis)
        c = [sum(self.inv[i][j] * zR[j] for j in range(d)) for i in range(d)]
        residual = {}
        for r, w in enumerate(self.words):
            val = sum(self.M[r][i] * c[i] for i in range(d)) - z[r]
            if val != 0:
                residual[w] = val
        return c, residual


def _rank(rows):
    A = [list(r) for r in rows]
    rank = 0
    ncols = len(A[0]) if A else 0
    for col in range(ncols):
        piv = next((r for r in range(rank, len(A)) if A[r][col] != 0), None)
        if piv is None:
            continue
        A[rank], A[piv] = A[piv], A[rank]
        for r in range(len(A)):
            if r != rank and A[r][col] != 0:
                f = A[r][col] / A[rank][col]
                A[r] = [x - f * y for x, y in zip(A[r], A[rank])]
        rank += 1
    return rank


def _inverse(A):
    d = len(A)
    aug = [list(map(Fraction, A[i])) + [Fraction(int(i == j)) for j in range(d)]
           for i in range(d)]
    for col in range(d):
        piv = next(r for r in range(col, d) if aug[r][col] != 0)
        aug[col], aug[piv] = aug[piv], aug[col]
        pv = aug[col][col]
        aug[col] = [x / pv for x in aug[col]]
        for r in range(d):
            if r != col and aug[r][col] != 0:
                f = aug[r][col]
                aug[r] = [x - f * y for x, y in zip(aug[r], aug[col])]
    return [row[d:] for row in aug]


def structure_constants(n):
    """Undeformed brackets of the basis. Returns (basis, table, residuals).

    table[(i, j)] = {k: coeff} for i <= j (κ-free part of [E_i, E_j]).
    residuals[(i, j)] = {word: coeff} for any part outside the basis span.
    """
    basis = build_basis(n)
    dec = Decomposer(basis)
    table, residuals = {}, {}
    for i, X in enumerate(basis):
        for j in range(i, len(basis)):
            Y = basis[j]
            br = kappa_free(bracket(X['elem'], Y['elem'],
                                    X['parity'], Y['parity']))
            c, res = dec.coords(br)
            table[(i, j)] = {k: c[k] for k in range(len(c)) if c[k] != 0}
            if res:
                residuals[(i, j)] = res
    return basis, table, residuals
