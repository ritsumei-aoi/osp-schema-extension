"""
Module to compute the inhomogeneous deformation (gamma structure) for C(n+1) = osp(2|2n).

Implements Option A sign convention from docs/math/C_inhomogeneous_definition.md:
  [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
  [a_1^sigma, b_j^s] = + gb_{sigma, j, s} * kappa
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
from typing import Dict, List, Tuple, Any
import sympy as sp

from src.C_generators import (
    build_c_basis,
    compute_structure_constants,
    order_key,
    normal_order_word,
)


def get_gb_params(n: int) -> List[str]:
    """Return ordered list of 4n deformation parameter labels."""
    params = []
    for sig in ("a1p", "a1m"):
        for j in range(1, n + 1):
            for s in ("p", "m"):
                params.append(f"gb_{sig}_b{j}{s}")
    return params


def osc_parity(osc: str) -> int:
    return 1 if osc.startswith("a_") else 0


def bracket_osc(u: str, v: str) -> Tuple[Fraction, Dict[str, Fraction]]:
    """Compute [u, v} = [u, v]_0 + kappa * [u, v]_1 in the deformed oscillator algebra."""
    pu, pv = osc_parity(u), osc_parity(v)
    c_0 = Fraction(0)
    c_k = defaultdict(Fraction)

    if pu == 0 and pv == 0:
        # Both bosons: [b_j^-, b_k^+] = delta_{jk}
        ux, vx = u.split("_"), v.split("_")
        if ux[1] == vx[1]:
            if ux[2] == "m" and vx[2] == "p":
                c_0 = Fraction(1)
            elif ux[2] == "p" and vx[2] == "m":
                c_0 = Fraction(-1)
    elif pu == 1 and pv == 1:
        # Both fermions: {a_1^-, a_1^+} = 1
        ux, vx = u.split("_"), v.split("_")
        if ux[2] != vx[2]:
            c_0 = Fraction(1)
    else:
        # One boson, one fermion
        # Option A: [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
        #           [a_1^sigma, b_j^s] = + gb_{sigma, j, s} * kappa
        if pu == 0 and pv == 1:
            bx, ax = u.split("_"), v.split("_")
            sig = ax[2]
            j = bx[1]
            s = bx[2]
            gb_name = f"gb_a1{sig}_b{j}{s}"
            c_k[gb_name] += Fraction(-1)
        else:
            ax, bx = u.split("_"), v.split("_")
            sig = ax[2]
            j = bx[1]
            s = bx[2]
            gb_name = f"gb_a1{sig}_b{j}{s}"
            c_k[gb_name] += Fraction(1)

    return c_0, c_k


def superbracket_monomials(
    u: str, v: str, x: str, y: str
) -> Tuple[Dict[Tuple[str, ...], Fraction], Dict[str, Dict[Tuple[str, ...], Fraction]]]:
    """Compute [u v, x y} in U(A) up to first order in kappa."""
    pu, pv = osc_parity(u), osc_parity(v)
    px, py = osc_parity(x), osc_parity(y)
    pxy = (px + py) % 2

    # Derived from graded Leibniz rule in associative superalgebra:
    # [u v, x y} = u [v, x y} + (-1)^{pv p(xy)} [u, x y} v
    # = [v, x} u y + (-1)^{pv px} [v, y} u x + (-1)^{pv pxy} [u, x} y v + (-1)^{pv pxy + pu px} [u, y} x v
    terms = []

    # Term 1: [v, x} u y
    c0, ck = bracket_osc(v, x)
    terms.append((Fraction(1), c0, ck, (u, y)))

    # Term 2: (-1)^{pv px} [v, y} u x
    c0, ck = bracket_osc(v, y)
    s2 = -1 if (pv * px) % 2 == 1 else 1
    terms.append((Fraction(s2), c0, ck, (u, x)))

    # Term 3: (-1)^{pv pxy} [u, x} y v
    c0, ck = bracket_osc(u, x)
    s3 = -1 if (pv * pxy) % 2 == 1 else 1
    terms.append((Fraction(s3), c0, ck, (y, v)))

    # Term 4: (-1)^{pv pxy + pu px} [u, y} x v
    c0, ck = bracket_osc(u, y)
    s4 = -1 if ((pv * pxy + pu * px) % 2 == 1) else 1
    terms.append((Fraction(s4), c0, ck, (x, v)))

    res_0 = defaultdict(Fraction)
    res_k = defaultdict(lambda: defaultdict(Fraction))

    for sign, c0, ck, w in terms:
        if c0 != 0:
            no = normal_order_word(list(w), sign * c0)
            for nw, nc in no.items():
                res_0[nw] += nc
        for gb_name, c_gb in ck.items():
            if c_gb != 0:
                no = normal_order_word(list(w), sign * c_gb)
                for nw, nc in no.items():
                    res_k[gb_name][nw] += nc

    return {w: c for w, c in res_0.items() if c != 0}, {
        gb: {w: c for w, c in wd.items() if c != 0} for gb, wd in res_k.items()
    }


def superbracket_polys(
    poly1: Dict[Tuple[str, ...], Fraction], poly2: Dict[Tuple[str, ...], Fraction]
) -> Tuple[Dict[Tuple[str, ...], Fraction], Dict[str, Dict[Tuple[str, ...], Fraction]]]:
    """Compute bracket of two polynomials in U(A)."""
    tot_0 = defaultdict(Fraction)
    tot_k = defaultdict(lambda: defaultdict(Fraction))
    for w1, c1 in poly1.items():
        if len(w1) == 0:
            continue
        for w2, c2 in poly2.items():
            if len(w2) == 0:
                continue
            u, v = w1
            x, y = w2
            r0, rk = superbracket_monomials(u, v, x, y)
            for w, c in r0.items():
                tot_0[w] += c1 * c2 * c
            for gb_name, wdict in rk.items():
                for w, c in wdict.items():
                    tot_k[gb_name][w] += c1 * c2 * c
    return {w: c for w, c in tot_0.items() if c != 0}, {
        gb: {w: c for w, c in wd.items() if c != 0} for gb, wd in tot_k.items()
    }


def compute_gamma_structure(n: int) -> Dict[str, Any]:
    """Compute Schema 2 JSON data including gamma coefficients."""
    # Load or generate Schema 1 base data
    _, schema1_data = compute_structure_constants(n)

    even_basis = schema1_data["basis"]["even"]
    odd_basis = schema1_data["basis"]["odd"]
    full_basis = even_basis + odd_basis
    extended_basis = full_basis + ["K"]

    _, _, generators = build_c_basis(n)

    # Word list including scalar 1 for K
    all_words = set()
    for g in generators.values():
        all_words.update(g["poly"].keys())
    all_words.add(())
    word_list = sorted(list(all_words))

    # Matrix including K
    M_sp = sp.Matrix([
        [
            generators[name]["poly"].get(w, Fraction(0))
            if name != "K"
            else (Fraction(1) if w == () else Fraction(0))
            for name in extended_basis
        ]
        for w in word_list
    ])

    gb_labels = get_gb_params(n)
    gamma_constants = []

    for i, X in enumerate(full_basis):
        for j, Y in enumerate(full_basis):
            _, rk = superbracket_polys(generators[X]["poly"], generators[Y]["poly"])
            for gb in gb_labels:
                wdict = rk.get(gb, {})
                if not wdict:
                    continue
                vec = sp.Matrix([wdict.get(w, Fraction(0)) for w in word_list])
                sol, _ = M_sp.gauss_jordan_solve(vec)
                for k, Z in enumerate(extended_basis):
                    coeff = sol[k]
                    if coeff != 0:
                        gamma_constants.append({
                            "X": X,
                            "Y": Y,
                            "param": gb,
                            "Z": Z,
                            "coeff": str(coeff),
                        })

    schema2_data = dict(schema1_data)
    schema2_data["inhomogeneous_deformation"] = {
        "description": "Inhomogeneous deformation (gamma structure) of C(n+1) parametrized by gb matrix",
        "parameters": {
            "count": 4 * n,
            "labels": gb_labels,
            "parity": 1,
            "matrix_shape": [2, 2 * n],
        },
        "exchange_relations": {
            "formula": "[b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa",
            "convention": "Option A (Direct Inhomogeneous Commutator)",
        },
        "gamma_constants": gamma_constants,
    }

    return schema2_data


def generate_all_gamma_schemas(output_dir: str = "data") -> None:
    """Generate Schema 2 JSON files for n=1, 2, 3."""
    os.makedirs(output_dir, exist_ok=True)
    for n in (1, 2, 3):
        schema2 = compute_gamma_structure(n)
        filename = os.path.join(output_dir, f"C_{n}_gamma.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(schema2, f, indent=2)
        print(f"Generated {filename} ({len(schema2['inhomogeneous_deformation']['gamma_constants'])} gamma constants)")


if __name__ == "__main__":
    generate_all_gamma_schemas()
