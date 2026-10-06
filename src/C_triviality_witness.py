"""
Concrete obstruction witness for the C(n+1) triviality analysis (Issue I08).

For a given n, finds a *minimal* linear combination w of the comparison equations (indexed by
(X, Y, Z)) such that
    w . (delta f) = 0   identically in the phi parameters   (so no coboundary contributes), while
    w . gamma     != 0   (a nonzero combination of gb parameters),
exhibiting explicitly that the inhomogeneous deformation gamma is NOT a coboundary.

Run:  python3 src/C_triviality_witness.py
"""

from __future__ import annotations
import os
import sys
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import C_triviality as t
import C_coboundary as ccb
import C_gamma as cgm


def witness(n):
    gb_syms = [sp.Symbol(s) for s in cgm.gb_list(n)]
    phi_syms = [sp.Symbol(s) for s in ccb.phi_symbols(ccb.Base(n))]
    gmap = t.gamma_map(n)
    dmap = t.deltaf_map(n)
    keys = sorted(set(gmap) | set(dmap))
    E, P, G = len(keys), len(phi_syms), len(gb_syms)
    M = sp.zeros(E, P)
    B = sp.zeros(E, G)
    pidx = {s: j for j, s in enumerate(phi_syms)}
    gidx = {s: j for j, s in enumerate(gb_syms)}
    for i, k in enumerate(keys):
        de = dmap.get(k, sp.Integer(0))
        ge = sp.expand(gmap.get(k, sp.Integer(0)))
        for s in phi_syms:
            M[i, pidx[s]] = de.coeff(s)
        for s in gb_syms:
            B[i, gidx[s]] = ge.coeff(s)
    best = None
    for w in M.T.nullspace():                 # cokernel of M
        wB = w.T * B
        if any(wB[j] != 0 for j in range(G)):
            supp = [(keys[i], w[i]) for i in range(E) if w[i] != 0]
            if best is None or len(supp) < len(best[0]):
                best = (supp, sp.expand(sum(wB[j] * gb_syms[j] for j in range(G))))
    return best


def main():
    # Only n=1 is shown: the cokernel of M is small enough to enumerate a *minimal* witness.
    # For n=2,3 non-triviality is established by the rank identity rank([M|B]) = rank(M) + 4n
    # in src/C_triviality.py (an analogous single-entry H_2 obstruction exists for every n).
    for n in (1,):
        supp, obstr = witness(n)
        print(f"C({n+1}) minimal obstruction witness ({len(supp)} term(s)):")
        for (X, Y, Z), c in supp:
            print(f"   coeff {c} on equation  [X={X}, Y={Y}] -> {Z}")
        print(f"   => w.(delta f) = 0 (all phi),  w.gamma = {obstr}  (nonzero)\n")


if __name__ == "__main__":
    main()
