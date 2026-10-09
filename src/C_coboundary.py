"""
Schema 4: Coboundary structure for C(n+1) = osp(2|2n).

Computes coboundary (delta f)(X,Y) for the odd linear map f: g -> g.
Formula: (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X,Y])

f is parameterized by phi_{i,j}: f(Z_j) = sum_i phi_{i,j} * Z_i (with p(Z_i) != p(Z_j)).
"""

from __future__ import annotations
import json
import os
from datetime import date
from fractions import Fraction


def load_s1(n: int) -> dict:
    with open(f"data/C_{n}_structure.json") as f:
        return json.load(f)


def build_sc_dict(s1: dict) -> dict[tuple[str, str], dict[str, Fraction]]:
    sc: dict[tuple[str, str], dict[str, Fraction]] = {}
    for e in s1["structure_constants"]:
        key = (e["X"], e["Y"])
        if key not in sc:
            sc[key] = {}
        z = e["Z"]
        sc[key][z] = sc[key].get(z, Fraction(0)) + Fraction(e["coeff"])
    for key in list(sc.keys()):
        sc[key] = {z: c for z, c in sc[key].items() if c != 0}
        if not sc[key]:
            del sc[key]
    return sc


def phi_label(target_gen: str, source_gen: str) -> str:
    """Parameter: phi_{target,source} meaning f(source) has component target."""
    return f"phi_{target_gen}__{source_gen}"


def bracket(sc_dict: dict, X: str, Y: str) -> dict[str, Fraction]:
    return dict(sc_dict.get((X, Y), {}))


def compute_coboundary(n: int) -> list[dict]:
    """
    Compute (delta f)(X, Y) symbolically for all pairs (X,Y) with X <= Y in basis order.
    Returns list of entries: {X, Y, Z, phi_param, coeff}.
    """
    s1 = load_s1(n)
    parity = s1["parity"]
    basis = s1["basis"]["even"] + s1["basis"]["odd"]
    sc_dict = build_sc_dict(s1)
    gen_order = {g: i for i, g in enumerate(basis)}

    # Odd map f: f(Z_j) = sum_{i: p(i) != p(j)} phi_{i,j} * Z_i
    # Parameterized terms: for each (i, j) with p(i) != p(j), there is a phi_{i,j} parameter.

    # Result: dict {(X, Y, Z, phi_label): Fraction}
    result: dict[tuple[str, str, str, str], Fraction] = {}

    def add(X, Y, Z, phi_lbl, coeff):
        c = Fraction(coeff)
        if c == 0:
            return
        key = (X, Y, Z, phi_lbl)
        result[key] = result.get(key, Fraction(0)) + c

    for X in basis:
        for Y in basis:
            if gen_order[X] > gen_order[Y]:
                continue
            pX = parity[X]
            pY = parity[Y]
            sign1 = (-1) ** pX
            sign2 = (-1) ** ((pX + 1) * pY)

            # f(Y) = sum_{A: p(A) != p(Y)} phi_{A,Y} * A
            # Term 1: (-1)^{p(X)} [X, f(Y)] = sign1 * sum_A phi_{A,Y} * [X, A]
            for A in basis:
                if parity[A] == pY:
                    continue  # f(Y) maps to parity-complement of Y
                phi_lbl = phi_label(A, Y)
                for Z, c in bracket(sc_dict, X, A).items():
                    add(X, Y, Z, phi_lbl, sign1 * c)

            # f(X) = sum_{B: p(B) != p(X)} phi_{B,X} * B
            # Term 2: -(-1)^{(p(X)+1)*p(Y)} [Y, f(X)] = -sign2 * sum_B phi_{B,X} * [Y, B]
            for B in basis:
                if parity[B] == pX:
                    continue
                phi_lbl = phi_label(B, X)
                for Z, c in bracket(sc_dict, Y, B).items():
                    add(X, Y, Z, phi_lbl, -sign2 * c)

            # [X,Y] = sum_W f_{XY}^W * W
            # f([X,Y]) = sum_W f_{XY}^W * f(W)
            #          = sum_W f_{XY}^W * sum_{C: p(C)!=p(W)} phi_{C,W} * C
            # Term 3: -f([X,Y]) = -sum_{W,C} f_{XY}^W * phi_{C,W} * C
            for W, f_coeff in bracket(sc_dict, X, Y).items():
                pW = parity[W]
                for C in basis:
                    if parity[C] == pW:
                        continue
                    phi_lbl = phi_label(C, W)
                    add(X, Y, C, phi_lbl, -f_coeff)

    # Collect into list, generating reverse brackets
    forward_entries = []
    reverse_entries = []

    # Group by (X, Y, Z, phi_lbl)
    for (X, Y, Z, phi_lbl), coeff in result.items():
        if coeff == 0:
            continue
        forward_entries.append({
            "X": X, "Y": Y, "Z": Z,
            "phi_param": phi_lbl,
            "coeff": str(coeff),
            "sign_rule": "graded"
        })

    # Generate reverse entries [Y,X] = -(-1)^{pX*pY} * [X,Y] so delta_f is also symmetric
    # Actually (delta f)(X,Y) = -(-1)^{pX*pY} (delta f)(Y,X) since it's a 2-cochain
    seen = {(e["X"], e["Y"]) for e in forward_entries}
    reverse_map: dict[tuple[str, str, str, str], Fraction] = {}
    for (X, Y, Z, phi_lbl), coeff in result.items():
        if X == Y:
            continue
        if coeff == 0:
            continue
        sign = -(-1) ** (parity[X] * parity[Y])
        rc = sign * coeff
        if rc != 0:
            key = (Y, X, Z, phi_lbl)
            reverse_map[key] = reverse_map.get(key, Fraction(0)) + rc

    for (X, Y, Z, phi_lbl), coeff in reverse_map.items():
        if coeff != 0:
            reverse_entries.append({
                "X": X, "Y": Y, "Z": Z,
                "phi_param": phi_lbl,
                "coeff": str(coeff),
                "sign_rule": "graded"
            })

    return forward_entries + reverse_entries


def build_schema4(n: int) -> dict:
    s1 = load_s1(n)
    parity = s1["parity"]
    basis = s1["basis"]["even"] + s1["basis"]["odd"]

    # Enumerate phi parameters (all parity-reversing pairs)
    phi_params = {}
    for target in basis:
        for source in basis:
            if parity[target] != parity[source]:
                lbl = phi_label(target, source)
                phi_params[lbl] = {
                    "target": target, "source": source,
                    "description": f"f({source}) has component {target}"
                }

    cobound = compute_coboundary(n)

    return {
        "schema_version": "5.0",
        "algebra": s1["algebra"],
        "odd_map_f": {
            "description": "Odd linear map f: g -> g (parity-reversing). f(Z_source) = sum phi_{target,source} * Z_target.",
            "phi_parameters": phi_params,
            "phi_count": len(phi_params)
        },
        "coboundary_formula": "(delta f)(X,Y) = (-1)^{p(X)} [X,f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y,f(X)] - f([X,Y])",
        "coboundary_coefficients": cobound,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": str(date.today()),
            "references": [
                "Frappat, Sciarrino, Sorba (2000)",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Building coboundary n={n}...", flush=True)
        schema = build_schema4(n)
        fname = f"data/C_{n}_coboundary.json"
        with open(fname, "w") as f:
            json.dump(schema, f, indent=2)
        cc = len(schema["coboundary_coefficients"])
        pc = schema["odd_map_f"]["phi_count"]
        print(f"  C_{n}_coboundary.json: {cc} coboundary entries, {pc} phi parameters")


if __name__ == "__main__":
    main()
