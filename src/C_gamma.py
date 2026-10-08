"""Inhomogeneous deformation gamma for C(n+1) (Schema 2, Issue I05).

Deformed oscillator relations (docs/math/C_inhomogeneous_definition.md):
    [b_j^s, a_1^sigma] = - gb_{sigma,j,s} * kappa,      sigma, s in {p, m}
All other relations are as in src/C_generators.py. kappa is odd, kappa^2 = 0,
and kappa is placed at the front of every monomial:
    kappa * w = (-1)^{F(w)} * w * kappa,   F(w) = number of fermions in w.

Elements are dicts: (k, monomial) -> sympy expression, with k in {0, 1} the
power of kappa. The bracket is [X,Y] = XY - (-1)^{pX pY} YX, and
    [X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y).
gamma(X,Y) is solved in the Schema 1 basis (linear in gb).
"""

import json
from fractions import Fraction
from pathlib import Path

import sympy

from C_generators import (
    build_basis,
    element_from_terms,
    is_fermion,
    order_key,
    parity_of,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def gb_symbol(sigma, j, s):
    return sympy.Symbol(f"gb_{sigma}_{j}_{s}")


def gb_symbols(n):
    return [gb_symbol(sig, j, s) for sig in ("p", "m") for j in range(1, n + 1) for s in ("p", "m")]


def _fermions(mono):
    return sum(1 for x in mono if is_fermion(x))


def _sigma_of(fermion):
    return fermion[-1]  # a_1_p -> 'p', a_1_m -> 'm'


def _s_of(boson):
    return boson[-1]  # b_k_p -> 'p', b_k_m -> 'm'


def _k_of(boson):
    return int(boson.split("_")[1])


def normal_order_kappa(word):
    """Normal-order a word with deformed boson-fermion contraction.

    Returns dict (k, monomial) -> sympy expression.
    """
    word = tuple(word)
    for i in range(len(word) - 1):
        x, y = word[i], word[i + 1]
        if x == y and is_fermion(x):
            return {}
        if order_key(x) > order_key(y):
            pre, post = word[:i], word[i + 2:]
            out = {}
            # x y = s * y x + (scalar or kappa-term)
            if is_fermion(x) and is_fermion(y):
                s, scalar = -1, 1
                kappa_term = None
            elif not is_fermion(x) and not is_fermion(y):
                s, scalar = 1, (-1 if _k_of(x) == _k_of(y) else 0)
                kappa_term = None
            else:
                # boson x (left), fermion y (right): [b, a] = -gb kappa
                s, scalar = 1, 0
                kappa_term = -gb_symbol(_sigma_of(y), _k_of(x), _s_of(x))
            for key, c in normal_order_kappa(pre + (y, x) + post).items():
                out[key] = out.get(key, 0) + s * c
            if scalar != 0:
                for key, c in normal_order_kappa(pre + post).items():
                    out[key] = out.get(key, 0) + scalar * c
            if kappa_term is not None:
                sign = (-1) ** _fermions(pre)
                for (k, mono), c in normal_order_kappa(pre + post).items():
                    if k == 0:
                        key = (1, mono)
                        out[key] = out.get(key, 0) + sign * kappa_term * c
            return {key: sympy.expand(c) for key, c in out.items() if sympy.expand(c) != 0}
    return {(0, word): sympy.Integer(1)}


def mul_kappa(X, Y):
    """Product of two deformed elements (kappa^2 = 0)."""
    out = {}
    for (kx, mx), cx in X.items():
        for (ky, my), cy in Y.items():
            if kx + ky > 1:
                continue
            sign = (-1) ** _fermions(mx) if ky else 1
            for (k, m), c in normal_order_kappa(mx + my).items():
                if kx + ky + k > 1:
                    continue
                key = (kx + ky + k, m)
                out[key] = out.get(key, 0) + sign * cx * cy * c
    return {key: sympy.expand(c) for key, c in out.items() if sympy.expand(c) != 0}


def bracket_kappa(X, pX, Y, pY):
    """Deformed super-bracket [X, Y] = XY - (-1)^{pX pY} YX."""
    sign = -1 if (pX and pY) else 1
    out = dict(mul_kappa(X, Y))
    for key, c in mul_kappa(Y, X).items():
        out[key] = out.get(key, 0) - sign * c
    return {key: sympy.expand(c) for key, c in out.items() if sympy.expand(c) != 0}


def _lift(element):
    """kappa-free Fraction element -> deformed element with sympy coefficients."""
    return {(0, mono): sympy.Rational(c.numerator, c.denominator) for mono, c in element.items()}


def gamma_of(X, pX, Y, pY, basis_elems):
    """Return dict basis_index -> sympy expr for gamma(X, Y), or {} if kappa-free."""
    br = bracket_kappa(X, pX, Y, pY)
    kappa_part = {mono: c for (k, mono), c in br.items() if k == 1}
    if not kappa_part:
        return {}
    monos = sorted({m for B in basis_elems for (_, m) in B} | set(kappa_part), key=str)
    A = sympy.Matrix([[B.get((0, m), 0) for B in basis_elems] for m in monos])
    b = sympy.Matrix([kappa_part.get(m, 0) for m in monos])
    sol = sympy.linsolve((A, b))
    if not sol:
        raise ValueError("gamma(X,Y) is not in the span of the Schema 1 basis")
    (vals,) = tuple(sol)
    return {i: sympy.expand(v) for i, v in enumerate(vals) if sympy.expand(v) != 0}


def build_gamma(n):
    """Compute all gamma(X,Y) for X <= Y in PBW order.

    gamma may contain the central element K (= scalar 1), which is appended as an
    extra target column. Returns (labels, parities, entries).
    """
    basis = build_basis(n)
    labels = [b["label"] for b in basis]
    parities = [b["parity"] for b in basis]
    elems = [_lift(element_from_terms(b["terms"])) for b in basis]
    K = {(0, ()): sympy.Integer(1)}
    targets = elems + [K]
    target_labels = labels + ["K"]
    entries = []
    for i in range(len(basis)):
        for j in range(i, len(basis)):
            g = gamma_of(elems[i], parities[i], elems[j], parities[j], targets)
            for z, c in sorted(g.items()):
                entries.append({"X": labels[i], "Y": labels[j], "Z": target_labels[z],
                                "coeff": str(c), "sign_rule": "graded"})
    return labels, parities, entries


def build_gamma_schema(n):
    labels, parities, entries = build_gamma(n)
    syms = gb_symbols(n)
    gb_matrix = [[str(gb_symbol(sig, j, s)) for j in range(1, n + 1) for s in ("p", "m")]
                 for sig in ("p", "m")]
    return {
        "schema_version": "5.0",
        "schema": "gamma",
        "algebra_ref": f"C_{n}_structure.json",
        "gb_matrix": {
            "shape": [2, 2 * n],
            "rows": ["a_1_p", "a_1_m"],
            "cols": [f"b_{j}_{s}" for j in range(1, n + 1) for s in ("p", "m")],
            "entries": gb_matrix,
            "parity": 1,
        },
        "inhomogeneous_deformation": {
            "convention": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)",
            "relation": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa",
            "gb_parameters": [str(s) for s in syms],
            "gamma": entries,
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": "2026-10-08",
        },
    }


