#!/usr/bin/env python3
"""check_nonK_coboundary.py — Does the non-K part of gamma lie in im(delta)?

Usage:
    python3 scripts/check_nonK_coboundary.py <WORKSPACE_DIR> <n>

Written for the data format of thm01-R-luna-G:
  - data/C_{n}_evaluated.json: "evaluated_structure_constants" entries
    {X, Y, Z, coeff, kappa_order}; kappa_order 1 terms are gamma.
  - data/C_{n}_coboundary.json: "coboundary_definition.coboundary_coefficients"
    entries {X, Y, Z, coefficients: [{parameter, coeff}]} for a general odd f.
Also reads the format of thm01-R-luna-r2-G:
  - evaluated: "structure_constants" entries {X, Y, Z, base_coeff, kappa_coeff}.
  - coboundary: "coboundary.coboundary_coefficients" entries
    {X, Y, Z, parameter, coeff} (one record per parameter).
And the format of thm01-R-luna-r3-G:
  - evaluated: "evaluated_structure.structure_constants" {X, Y, Z, base_coeff, kappa_coeff}.
  - coboundary: "coboundary.coefficients" {X, Y, Z, coeff} where coeff is a
    linear expression in the phi parameters (parsed with sympy).
Other runs may use other formats; adapt the two readers below.

It drops the gamma terms with target K (the central identity), forms the
coboundary matrix D over the odd-map parameters, and compares
rank(D) with rank([D | gamma_nonK]) in exact rational arithmetic (sympy).
Equal ranks mean the non-K part of gamma is a coboundary for the evaluated
gb assignment.
"""
import json
import sys
from fractions import Fraction as F

import sympy as sp

ws, n = sys.argv[1], int(sys.argv[2])
ev = json.load(open(f"{ws}/data/C_{n}_evaluated.json"))
cb = json.load(open(f"{ws}/data/C_{n}_coboundary.json"))

def gamma_terms(ev):
    if "evaluated_structure_constants" in ev:          # luna-G format
        for e in ev["evaluated_structure_constants"]:
            if e["kappa_order"] == 1:
                yield e["X"], e["Y"], e["Z"], F(e["coeff"])
    else:                                              # luna-r2-G / r3-G format
        sc = ev["structure_constants"] if "structure_constants" in ev else ev["evaluated_structure"]["structure_constants"]
        for e in sc:
            yield e["X"], e["Y"], e["Z"], F(e["kappa_coeff"])


def coboundary_terms(cb):
    if "coboundary_definition" in cb:                  # luna-G format
        for e in cb["coboundary_definition"]["coboundary_coefficients"]:
            for c in e["coefficients"]:
                yield e["X"], e["Y"], e["Z"], c["parameter"], F(c["coeff"])
    elif "coboundary_coefficients" in cb["coboundary"]:  # luna-r2-G format
        for e in cb["coboundary"]["coboundary_coefficients"]:
            yield e["X"], e["Y"], e["Z"], e["parameter"], F(e["coeff"])
    else:                                              # luna-r3-G format
        for e in cb["coboundary"]["coefficients"]:
            expr = sp.sympify(e["coeff"])
            for sym, c in expr.as_coefficients_dict().items():
                if sym == 1:
                    raise ValueError(f"constant term in coboundary coefficient: {e}")
                yield e["X"], e["Y"], e["Z"], str(sym), F(str(sp.Rational(c)))


g, gK = {}, {}
for X, Y, Z, c in gamma_terms(ev):
    if c == 0:
        continue
    tgt = gK if Z == "K" else g
    tgt[(X, Y, Z)] = tgt.get((X, Y, Z), 0) + c

if "odd_linear_map" in cb and "coefficients" in cb["odd_linear_map"]:
    params = sorted({c["parameter"] for v in cb["odd_linear_map"]["coefficients"].values() for c in v})
elif "odd_linear_map" in cb:
    params = sorted(e["coefficient"] for e in cb["odd_linear_map"]["entries"])
else:
    params = sorted(p["label"] for p in cb["linear_map"]["parameters"])
pi = {p: i for i, p in enumerate(params)}
D = {}
for X, Y, Z, par, c in coboundary_terms(cb):
    row = D.setdefault((X, Y, Z), {})
    row[pi[par]] = row.get(pi[par], 0) + c

keys = sorted(set(D) | set(g))
A = sp.Matrix([[D.get(k, {}).get(j, 0) for j in range(len(params))] for k in keys])
b = sp.Matrix([g.get(k, 0) for k in keys])
rA, rAb = A.rank(), A.row_join(b).rank()
print(f"n={n} assignment={ev.get('gb_assignment', {}).get('profile')} unknowns={len(params)} "
      f"equations={len(keys)} nonK_terms={len(g)} K_terms={len(gK)} "
      f"rank(D)={rA} rank([D|g])={rAb} nonK_is_coboundary={rA == rAb}")
