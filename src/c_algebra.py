"""Oscillator realization of C(n+1) = osp(2|2n) and its inhomogeneous deformation.

Associative algebra used for all computations (exact, rational arithmetic):

* standard fermion pair a^+, a^-  with  {a^-, a^+} = 1  and  (a^+)^2 = (a^-)^2 = 0
* bosons b_k^+, b_k^-  (k = 1..n)  with  [b_k^-, b_l^+] = delta_kl, all other bosonic
  commutators zero
* fermions and bosons commute (b is even)
* deformation (C_inhomogeneous_definition.md):  [b_k^s, a^sigma] = -gb[sigma,k,s] * kappa,
  kappa central, kappa^2 = 0.  Hence  b a = a b - gb*kappa.

An element is a dict  {(fermion_word, boson_word, tag): Fraction}.
  * fermion_word : normal-ordered tuple of ('F', '+'/'-'), at most a^+ a^-
  * boson_word   : normal-ordered tuple of ('B', '+'/'-', k), '+' letters first, sorted by k
  * tag          : None for the kappa-free part, or the gb label (sigma, k, s) meaning the
                   term carries kappa * gb[sigma,k,s]  (kappa^2 = 0 means one tag at most)

Normal ordering convention (also the PBW convention of the oscillator words):
fermions to the left of bosons, a^+ before a^-, b^+ before b^-, bosons sorted by index.
"""

from fractions import Fraction
from functools import lru_cache

IDENTITY_KEY = ((), (), None)


def F(sign):
    """Fermionic letter a^sign."""
    return ('F', sign)


def B(sign, k):
    """Bosonic letter b_k^sign."""
    return ('B', sign, k)


def _clean(terms):
    return {key: val for key, val in terms.items() if val != 0}


def _accumulate(out, terms, coeff):
    for key, val in terms.items():
        out[key] = out.get(key, 0) + coeff * val
    return out


@lru_cache(maxsize=None)
def _normal(word, tag):
    """Normal-order a word of letters.  Returns {(fer, bos, tag): Fraction}."""
    for i in range(len(word) - 1):
        x, y = word[i], word[i + 1]
        swapped = word[:i] + (y, x) + word[i + 2:]
        rest = word[:i] + word[i + 2:]
        if x[0] == 'B' and y[0] == 'F':
            # b a = a b + [b, a] = a b - gb * kappa   (kappa only once, so tag must be None)
            out = _accumulate({}, _normal(swapped, tag), 1)
            if tag is None:
                _accumulate(out, _normal(rest, (y[1], x[2], x[1])), -1)
            return _clean(out)
        if x[0] == 'F' and y[0] == 'F':
            if x[1] == y[1]:
                return {}
            if x[1] == '-':
                # a^- a^+ = -a^+ a^- + 1
                out = _accumulate({}, _normal(swapped, tag), -1)
                return _clean(_accumulate(out, _normal(rest, tag), 1))
        if x[0] == 'B' and y[0] == 'B':
            if x[1] == '-' and y[1] == '+':
                # b^-_k b^+_l = b^+_l b^-_k + delta_kl
                out = _accumulate({}, _normal(swapped, tag), 1)
                if x[2] == y[2]:
                    _accumulate(out, _normal(rest, tag), 1)
                return _clean(out)
            if x[1] == y[1] and x[2] > y[2]:
                return _clean(_accumulate({}, _normal(swapped, tag), 1))
    fer = tuple(letter for letter in word if letter[0] == 'F')
    bos = tuple(letter for letter in word if letter[0] == 'B')
    return {(fer, bos, tag): Fraction(1)}


def mono(*letters):
    """Element given by the normal-ordered form of a product of letters (kappa-free)."""
    return dict(_normal(tuple(letters), None))


def lin(*terms):
    """Linear combination sum(c * X) of elements given as (c, X) pairs."""
    out = {}
    for coeff, elem in terms:
        _accumulate(out, elem, Fraction(coeff))
    return _clean(out)


def mul(X, Y):
    """Associative product in the deformed algebra (kappa^2 = 0)."""
    out = {}
    for (f1, b1, t1), c1 in X.items():
        for (f2, b2, t2), c2 in Y.items():
            if t1 is not None and t2 is not None:
                continue
            tag = t1 if t1 is not None else t2
            _accumulate(out, _normal(f1 + b1 + f2 + b2, tag), c1 * c2)
    return _clean(out)