def write_gamma_schema(n, out_dir=DATA_DIR):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"C_{n}_gamma.json"
    with path.open("w") as f:
        json.dump(build_gamma_schema(n), f, indent=2)
        f.write("\n")
    return path


def consistency_report(n):
    """Checks of gamma against Schema 1 conventions. Returns a dict of counts."""
    from C_generators import bracket as bracket_0
    labels, parities, entries = build_gamma(n)
    parity = dict(zip(labels + ["K"], parities + [0]))
    syms = gb_symbols(n)
    report = {"entries": len(entries), "parity_violations": 0,
              "nonlinear_in_gb": 0, "symmetry_violations": 0, "kappa_free_mismatches": 0}
    for e in entries:
        pX, pY, pZ = parity[e["X"]], parity[e["Y"]], parity[e["Z"]]
        if pZ != (pX + pY + 1) % 2:
            report["parity_violations"] += 1
        expr = sympy.sympify(e["coeff"])
        if expr.is_polynomial(*syms) is False or sympy.Poly(expr, *syms).total_degree() != 1:
            report["nonlinear_in_gb"] += 1
    # graded symmetry: gamma(Y,X) = -(-1)^{pX pY} gamma(X,Y) for X < Y
    basis = build_basis(n)
    elems = {b["label"]: _lift(element_from_terms(b["terms"])) for b in basis}
    pars = {b["label"]: b["parity"] for b in basis}
    stored = {}
    for e in entries:
        stored.setdefault((e["X"], e["Y"]), {})[e["Z"]] = sympy.sympify(e["coeff"])
    K = {(0, ()): sympy.Integer(1)}
    targets = [elems[l] for l in labels] + [K]
    target_labels = labels + ["K"]
    for X in labels:
        for Y in labels:
            if labels.index(X) >= labels.index(Y):
                continue
            g_yx = gamma_of(elems[Y], pars[Y], elems[X], pars[X], targets)
            g_yx = {target_labels[z]: c for z, c in g_yx.items()}
            s = -1 if (pars[X] and pars[Y]) else 1
            expected = {z: -s * c for z, c in stored.get((X, Y), {}).items()}
            for z in set(expected) | set(g_yx):
                if sympy.expand(expected.get(z, 0) - g_yx.get(z, 0)) != 0:
                    report["symmetry_violations"] += 1
    # kappa-free part of the deformed bracket must equal Schema 1 brackets
    for X in labels:
        for Y in labels:
            br = bracket_kappa(elems[X], pars[X], elems[Y], pars[Y])
            zero_part = {m: c for (k, m), c in br.items() if k == 0}
            ref = bracket_0(
                {m: Fraction(int(c.p), int(c.q)) for (k, m), c in elems[X].items()}, pars[X],
                {m: Fraction(int(c.p), int(c.q)) for (k, m), c in elems[Y].items()}, pars[Y])
            for m in set(zero_part) | set(ref):
                diff = sympy.expand(zero_part.get(m, 0)) - sympy.Rational(
                    ref.get(m, Fraction(0)).numerator, ref.get(m, Fraction(0)).denominator)
                if diff != 0:
                    report["kappa_free_mismatches"] += 1
                    break
    return report


if __name__ == "__main__":
    for rank in (1, 2, 3):
        print(write_gamma_schema(rank))
        print("consistency", rank, consistency_report(rank))
