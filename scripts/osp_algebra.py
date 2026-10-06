#!/usr/bin/env python3
"""
osp_algebra.py
==============

Core engine for the inhomogeneous ("gb") deformation of C(n+1) = osp(2|2n).

Everything is computed inside the deformed Weyl--Clifford algebra

    W_kappa(n) = U(A) / (K - 1),      A = V (+) C.K (+) C.kappa,

with V = span{ b_j^+, b_j^- (even) ; a^+, a^- (odd) },  K even central,
kappa ODD central.  Because kappa is odd and central,

    [kappa, kappa] = 0   ==>   2 kappa^2 = 0   ==>   kappa^2 = 0,

exactly (not just to first order).  Hence every coefficient appearing below is
a polynomial of degree <= 1 in the deformation parameters gb, and the class
`Lin` (affine-linear forms in the gb symbols) is a *closed* arithmetic.

Defining relations (skew-supersymmetric pre-oscillator form):

    v_i v_j - (-1)^{p_i p_j} v_j v_i = omega_ij + mu_ij * kappa

    omega(b_j^-, b_k^+) = delta_jk = -omega(b_j^+, b_k^-)     (antisymmetric, even block)
    omega(a^+, a^-)     = omega(a^-, a^+) = 1                 (symmetric, odd block)
    mu(b_j^s, a^sigma)  = -gb[sigma, j, s] = -mu(a^sigma, b_j^s)

which reproduces  [b_j^s, a_1^sigma] = -gb_{sigma,j,s} . kappa  of
docs/math/C_inhomogeneous_definition.md.

Monomials are stored as (sorted_word, kflag) with all kappa's moved to the
FRONT; moving kappa past a word w costs a sign (-1)^{p(w)}.
"""

from fractions import Fraction
import itertools

# --------------------------------------------------------------------------
# Affine-linear forms in the gb symbols.  key None = constant term.
# --------------------------------------------------------------------------


class Lin(dict):
    """Affine-linear polynomial  c0 + sum_s c_s * s   over Fraction."""

    def __add__(self, other):
        out = Lin(self)
        for k, v in other.items():
            nv = out.get(k, Fraction(0)) + v
            if nv:
                out[k] = nv
            else:
                out.pop(k, None)
        return out

    def __mul__(self, scalar):
        if scalar == 0:
            return Lin()
        return Lin({k: v * scalar for k, v in self.items()})

    def __neg__(self):
        return self * Fraction(-1)

    def __sub__(self, other):
        return self + (-other)

    def is_zero(self):
        return not any(self.values())

    def subs(self, values):
        """Numerically evaluate: values maps symbol -> Fraction."""
        tot = self.get(None, Fraction(0))
        for k, v in self.items():
            if k is not None:
                tot += v * values[k]
        return tot

    def as_str(self):
        if self.is_zero():
            return "0"
        parts = []
        for k in sorted(self.keys(), key=lambda x: ("", "") if x is None else ("z", x)):
            v = self[k]
            if not v:
                continue
            parts.append(f"{v}" if k is None else f"{v}*{k}")
        return " + ".join(parts)


def const(c):
    c = Fraction(c)
    return Lin() if c == 0 else Lin({None: c})


def sym(name, c=1):
    c = Fraction(c)
    return Lin() if c == 0 else Lin({name: c})


ZERO = Lin()
ONE = const(1)


# --------------------------------------------------------------------------
# The algebra W_kappa(n)
# --------------------------------------------------------------------------