def parity(X):
    """Parity of a homogeneous element: number of fermionic letters mod 2."""
    parities = {len(key[0]) % 2 for key in X}
    if len(parities) != 1:
        raise ValueError('element is not homogeneous')
    return parities.pop()


def bracket(X, Y):
    """Graded commutator [X, Y] = XY - (-1)^{p(X)p(Y)} YX."""
    sign = (-1) ** (parity(X) * parity(Y))
    out = _accumulate({}, mul(X, Y), 1)
    return _clean(_accumulate(out, mul(Y, X), -sign))


def letter_label(letter):
    """JSON label of an oscillator letter, e.g. ('F','+') -> a_1_p, ('B','-',2) -> b_2_m."""
    if letter[0] == 'F':
        return 'a_1_p' if letter[1] == '+' else 'a_1_m'
    return 'b_%d_%s' % (letter[2], 'p' if letter[1] == '+' else 'm')


def gb_label(sigma, k, s):
    """Label of the deformation parameter gb_{a_1^sigma, b_k^s}."""
    sym = {'+': 'p', '-': 'm'}
    return 'gb_a1%s_b%d%s' % (sym[sigma], k, sym[s])


def gb_tag_order(n):
    """All gb tags (sigma, k, s) for rank n, in a fixed order (2 x 2n = 4n parameters)."""
    return [(sigma, k, s) for sigma in '+-' for k in range(1, n + 1) for s in '+-']


