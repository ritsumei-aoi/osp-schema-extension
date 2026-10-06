"""Exact normal-ordering engine for the (deformed) oscillator superalgebra of C(n+1).

Generators of the pre-oscillator algebra A = V + C K + C kappa:
    a_1_p, a_1_m        (odd)   {a_1_m, a_1_p} = K = 1, (a_1_p)^2 = (a_1_m)^2 = 0
    b_k_p, b_k_m        (even)  [b_k_m, b_l_p] = delta_kl
    kappa               (odd)   central, kappa^2 = 0
Deformation (Issue I05): [b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa.

Elements of U(A) are dicts {word (tuple of labels): Fraction}, words normal-ordered w.r.t.
    kappa < a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m
(see handover/notation.md).
"""
from fractions import Fraction

KAPPA = "kappa"


def gb_label(sigma, j, s):
    """Label of gb_{a_1^sigma, b_j^s}; sigma, s in {'p', 'm'}."""
    return f"gb_{sigma}_{j}_{s}"


def gb_labels(n):
    """All 4n gb labels, ordered row-major in the 2 x 2n gb matrix."""
    return [gb_label(sig, j, s) for sig in ("p", "m") for j in range(1, n + 1) for s in ("p", "m")]


class OscillatorAlgebra:
    def __init__(self, n, gb=None):
        """gb: optional dict {gb_label: number}; missing labels are 0 (undeformed)."""
        self.n = n
        self.order = ["a_1_p", "a_1_m"] + [f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")]
        self.rank = {KAPPA: -1}
        self.rank.update({x: i for i, x in enumerate(self.order)})
        self.gb = {k: Fraction(v) for k, v in (gb or {}).items() if v != 0}

    # -- basic data -------------------------------------------------------
    @staticmethod
    def sym_parity(x):
        return 1 if (x == KAPPA or x.startswith("a_")) else 0

    def word_parity(self, w):
        return sum(self.sym_parity(x) for x in w) % 2

    def _central_bracket(self, x, y):
        """Supercommutator [x, y] of two generators of A, returned as an element."""
        if x == KAPPA or y == KAPPA:
            return {}
        if x.startswith("b_") and y.startswith("b_"):
            _, kx, sx = x.split("_")
            _, ky, sy = y.split("_")
            if kx != ky or sx == sy:
                return {}
            return {(): Fraction(1 if sx == "m" else -1)}
        if x.startswith("a_") and y.startswith("a_"):
            return {(): Fraction(1)} if x != y else {}
        # mixed boson / fermion
        if x.startswith("b_"):
            _, j, s = x.split("_")
            sig = y.split("_")[2]
            c = -self.gb.get(gb_label(sig, j, s), 0)
        else:
            _, j, s = y.split("_")
            sig = x.split("_")[2]
            c = self.gb.get(gb_label(sig, j, s), 0)
        return {(KAPPA,): Fraction(c)} if c else {}

    # -- normal ordering --------------------------------------------------
    def normalize(self, elem):
        out = {}
        stack = [(tuple(w), Fraction(c)) for w, c in elem.items() if c != 0]
        while stack:
            w, c = stack.pop()
            for i in range(len(w) - 1):
                x, y = w[i], w[i + 1]
                if x == y and self.sym_parity(x) == 1:
                    break  # square of an odd generator vanishes
                if self.rank[x] > self.rank[y]:
                    sign = -1 if self.sym_parity(x) and self.sym_parity(y) else 1
                    stack.append((w[:i] + (y, x) + w[i + 2:], c * sign))
                    for cw, cc in self._central_bracket(x, y).items():
                        stack.append((w[:i] + cw + w[i + 2:], c * cc))
                    break
            else:
                out[w] = out.get(w, 0) + c
                if out[w] == 0:
                    del out[w]
        return out

    # -- algebra operations -----------------------------------------------
    @staticmethod
    def add(*elems, coeffs=None):
        out = {}
        coeffs = coeffs or [1] * len(elems)
        for e, k in zip(elems, coeffs):
            for w, c in e.items():
                out[w] = out.get(w, 0) + k * c
        return {w: c for w, c in out.items() if c != 0}

    def mul(self, e1, e2):
        prod = {}
        for w1, c1 in e1.items():
            for w2, c2 in e2.items():
                w = w1 + w2
                prod[w] = prod.get(w, 0) + c1 * c2
        return self.normalize(prod)

    def parity(self, e):
        ps = {self.word_parity(w) for w in e}
        if len(ps) > 1:
            raise ValueError("inhomogeneous element")
        return ps.pop() if ps else 0

    def bracket(self, e1, e2):
        p1, p2 = self.parity(e1), self.parity(e2)
        sign = -1 if (p1 and p2) else 1
        return self.add(self.mul(e1, e2), self.mul(e2, e1), coeffs=[1, -sign])

    @staticmethod
    def split_kappa(e):
        """Split e = e0 + kappa * e1; returns (e0, e1)."""
        e0, e1 = {}, {}
        for w, c in e.items():
            if w and w[0] == KAPPA:
                e1[w[1:]] = c
            else:
                e0[w] = c
        return e0, e1
