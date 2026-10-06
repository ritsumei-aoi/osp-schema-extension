"""C(n+1) = osp(2|2n) structure-constant generator (Schema 1, v5.0 extension).

Oscillator letters (normal-ordering rank):
    K < a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ...
K stands for the odd central element kappa (kappa^2 = 0, graded central).
Relations: {a_1_m, a_1_p} = 1 (CAR), [b_k_m, b_l_p] = delta_kl (CCR),
[b_j^s, a^sigma] = -gb[sigma, j, s] * kappa (deformation; gb = {} -> undeformed).
The even central element K_even is identified with the scalar 1 (see notation.md).
"""
import json
import os
from fractions import Fraction

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
FERMIONS = ("a_1_p", "a_1_m")


# ----------------------------------------------------------------- basis ----
def even_names(n):
    names = [f"H_{k}" for k in range(1, n + 2)]
    names += [f"E_2del{k}_p" for k in range(1, n + 1)]
    names += [f"E_del{i}_del{j}_pp" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    names += [f"E_2del{k}_m" for k in range(1, n + 1)]
    names += [f"E_del{i}_del{j}_mm" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    for t in ("pm", "mp"):
        names += [f"E_del{i}_del{j}_{t}" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    return names


def odd_names(n):
    return [f"E_eps1_del{k}_{e}{d}" for e in "pm" for d in "pm" for k in range(1, n + 1)]


def basis_names(n):
    """Full PBW-ordered basis: odd first, then even (kappa excluded, K = 1)."""
    return odd_names(n) + even_names(n)


def parity_of(name):
    """Parity of a basis element (K and H, E_2del, E_del are even)."""
    return 1 if name.startswith("E_eps1") else 0


def realization(name, n):
    """Oscillator realization as {word(tuple): Fraction} in normal-ordered form."""
    F = Fraction
    if name.startswith("H_"):
        k = int(name[2:])
        if k == 1:
            return {("a_1_p", "a_1_m"): F(1), ("b_1_p", "b_1_m"): F(1)}
        if k <= n:
            return {(f"b_{k-1}_p", f"b_{k-1}_m"): F(1), (f"b_{k}_p", f"b_{k}_m"): F(-1)}
        return {(f"b_{n}_p", f"b_{n}_m"): F(-1), (): F(-1, 2)}
    if name.startswith("E_2del"):
        k, s = name[6:].split("_")
        return {(f"b_{k}_{s}", f"b_{k}_{s}"): F(1)}
    if name.startswith("E_del"):
        parts = name.split("_")
        i, j, st = parts[1][3:], parts[2][3:], parts[3]
        return {(f"b_{i}_{st[0]}", f"b_{j}_{st[1]}"): F(1)}
    if name.startswith("E_eps1"):
        parts = name.split("_")
        k = parts[2][3:]
        e, d = parts[3]
        return {(f"a_1_{e}", f"b_{k}_{d}"): F(1)}
    raise ValueError(name)


# --------------------------------------------------- oscillator algebra ----
def _rank(letter):
    if letter == "K":
        return 0
    if letter == "a_1_p":
        return 1
    if letter == "a_1_m":
        return 2
    _, k, s = letter.split("_")
    return 3 + 2 * (int(k) - 1) + (0 if s == "p" else 1)


def _is_ferm(x):
    return x.startswith("a_")


class Oscillators:
    """Normal-ordering engine; gb maps (sigma, j, s) -> Fraction."""

    def __init__(self, gb=None):
        self.gb = dict(gb or {})
        self._cache = {}

    def reduce_word(self, w):
        if w in self._cache:
            return self._cache[w]
        res = {}
        for i in range(len(w) - 1):
            x, y = w[i], w[i + 1]
            if x == y and (x == "K" or _is_ferm(x)):
                res = {}
                break
            if _rank(x) <= _rank(y):
                continue
            pre, post = w[:i], w[i + 2:]
            terms = []
            if y == "K":
                terms.append((pre + (y, x) + post, Fraction(-1 if _is_ferm(x) else 1)))
            elif _is_ferm(x) and _is_ferm(y):  # a_m a_p = 1 - a_p a_m
                terms.append((pre + post, Fraction(1)))
                terms.append((pre + (y, x) + post, Fraction(-1)))
            elif not _is_ferm(x) and not _is_ferm(y):  # bosons
                terms.append((pre + (y, x) + post, Fraction(1)))
                if x.split("_")[1] == y.split("_")[1]:  # b^- b^+ = b^+ b^- + 1
                    terms.append((pre + post, Fraction(1)))
            else:  # boson x, fermion y: b a = a b - gb kappa
                terms.append((pre + (y, x) + post, Fraction(1)))
                _, j, s = x.split("_")
                g = self.gb.get((y[-1], int(j), s), 0)
                if g:
                    terms.append((pre + ("K",) + post, -Fraction(g)))
            for tw, c in terms:
                for rw, rc in self.reduce_word(tw).items():
                    res[rw] = res.get(rw, 0) + c * rc
            res = {k: v for k, v in res.items() if v != 0}
            break
        else:
            res = {w: Fraction(1)}
        self._cache[w] = res
        return res

    def mul(self, p, q):
        out = {}
        for w1, c1 in p.items():
            for w2, c2 in q.items():
                for w, c in self.reduce_word(w1 + w2).items():
                    out[w] = out.get(w, 0) + c1 * c2 * c
        return {k: v for k, v in out.items() if v != 0}

    def bracket(self, p, px, q, qx):
        """Graded bracket [p,q} = pq - (-1)^{px qx} qp."""
        out = dict(self.mul(p, q))
        sgn = -1 if (px * qx) % 2 == 0 else 1
        for w, c in self.mul(q, p).items():
            out[w] = out.get(w, 0) + sgn * c
        return {k: v for k, v in out.items() if v != 0}


# ------------------------------------------------ expansion in the basis ----
class BasisExpander:
    """Exact expansion of oscillator polynomials in the span of the basis."""

    def __init__(self, n, with_K=False):
        """with_K=True adds the even central element K (scalar 1, label "K") as an extra
        target column; needed for the kappa-part gamma (kappa*K terms), see I05."""
        import sympy
        self.n = n
        self.names = basis_names(n) + (["K"] if with_K else [])
        self.real = {nm: realization(nm, n) for nm in basis_names(n)}
        if with_K:
            self.real["K"] = {(): Fraction(1)}
        words = sorted({w for r in self.real.values() for w in r}, key=lambda w: (len(w), w))
        self.words = words
        self.widx = {w: i for i, w in enumerate(words)}
        M = sympy.zeros(len(words), len(self.names))
        for j, nm in enumerate(self.names):
            for w, c in self.real[nm].items():
                M[self.widx[w], j] = sympy.Rational(c.numerator, c.denominator)
        L = (M.T * M).inv() * M.T
        self.L = [[Fraction(int(L[i, j].p), int(L[i, j].q)) for j in range(L.shape[1])]
                  for i in range(L.shape[0])]

    def expand(self, poly):
        """Return {basis_name: Fraction}; raises if poly is outside the span."""
        vec = [Fraction(0)] * len(self.words)
        for w, c in poly.items():
            if w not in self.widx:
                raise ValueError(f"word {w} outside basis span")
            vec[self.widx[w]] = c
        coeffs = {}
        for i, nm in enumerate(self.names):
            c = sum((self.L[i][j] * vec[j] for j in range(len(vec)) if vec[j]), Fraction(0))
            if c:
                coeffs[nm] = c
        check = {}
        for nm, c in coeffs.items():
            for w, rc in self.real[nm].items():
                check[w] = check.get(w, 0) + c * rc
        if {k: v for k, v in check.items() if v} != {k: v for k, v in poly.items() if v}:
            raise ValueError(f"poly {poly} not in span of basis")
        return coeffs


def frac_str(c):
    c = Fraction(c)
    return str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"


def structure_constants(n, expander=None):
    """All non-zero [X,Y} = sum Z coeff, for every ordered pair (X,Y)."""
    ex = expander or BasisExpander(n)
    osc = Oscillators()
    entries = []
    for X in ex.names:
        for Y in ex.names:
            br = osc.bracket(ex.real[X], parity_of(X), ex.real[Y], parity_of(Y))
            for Z, c in ex.expand(br).items():
                entries.append({"X": X, "Y": Y, "Z": Z, "coeff": frac_str(c),
                                "sign_rule": "graded"})
    return entries


# ----------------------------------------------------------- JSON output ----
def _sorted_terms(r):
    return sorted(r.items(), key=lambda t: (len(t[0]), t[0]), reverse=True)


def _frappat(r):
    def sym(l):
        if l.startswith("a_"):
            return "a_1^" + ("+" if l[-1] == "p" else "-")
        _, k, s = l.split("_")
        return f"b_{k}^" + ("+" if s == "p" else "-")
    return " + ".join(f"{frac_str(c)}*" + (" ".join(sym(l) for l in w) or "1")
                      for w, c in _sorted_terms(r))


def realization_json(name, n):
    r = realization(name, n)
    return {"standard_form": [{"words": list(w), "coeff": frac_str(c)}
                              for w, c in _sorted_terms(r)],
            "frappat_form": _frappat(r), "parity": parity_of(name)}


def build_schema1(n, today="2026-10-06"):
    ex = BasisExpander(n)
    ev, od = even_names(n), odd_names(n)
    bos = [f"b_{k}_{s}" for k in range(1, n + 1) for s in "pm"]
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})",
            "alternative_notation": {"osp": f"osp(2|{2*n})",
                                     "dimension_formula": "osp(2m|2n) with m=1"},
            "dimension": {"total": len(ev) + len(od), "even": len(ev), "odd": len(od)},
        },
        "oscillator_generators": {
            "fermions": {"m": 1, "count": 2, "labels": list(FERMIONS), "parity": 1,
                         "description": "Standard fermionic pair a_1^pm (CAR); replaces a_0."},
            "bosons": {"count": 2 * n, "n": n, "labels": bos,
                       "description": "Bosonic oscillators b_i^pm with i=1,...,n"},
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations (CAR)",
                "relations": {"conjugate_pair": "{a_1^-, a_1^+} = 1",
                              "same_type": "(a_1^+)^2 = (a_1^-)^2 = 0"}},
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                              "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"}},
            "mixed_commutators": {"boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed Schema 1)"},
        },
        "central_elements": {
            "kappa": {"parity": 1, "nilpotent": True, "relation": "kappa^2 = 0",
                      "description": "Odd central element; carries the deformation (Schema 2)."},
            "K": {"parity": 0, "identification": "scalar 1",
                  "description": "Even central element; identified with 1, not a basis element."},
        },
        "basis": {"even": ev, "odd": od,
                  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"},
        "parity": {nm: parity_of(nm) for nm in ex.names},
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ", ".join(list(FERMIONS) + bos),
            "realizations": {nm: realization_json(nm, n) for nm in od + ev},
        },
        "structure_constants": structure_constants(n, ex),
        "metadata": {
            "generated_by": "src/C_generators.py", "generation_date": today,
            "convention": "[X,Y} = XY - (-1)^{p(X)p(Y)} YX; E_{±2δ_k} = (b_k^±)^2 (no 1/2)",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"],
        },
    }


def main(ns=(1, 2, 3)):
    os.makedirs(DATA_DIR, exist_ok=True)
    for n in ns:
        d = build_schema1(n)
        path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
        with open(path, "w") as f:
            json.dump(d, f, indent=1)
        print(path, d["algebra"]["dimension"], len(d["structure_constants"]), "entries")


if __name__ == "__main__":
    main()
