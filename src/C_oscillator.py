"""Oscillator algebra for C(n+1) = osp(2|2n).

Provides a symbolic normal-order algorithm for polynomials in the oscillators
{a_1_p, a_1_m, b_k_p, b_k_m} using the relations

    {a_1^-, a_1^+} = 1,  (a_1^+)^2 = (a_1^-)^2 = 0
    [b_i^-, b_j^+] = delta_{ij},  all other boson brackets vanish
    [b_k^s, a_1^sigma] = 0  (undeformed)

The normal order is:  a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ...
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Tuple

Word = Tuple[str, ...]
Poly = Dict[Word, Fraction]


def osc_index(sym: str) -> int:
    if sym == "a_1_p":
        return 0
    if sym == "a_1_m":
        return 1
    _, k, s = sym.split("_")
    k = int(k)
    return 2 + 2 * (k - 1) + (0 if s == "p" else 1)


def parity_sym(sym: str) -> int:
    return 1 if sym.startswith("a_") else 0


def poly_add(a: Poly, b: Poly, c: Fraction = Fraction(1)) -> Poly:
    out: Poly = dict(a)
    for w, v in b.items():
        nv = out.get(w, Fraction(0)) + c * v
        if nv == 0:
            out.pop(w, None)
        else:
            out[w] = nv
    return out


def poly_scale(a: Poly, c) -> Poly:
    c = Fraction(c)
    if c == 0:
        return {}
    return {w: c * v for w, v in a.items()}


def mono(word, coeff=1) -> Poly:
    return {tuple(word): Fraction(coeff)}


def normalize_word(word: Word) -> Poly:
    final: Poly = {}
    stack: List[Tuple[Fraction, List[str]]] = [(Fraction(1), list(word))]
    while stack:
        c, w = stack.pop()
        if any(w[i] == w[i + 1] and parity_sym(w[i]) == 1 for i in range(len(w) - 1)):
            continue
        pivot = None
        for i in range(len(w) - 1):
            if osc_index(w[i]) > osc_index(w[i + 1]):
                pivot = i
                break
        if pivot is None:
            key = tuple(w)
            nv = final.get(key, Fraction(0)) + c
            if nv == 0:
                final.pop(key, None)
            else:
                final[key] = nv
            continue
        s, t = w[pivot], w[pivot + 1]
        ps, pt = parity_sym(s), parity_sym(t)
        if ps == 1 and pt == 1:
            sign = Fraction(-1)
            anti = Fraction(1) if {s, t} == {"a_1_p", "a_1_m"} else Fraction(0)
        elif ps == 0 and pt == 0:
            sign = Fraction(1)
            anti = Fraction(0)
            if s[0] == "b" and t[0] == "b":
                ks = int(s.split("_")[1])
                kt = int(t.split("_")[1])
                if ks == kt and s[-1] == "m" and t[-1] == "p":
                    anti = Fraction(1)
        else:
            sign = Fraction(1)
            anti = Fraction(0)
        stack.append((sign * c, w[:pivot] + [t, s] + w[pivot + 2:]))
        if anti != 0:
            stack.append((c * anti, w[:pivot] + w[pivot + 2:]))
    return final


def poly_mul(a: Poly, b: Poly) -> Poly:
    out: Poly = {}
    for wa, va in a.items():
        for wb, vb in b.items():
            nf = normalize_word(wa + wb)
            for ww, vv in nf.items():
                nv = out.get(ww, Fraction(0)) + va * vb * vv
                if nv == 0:
                    out.pop(ww, None)
                else:
                    out[ww] = nv
    return out


def graded_bracket(X: Poly, Y: Poly, pX: int, pY: int) -> Poly:
    XY = poly_mul(X, Y)
    YX = poly_mul(Y, X)
    sign = 1 if (pX * pY) % 2 == 0 else -1
    return poly_add(XY, YX, Fraction(-sign))
