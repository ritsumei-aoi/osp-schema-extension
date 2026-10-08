"""
Exact model of the deformed oscillator superalgebra  U(A_gb)  with  K = 1.

Generators (normal-order index : symbol : parity):
    0        : kappa  : odd   (central, kappa^2 = 0)
    1        : a+     : odd
    2        : a-     : odd
    3+2(j-1) : b_j^+  : even    (j = 1..n)
    4+2(j-1) : b_j^-  : even

Defining super-commutators ([x,y] = xy - (-1)^{p(x)p(y)} yx), everything
else (super)commutes:
    [a-, a+]       = 1                      (CAR, K = 1)
    [b_j^-, b_j^+] = 1                      (CCR, K = 1)
    [b_j^s, a^sig] = - gb_{sig,j,s} * kappa (inhomogeneous deformation)
    [kappa, x]     = 0  for every x         (kappa is central, hence kappa^2 = 0)

Elements of U(A_gb) are stored as dicts  {monomial: coefficient}, where a
monomial is a non-decreasing tuple of generator indices (odd generators
never repeated) and a coefficient is a *polynomial in the gb parameters
with rational coefficients*, stored as {gb_index_tuple: Fraction}.

The gb parameters are numbered  gb_index = (sig, j, s)  with sig, s in
{'+','-'}  and  j in 1..n ; the flat index used in the artifacts is
    gb_flat = 4*(j-1) + 2*[sig == '-'] + [s == '-'].
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import product

# ----------------------------------------------------------------------------
# coefficient ring:  Q[gb]   represented as {tuple(sorted gb_flat indices): Fraction}
# ----------------------------------------------------------------------------
ONE = ()  # the constant monomial in Q[gb]


def c_add(x: dict, y: dict) -> dict:
    out = dict(x)
    for k, v in y.items():
        nv = out.get(k, Fraction(0)) + v
        if nv == 0:
            out.pop(k, None)
        else:
            out[k] = nv
    return out


def c_scale(x: dict, s) -> dict:
    s = Fraction(s)
    if s == 0:
        return {}
    return {k: v * s for k, v in x.items()}


def c_mul(x: dict, y: dict) -> dict:
    out: dict = {}
    for k1, v1 in x.items():
        for k2, v2 in y.items():
            k = tuple(sorted(k1 + k2))
            nv = out.get(k, Fraction(0)) + v1 * v2
            if nv == 0:
                out.pop(k, None)
            else:
                out[k] = nv
    return out


def c_const(q) -> dict:
    q = Fraction(q)
    return {ONE: q} if q != 0 else {}


def c_gb(flat: int, q=1) -> dict:
    return {(flat,): Fraction(q)}


# ----------------------------------------------------------------------------
# the algebra
# ----------------------------------------------------------------------------
class OscillatorAlgebra:
    def __init__(self, n: int):
        self.n = n
        self.ngen = 3 + 2 * n
        self.parity = [1, 1, 1] + [0] * (2 * n)
        self.names = ["kappa", "a+", "a-"] + sum(
            ([f"b{j}+", f"b{j}-"] for j in range(1, n + 1)), []
        )
        self.gb_names = []
        for j in range(1, n + 1):
            for sig in "+-":
                for s in "+-":
                    self.gb_names.append(f"gb[a{sig},b{j}{s}]")
        self._no_cache: dict = {}

    # generator helpers ----------------------------------------------------
    def bp(self, j):  # b_j^+
        return 3 + 2 * (j - 1)

    def bm(self, j):  # b_j^-
        return 4 + 2 * (j - 1)

    @staticmethod
    def gb_flat(sig: str, j: int, s: str) -> int:
        return 4 * (j - 1) + 2 * (sig == "-") + (s == "-")

    def p(self, g: int) -> int:
        return self.parity[g]

    # elementary brackets  [x, y]  for generators (returned as an element) ---
    def gen_bracket(self, x: int, y: int) -> dict:
        """Super-commutator of two generators, as an element of U(A_gb)."""
        if x == 0 or y == 0:
            return {}
        if {x, y} == {1, 2}:  # [a-, a+] = 1 = -[a+, a-]
            return {(): c_const(1 if x == 2 else -1)}
        if x >= 3 and y >= 3:
            jx, sx = divmod(x - 3, 2)
            jy, sy = divmod(y - 3, 2)
            if jx == jy and sx != sy:  # [b-, b+] = 1
                return {(): c_const(1 if sx == 1 else -1)}
            return {}
        # one of them is a (odd), the other b (even)
        if x >= 3:  # [b, a] = -gb kappa
            b, a = x, y
            sign = 1
        else:  # [a, b] = -[b, a] (a odd, b even: (-1)^{0}=1)
            b, a = y, x
            sign = -1
        j, s = divmod(b - 3, 2)
        sig = "+" if a == 1 else "-"
        flat = self.gb_flat(sig, j + 1, "+" if s == 0 else "-")
        return {(0,): c_gb(flat, -sign)}

    # normal ordering --------------------------------------------------------
    def normal_order(self, mono: tuple) -> dict:
        """Rewrite an arbitrary word in the generators into normal-ordered form."""
        if mono in self._no_cache:
            return self._no_cache[mono]
        res = self._normal_order(mono)
        self._no_cache[mono] = res
        return res

    def _normal_order(self, mono: tuple) -> dict:
        for i in range(len(mono) - 1):
            x, y = mono[i], mono[i + 1]
            if x > y:
                # x y = (-1)^{p(x)p(y)} y x + [x, y]
                sign = -1 if (self.p(x) and self.p(y)) else 1
                head, tail = mono[:i], mono[i + 2:]
                out = c_scale_elem(self.normal_order(head + (y, x) + tail), sign)
                br = self.gen_bracket(x, y)
                for m, coef in br.items():
                    sub = self.normal_order(head + m + tail)
                    out = e_add(out, e_scale_coef(sub, coef))
                return out
            if x == y and self.p(x):  # odd generator squared = 0 (kappa^2 = 0 too)
                return {}
        return {mono: c_const(1)}

    # element operations -----------------------------------------------------
    def mul(self, A: dict, B: dict) -> dict:
        out: dict = {}
        for m1, c1 in A.items():
            for m2, c2 in B.items():
                c = c_mul(c1, c2)
                if not c:
                    continue
                for m, cc in self.normal_order(m1 + m2).items():
                    out = e_add(out, {m: c_mul(c, cc)})
        return out

    def elem_parity(self, A: dict) -> int:
        ps = {sum(self.p(g) for g in m) % 2 for m in A}
        if len(ps) > 1:
            raise ValueError("inhomogeneous element")
        return ps.pop() if ps else 0

    def bracket(self, A: dict, B: dict) -> dict:
        """Super-commutator [A, B] = AB - (-1)^{p(A)p(B)} BA."""
        pa, pb = self.elem_parity(A), self.elem_parity(B)
        sign = -1 if (pa and pb) else 1
        return e_add(self.mul(A, B), c_scale_elem(self.mul(B, A), -sign))

    def word(self, *gens: int, coef=1) -> dict:
        return e_scale_coef(self.normal_order(tuple(gens)), c_const(coef))


# element-level helpers --------------------------------------------------------
def e_add(A: dict, B: dict) -> dict:
    out = dict(A)
    for m, c in B.items():
        nc = c_add(out.get(m, {}), c)
        if nc:
            out[m] = nc
        else:
            out.pop(m, None)
    return out


def c_scale_elem(A: dict, s) -> dict:
    return {m: c_scale(c, s) for m, c in A.items()} if Fraction(s) != 0 else {}


def e_scale_coef(A: dict, coef: dict) -> dict:
    out = {}
    for m, c in A.items():
        nc = c_mul(c, coef)
        if nc:
            out[m] = nc
    return out


def split_kappa(A: dict):
    """Write A = A0 + kappa * A1 (kappa normal-ordered to the far left)."""
    A0, A1 = {}, {}
    for m, c in A.items():
        if m and m[0] == 0:
            A1[m[1:]] = c
        else:
            A0[m] = c
    return A0, A1