class OscAlgebra:
    """Deformed Weyl--Clifford algebra for C(n+1) = osp(2|2n)."""

    def __init__(self, n, gb=None):
        """gb: dict (sigma, j, s) -> Lin.  Default: independent symbols."""
        self.n = n
        self.N = 2 * n + 2
        self.names = []
        self.par = []
        for j in range(1, n + 1):
            self.names += [f"b{j}+", f"b{j}-"]
            self.par += [0, 0]
        self.names += ["a+", "a-"]
        self.par += [1, 1]
        self.index = {nm: i for i, nm in enumerate(self.names)}

        if gb is None:
            gb = {}
            for sigma in "+-":
                for j in range(1, n + 1):
                    for s in "+-":
                        gb[(sigma, j, s)] = sym(f"gb[{sigma},{j},{s}]")
        self.gb = gb

        # omega (undeformed, parity-preserving) ---------------------------
        self.omega = [[Fraction(0)] * self.N for _ in range(self.N)]
        for j in range(1, n + 1):
            p, m = self.index[f"b{j}+"], self.index[f"b{j}-"]
            self.omega[m][p] = Fraction(1)
            self.omega[p][m] = Fraction(-1)
        ap, am = self.index["a+"], self.index["a-"]
        self.omega[ap][am] = Fraction(1)
        self.omega[am][ap] = Fraction(1)

        # mu (deformation, parity-reversing, antisymmetric) ---------------
        self.mu = [[ZERO] * self.N for _ in range(self.N)]
        for sigma in "+-":
            ai = self.index[f"a{sigma}"]
            for j in range(1, n + 1):
                for s in "+-":
                    bi = self.index[f"b{j}{s}"]
                    g = gb[(sigma, j, s)]
                    self.mu[bi][ai] = -g
                    self.mu[ai][bi] = g

        self._norm_cache = {}

    # -- parity -----------------------------------------------------------
    def wpar(self, word):
        return sum(self.par[i] for i in word) % 2

    def key_par(self, key):
        word, k = key
        return (self.wpar(word) + k) % 2

    # -- normalisation ----------------------------------------------------
    def norm_word(self, word, k):
        """Normal form of kappa^k * v_{word}.  Returns element dict."""
        ck = (word, k)
        if ck in self._norm_cache:
            return self._norm_cache[ck]
        res = self._norm_word_raw(word, k)
        self._norm_cache[ck] = res
        return res

    def _norm_word_raw(self, word, k):
        if k > 1:
            return {}
        for idx in range(len(word) - 1):
            i, j = word[idx], word[idx + 1]
            if i == j and self.par[i] == 1:
                # v_i v_i = 1/2 (omega_ii + mu_ii kappa);  mu_ii = 0 (same parity)
                rest = word[:idx] + word[idx + 2:]
                out = {}
                if self.omega[i][i]:
                    add_into(out, self.norm_word(rest, k), const(self.omega[i][i]) * Fraction(1, 2))
                return out
            if i > j:
                sgn = Fraction(-1) if (self.par[i] and self.par[j]) else Fraction(1)
                swapped = word[:idx] + (j, i) + word[idx + 2:]
                rest = word[:idx] + word[idx + 2:]
                out = {}
                add_into(out, self.norm_word(swapped, k), sgn)
                if self.omega[i][j]:
                    add_into(out, self.norm_word(rest, k), const(self.omega[i][j]))
                if k == 0 and not self.mu[i][j].is_zero():
                    # kappa produced at position idx must travel to the front
                    head_sign = Fraction(-1) ** self.wpar(word[:idx])
                    add_into(out, self.norm_word(rest, 1), self.mu[i][j] * head_sign)
                return out
        return {(tuple(word), k): ONE}

    # -- element arithmetic ----------------------------------------------
    def mul(self, X, Y):
        out = {}
        for (w1, k1), c1 in X.items():
            for (w2, k2), c2 in Y.items():
                if k1 + k2 > 1:
                    continue
                # move kappa^{k2} left past w1
                sgn = Fraction(-1) ** (k2 * self.wpar(w1))
                piece = self.norm_word(w1 + w2, k1 + k2)
                add_into(out, piece, mul_lin(c1, c2) * sgn)
        return prune(out)

    def bracket(self, X, Y):
        """Super-commutator of homogeneous elements."""
        pX, pY = self.parity(X), self.parity(Y)
        out = self.mul(X, Y)
        add_into(out, self.mul(Y, X), Fraction(-1) ** (pX * pY) * Fraction(-1))
        return prune(out)

    def parity(self, X):
        ps = {self.key_par(k) for k, c in X.items() if not c.is_zero()}
        if len(ps) > 1:
            raise ValueError("inhomogeneous element")
        return ps.pop() if ps else 0

    def kappa_times(self, X):
        """kappa . X (kappa written on the left)."""
        out = {}
        for (w, k), c in X.items():
            if k:
                continue
            out[(w, 1)] = out.get((w, 1), ZERO) + c
        return prune(out)

    def gen(self, name):
        i = self.index[name]
        return {((i,), 0): ONE}

    def elt(self, *terms):
        """elt((coeff, name_or_element), ...)"""
        out = {}
        for c, t in terms:
            if isinstance(t, str):
                t = self.gen(t)
            add_into(out, t, c)
        return prune(out)


# --------------------------------------------------------------------------
# dict helpers
# --------------------------------------------------------------------------


def mul_lin(a, b):
    """Product of two affine-linear forms; must stay affine-linear."""
    if a.is_zero() or b.is_zero():
        return ZERO
    out = Lin()
    for k1, v1 in a.items():
        for k2, v2 in b.items():
            if k1 is not None and k2 is not None:
                raise ValueError("quadratic in gb -- should never happen (kappa^2=0)")
            k = k1 if k2 is None else k2
            nv = out.get(k, Fraction(0)) + v1 * v2
            if nv:
                out[k] = nv
            else:
                out.pop(k, None)
    return out


def add_into(dst, src, factor=1):
    if isinstance(factor, (int, Fraction)):
        factor = const(factor)
    for k, v in src.items():
        nv = dst.get(k, ZERO) + mul_lin(v, factor)
        if nv.is_zero():
            dst.pop(k, None)
        else:
            dst[k] = nv
    return dst


def prune(X):
    return {k: v for k, v in X.items() if not v.is_zero()}


def scale(X, c):
    return prune({k: v * Fraction(c) for k, v in X.items()})


def sub(X, Y):
    out = dict(X)
    add_into(out, Y, Fraction(-1))
    return prune(out)
