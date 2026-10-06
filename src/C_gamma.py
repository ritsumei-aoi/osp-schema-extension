"""Schema 2 (gamma / inhomogeneous deformation) builder for C(n+1).

The deformation is defined by the modified boson-fermion relations

    a_1^sigma · b_j^s - b_j^s · a_1^sigma = gb_{sigma, j, s} · kappa.

Since kappa is odd central with kappa^2 = 0 we only need first-order gb terms:
a single (b_j^s, a_1^sigma) pivot swap during normalization emits a kappa
piece proportional to -gb_{sigma, j, s} times the word with the pair removed.
Further swaps on a kappa-branch would give kappa^2 = 0 and are discarded.
"""

from __future__ import annotations

import json
import os
from datetime import date
from fractions import Fraction
from typing import Dict, List, Tuple

import sympy as sp

from src.C_generators import build_basis, serialize_poly
from src.C_oscillator import Poly, normalize_word, osc_index, parity_sym

PolyS = Dict[Tuple[str, ...], sp.Expr]


def gb_sym(sigma: str, j: int, s: str) -> sp.Symbol:
    return sp.Symbol(f"gb_a1{sigma}_b{j}{s}")


def _add_s(a: PolyS, b: PolyS, c: sp.Expr = sp.Integer(1)) -> PolyS:
    out = dict(a)
    for w, v in b.items():
        nv = sp.expand(out.get(w, sp.Integer(0)) + c * v)
        if nv == 0:
            out.pop(w, None)
        else:
            out[w] = nv
    return out


def _frac_to_sympy(p: Poly) -> PolyS:
    return {w: sp.Rational(c.numerator, c.denominator) for w, c in p.items()}


def normalize_deformed(word: Tuple[str, ...]) -> Tuple[PolyS, PolyS]:
    """Return (body, kappa_part) in sympy coefficients.

    body matches the undeformed normal form; kappa_part collects first-order
    gb corrections.
    """
    body_frac = normalize_word(word)
    body: PolyS = _frac_to_sympy(body_frac)
    kappa_part: PolyS = {}

    # Recursive κ branch extraction.
    stack: List[Tuple[sp.Expr, List[str], bool]] = [(sp.Integer(1), list(word), False)]
    while stack:
        c, w, has_k = stack.pop()
        if c == 0:
            continue
        if any(w[i] == w[i + 1] and parity_sym(w[i]) == 1 for i in range(len(w) - 1)):
            continue
        pivot = None
        for i in range(len(w) - 1):
            if osc_index(w[i]) > osc_index(w[i + 1]):
                pivot = i
                break
        if pivot is None:
            if has_k:
                key = tuple(w)
                nv = sp.expand(kappa_part.get(key, sp.Integer(0)) + c)
                if nv == 0:
                    kappa_part.pop(key, None)
                else:
                    kappa_part[key] = nv
            continue
        s, t = w[pivot], w[pivot + 1]
        ps, pt = parity_sym(s), parity_sym(t)
        if ps == 1 and pt == 1:
            sign = sp.Integer(-1)
            anti = sp.Integer(1) if {s, t} == {"a_1_p", "a_1_m"} else sp.Integer(0)
            stack.append((sign * c, w[:pivot] + [t, s] + w[pivot + 2:], has_k))
            if anti != 0:
                stack.append((c * anti, w[:pivot] + w[pivot + 2:], has_k))
        elif ps == 0 and pt == 0:
            sign = sp.Integer(1)
            anti = sp.Integer(0)
            if s[0] == "b" and t[0] == "b":
                ks = int(s.split("_")[1])
                kt = int(t.split("_")[1])
                if ks == kt and s[-1] == "m" and t[-1] == "p":
                    anti = sp.Integer(1)
            stack.append((sign * c, w[:pivot] + [t, s] + w[pivot + 2:], has_k))
            if anti != 0:
                stack.append((c * anti, w[:pivot] + w[pivot + 2:], has_k))
        else:
            sign = sp.Integer(1)
            delta = sp.Integer(0)
            if ps == 0 and pt == 1 and s[0] == "b":
                sigma = t[-1]
                j = int(s.split("_")[1])
                b_sign = s[-1]
                delta = -gb_sym(sigma, j, b_sign)
            stack.append((sign * c, w[:pivot] + [t, s] + w[pivot + 2:], has_k))
            if delta != 0 and not has_k:
                stack.append((c * delta, w[:pivot] + w[pivot + 2:], True))
    return body, kappa_part


def mul_deformed(X_body: PolyS, X_kap: PolyS, Y_body: PolyS, Y_kap: PolyS):
    """Multiply (X_body + kappa * X_kap)(Y_body + kappa * Y_kap)."""
    out_body: PolyS = {}
    out_kap: PolyS = {}

    def accum(target: PolyS, w: Tuple[str, ...], v: sp.Expr):
        nv = sp.expand(target.get(w, sp.Integer(0)) + v)
        if nv == 0:
            target.pop(w, None)
        else:
            target[w] = nv

    for wa, va in X_body.items():
        for wb, vb in Y_body.items():
            body_nf, kap_nf = normalize_deformed(wa + wb)
            for ww, vv in body_nf.items():
                accum(out_body, ww, va * vb * vv)
            for ww, vv in kap_nf.items():
                accum(out_kap, ww, va * vb * vv)
    # cross terms: X_body * (kappa Y_kap); kappa stays odd central
    # X_body(a) * kappa Y_kap(d) = (-1)^{p(a)} kappa (a d) — but a d normalization
    # doesn't propagate kappa further since κ² = 0. For κ coefficient tracking
    # we only need the body of a*d.
    for wa, va in X_body.items():
        parity_a = sum(parity_sym(s) for s in wa) % 2
        sign = sp.Integer(1 if parity_a == 0 else -1)
        for wd, vd in Y_kap.items():
            body_nf = _frac_to_sympy(normalize_word(wa + wd))
            for ww, vv in body_nf.items():
                accum(out_kap, ww, sign * va * vd * vv)
    for wb, vb in X_kap.items():
        for wc, vc in Y_body.items():
            body_nf = _frac_to_sympy(normalize_word(wb + wc))
            for ww, vv in body_nf.items():
                accum(out_kap, ww, vb * vc * vv)
    # kappa * kappa = 0 drops
    return out_body, out_kap


