"""Oscillator superalgebra engine for C(n+1) = osp(2|2n).

Works in U(A) where A = span{a_1^±, b_k^±} + C K + C kappa (K = 1, kappa odd central,
kappa^2 = 0).  Optional deformation: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa.

An element is a dict  (kappa_power, word) -> Lin  where `word` is a tuple of oscillator
indices in normal order and Lin is a linear form over parameters ('1' = constant).
Conventions: handover/notation.md.
"""
from fractions import Fraction
from functools import lru_cache

ONE = "1"


# ---------------------------------------------------------------- linear forms
def lin(c=1, key=ONE):
    c = Fraction(c)
    return {key: c} if c else {}


def lin_add(a, b, s=1):
    out = dict(a)
    for k, v in b.items():
        w = out.get(k, 0) + s * v
        if w:
            out[k] = w
        else:
            out.pop(k, None)
    return out


def lin_scale(a, c):
    c = Fraction(c)
    return {k: v * c for k, v in a.items()} if c else {}


def lin_is_const(a):
    return all(k == ONE for k in a)


def lin_mul(a, b):
    """Product of linear forms; at least one factor must be constant."""
    if lin_is_const(a):
        return lin_scale(b, a.get(ONE, 0))
    if lin_is_const(b):
        return lin_scale(a, b.get(ONE, 0))
    raise ValueError("product of two non-constant parameters (should be killed by kappa^2=0)")


def lin_str(a):
    return {k: str(v) for k, v in sorted(a.items())}


def lin_from_json(d):
    return {k: Fraction(v) for k, v in d.items() if Fraction(v)}


# ---------------------------------------------------------------- oscillators
class Oscillators:
    """Oscillator labels/indices for rank n.  Order: a_1_p, a_1_m, b_1_p, b_1_m, ..."""

    def __init__(self, n, deformed=False, gb_values=None):
        """gb_values: optional {gb name: number}; substitutes numeric gb directly in the relation."""
        self.n = n
        self.deformed = deformed or gb_values is not None
        self.gb_values = gb_values
        self.labels = ["a_1_p", "a_1_m"]
        for k in range(1, n + 1):
            self.labels += [f"b_{k}_p", f"b_{k}_m"]
        self.index = {l: i for i, l in enumerate(self.labels)}
        self._no = lru_cache(maxsize=None)(self._normal_order)

    def parity(self, i):
        return 1 if i < 2 else 0

    def word_parity(self, w):
        return sum(1 for i in w if i < 2) % 2

    @staticmethod
    def gb_name(sigma, j, s):
        return f"gb_a1{sigma}_b{j}{s}"

    def gb_names(self):
        return [self.gb_name(sg, j, s) for sg in "pm" for j in range(1, self.n + 1) for s in "pm"]

    def swap_scalar(self, x, y):
        """For x > y return (kappa_power, Lin) of [x, y} = x y - (-1)^{p p} y x."""
        if x == 1 and y == 0:  # {a-, a+} = 1
            return 0, lin(1)
        if x >= 2 and y < 2:  # [b_j^s, a^sigma] = -gb kappa
            if not self.deformed:
                return 0, {}
            j, s = (x - 2) // 2 + 1, "pm"[(x - 2) % 2]
            sigma = "pm"[y]
            if self.gb_values is not None:
                return 1, lin(-Fraction(self.gb_values.get(self.gb_name(sigma, j, s), 0)))
            return 1, lin(-1, self.gb_name(sigma, j, s))
        if x >= 2 and y >= 2 and x % 2 == 1 and y == x - 1:  # [b_j^-, b_j^+] = 1
            return 0, lin(1)
        return 0, {}

    def _normal_order(self, w):
        """Normal order the word w; returns dict (kappa, word) -> Lin."""
        for i in range(len(w) - 1):
            x, y = w[i], w[i + 1]
            if x == y and x < 2:
                return {}  # (a^±)^2 = 0
            if x > y:
                out = {}
                sign = -1 if (self.parity(x) and self.parity(y)) else 1
                for key, c in self._no(w[:i] + (y, x) + w[i + 2:]).items():
                    _acc(out, key, lin_scale(c, sign))
                kp, c0 = self.swap_scalar(x, y)
                if c0:
                    pre, post = w[:i], w[i + 2:]
                    s2 = -1 if (kp and self.word_parity(pre)) else 1
                    for (k2, w2), c2 in self._no(pre + post).items():
                        if kp + k2 > 1:
                            continue
                        _acc(out, (kp + k2, w2), lin_scale(lin_mul(c0, c2), s2))
                return out
        return {(0, w): lin(1)}

    def normal_order(self, w):
        return self._no(tuple(w))


def _acc(out, key, c):
    if not c:
        return
    v = lin_add(out.get(key, {}), c)
    if v:
        out[key] = v
    else:
        out.pop(key, None)


# ---------------------------------------------------------------- elements
def elem_add(a, b, s=1):
    out = dict(a)
    for k, c in b.items():
        _acc(out, k, lin_scale(c, s))
    return out


def elem_mul(osc, A, B):
    out = {}
    for (k1, w1), c1 in A.items():
        for (k2, w2), c2 in B.items():
            if k1 + k2 > 1:
                continue
            # kappa^{k1} w1 kappa^{k2} w2 = (-1)^{k2 p(w1)} kappa^{k1+k2} w1 w2
            s = -1 if (k2 and osc.word_parity(w1)) else 1
            c12 = lin_scale(lin_mul(c1, c2), s)
            for (k3, w3), c3 in osc.normal_order(w1 + w2).items():
                if k1 + k2 + k3 > 1:
                    continue
                _acc(out, (k1 + k2 + k3, w3), lin_mul(c12, c3))
    return out


def elem_parity(osc, A):
    ps = {(k + osc.word_parity(w)) % 2 for (k, w) in A}
    if len(ps) > 1:
        raise ValueError("inhomogeneous element")
    return ps.pop() if ps else 0


def bracket(osc, A, B, pA, pB):
    sign = -1 if (pA and pB) else 1
    return elem_add(elem_mul(osc, A, B), elem_mul(osc, B, A), -sign)


# ---------------------------------------------------------------- linear algebra (exact)
def solve_square(M, rhs_list):
    """Exact inverse application: M (list of rows of Fractions, square, invertible).
    rhs_list: list of RHS vectors whose entries are Lin. Returns list of solution vectors."""
    N = len(M)
    A = [list(row) + [Fraction(int(i == j)) for j in range(N)] for i, row in enumerate(M)]
    for col in range(N):
        piv = next(r for r in range(col, N) if A[r][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        p = A[col][col]
        A[col] = [v / p for v in A[col]]
        for r in range(N):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [a - f * b for a, b in zip(A[r], A[col])]
    inv = [row[N:] for row in A]
    sols = []
    for rhs in rhs_list:
        sol = []
        for i in range(N):
            acc = {}
            for j in range(N):
                if inv[i][j] and rhs[j]:
                    acc = lin_add(acc, lin_scale(rhs[j], inv[i][j]))
            sol.append(acc)
        sols.append(sol)
    return sols
