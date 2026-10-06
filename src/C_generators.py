"""Basis, realization and Schema 1 structure constants for C(n+1) = osp(2|2n).

Usage:  python src/C_generators.py   (writes data/C_{n}_structure.json, n=1,2,3)
Conventions: handover/notation.md; schema: docs/json_schema_specification.md.
"""
import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osc_algebra import bracket, add_to  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def mono(n, fp=0, fm=0, **bos):
    """Monomial helper: bos given as p1=..,q1=..  (exponents of b_k^+ / b_k^-)."""
    B = [0] * (2 * n)
    for key, e in bos.items():
        B[2 * (int(key[1:]) - 1) + (0 if key[0] == 'p' else 1)] = e
    return (0, fp, fm, tuple(B))


def build_basis(n):
    """Return (names, parity dict, realization dict) in PBW order: odd then even."""
    odd = []
    for sg in ("pp", "pm", "mp", "mm"):
        for k in range(1, n + 1):
            odd.append(f"E_eps1_del{k}_{sg}")
    even = [f"H_{k}" for k in range(1, n + 2)]
    even += [f"E_2del{k}_p" for k in range(1, n + 1)]
    pairs = [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    even += [f"E_del{i}_del{j}_pp" for i, j in pairs]
    even += [f"E_2del{k}_m" for k in range(1, n + 1)]
    even += [f"E_del{i}_del{j}_mm" for i, j in pairs]
    even += [f"E_del{i}_del{j}_pm" for i, j in pairs]
    even += [f"E_del{i}_del{j}_mp" for i, j in pairs]

    R = {}
    for k in range(1, n + 1):
        for sg in ("pp", "pm", "mp", "mm"):
            fp, fm = (1, 0) if sg[0] == 'p' else (0, 1)
            b = {("p" if sg[1] == 'p' else "q") + str(k): 1}
            R[f"E_eps1_del{k}_{sg}"] = {mono(n, fp, fm, **b): Fraction(1)}
    # Cartan
    R["H_1"] = {mono(n, 1, 1): Fraction(1), mono(n, p1=1, q1=1): Fraction(1)}
    for k in range(2, n + 1):
        d = {}
        add_to(d, mono(n, **{f"p{k-1}": 1, f"q{k-1}": 1}), Fraction(1))
        add_to(d, mono(n, **{f"p{k}": 1, f"q{k}": 1}), Fraction(-1))
        R[f"H_{k}"] = d
    R[f"H_{n+1}"] = {mono(n, **{f"p{n}": 1, f"q{n}": 1}): Fraction(-1), mono(n): Fraction(-1, 2)}
    for k in range(1, n + 1):
        R[f"E_2del{k}_p"] = {mono(n, **{f"p{k}": 2}): Fraction(1, 2)}
        R[f"E_2del{k}_m"] = {mono(n, **{f"q{k}": 2}): Fraction(1, 2)}
    for i, j in pairs:
        for sg in ("pp", "pm", "mp", "mm"):
            e = {("p" if sg[0] == 'p' else "q") + str(i): 1}
            e[("p" if sg[1] == 'p' else "q") + str(j)] = 1
            R[f"E_del{i}_del{j}_{sg}"] = {mono(n, **e): Fraction(1)}
    parity = {x: 1 for x in odd}
    parity.update({x: 0 for x in even})
    names = odd + even
    assert set(R) == set(names)
    return names, parity, R


class Decomposer:
    """Exact coordinates of an oscillator element in the basis (least squares left inverse)."""

    def __init__(self, names, R):
        self.names = names
        self.R = R
        monos = sorted({m for r in R.values() for m in r})
        self.monos = monos
        self.row = {m: i for i, m in enumerate(monos)}
        N = len(names)
        # Gram matrix inverse with Fractions (Gauss-Jordan)
        cols = [{self.row[m]: c for m, c in R[x].items()} for x in names]
        G = [[Fraction(0)] * N for _ in range(N)]
        for a in range(N):
            for b in range(N):
                G[a][b] = sum(c * cols[b].get(r, 0) for r, c in cols[a].items())
        self.cols = cols
        self.Ginv = _invert(G)

    def decompose(self, X):
        """Return ({name: coeff}, residual dict). Residual != {} means X not in span of basis."""
        names = self.names
        N = len(names)
        v = {}
        resid = {}
        for m, c in X.items():
            if m in self.row:
                v[self.row[m]] = c
            else:
                resid[m] = c
        rhs = [sum(c * v.get(r, 0) for r, c in self.cols[a].items()) for a in range(N)]
        coef = [sum(self.Ginv[a][b] * rhs[b] for b in range(N) if rhs[b]) for a in range(N)]
        # residual: X - sum coef * R
        res = dict(X)
        for a, x in enumerate(names):
            if coef[a]:
                for m, c in self.R[x].items():
                    add_to(res, m, -coef[a] * c)
        return {names[a]: coef[a] for a in range(N) if coef[a]}, res


def _invert(G):
    N = len(G)
    A = [row[:] + [Fraction(int(i == j)) for j in range(N)] for i, row in enumerate(G)]
    for c in range(N):
        p = next(r for r in range(c, N) if A[r][c] != 0)
        A[c], A[p] = A[p], A[c]
        inv = 1 / A[c][c]
        A[c] = [x * inv for x in A[c]]
        for r in range(N):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [x - f * y for x, y in zip(A[r], A[c])]
    return [row[N:] for row in A]


def structure_constants(n):
    """All nonzero brackets [X,Y} as {(X,Y): {Z: Fraction}}; raises if the span is not closed."""
    names, parity, R = build_basis(n)
    dec = Decomposer(names, R)
    sc = {}
    for X in names:
        for Y in names:
            br = bracket(R[X], R[Y], n, parity[X], parity[Y])
            coef, res = dec.decompose(br)
            if res:
                raise RuntimeError(f"bracket [{X},{Y}] leaves span of basis: {res}")
            if coef:
                sc[(X, Y)] = coef
    return names, parity, R, sc


def word_list(m, n):
    _k, fp, fm, B = m
    w = ["a_1_p"] * fp + ["a_1_m"] * fm
    for j in range(n):
        w += [f"b_{j+1}_p"] * B[2 * j] + [f"b_{j+1}_m"] * B[2 * j + 1]
    return w


def frac_str(c):
    c = Fraction(c)
    return str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"


def _frappat(terms):
    out = ""
    for t in terms:
        c = Fraction(t["coeff"])
        body = " ".join(f"{w.rsplit('_', 1)[0].replace('_', '_')}^{'+' if w.endswith('_p') else '-'}"
                        for w in t["words"])
        mag = abs(c)
        part = (f"{frac_str(mag)} " if mag != 1 or not body else "") + body
        part = part.strip()
        out += (" - " if c < 0 else (" + " if out else "")) + part if out else (("-" if c < 0 else "") + part)
    return out


def build_schema1(n, date=None):
    names, parity, R, sc = structure_constants(n)
    odd = [x for x in names if parity[x]]
    even = [x for x in names if not parity[x]]
    ne, no = 2 * n * n + n + 1, 4 * n
    bl = [f"b_{k}_{s}" for k in range(1, n + 1) for s in "pm"]
    realizations = {}
    for x in names:
        terms = []
        for m, c in sorted(R[x].items(), key=lambda t: (-len(word_list(t[0], n)), word_list(t[0], n))):
            terms.append({"words": word_list(m, n), "coeff": frac_str(c)})
        realizations[x] = {
            "standard_form": terms,
            "frappat_form": _frappat(terms),
            "parity": parity[x],
        }
    idx = {x: i for i, x in enumerate(names)}
    entries = []
    for (X, Y) in sorted(sc, key=lambda t: (idx[t[0]], idx[t[1]])):
        for Z in sorted(sc[(X, Y)], key=lambda z: idx[z]):
            entries.append({"X": X, "Y": Y, "Z": Z, "coeff": frac_str(sc[(X, Y)][Z]), "sign_rule": "graded"})
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})",
            "alternative_notation": {"osp": f"osp(2|{2*n})", "dimension_formula": "osp(2m|2n) with m=1"},
            "dimension_formula": {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"},
            "dimension": {"total": ne + no, "even": ne, "odd": no},
        },
        "oscillator_generators": {
            "fermions": {"m": 1, "count": 2, "labels": ["a_1_p", "a_1_m"], "parity": 1,
                         "description": "Standard fermionic pair a_1^±; CAR {a_1^-, a_1^+} = 1."},
            "bosons": {"count": 2 * n, "n": n, "labels": bl, "parity": 0,
                       "description": "Bosonic oscillators b_k^± with k=1,...,n"},
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "CAR for the standard fermionic pair",
                "relations": {"conjugate_pair": "{a_1^-, a_1^+} = 1",
                              "same_type": "{a_1^±, a_1^±} = 0, i.e. (a_1^±)^2 = 0"}},
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                              "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"}},
            "mixed_commutators": {"boson_fermion": "[b_i^±, a_1^±] = 0"},
        },
        "central_elements": {
            "kappa": {"label": "kappa", "parity": 1, "relation": "kappa^2 = 0",
                      "description": "Odd nilpotent central element of the inhomogeneous extension"},
            "K": {"label": "K", "parity": 0, "value": "1",
                  "description": "Even central identity element; identified with scalar 1, excluded from basis"},
        },
        "basis": {
            "even": even, "odd": odd,
            "ordering_convention": "PBW: kappa < [odd: E_eps1_del{k}_pp,pm,mp,mm] < [even: H, E_2del_p, E_del_del_pp, "
                                   "E_2del_m, E_del_del_mm, E_del_del_pm, E_del_del_mp]  (K = 1 excluded)",
        },
        "parity": {x: parity[x] for x in names},
        "generator_realization": {
            "description": "Standard form (normal-ordered, Weyl-symmetrized)",
            "ordering": "a_1_p, a_1_m, " + ", ".join(bl),
            "realizations": realizations,
        },
        "structure_constants": entries,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": date or datetime.date.today().isoformat(),
            "references": ["Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                           "Bakalov and Sullivan (2017)"],
        },
    }


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for n in (1, 2, 3):
        d = build_schema1(n)
        path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
        with open(path, "w") as f:
            json.dump(d, f, indent=1, ensure_ascii=False)
        print(f"n={n}: {path}: even={d['algebra']['dimension']['even']} odd={d['algebra']['dimension']['odd']} "
              f"nonzero brackets entries={len(d['structure_constants'])}")


if __name__ == "__main__":
    main()
