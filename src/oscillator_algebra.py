"""Symbolic oscillator algebra engine for C(n+1) = osp(2|2n).

Oscillators (letters) are indexed by integers:
    0 -> a_1_p   (fermion, parity 1)
    1 -> a_1_m   (fermion, parity 1)
    2k   -> b_k_p  (boson, k = 1..n)
    2k+1 -> b_k_m  (boson, k = 1..n)

Relations:
    {a_1_m, a_1_p} = 1,  (a_1_p)^2 = (a_1_m)^2 = 0        (CAR)
    [b_k_m, b_l_p] = delta_kl                              (CCR)
    [b_k_s, a_1_sigma] = -gb_{sigma,k,s} * kappa           (deformed; 0 classically)

Elements are finite linear combinations of normal-ordered words
(letter tuples sorted ascending) with Fraction coefficients, plus a
first-order kappa part: a map (gb_label, word) -> Fraction representing
kappa * sum gb * coeff * word, with kappa written at the far left.
kappa is odd and central (supercommutes); kappa^2 = 0, so all
second-order deformed terms are dropped.
"""

from fractions import Fraction


def letter_name(letter):
    if letter == 0:
        return "a_1_p"
    if letter == 1:
        return "a_1_m"
    k, rem = divmod(letter, 2)
    return f"b_{k}_{'p' if rem == 0 else 'm'}"


def letter_index(name):
    if name == "a_1_p":
        return 0
    if name == "a_1_m":
        return 1
    _, k, s = name.split("_")
    return 2 * int(k) + (0 if s == "p" else 1)


def is_fermion(letter):
    return letter < 2


def word_parity(word):
    return sum(1 for l in word if is_fermion(l)) % 2


def gb_label(fermion_letter, boson_letter):
    sigma = "p" if fermion_letter == 0 else "m"
    k = boson_letter // 2
    s = "p" if boson_letter % 2 == 0 else "m"
    return f"gb_{sigma}_{k}_{s}"


def normal_order(word, coeff, deform):
    """Normal-order a word. Returns (terms, kterms):
    terms:  {word_tuple: Fraction}
    kterms: {(gb_label, word_tuple): Fraction}  -- first order in kappa.
    """
    terms = {}
    kterms = {}
    # worklist entries: (word, coeff, in_kappa_sector)
    stack = [(tuple(word), Fraction(coeff), False)]
    while stack:
        w, c, in_k = stack.pop()
        if isinstance(c, tuple):
            # kappa-sector item carries (gb, Fraction)
            gb, cf = c
        i = 0
        done = True
        for i in range(len(w) - 1):
            x, y = w[i], w[i + 1]
            if x == y and is_fermion(x):
                # (a^pm)^2 = 0 -> whole term vanishes
                done = None
                break
            if x > y:
                done = False
                break
        if done is None:
            continue
        if done:
            if in_k:
                gb, cf = c
                key = (gb, w)
                kterms[key] = kterms.get(key, Fraction(0)) + cf
                if kterms[key] == 0:
                    del kterms[key]
            else:
                terms[w] = terms.get(w, Fraction(0)) + c
                if terms[w] == 0:
                    del terms[w]
            continue
        x, y = w[i], w[i + 1]
        swapped = w[:i] + (y, x) + w[i + 2 :]
        removed = w[:i] + w[i + 2 :]
        fx, fy = is_fermion(x), is_fermion(y)
        if fx and fy:
            # x = a_1_m, y = a_1_p:  a- a+ = -a+ a- + 1
            if in_k:
                gb, cf = c
                stack.append((swapped, (gb, -cf), True))
                stack.append((removed, (gb, cf), True))
            else:
                stack.append((swapped, -c, False))
                stack.append((removed, c, False))
        elif not fx and fy:
            # x boson, y fermion: b a = a b - gb*kappa  (classically commute)
            if in_k:
                stack.append((swapped, c, True))  # drop kappa^2 term
            else:
                stack.append((swapped, c, False))
                lbl = gb_label(y, x)
                sign = -1 if word_parity(w[:i]) else 1
                stack.append((removed, (lbl, -c * sign), True))
        else:
            # both bosons
            if x // 2 == y // 2:
                # b_k_m b_k_p = b_k_p b_k_m + 1
                if in_k:
                    gb, cf = c
                    stack.append((swapped, (gb, cf), True))
                    stack.append((removed, (gb, cf), True))
                else:
                    stack.append((swapped, c, False))
                    stack.append((removed, c, False))
            else:
                stack.append((swapped, c, True) if in_k else (swapped, c, False))
    return terms, kterms


class Element:
    """Linear combination of normal-ordered oscillator words (+ kappa part)."""

    def __init__(self, terms=None, kterms=None):
        self.terms = dict(terms or {})
        self.kterms = dict(kterms or {})

    @classmethod
    def from_words(cls, word_coeffs):
        e = cls()
        for word, coeff in word_coeffs:
            e.terms[tuple(word)] = e.terms.get(tuple(word), Fraction(0)) + Fraction(coeff)
        return e

    def __add__(self, other):
        out = Element(self.terms, self.kterms)
        for w, c in other.terms.items():
            out.terms[w] = out.terms.get(w, Fraction(0)) + c
            if out.terms[w] == 0:
                del out.terms[w]
        for k, c in other.kterms.items():
            out.kterms[k] = out.kterms.get(k, Fraction(0)) + c
            if out.kterms[k] == 0:
                del out.kterms[k]
        return out

    def scale(self, s):
        s = Fraction(s)
        return Element(
            {w: c * s for w, c in self.terms.items()},
            {k: c * s for k, c in self.kterms.items()},
        )

    def mul(self, other, deform=False):
        out = Element()
        for w1, c1 in self.terms.items():
            for w2, c2 in other.terms.items():
                t, kt = normal_order(w1 + w2, c1 * c2, deform)
                for w, c in t.items():
                    out.terms[w] = out.terms.get(w, Fraction(0)) + c
                if deform:
                    for k, c in kt.items():
                        out.kterms[k] = out.kterms.get(k, Fraction(0)) + c
        if deform:
            # (kappa W1) * W2 : kappa stays left, classical product
            for (gb, w1), c1 in self.kterms.items():
                for w2, c2 in other.terms.items():
                    t, _ = normal_order(w1 + w2, c1 * c2, False)
                    for w, c in t.items():
                        out.kterms[(gb, w)] = out.kterms.get((gb, w), Fraction(0)) + c
            # W1 * (kappa W2) = (-1)^{p(W1)} kappa W1 W2
            for w1, c1 in self.terms.items():
                sign = -1 if word_parity(w1) else 1
                for (gb, w2), c2 in other.kterms.items():
                    t, _ = normal_order(w1 + w2, sign * c1 * c2, False)
                    for w, c in t.items():
                        out.kterms[(gb, w)] = out.kterms.get((gb, w), Fraction(0)) + c
            # kappa * kappa = 0: nothing from kterms x kterms
        out.terms = {w: c for w, c in out.terms.items() if c != 0}
        out.kterms = {k: c for k, c in out.kterms.items() if c != 0}
        return out

    def parity(self):
        """Parity if homogeneous (ignoring the kappa prefix), else None."""
        ps = {word_parity(w) for w in self.terms if w}
        if len(ps) == 1:
            return ps.pop()
        return None


def super_bracket(x, y, px, py, deform=False):
    """[X, Y} = XY - (-1)^{p(X)p(Y)} YX for homogeneous X, Y of parities px, py."""
    sign = -1 if (px and py) else 1
    return x.mul(y, deform) + y.mul(x, deform).scale(-sign)
