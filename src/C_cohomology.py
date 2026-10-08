"""Supplementary (Issue I08): dimension of the odd second cohomology H^2(g, g~)_odd for C(n+1).

Odd 2-cochains c: g x g -> g~ (p(c(X,Y)) = p(X)+p(Y)+1) with graded antisymmetry are parameterized by
components c_{XY}^Z with index(X) <= index(Y) (even X = Y excluded).  The cocycle condition is the
kappa^1 part of the super Jacobi identity of g~ (+) kappa g~ deformed by c; it is linear in c, so the
cocycle space Z^2 is the kernel of the matrix obtained by evaluating the Jacobiators at unit cochains.
B^2 = image of delta on odd 1-cochains (rank computed in C_triviality).  H^2 = Z^2 / B^2.

Usage: python src/C_cohomology.py 1 2        (n = 3 has ~10^4 unknowns; feasible but slow, not run by default)
"""
from __future__ import annotations

import itertools
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import C_gamma as CG  # noqa: E402
import C_generators as G  # noqa: E402
import verify_C_structure as V  # noqa: E402
from C_triviality import EchelonReducer, TrivialitySystem  # noqa: E402


def unit_cochain_entries(n: int):
    s1 = json.load(open(G.structure_path(n)))
    basis = s1["basis"]["odd"] + s1["basis"]["even"]
    par = dict(s1["parity"])
    par["K"] = 0
    idx = {g: i for i, g in enumerate(basis)}
    units = []
    for X in basis:
        for Y in basis:
            if idx[X] > idx[Y]:
                continue
            if X == Y and par[X] == 0:
                continue
            for Z in basis + ["K"]:
                if par[Z] == (par[X] + par[Y] + 1) % 2:
                    units.append((X, Y, Z))
    return basis, par, units, s1


def cocycle_rank(n: int):
    basis, par, units, s1 = unit_cochain_entries(n)
    g_triples = list(itertools.combinations_with_replacement(basis, 3))
    rows = {}  # (triple, W) -> {unit index: coeff}
    for u, (X, Y, Z) in enumerate(units):
        sign = -1 if (par[X] and par[Y]) else 1
        entries = [{"X": X, "Y": Y, "Z": Z, "linear_form": {"t": "1"}}]
        if (X, Y) != (Y, X):
            entries.append({"X": Y, "Y": X, "Z": Z, "linear_form": {"t": str(-sign)}})
        fake = {"inhomogeneous_deformation": {"gamma": entries}}
        Lb, Lp, Lt = CG.extended_algebra(n, {"t": Fraction(1)}, s1, fake)
        for T in g_triples:
            j = V.jacobiator(Lt, Lp, *T)
            for W, c in j.items():
                rows.setdefault((T, W), {})[u] = c
    red = EchelonReducer(len(units))
    for r in rows.values():
        red.add(r)
    return len(units), red.rank


def main(ns):
    for n in ns:
        n_unknowns, rank_J = cocycle_rank(n)
        z2 = n_unknowns - rank_J
        b2 = TrivialitySystem(n, "K").solvability_conditions()[0]
        print(f"n={n}: odd 2-cochains={n_unknowns}, rank(cocycle map)={rank_J}, dim Z^2_odd={z2}, "
              f"dim B^2_odd={b2}, dim H^2(g, g~)_odd={z2 - b2}")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [1, 2])
