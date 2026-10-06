#!/usr/bin/env python3
"""The kernel of delta on odd 1-cochains = inner odd derivations ad(u), u in g_1.

This identifies the rank deficiency 4n found in analyze_triviality.py step [8]
with dim g_1, i.e. with the vanishing of H^1(g; g) for the simple Lie
superalgebra g = C(n+1).
"""
from fractions import Fraction
import numpy as np

from osp_algebra import ZERO
from osp_deformation import Deformation, delta_f

for n in (1, 2, 3):
    gb0 = {k: ZERO for k in Deformation(n).A.gb}
    D = Deformation(n, gb=gb0, section="SYM").compute()
    D.C0 = D.C
    d = D.dim
    cols = []
    for u in range(d):
        if D.zpar[u] != 1:
            continue
        phi = [[D.C[u][j][i] for j in range(d)] for i in range(d)]
        df = delta_f(D, phi)
        nz = sum(1 for a in range(d) for b in range(d) for c in range(d)
                 if not df[(a, b)][c].is_zero())
        assert nz == 0, (n, u, nz)
        cols.append(np.array([float(phi[i][j].get(None, Fraction(0)))
                              for i in range(d) for j in range(d)]))
    M = np.array(cols)
    rk = np.linalg.matrix_rank(M)
    print(f"n={n}: delta(ad u) = 0 for all {len(cols)} odd u;  "
          f"dim span{{ad u}} = {rk}  (= dim g_1 = {4*n})")
    assert rk == 4 * n == len(cols)
print("kernel identification OK")
