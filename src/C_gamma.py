"""Inhomogeneous deformation gamma for C(n+1) (Schema 2, I05).

The deformed oscillator relation (docs/math/C_inhomogeneous_definition.md) is

    [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa,

with kappa odd, central and kappa^2 = 0. All other relations are undeformed.
Brackets of basis elements are then

    [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y),

where [X, Y]_0 is the Schema 1 bracket (I03) and gamma(X, Y) is linear in gb.
Both parts come from one computation: kappa is a formal symbol with kappa^2 = 0,
so its kappa^0 coefficient is the undeformed bracket and its kappa^1
coefficient is gamma.

Convention: kappa is central (it commutes with every oscillator), as the
schema states. This removes any sign from moving kappa past odd oscillators.
"""

import json
from pathlib import Path

import sympy

from C_generators import Oscillators, basis


KAPPA = sympy.Symbol("kappa")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def gb_symbol(fermion, boson):
    """gb parameter for the pair (a_1^sigma, b_j^s), e.g. gb_a_1_p__b_1_m."""
    return sympy.Symbol(f"gb_{fermion}__{boson}")


def gb_labels(n):
    """Rows: fermion labels. Columns: boson labels, in the order used by the schema."""
    rows = ["a_1_p", "a_1_m"]
    cols = [f"b_{j}_{s}" for j in range(1, n + 1) for s in ("p", "m")]
    return rows, cols


def rat(q):
    return sympy.Rational(q.numerator, q.denominator)


class DeformedOscillators(Oscillators):
    """Oscillators with the deformed boson-fermion commutator."""

    def contraction(self, x, y):
        x_f, y_f = self.is_fermion(x), self.is_fermion(y)
        if x_f and y_f:
            # CAR is undeformed: {a_1_m, a_1_p} = 1.
            return sympy.Integer(1) if {x, y} == {"a_1_p", "a_1_m"} else sympy.Integer(0)
        if not x_f and not y_f:
            return rat(super().contraction(x, y))
        # Mixed pair: [b, a] = -gb * kappa, so [a, b] = +gb * kappa.
        if x_f:
            return KAPPA * gb_symbol(x, y)
        return -KAPPA * gb_symbol(y, x)


def normal_sympy(osc, word, cache):
    """Normal-order a word; coefficients are sympy expressions."""
    if word in cache:
        return cache[word]
    result = None
    for i in range(len(word) - 1):
        x, y = word[i], word[i + 1]
        if x == y and osc.is_fermion(x):
            result = {}
            break
        if osc.order[x] > osc.order[y]:
            # xy = s * yx + [x, y}, with s = -1 only for two fermions.
            sign = -1 if (osc.is_fermion(x) and osc.is_fermion(y)) else 1
            result = {}
            for u, c in normal_sympy(osc, word[:i] + (y, x) + word[i + 2:], cache).items():
                result[u] = result.get(u, 0) + sign * c
            c0 = osc.contraction(x, y)
            if c0 != 0:
                for u, c in normal_sympy(osc, word[:i] + word[i + 2:], cache).items():
                    result[u] = result.get(u, 0) + c0 * c
            break
    if result is None:
        result = {word: sympy.Integer(1)}
    result = {u: sympy.expand(c) for u, c in result.items()}
    result = {u: c for u, c in result.items() if c != 0}
    cache[word] = result
    return result


def normal_poly(osc, poly, cache):
    out = {}
    for w, c in poly.items():
        for u, d in normal_sympy(osc, w, cache).items():
            out[u] = out.get(u, 0) + c * d
    return {u: sympy.expand(c) for u, c in out.items() if sympy.expand(c) != 0}


def deformed_brackets(n):
    """Brackets [X, Y]_gamma for all ordered pairs, as {word: expr} with kappa^2 = 0."""
    osc = DeformedOscillators(n)
    elems = basis(n)
    labels = [e[0] for e in elems]
    parity = {e[0]: e[1] for e in elems}
    cache = {}
    polys = {
        label: normal_poly(osc, {w: rat(c) for w, c in poly.items()}, cache)
        for label, _, poly in elems
    }

    def mul(A, B):
        p = {}
        for wa, ca in A.items():
            for wb, cb in B.items():
                p[wa + wb] = p.get(wa + wb, 0) + ca * cb
        return normal_poly(osc, p, cache)

    def graded(A, pA, B, pB):
        sign = -1 if (pA * pB) % 2 else 1
        out = dict(mul(A, B))
        for w, c in mul(B, A).items():
            out[w] = out.get(w, 0) - sign * c
        out = {w: sympy.expand(c).subs(KAPPA**2, 0) for w, c in out.items()}
        return {w: c for w, c in out.items() if c != 0}

    brackets = {}
    for X in labels:
        for Y in labels:
            brackets[(X, Y)] = graded(polys[X], parity[X], polys[Y], parity[Y])
    return labels, parity, brackets


def solve_in_basis(labels, polys_basis, expr_by_word):
    """Express {word: expr} in the basis, plus the central scalar K = 1."""
    cols = labels + ["K"]
    polys_all = dict(polys_basis, K={(): sympy.Integer(1)})
    monomials = sorted(
        {m for p in polys_all.values() for m in p} | set(expr_by_word) | {()}
    )
    A = sympy.Matrix([[polys_all[c].get(m, 0) for c in cols] for m in monomials])
    rhs = sympy.Matrix([expr_by_word.get(m, 0) for m in monomials])
    sol, params = A.gauss_jordan_solve(rhs)
    assert not params, "basis is not unique"
    out = {}
    for c, s in zip(cols, sol):
        s = sympy.expand(s)
        if s != 0:
            out[c] = s
    return out


