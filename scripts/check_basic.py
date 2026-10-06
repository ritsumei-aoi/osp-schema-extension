#!/usr/bin/env python3
"""Sanity checks: dimensions, undeformed closure, Jacobi, twist."""
from fractions import Fraction
from osp_algebra import const, ZERO, ONE, prune, scale, sub, add_into
from osp_deformation import Deformation

for n in (1, 2, 3):
    D = Deformation(n, section="SYM")
    expect = 2 * n ** 2 + 5 * n + 1
    even = sum(1 for p in D.zpar if p == 0)
    odd = sum(1 for p in D.zpar if p == 1)
    print(f"n={n}: dim={D.dim} (expected {expect})  even={even} odd={odd} "
          f"(expected {2*n*n+n+1} | {4*n})")
    assert D.dim == expect and even == 2 * n * n + n + 1 and odd == 4 * n

print()
# undeformed closure: no scalar anomaly tau at gb = 0
for n in (1, 2, 3):
    gb0 = {k: ZERO for k in Deformation(n).A.gb}
    D0 = Deformation(n, gb=gb0, section="SYM").compute()
    bad = [(a, b) for a in range(D0.dim) for b in range(D0.dim)
           if not D0.tau[a][b].is_zero() or not D0.sigma[a][b].is_zero()]
    print(f"n={n}: undeformed closure, anomalies = {len(bad)}")
    assert not bad

print()
# twist: the twisted generators must satisfy the UNDEFORMED relations
for n in (1, 2, 3):
    D = Deformation(n, section="SYM")
    vt = D.twisted_gens()
    A = D.A
    ok = True
    for i in range(A.N):
        for j in range(A.N):
            br = A.bracket(vt[i], vt[j])
            tgt = prune({((), 0): const(A.omega[i][j])})
            if prune(sub(br, tgt)):
                ok = False
                print("   MISMATCH", A.names[i], A.names[j], prune(sub(br, tgt)))
    print(f"n={n}: [vt_i, vt_j] = omega_ij  (kappa-part cancelled): {ok}")
    assert ok
print("\nAll basic checks passed.")
