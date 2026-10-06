"""Schema 4 (coboundary) builder for C(n+1).

Defines a general parity-reversing linear map f : g -> g, parameterized by
sympy symbols phi_{i,j}, and computes the coboundary

    (δf)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X, Y])

over all basis pairs. The structure constants from Schema 1 provide the
underlying Lie bracket, which is the undeformed C(n+1) bracket.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import date
from fractions import Fraction
from typing import Dict, List, Tuple

import sympy as sp

from src.C_generators import build_basis, structure_constants


def phi_symbol(i: str, j: str) -> sp.Symbol:
    return sp.Symbol(f"phi__{i}__{j}")


def build_phi(labels, pars):
    """Return (phi, f_map): phi is {(i,j): symbol}, f_map[j] = list of (i, symbol)."""
    phi: Dict[Tuple[str, str], sp.Symbol] = {}
    f_map: Dict[str, List[Tuple[str, sp.Symbol]]] = defaultdict(list)
    for j in labels:
        for i in labels:
            if pars[i] != pars[j]:
                s = phi_symbol(i, j)
                phi[(i, j)] = s
                f_map[j].append((i, s))
    return phi, f_map


def build_bracket_table(n: int):
    """Return dict[(X,Y)] = {Z: Fraction} covering both orders."""
    sc, even, odd, reals, pars, _ = structure_constants(n)
    table: Dict[Tuple[str, str], Dict[str, Fraction]] = defaultdict(dict)
    for e in sc:
        X, Y, Z, c = e["X"], e["Y"], e["Z"], Fraction(e["coeff"])
        table[(X, Y)][Z] = c
        # [Y, X} = -(-1)^{p(X)p(Y)} [X, Y}
        if X != Y:
            sign = 1 if (pars[X] * pars[Y]) % 2 == 0 else -1
            table[(Y, X)][Z] = -sign * c
    return table, even, odd, pars


def apply_f_to_bracket(X: str, Y_expansion: List[Tuple[str, sp.Expr]],
                       bracket_table, pars):
    """Compute [X, sum coeff_i Z_i] as a sympy-coeff dict over basis Z."""
    out: Dict[str, sp.Expr] = {}
    for Zi, cc in Y_expansion:
        br = bracket_table.get((X, Zi), {})
        for W, bc in br.items():
            nv = sp.expand(out.get(W, sp.Integer(0)) + cc * sp.Rational(bc.numerator, bc.denominator))
            if nv == 0:
                out.pop(W, None)
            else:
                out[W] = nv
    return out


def apply_f(expansion: Dict[str, sp.Expr], f_map):
    """Apply f to a sympy-coeff basis combination."""
    out: Dict[str, sp.Expr] = {}
    for Z, c in expansion.items():
        for i, phi_sym in f_map[Z]:
            nv = sp.expand(out.get(i, sp.Integer(0)) + c * phi_sym)
            if nv == 0:
                out.pop(i, None)
            else:
                out[i] = nv
    return out


def coboundary_entries(n: int):
    bracket_table, even, odd, pars = build_bracket_table(n)
    labels = even + odd
    phi, f_map = build_phi(labels, pars)
    entries = []
    for X in labels:
        for Y in labels:
            pX, pY = pars[X], pars[Y]
            # f(Y) and f(X) as sympy expansions
            fY = [(i, s) for i, s in f_map[Y]]
            fX = [(i, s) for i, s in f_map[X]]
            # [X, f(Y)]
            t1 = apply_f_to_bracket(X, fY, bracket_table, pars)
            # [Y, f(X)]
            t2 = apply_f_to_bracket(Y, fX, bracket_table, pars)
            # f([X,Y])
            br_xy = bracket_table.get((X, Y), {})
            xy_sympy = {Z: sp.Rational(c.numerator, c.denominator) for Z, c in br_xy.items()}
            t3 = apply_f(xy_sympy, f_map)
            # Combine with signs
            sign1 = sp.Integer(1 if pX % 2 == 0 else -1)
            sign2 = sp.Integer(1 if ((pX + 1) * pY) % 2 == 0 else -1)
            combined: Dict[str, sp.Expr] = {}
            for Z, c in t1.items():
                combined[Z] = combined.get(Z, sp.Integer(0)) + sign1 * c
            for Z, c in t2.items():
                combined[Z] = combined.get(Z, sp.Integer(0)) - sign2 * c
            for Z, c in t3.items():
                combined[Z] = combined.get(Z, sp.Integer(0)) - c
            for Z, c in combined.items():
                ce = sp.expand(c)
                if ce == 0:
                    continue
                entries.append({"X": X, "Y": Y, "Z": Z, "coeff": str(ce)})
    return entries, even, odd, phi


def build_coboundary_json(n: int) -> dict:
    entries, even, odd, phi = coboundary_entries(n)
    phi_labels = sorted(str(s) for s in phi.values())
    return {
        "schema_version": "5.0",
        "schema_layer": 4,
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
        },
        "linear_map_f": {
            "description": "Odd linear map f: g -> g, parity-reversing, "
                           "parameterized by symbols phi__i__j for each "
                           "parity-opposite (target, source) pair.",
            "parity_constraint": "p(f(X)) = p(X) + 1 (mod 2)",
            "phi_symbols": phi_labels,
            "phi_count": len(phi_labels),
        },
        "delta_f_coefficients": entries,
        "basis": {"even": even, "odd": odd},
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": str(date.today()),
        },
    }


def main():
    out_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
    )
    os.makedirs(out_dir, exist_ok=True)
    for n in (1, 2, 3):
        obj = build_coboundary_json(n)
        path = os.path.join(out_dir, f"C_{n}_coboundary.json")
        with open(path, "w") as f:
            json.dump(obj, f, indent=2)
        print(
            f"wrote {path} ({obj['linear_map_f']['phi_count']} phi, "
            f"{len(obj['delta_f_coefficients'])} entries)"
        )


if __name__ == "__main__":
    main()