def build_basis(n):
    """Basis of C(n+1) in PBW order  kappa < [odd] < [even]  (see notation.md).

    Returns a list of dicts {label, parity, element, words}.  'words' is the same
    element written as a list of (coefficient, [oscillator labels]) pairs.
    """
    if n < 1:
        raise ValueError('n must be >= 1')
    half = Fraction(1, 2)
    odd = []
    for k in range(1, n + 1):
        odd.append(('E_eps1_del%d_pp' % k, mono(F('+'), B('+', k))))
        odd.append(('E_eps1_del%d_pm' % k, mono(F('+'), B('-', k))))
        odd.append(('E_eps1_del%d_mp' % k, mono(F('-'), B('+', k))))
        odd.append(('E_eps1_del%d_mm' % k, mono(F('-'), B('-', k))))

    even = [('H_1', lin((1, mono(F('+'), F('-'))), (1, mono(B('+', 1), B('-', 1)))))]
    for k in range(2, n + 1):
        even.append(('H_%d' % k, lin((1, mono(B('+', k - 1), B('-', k - 1))),
                                       (-1, mono(B('+', k), B('-', k))))))
    even.append(('H_%d' % (n + 1), lin((-1, mono(B('+', n), B('-', n))),
                                         (-half, {IDENTITY_KEY: Fraction(1)}))))
    for k in range(1, n + 1):
        even.append(('E_2del%d_p' % k, lin((half, mono(B('+', k), B('+', k))))))
    pairs = [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    for i, j in pairs:
        even.append(('E_del%d_del%d_pp' % (i, j), mono(B('+', i), B('+', j))))
    for k in range(1, n + 1):
        even.append(('E_2del%d_m' % k, lin((half, mono(B('-', k), B('-', k))))))
    for i, j in pairs:
        even.append(('E_del%d_del%d_mm' % (i, j), mono(B('-', i), B('-', j))))
    for i, j in pairs:
        even.append(('E_del%d_del%d_pm' % (i, j), mono(B('+', i), B('-', j))))
    for i, j in pairs:
        even.append(('E_del%d_del%d_mp' % (i, j), mono(B('-', i), B('+', j))))

    basis = []
    for label, elem in odd:
        basis.append({'label': label, 'parity': 1, 'element': elem})
    for label, elem in even:
        basis.append({'label': label, 'parity': 0, 'element': elem})
    for entry in basis:
        entry['words'] = element_words(entry['element'])
        parities = {len(key[0]) % 2 for key in entry['element']}
        if parities != {entry['parity']}:
            raise ValueError('parity mismatch for %s' % entry['label'])
    return basis


def element_words(elem):
    """Oscillator-word form of a kappa-free element: [(Fraction, [labels]), ...]."""
    out = []
    for (fer, bos, tag), coeff in sorted(elem.items(), key=lambda kv: repr(kv[0])):
        if tag is not None:
            raise ValueError('element_words only accepts kappa-free elements')
        out.append((coeff, [letter_label(x) for x in fer + bos]))
    return out


class Span:
    """Exact linear span with coordinate extraction (Gaussian elimination over Q).

    Built from linearly independent vectors; express(v) returns the coefficients of v in
    that basis, or None if v is not in the span.
    """

    def __init__(self, vectors):
        self.rows = []
        for idx, vec in enumerate(vectors):
            rem, combo = self._reduce(dict(vec), {idx: Fraction(1)})
            if not rem:
                raise ValueError('vector %d is linearly dependent on earlier ones' % idx)
            pivot = next(iter(rem))
            factor = rem[pivot]
            self.rows.append((pivot,
                              {k: v / factor for k, v in rem.items()},
                              {k: v / factor for k, v in combo.items()}))

    def _reduce(self, vec, combo):
        for pivot, row_vec, row_combo in self.rows:
            f = vec.get(pivot)
            if f:
                _accumulate(vec, row_vec, -f)
                _accumulate(combo, row_combo, -f)
                vec = _clean(vec)
                combo = _clean(combo)
        return _clean(vec), _clean(combo)

    def express(self, vec):
        # _reduce returns combo = -(sum of f * row_combo); the coordinates of vec are its negative
        rem, combo = self._reduce(dict(vec), {})
        if rem:
            return None
        return {k: -v for k, v in combo.items()}

    def decompose(self, vec):
        """Write vec = (element of the span) + c * IDENTITY_KEY.

        Returns (coefficients, c), or None if vec has components outside span + C*K.
        The decomposition is unique because K is not in the span.
        """
        rem, combo = self._reduce(dict(vec), {})
        if any(key != IDENTITY_KEY for key in rem):
            return None
        return {k: -v for k, v in combo.items()}, rem.get(IDENTITY_KEY, 0)


def structure(n):
    """Compute all brackets of the basis.

    Returns (basis, sc, gamma, gamma_K) where
      sc[(a, b)]          = {c: Fraction}  with [X_a, X_b]_0 = sum_c sc c X_c
      gamma[(a, b)][tag]  = {c: Fraction}  g-valued kappa*gb_tag part of [X_a, X_b]:
                            [X_a, X_b]_gamma = [X_a, X_b]_0 + kappa * sum_tag gb_tag * gamma(X_a, X_b)
      gamma_K[(a, b)][tag] = Fraction      coefficient of kappa*gb_tag*K (K = identity, central)
    The K-components are split off because the framework of C_inhomogeneous_definition.md
    takes gamma with values in g; K is identified with the scalar 1 and excluded from the basis.
    Raises ValueError if a g-valued component leaves the span of the basis (closure failure),
    or if the kappa-free bracket has a K-component.
    """
    basis = build_basis(n)
    span = Span([entry['element'] for entry in basis])
    sc = {}
    gamma = {}
    gamma_K = {}
    for a, A in enumerate(basis):
        for b, Bb in enumerate(basis):
            br = bracket(A['element'], Bb['element'])
            free = {key: val for key, val in br.items() if key[2] is None}
            res = span.decompose(free)
            if res is None or res[1] != 0:
                raise ValueError('closure failure in kappa-free bracket %s %s' % (A['label'], Bb['label']))
            sc[(a, b)] = res[0]
            by_tag = {}
            for key, val in br.items():
                if key[2] is not None:
                    by_tag.setdefault(key[2], {})[(key[0], key[1], None)] = val
            gamma[(a, b)] = {}
            gamma_K[(a, b)] = {}
            for tag, vec in by_tag.items():
                res = span.decompose(vec)
                if res is None:
                    raise ValueError('closure failure in kappa part %s %s tag %s' % (A['label'], Bb['label'], tag))
                coeffs, k_part = res
                if coeffs:
                    gamma[(a, b)][tag] = coeffs
                if k_part != 0:
                    gamma_K[(a, b)][tag] = k_part
    return basis, sc, gamma, gamma_K
