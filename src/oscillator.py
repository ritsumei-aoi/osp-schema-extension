"""Exact super oscillator algebra used to realize C(n+1) = osp(2|2n).

Oscillators: fermionic pair a_1_p, a_1_m (parity 1) and bosons b_k_p, b_k_m
(parity 0), plus an odd central element kappa (kappa^2 = 0).

An element is a dict mapping (kappa, gb, word) -> Fraction, where
  kappa in {0, 1}   power of kappa (always written on the far left),
  gb    : str|None  deformation parameter label multiplying a kappa term
                    (kappa^2 = 0 so at most one gb factor appears),
  word  : tuple     oscillator labels in normal order (see notation.md).

Relations (super-commutators [x, y} = xy - (-1)^{p(x)p(y)} yx):
  {a_1_m, a_1_p} = 1, (a_1_p)^2 = (a_1_m)^2 = 0,
  [b_k_m, b_l_p] = delta_kl, [b_k_s, b_l_s] = 0,
  [b_j_s, a_1_sigma] = 0                          (undeformed)
  [b_j_s, a_1_sigma] = -gb_{sigma}_{j}_{s} kappa  (deformed)
"""
from fractions import Fraction


def osc_parity(x):
    return 1 if x.startswith("a_") else 0


def gb_label(sigma, j, s):
    return f"gb_{sigma}_{j}_{s}"


class OscillatorAlgebra:
    def __init__(self, n, deformed=False):
        self.n = n
        self.deformed = deformed
        self.order = ["a_1_p", "a_1_m"]
        for k in range(1, n + 1):
            self.order += [f"b_{k}_p", f"b_{k}_m"]
        self.rank = {x: i for i, x in enumerate(self.order)}

    # -- elementary super-commutators -------------------------------------
    def supercomm(self, x, y):
        """[x, y} as a list of (kappa, gb, coeff)."""
        px, py = osc_parity(x), osc_parity(y)
        if px and py:  # both fermions
            if {x, y} == {"a_1_p", "a_1_m"}:
                return [(0, None, Fraction(1))]
            return []
        if not px and not py:  # both bosons
            _, k, sx = x.split("_")
            _, l, sy = y.split("_")
            if k != l or sx == sy:
                return []
            return [(0, None, Fraction(1 if sx == "m" else -1))]
        if not self.deformed:
            return []
        # mixed: [b_j^s, a^sigma] = -gb kappa ; [a^sigma, b_j^s] = +gb kappa
        if px:  # x fermion, y boson
            sigma = x.split("_")[2]
            _, j, s = y.split("_")
            return [(1, gb_label(sigma, j, s), Fraction(1))]
        sigma = y.split("_")[2]
        _, j, s = x.split("_")
        return [(1, gb_label(sigma, j, s), Fraction(-1))]

    # -- normal ordering ---------------------------------------------------
    def normal_order(self, elem):
        out = {}
        stack = list(elem.items())
        while stack:
            (kap, gb, word), c = stack.pop()
            if c == 0:
                continue
            pos = None
            for i in range(len(word) - 1):
                x, y = word[i], word[i + 1]
                if self.rank[x] > self.rank[y] or (x == y and osc_parity(x)):
                    pos = i
                    break
            if pos is None:
                key = (kap, gb, word)
                out[key] = out.get(key, 0) + c
                if out[key] == 0:
                    del out[key]
                continue
            x, y = word[pos], word[pos + 1]
            u, v = word[:pos], word[pos + 2:]
            if x == y:  # a^± a^± = (1/2){a^±, a^±} = 0
                continue
            sign = -1 if (osc_parity(x) and osc_parity(y)) else 1
            stack.append(((kap, gb, u + (y, x) + v), sign * c))
            for k2, g2, c2 in self.supercomm(x, y):
                if k2 == 0:
                    stack.append(((kap, gb, u + v), c * c2))
                else:
                    if kap:
                        continue  # kappa^2 = 0
                    pu = sum(osc_parity(z) for z in u) % 2
                    stack.append(((1, g2, u + v), c * c2 * (-1) ** pu))
        return out

    # -- products / brackets -------------------------------------------------
    def mul(self, A, B):
        raw = {}
        for (ka, ga, wa), ca in A.items():
            for (kb, gbb, wb), cb in B.items():
                if ka and kb:
                    continue
                sign = 1
                if kb:  # move kappa of B to the far left through wa
                    sign = (-1) ** (sum(osc_parity(z) for z in wa) % 2)
                key = (ka or kb, ga or gbb, wa + wb)
                raw[key] = raw.get(key, 0) + sign * ca * cb
        return self.normal_order(raw)

    def bracket(self, A, pa, B, pb):
        AB = self.mul(A, B)
        BA = self.mul(B, A)
        s = -1 if (pa and pb) else 1
        out = dict(AB)
        for k, c in BA.items():
            out[k] = out.get(k, 0) - s * c
            if out[k] == 0:
                del out[k]
        return out


def from_standard_form(terms):
    """[{'words': [...], 'coeff': '1/2'}, ...] -> element (undeformed, no kappa)."""
    out = {}
    for t in terms:
        key = (0, None, tuple(t["words"]))
        out[key] = out.get(key, 0) + Fraction(t["coeff"])
    return out
