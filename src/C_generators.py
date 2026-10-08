"""Weyl-symmetric oscillator realization of C(n+1) = osp(2|2n).

Oscillators (canonical index order):
    0: a1p (a_1^+, odd)   1: a1m (a_1^-, odd)
    2: b1p, 3: b1m, 4: b2p, 5: b2m, ...   (b_k^± even)

Relations:
    {a1m, a1p} = 1,  [b_k^-, b_k^+] = 1,  all other (anti)commutators 0,
    plus the optional inhomogeneous deformation  [b_j^s, a_1^σ] = -gb[σ,j,s] κ,
    with κ nilpotent (κ² = 0) and central.

Coefficients are dual numbers (c0, ck) meaning c0 + ck·κ.

Basis: the Weyl-symmetrized quadratic elements
    W(x,y) = ½ (x y + (-1)^{p(x)p(y)} y x),   x <= y, W(x,x) for bosons,
which span osp(2|2n) (dimension 2n²+5n+1 in total, no constants needed).
"""
from fractions import Fraction
from functools import lru_cache
import json
import sys

import sympy

ZERO = (Fraction(0), Fraction(0))
ONE = (Fraction(1), Fraction(0))


def dadd(x, y):
    return (x[0] + y[0], x[1] + y[1])


def dmul(x, y):
    return (x[0] * y[0], x[0] * y[1] + x[1] * y[0])


def dscale(x, s):
    return (x[0] * s, x[1] * s)


def is_zero(x):
    return x[0] == 0 and x[1] == 0


def add_into(dst, key, val):
    if is_zero(val):
        return
    new = dadd(dst.get(key, ZERO), val)
    if is_zero(new):
        dst.pop(key, None)
    else:
        dst[key] = new


class OscAlgebra:
    """Symbolic oscillator algebra for C(n+1) with optional deformation gb."""

    def __init__(self, n, gb=None):
        self.n = n
        self.labels = ["a1p", "a1m"]
        self.par = [1, 1]
        for k in range(1, n + 1):
            self.labels += [f"b{k}p", f"b{k}m"]
            self.par += [0, 0]
        self.dim_osc = len(self.labels)
        # gb keys: (sigma, k, s) with sigma, s in {'p','m'}, k in 1..n
        self.gb = {} if gb is None else {key: Fraction(v) for key, v in gb.items()}
        self._cache = {}

    def boson_info(self, i):
        """Return (k, s) for a bosonic index i >= 2."""
        k = (i - 2) // 2 + 1
        s = "p" if (i - 2) % 2 == 0 else "m"
        return k, s

    def comm(self, x, y):
        """Graded bracket [x, y] for ordered oscillator pair, with x or y even."""
        px, py = self.par[x], self.par[y]
        if px == 0 and py == 0:
            kx, sx = self.boson_info(x)
            ky, sy = self.boson_info(y)
            if kx == ky and sx == "m" and sy == "p":
                return ONE
            if kx == ky and sx == "p" and sy == "m":
                return (Fraction(-1), Fraction(0))
            return ZERO
        if px == 0 and py == 1:
            kx, sx = self.boson_info(x)
            sigma = "p" if y == 0 else "m"
            g = self.gb.get((sigma, kx, sx), Fraction(0))
            return (Fraction(0), -g)
        if px == 1 and py == 0:
            return dscale(self.comm(y, x), -1)
        raise ValueError("comm called on two odd oscillators")

    def bracket(self, x, y):
        """Constant B(x,y) with  x*y = s*y*x + B(x,y), s = -1 if both odd."""
        if self.par[x] and self.par[y]:
            if {x, y} == {0, 1}:
                return ONE
            return ZERO
        return self.comm(x, y)

    def normal(self, word):
        """Normal-order a word (tuple of oscillator indices); returns dict."""
        if word in self._cache:
            return self._cache[word]
        out = None
        for pos in range(len(word) - 1):
            x, y = word[pos], word[pos + 1]
            if x == y and self.par[x]:
                out = {}
                break
            if x > y:
                s = -1 if (self.par[x] and self.par[y]) else 1
                out = {}
                for w, c in self.normal(word[:pos] + (y, x) + word[pos + 2:]).items():
                    add_into(out, w, dscale(c, s))
                for w, c in self.normal(word[:pos] + word[pos + 2:]).items():
                    add_into(out, w, dmul(self.bracket(x, y), c))
                break
        if out is None:
            out = {word: ONE}
        self._cache[word] = out
        return out

    def mul(self, X, Y):
        out = {}
        for u, cu in X.items():
            for v, cv in Y.items():
                c = dmul(cu, cv)
                for w, cw in self.normal(u + v).items():
                    add_into(out, w, dmul(c, cw))
        return out

    def sym(self, i, j):
        """Weyl-symmetrized quadratic W(i,j)."""
        s = -1 if (self.par[i] and self.par[j]) else 1
        out = {}
        for w, c in self.normal((i, j)).items():
            add_into(out, w, dscale(c, Fraction(1, 2)))
        for w, c in self.normal((j, i)).items():
            add_into(out, w, dscale(c, Fraction(s, 2)))
        return out

    def supercommutator(self, X, px, Y, py):
        sign = -1 if (px and py) else 1
        out = dict(self.mul(X, Y))
        for w, c in self.mul(Y, X).items():
            add_into(out, w, dscale(c, -sign))
        return out

    def basis_pairs(self):
        """Index pairs (i,j), i<=j, whose symmetric element is nonzero.

        Odd elements come first (PBW convention), then even; ties by (i,j)."""
        pairs = []
        for i in range(self.dim_osc):
            for j in range(i, self.dim_osc):
                if not self.sym(i, j):
                    continue
                pairs.append((i, j))
        odd = [p for p in pairs if (self.par[p[0]] + self.par[p[1]]) % 2 == 1]
        even = [p for p in pairs if (self.par[p[0]] + self.par[p[1]]) % 2 == 0]
        return odd + even

    def pair_label(self, i, j):
        return f"W({self.labels[i]},{self.labels[j]})"