def deformed_bracket(X_body: PolyS, Y_body: PolyS, pX: int, pY: int):
    xy_b, xy_k = mul_deformed(X_body, {}, Y_body, {})
    yx_b, yx_k = mul_deformed(Y_body, {}, X_body, {})
    sign = sp.Integer(1 if (pX * pY) % 2 == 0 else -1)
    body = _add_s(xy_b, yx_b, -sign)
    kap = _add_s(xy_k, yx_k, -sign)
    return body, kap


def project_sympy(P: PolyS, n: int) -> Dict[str, sp.Expr]:
    """Sympy-coefficient variant of src.C_generators.project."""
    P = dict(P)
    coeffs: Dict[str, sp.Expr] = {}

    def take(w):
        v = P.pop(w, sp.Integer(0))
        return sp.expand(v)

    for k in range(1, n + 1):
        for word, label in [
            (("a_1_p", f"b_{k}_p"), f"E_eps1_del{k}_pp"),
            (("a_1_p", f"b_{k}_m"), f"E_eps1_del{k}_pm"),
            (("a_1_m", f"b_{k}_p"), f"E_eps1_del{k}_mp"),
            (("a_1_m", f"b_{k}_m"), f"E_eps1_del{k}_mm"),
        ]:
            v = take(word)
            if v != 0:
                coeffs[label] = v

    v_a = take(("a_1_p", "a_1_m"))
    if v_a != 0:
        coeffs["H_1"] = v_a
        w = ("b_1_p", "b_1_m")
        P[w] = sp.expand(P.get(w, sp.Integer(0)) - v_a)
        if P[w] == 0:
            P.pop(w, None)

    for k in range(1, n + 1):
        for suff, lbl in [("p", f"E_2del{k}_p"), ("m", f"E_2del{k}_m")]:
            w = (f"b_{k}_{suff}", f"b_{k}_{suff}")
            v = take(w)
            if v != 0:
                coeffs[lbl] = v
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for w, lbl in [
                ((f"b_{i}_p", f"b_{j}_p"), f"E_del{i}_del{j}_pp"),
                ((f"b_{i}_m", f"b_{j}_m"), f"E_del{i}_del{j}_mm"),
                ((f"b_{i}_p", f"b_{j}_m"), f"E_del{i}_del{j}_pm"),
                ((f"b_{i}_m", f"b_{j}_p"), f"E_del{i}_del{j}_mp"),
            ]:
                v = take(w)
                if v != 0:
                    coeffs[lbl] = v

    v_bb = [take((f"b_{k}_p", f"b_{k}_m")) for k in range(1, n + 1)]
    v_const = take(())

    c: Dict[int, sp.Expr] = {}
    if n == 1:
        c[2] = -2 * v_const
    else:
        c[n + 1] = -2 * v_const
        c[n] = -v_bb[n - 1] - c[n + 1]
        for k in range(n - 1, 1, -1):
            c[k] = c[k + 1] - v_bb[k - 1]
    for k in range(2, n + 2):
        if sp.simplify(c[k]) != 0:
            cur = coeffs.get(f"H_{k}", sp.Integer(0))
            coeffs[f"H_{k}"] = sp.expand(cur + c[k])
            if coeffs[f"H_{k}"] == 0:
                coeffs.pop(f"H_{k}", None)

    return coeffs


def build_gamma(n: int):
    even, odd, reals_frac, pars = build_basis(n)
    reals: Dict[str, PolyS] = {k: _frac_to_sympy(v) for k, v in reals_frac.items()}
    labels = even + odd
    gamma_entries = []
    for i, X in enumerate(labels):
        for Y in labels[i:]:
            body, kap = deformed_bracket(reals[X], reals[Y], pars[X], pars[Y])
            if not kap:
                continue
            coeffs = project_sympy(kap, n)
            for Z, c in coeffs.items():
                if sp.simplify(c) == 0:
                    continue
                gamma_entries.append(
                    {
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coeff": str(c),
                    }
                )
    return gamma_entries, even, odd


def build_gamma_json(n: int) -> dict:
    entries, even, odd = build_gamma(n)
    gb_labels = []
    for sigma in ("p", "m"):
        for j in range(1, n + 1):
            for s in ("p", "m"):
                gb_labels.append(f"gb_a1{sigma}_b{j}{s}")
    return {
        "schema_version": "5.0",
        "schema_layer": 2,
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
        },
        "gb_parameters": {
            "shape": f"2 x {2 * n}",
            "count": 4 * n,
            "parity": 1,
            "labels": gb_labels,
            "description": "First-order inhomogeneous deformation parameters",
        },
        "gamma_coefficients": entries,
        "basis": {"even": even, "odd": odd},
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": str(date.today()),
        },
    }


def main():
    out_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
    )
    os.makedirs(out_dir, exist_ok=True)
    for n in (1, 2, 3):
        obj = build_gamma_json(n)
        path = os.path.join(out_dir, f"C_{n}_gamma.json")
        with open(path, "w") as f:
            json.dump(obj, f, indent=2)
        print(f"wrote {path} ({len(obj['gamma_coefficients'])} γ entries)")


if __name__ == "__main__":
    main()