def split_kappa(n):
    """Return (labels, parity, undeformed, gamma) as dicts of basis-coefficient tables.

    undeformed[(X,Y)] = {Z: rational}, the kappa^0 part (should equal Schema 1).
    gamma[(X,Y)]      = {Z: linear form in gb}, the kappa^1 part.
    """
    labels, parity, brackets = deformed_brackets(n)
    osc = Oscillators(n)
    polys_basis = {
        label: {w: rat(c) for w, c in osc.normal(poly).items()} for label, _, poly in basis(n)
    }
    undeformed, gamma = {}, {}
    for (X, Y), expr in brackets.items():
        k0 = {w: sympy.expand(c).coeff(KAPPA, 0) for w, c in expr.items()}
        k1 = {w: sympy.expand(c).coeff(KAPPA, 1) for w, c in expr.items()}
        k0 = {w: c for w, c in k0.items() if c != 0}
        k1 = {w: c for w, c in k1.items() if c != 0}
        if k0:
            undeformed[(X, Y)] = solve_in_basis(labels, polys_basis, k0)
        if k1:
            gamma[(X, Y)] = solve_in_basis(labels, polys_basis, k1)
    return labels, parity, undeformed, gamma


def check_against_schema1(n, undeformed):
    """Compare the kappa^0 table with data/C_{n}_structure.json.

    The file stores each unordered pair once, in PBW order (odd block first).
    We compare exactly those pairs, in that orientation.
    """
    data = json.loads((DATA / f"C_{n}_structure.json").read_text())
    labels = data["basis"]["odd"] + data["basis"]["even"]  # PBW order (I01)
    stored = {}
    for e in data["structure_constants"]:
        stored.setdefault((e["X"], e["Y"]), {})[e["Z"]] = sympy.Rational(e["coeff"])
    problems = []
    for i, X in enumerate(labels):
        for Y in labels[i:]:
            ours = undeformed.get((X, Y), {})
            ref = stored.get((X, Y), {})
            if ours != ref:
                problems.append(((X, Y), ours, ref))
    return problems


def check_gamma_antisymmetry(labels, parity, gamma):
    """gamma(X,Y) = -(-1)^(p(X)p(Y)) gamma(Y,X) for all ordered pairs."""
    bad = []
    for X in labels:
        for Y in labels:
            sign = -1 if (parity[X] * parity[Y]) % 2 else 1
            lhs = gamma.get((X, Y), {})
            rhs = {z: -sign * c for z, c in gamma.get((Y, X), {}).items()}
            if {z: sympy.expand(c) for z, c in lhs.items()} != {
                z: sympy.expand(c) for z, c in rhs.items()
            }:
                bad.append((X, Y))
    return bad


def to_json(n):
    labels, parity, undeformed, gamma = split_kappa(n)
    rows, cols = gb_labels(n)
    problems = check_against_schema1(n, undeformed)
    assert not problems, f"kappa^0 part disagrees with Schema 1: {problems[:3]}"
    anti_bad = check_gamma_antisymmetry(labels, parity, gamma)
    assert not anti_bad, f"gamma not antisymmetric on {anti_bad[:3]}"
    # kappa*K components are expected: a single contraction followed by the
    # undeformed boson commutator leaves kappa times a constant. They are kept.
    k_components = sum(1 for terms in gamma.values() if "K" in terms)
    entries = []
    for i, X in enumerate(labels):
        for Y in labels[i:]:
            for Z, c in gamma.get((X, Y), {}).items():
                entries.append({"X": X, "Y": Y, "Z": Z, "coeff": str(c), "sign_rule": "graded"})
    return {
        "schema_version": "5.0",
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n + 1})"},
        "gb_matrix": {
            "shape": [len(rows), len(cols)],
            "parity": 1,
            "rows": rows,
            "columns": cols,
            "entries": [
                [str(gb_symbol(r, c)) for c in cols] for r in rows
            ],
            "description": "gb_{sigma,j,s}: row = fermion a_1^sigma, column = boson b_j^s",
        },
        "inhomogeneous_deformation": {
            "central_element": "kappa",
            "kappa_parity": 1,
            "deformed_relation": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa",
            "undeformed_relations": "all others (CAR, CCR, and mixed relations as in Schema 1)",
            "gamma_convention": "[X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)",
            "gamma": entries,
        },
        "consistency": {
            "kappa_zero_part_matches_schema1": True,
            "gamma_antisymmetric": True,
            "pairs_with_kappa_K_component": k_components,
            "pairs_checked": len(labels) * (len(labels) + 1) // 2,
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
            ],
        },
    }


def main():
    out_dir = DATA
    for n in (1, 2, 3):
        doc = to_json(n)
        path = out_dir / f"C_{n}_gamma.json"
        path.write_text(json.dumps(doc, indent=2) + "\n")
        print(f"wrote {path.name}: gamma entries={len(doc['inhomogeneous_deformation']['gamma'])}")
    return 0


if __name__ == "__main__":
    main()
