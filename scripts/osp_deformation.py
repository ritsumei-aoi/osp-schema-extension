"""
Exact (rational arithmetic) model of the inhomogeneous deformation of
C(n+1) = osp(2|2n) realised inside the universal enveloping algebra of the
extended oscillator superalgebra  A = V (+) C K (+) C kappa.

Conventions (see docs/math/*.md):

  * V is spanned by the odd pair a^+, a^- (CAR, {a^-, a^+} = 1) and the even
    oscillators b_j^+, b_j^- (CCR, [b_k^-, b_l^+] = delta_kl), j = 1..n.
  * K is even central and is set to 1 (we work in U(A)/(K-1)).
  * kappa is odd and central; hence kappa^2 = (1/2)[kappa,kappa] = 0.
  * The deformation is  [b_j^s, a^sigma] = - gb_{sigma,j,s} * kappa .
    The gb's are treated as (commuting) scalar indeterminates; every
    computation is linear in gb because each gb comes with one kappa and
    kappa^2 = 0.

The generators of the Lie superalgebra g = C(n+1) are the quadratic elements
listed in docs/math/Cn1_definition.md.  Every bracket [Z_i, Z_j] computed in
U(A_gb) decomposes uniquely as

    [Z_i, Z_j] = sum_k c_ij^k Z_k + c_ij^0 * 1 + kappa * ( sum_k gamma_ij^k Z_k + gamma_ij^0 * 1 ).

c_ij^k are the undeformed structure constants, gamma_ij^k is the g-valued part
of the deformation cocycle and gamma_ij^0 is its scalar part (invisible in the
adjoint representation).
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Dict, Tuple, List, Optional

# ---------------------------------------------------------------------------
# Polynomials in the gb indeterminates with rational coefficients
# ---------------------------------------------------------------------------

Mono = Tuple[int, ...]  # sorted tuple of gb indices (monomial)


class Poly:
    """Sparse polynomial in the gb variables, Fraction coefficients."""

    __slots__ = ("t",)

    def __init__(self, t: Optional[Dict[Mono, Fraction]] = None):
        self.t = {} if t is None else {k: v for k, v in t.items() if v != 0}

    # constructors -------------------------------------------------------
    @staticmethod
    def const(c) -> "Poly":
        c = Fraction(c)
        return Poly({(): c}) if c != 0 else Poly()

    @staticmethod
    def var(i: int) -> "Poly":
        return Poly({(i,): Fraction(1)})

    # arithmetic ---------------------------------------------------------
    def __add__(self, o: "Poly") -> "Poly":
        t = dict(self.t)
        for k, v in o.t.items():
            t[k] = t.get(k, Fraction(0)) + v
        return Poly(t)

    def __neg__(self) -> "Poly":
        return Poly({k: -v for k, v in self.t.items()})

    def __sub__(self, o: "Poly") -> "Poly":
        return self + (-o)

    def __mul__(self, o) -> "Poly":
        if not isinstance(o, Poly):
            c = Fraction(o)
            return Poly({k: v * c for k, v in self.t.items()})
        t: Dict[Mono, Fraction] = {}
        for k1, v1 in self.t.items():
            for k2, v2 in o.t.items():
                k = tuple(sorted(k1 + k2))
                t[k] = t.get(k, Fraction(0)) + v1 * v2
        return Poly(t)

    __rmul__ = __mul__

    # queries ------------------------------------------------------------
    def is_zero(self) -> bool:
        return not self.t

    def degree(self) -> int:
        return max((len(k) for k in self.t), default=-1)

    def const_part(self) -> Fraction:
        return self.t.get((), Fraction(0))

    def coeff(self, i: int) -> Fraction:
        """Coefficient of the linear monomial gb_i."""
        return self.t.get((i,), Fraction(0))

    def __eq__(self, o) -> bool:
        return isinstance(o, Poly) and self.t == o.t

    def __hash__(self):
        return hash(frozenset(self.t.items()))

    def __repr__(self) -> str:
        if not self.t:
            return "0"
        parts = []
        for k, v in sorted(self.t.items()):
            mono = "*".join(f"gb[{i}]" for i in k) if k else ""
            parts.append(f"({v})" + ("*" + mono if mono else ""))
        return " + ".join(parts)

    def to_json(self):
        return {"*".join(str(i) for i in k) if k else "1": str(v) for k, v in self.t.items()}


ZERO = Poly()
ONE = Poly.const(1)

# ---------------------------------------------------------------------------
# The oscillator superalgebra U(A_gb)
# ---------------------------------------------------------------------------

Word = Tuple[int, ...]
Elem = Dict[Word, Poly]


class OscillatorAlgebra:
    """
    Generators, in normal-ordering position:
        0            : kappa      (odd, central, kappa^2 = 0)
        1            : a^+        (odd)
        2            : a^-        (odd)
        3 + 2(j-1)   : b_j^+      (even)
        4 + 2(j-1)   : b_j^-      (even)
    Deformation parameters gb_{sigma,j,s} are indexed by  gb_index(sigma, j, s).
    """

    def __init__(self, n: int, deformed: bool = True):
        self.n = n
        self.deformed = deformed
        self.ngen = 3 + 2 * n
        self.parity = [1, 1, 1] + [0] * (2 * n)
        self.names = ["kappa", "a+", "a-"] + [f"b{j}{s}" for j in range(1, n + 1) for s in "+-"]
        self._memo: Dict[Word, Elem] = {}
        # gb index map
        self.gb_index: Dict[Tuple[str, int, str], int] = {}
        self.gb_label: List[Tuple[str, int, str]] = []
        for sigma in "+-":
            for j in range(1, n + 1):
                for s in "+-":
                    self.gb_index[(sigma, j, s)] = len(self.gb_label)
                    self.gb_label.append((sigma, j, s))
        self.ngb = len(self.gb_label)

    # generator bookkeeping ---------------------------------------------
    def b(self, j: int, s: str) -> int:
        return 3 + 2 * (j - 1) + (0 if s == "+" else 1)

    def a(self, sigma: str) -> int:
        return 1 if sigma == "+" else 2

    def gen_info(self, x: int):
        """Return ('kappa',), ('a', sigma) or ('b', j, s)."""
        if x == 0:
            return ("kappa",)
        if x in (1, 2):
            return ("a", "+" if x == 1 else "-")
        j = (x - 3) // 2 + 1
        s = "+" if (x - 3) % 2 == 0 else "-"
        return ("b", j, s)

    # elementary brackets ------------------------------------------------
    def gen_bracket(self, x: int, y: int) -> Elem:
        """Super-commutator [x, y] of two generators, as an element of U(A)."""
        ix, iy = self.gen_info(x), self.gen_info(y)
        if ix[0] == "kappa" or iy[0] == "kappa":
            return {}
        if ix[0] == "a" and iy[0] == "a":
            # {a^+, a^-} = 1, {a^+, a^+} = {a^-, a^-} = 0
            return {(): ONE} if ix[1] != iy[1] else {}
        if ix[0] == "b" and iy[0] == "b":
            _, j, s = ix
            _, k, t = iy
            if j != k or s == t:
                return {}
            # [b_j^-, b_j^+] = 1,  [b_j^+, b_j^-] = -1
            return {(): ONE} if s == "-" else {(): Poly.const(-1)}
        # mixed: [b_j^s, a^sigma] = - gb_{sigma,j,s} kappa ;  [a^sigma, b_j^s] = + gb kappa
        if not self.deformed:
            return {}
        if ix[0] == "b":
            _, j, s = ix
            sigma = iy[1]
            return {(0,): -Poly.var(self.gb_index[(sigma, j, s)])}
        else:
            sigma = ix[1]
            _, j, s = iy
            return {(0,): Poly.var(self.gb_index[(sigma, j, s)])}

    # normal ordering ----------------------------------------------------
    def nf(self, word: Word) -> Elem:
        """Normal-ordered form of a word (product of generators)."""
        if word in self._memo:
            return self._memo[word]
        res: Elem = {}
        for i in range(len(word) - 1):
            x, y = word[i], word[i + 1]
            if x == y and self.parity[x] == 1:
                res = {}  # x^2 = (1/2)[x,x] = 0 for odd generators
                break
            if x > y:
                sign = -1 if (self.parity[x] and self.parity[y]) else 1
                w1 = word[:i] + (y, x) + word[i + 2:]
                for w, c in self.nf(w1).items():
                    _acc(res, w, c * sign)
                for bw, bc in self.gen_bracket(x, y).items():
                    w2 = word[:i] + bw + word[i + 2:]
                    for w, c in self.nf(w2).items():
                        _acc(res, w, c * bc)
                break
        else:
            res = {word: ONE}
        self._memo[word] = res
        return res

    # element arithmetic -------------------------------------------------
    def mul(self, u: Elem, v: Elem) -> Elem:
        res: Elem = {}
        for w1, c1 in u.items():
            for w2, c2 in v.items():
                for w, c in self.nf(w1 + w2).items():
                    _acc(res, w, c * c1 * c2)
        return res

    @staticmethod
    def add(u: Elem, v: Elem, cv=1) -> Elem:
        res = dict(u)
        for w, c in v.items():
            _acc(res, w, c * cv)
        return res

    @staticmethod
    def scale(u: Elem, c) -> Elem:
        return {w: v * c for w, v in u.items() if not (v * c).is_zero()}

    def word_parity(self, w: Word) -> int:
        return sum(self.parity[x] for x in w) % 2

    def elem_parity(self, u: Elem) -> int:
        ps = {self.word_parity(w) for w in u}
        assert len(ps) <= 1, "inhomogeneous element"
        return ps.pop() if ps else 0

    def bracket(self, u: Elem, v: Elem) -> Elem:
        """Super-commutator of homogeneous elements."""
        pu, pv = self.elem_parity(u), self.elem_parity(v)
        sign = -1 if (pu and pv) else 1
        return self.add(self.mul(u, v), self.mul(v, u), -sign)

    def gen(self, x: int) -> Elem:
        return {(x,): ONE}

    def const(self, c) -> Elem:
        c = Poly.const(c)
        return {(): c} if not c.is_zero() else {}


def _acc(res: Elem, w: Word, c: Poly):
    if c.is_zero():
        return
    cur = res.get(w)
    new = c if cur is None else cur + c
    if new.is_zero():
        res.pop(w, None)
    else:
        res[w] = new


# ---------------------------------------------------------------------------
# The Lie superalgebra g = C(n+1) inside U(A)
# ---------------------------------------------------------------------------


class Cn1:
    """
    Basis of g = osp(2|2n) (dimension 2n^2+5n+1) with explicit oscillator
    expressions.  `ordering` selects how the odd generators are written in the
    *deformed* algebra:
        'doc'  : E_{+-eps +- delta_l} = a^sigma b_l^s   (fermion first, as in the docs)
        'sym'  : E = (1/2)(a^sigma b_l^s + b_l^s a^sigma)   (super-symmetrised)
    The two choices differ by kappa*scalar terms only.
    """

    def __init__(self, n: int, deformed: bool = True, ordering: str = "doc"):
        self.n = n
        self.A = OscillatorAlgebra(n, deformed=deformed)
        self.ordering = ordering
        self.labels: List[str] = []
        self.elems: List[Elem] = []
        self.parity: List[int] = []
        self.weight: List[Tuple[int, ...]] = []  # (eps, delta_1, ..., delta_n)
        self.lead: List[Word] = []  # leading quadratic word
        self.desc: List[str] = []
        self._build(self.A.gen(1), self.A.gen(2), lambda j, s: self.A.gen(self.A.b(j, s)), self)
        self.dim = len(self.elems)
        self.index = {lab: i for i, lab in enumerate(self.labels)}

    def substituted_elems(self, ap: Elem, am: Elem) -> List[Elem]:
        """The same oscillator expressions with a^+, a^- replaced by ap, am."""

        class _Sink:
            labels, elems, parity, weight, desc = [], [], [], [], []

        sink = _Sink()
        self._build(ap, am, lambda j, s: self.A.gen(self.A.b(j, s)), sink)
        assert sink.labels == self.labels
        return sink.elems

    def _build(self, ap: Elem, am: Elem, b, sink):
        A, n = self.A, self.n

        def add(label, elem, par, wt, desc):
            sink.labels.append(label)
            sink.elems.append(elem)
            sink.parity.append(par)
            sink.weight.append(tuple(wt))
            sink.desc.append(desc)

        half = Fraction(1, 2)
        # --- even part: sp(2n) -------------------------------------------------
        for k in range(1, n + 1):
            for l in range(k, n + 1):
                wt = [0] * (n + 1)
                wt[k] += 1
                wt[l] += 1
                lab = f"E_{{2d{k}}}" if k == l else f"E_{{d{k}+d{l}}}"
                add(lab, A.mul(b(k, "+"), b(l, "+")), 0, wt, f"b{k}+ b{l}+")
        for k in range(1, n + 1):
            for l in range(k, n + 1):
                wt = [0] * (n + 1)
                wt[k] -= 1
                wt[l] -= 1
                lab = f"E_{{-2d{k}}}" if k == l else f"E_{{-d{k}-d{l}}}"
                add(lab, A.mul(b(k, "-"), b(l, "-")), 0, wt, f"b{k}- b{l}-")
        for k in range(1, n + 1):
            for l in range(1, n + 1):
                wt = [0] * (n + 1)
                wt[k] += 1
                wt[l] -= 1
                if k == l:
                    e = A.add(A.mul(b(k, "+"), b(k, "-")), A.const(half))
                    add(f"h{k}", e, 0, wt, f"b{k}+ b{k}- + 1/2  = (1/2){{b{k}+, b{k}-}}")
                else:
                    add(f"E_{{d{k}-d{l}}}", A.mul(b(k, "+"), b(l, "-")), 0, wt, f"b{k}+ b{l}-")
        # --- even part: so(2) -------------------------------------------------
        e = A.add(A.mul(ap, am), A.const(-half))
        add("N", e, 0, [0] * (n + 1), "a+ a- - 1/2 = (1/2)(a+ a- - a- a+)")
        # --- odd part ----------------------------------------------------------
        for sigma, sg in (("+", 1), ("-", -1)):
            for l in range(1, n + 1):
                for s, ss in (("+", 1), ("-", -1)):
                    wt = [0] * (n + 1)
                    wt[0] = sg
                    wt[l] = ss
                    asig = ap if sigma == "+" else am
                    if self.ordering == "doc":
                        e = A.mul(asig, b(l, s))
                        d = f"a{sigma} b{l}{s}"
                    else:
                        e = A.scale(A.add(A.mul(asig, b(l, s)), A.mul(b(l, s), asig)), half)
                        d = f"(1/2)(a{sigma} b{l}{s} + b{l}{s} a{sigma})"
                    lab = f"E_{{{'' if sg > 0 else '-'}e{'+' if ss > 0 else '-'}d{l}}}"
                    add(lab, e, 1, wt, d)
        # leading words (the unique kappa-free quadratic word of each element)
        if sink is self:
            for e in self.elems:
                quads = [w for w in e if len(w) == 2 and 0 not in w]
                assert len(quads) == 1, (quads, e)
                self.lead.append(quads[0])

    # ------------------------------------------------------------------
    def decompose(self, e: Elem):
        """
        e = sum_k c^k Z_k + c0 + kappa (sum_k g^k Z_k + g0).
        Returns (c: dict, c0: Poly, g: dict, g0: Poly).  Raises if e is not of
        this form.
        """
        part0: Elem = {w: c for w, c in e.items() if not (w and w[0] == 0)}
        part1: Elem = {w[1:]: c for w, c in e.items() if (w and w[0] == 0)}
        # basis elements may themselves contain kappa*scalar terms (symmetrised
        # ordering): Z_k = Z_k^(0) + kappa z_k.  Then
        #   e_0 = sum c^k Z_k^(0) + c0,   e_1 = sum c^k z_k + sum g^k Z_k^(0) + g0.
        ck, c0 = self._decomp_quadratic(part0)
        for k, v in ck.items():
            for w, z in self.elems[k].items():
                if w and w[0] == 0:
                    _acc(part1, w[1:], -(v * z))
        gk, g0 = self._decomp_quadratic(part1)
        return ck, c0, gk, g0

    def _decomp_quadratic(self, p: Elem):
        p = dict(p)
        coeffs: Dict[int, Poly] = {}
        for k, w in enumerate(self.lead):
            c = p.get(w)
            if c is None:
                continue
            coeffs[k] = c
            for w2, c2 in self.elems[k].items():
                if w2 and w2[0] == 0:
                    continue  # kappa part of Z_k handled by the caller
                _acc(p, w2, -(c * c2))
        c0 = p.pop((), ZERO)
        assert not p, f"non-decomposable remainder: {p}"
        return coeffs, c0

    def structure(self):
        """
        Compute all brackets.  Returns
          c[(i,j)]  : dict k -> Fraction      (undeformed structure constants)
          gamma[(i,j)] : dict k -> Poly       (g-valued, linear in gb)
          gamma0[(i,j)] : Poly                (scalar part, linear in gb)
        """
        c, gamma, gamma0 = {}, {}, {}
        for i in range(self.dim):
            for j in range(self.dim):
                ck, c0, gk, g0 = self.decompose(self.A.bracket(self.elems[i], self.elems[j]))
                assert c0.is_zero(), f"scalar term in undeformed bracket {i},{j}: {c0}"
                for k, v in ck.items():
                    assert v.degree() == 0, f"gb-dependence in undeformed part {i},{j}"
                for k, v in gk.items():
                    assert v.degree() == 1 and v.const_part() == 0, (i, j, k, v)
                assert g0.is_zero() or (g0.degree() == 1 and g0.const_part() == 0)
                c[(i, j)] = {k: v.const_part() for k, v in ck.items()}
                gamma[(i, j)] = gk
                gamma0[(i, j)] = g0
        return c, gamma, gamma0


# ---------------------------------------------------------------------------
# Cochain operators (conventions of docs/math/C_coboundary_definition.md)
# ---------------------------------------------------------------------------


def delta_f(cn: Cn1, c, phi: Dict[Tuple[int, int], Fraction]):
    """
    (delta f)(Z_i, Z_j) = (-1)^{p_i} [Z_i, f(Z_j)] - (-1)^{(p_i+1) p_j} [Z_j, f(Z_i)] - f([Z_i, Z_j])
    with f(Z_j) = sum_m phi[(m, j)] Z_m.  Returns dict (i,j) -> dict m -> Fraction.
    """
    dim, p = cn.dim, cn.parity
    # f as column lists
    fcol: Dict[int, Dict[int, Fraction]] = {}
    for (m, j), v in phi.items():
        if v != 0:
            fcol.setdefault(j, {})[m] = v
    out = {}
    for i in range(dim):
        for j in range(dim):
            acc: Dict[int, Fraction] = {}
            s1 = -1 if p[i] else 1
            for k, v in fcol.get(j, {}).items():
                for m, cc in c[(i, k)].items():
                    acc[m] = acc.get(m, Fraction(0)) + s1 * v * cc
            s2 = -1 if ((p[i] + 1) * p[j]) % 2 else 1
            for k, v in fcol.get(i, {}).items():
                for m, cc in c[(j, k)].items():
                    acc[m] = acc.get(m, Fraction(0)) - s2 * v * cc
            for k, cc in c[(i, j)].items():
                for m, v in fcol.get(k, {}).items():
                    acc[m] = acc.get(m, Fraction(0)) - cc * v
            out[(i, j)] = {m: v for m, v in acc.items() if v != 0}
    return out


def d2(cn: Cn1, c, g: Dict[Tuple[int, int], Dict[int, Fraction]]):
    """
    Cocycle operator on odd 2-cochains gamma (dict (i,j) -> dict m -> coeff),
    obtained as the kappa-coefficient of the super-Jacobi identity of
    [X,Y]_gamma = [X,Y] + kappa gamma(X,Y):

      (d gamma)(X,Y,Z) = gamma(X,[Y,Z]) + (-1)^{p_X}[X,gamma(Y,Z)]
                         - gamma([X,Y],Z) - [gamma(X,Y),Z]
                         - (-1)^{p_X p_Y} gamma(Y,[X,Z]) - (-1)^{p_X p_Y + p_Y}[Y,gamma(X,Z)]
    Returns dict (i,j,k) -> dict m -> coeff (only nonzero entries).
    """
    dim, p = cn.dim, cn.parity

    def G(a, b):
        return g.get((a, b), {})

    out = {}
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                acc: Dict[int, Fraction] = {}
                si = -1 if p[i] else 1
                sij = -1 if (p[i] * p[j]) % 2 else 1
                sijj = -1 if (p[i] * p[j] + p[j]) % 2 else 1
                for l, cc in c[(j, k)].items():          # gamma(X,[Y,Z])
                    for m, v in G(i, l).items():
                        acc[m] = acc.get(m, Fraction(0)) + cc * v
                for m, v in G(j, k).items():             # (-1)^{p_X}[X,gamma(Y,Z)]
                    for mm, cc in c[(i, m)].items():
                        acc[mm] = acc.get(mm, Fraction(0)) + si * v * cc
                for l, cc in c[(i, j)].items():          # - gamma([X,Y],Z)
                    for m, v in G(l, k).items():
                        acc[m] = acc.get(m, Fraction(0)) - cc * v
                for m, v in G(i, j).items():             # - [gamma(X,Y),Z]
                    for mm, cc in c[(m, k)].items():
                        acc[mm] = acc.get(mm, Fraction(0)) - v * cc
                for l, cc in c[(i, k)].items():          # - (-1)^{p_X p_Y} gamma(Y,[X,Z])
                    for m, v in G(j, l).items():
                        acc[m] = acc.get(m, Fraction(0)) - sij * cc * v
                for m, v in G(i, k).items():             # - (-1)^{p_X p_Y + p_Y}[Y,gamma(X,Z)]
                    for mm, cc in c[(j, m)].items():
                        acc[mm] = acc.get(mm, Fraction(0)) - sijj * v * cc
                acc = {m: v for m, v in acc.items() if v != 0}
                if acc:
                    out[(i, j, k)] = acc
    return out


# ---------------------------------------------------------------------------
# Sparse exact linear algebra over Q
# ---------------------------------------------------------------------------


class Echelon:
    """Incremental reduced row echelon form with Fraction entries.

    Rows are dicts col -> Fraction, optionally carrying a list of right-hand
    sides (one per system).  Supports rank and solving A x = b.
    """

    def __init__(self, nrhs: int = 0):
        self.pivots: Dict[int, Tuple[Dict[int, Fraction], List[Fraction]]] = {}
        self.nrhs = nrhs
        self.inconsistent = [False] * nrhs

    def reduce(self, row: Dict[int, Fraction], rhs: List[Fraction]):
        row = dict(row)
        rhs = list(rhs)
        changed = True
        while True:
            cols = [c for c in row if c in self.pivots]
            if not cols:
                break
            col = min(cols)
            prow, prhs = self.pivots[col]
            f = row[col]
            for cc, v in prow.items():
                nv = row.get(cc, Fraction(0)) - f * v
                if nv == 0:
                    row.pop(cc, None)
                else:
                    row[cc] = nv
            for t in range(self.nrhs):
                rhs[t] -= f * prhs[t]
        return row, rhs

    def add(self, row: Dict[int, Fraction], rhs: Optional[List[Fraction]] = None) -> bool:
        """Insert a row; returns True if it increased the rank."""
        if rhs is None:
            rhs = [Fraction(0)] * self.nrhs
        row, rhs = self.reduce(row, rhs)
        if not row:
            for t in range(self.nrhs):
                if rhs[t] != 0:
                    self.inconsistent[t] = True
            return False
        col = min(row)
        f = row[col]
        row = {cc: v / f for cc, v in row.items()}
        rhs = [v / f for v in rhs]
        # back-substitute into existing pivots to keep RREF
        for pc, (prow, prhs) in self.pivots.items():
            if col in prow:
                g = prow[col]
                for cc, v in row.items():
                    nv = prow.get(cc, Fraction(0)) - g * v
                    if nv == 0:
                        prow.pop(cc, None)
                    else:
                        prow[cc] = nv
                for t in range(self.nrhs):
                    prhs[t] -= g * rhs[t]
        self.pivots[col] = (row, rhs)
        return True

    @property
    def rank(self) -> int:
        return len(self.pivots)

    def particular_solution(self, t: int) -> Optional[Dict[int, Fraction]]:
        """Solution with all free variables set to 0 for system t."""
        if self.inconsistent[t]:
            return None
        return {col: prhs[t] for col, (prow, prhs) in self.pivots.items() if prhs[t] != 0}


def product_is_zero(rows_d, delta_cols):
    """Check that for every column vector v of delta, every row of d satisfies row . v == 0."""
    for row in rows_d:
        for v in delta_cols:
            s = sum((row[c] * v[c] for c in row if c in v), Fraction(0))
            if s != 0:
                return False
    return True
