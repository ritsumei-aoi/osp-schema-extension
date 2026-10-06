#!/usr/bin/env python3
"""
The scalar (non-adjoint) term and the "up to scalar" clause.
===========================================================

With the NAIVE section Z^0_{ij} = v_i v_j - 1/2 omega_ij the bracket of two
elements of g acquires, besides the adjoint-valued kappa-term gamma, an extra
term  sigma(X,Y) . kappa  with sigma(X,Y) a SCALAR.  We show:

  (a)  sigma(X,Y) = phi([X,Y])  for the odd linear functional phi: g -> C
       supported on g_1 with  phi(b_j^s o a^sigma) = +1/2 gb[sigma,j,s] ,
       i.e. sigma = -delta(phi) is a coboundary of an odd SCALAR 1-cochain;

  (b)  phi is uniquely determined by gb (it does not depend on which
       trivialising f one picks), so phi = 0 <=> gb = 0;

  (c)  consequently, in the NAIVE section the pair (gamma, sigma) is a
       coboundary of an f with values in g (+) C, but of NO f with values in
       g alone, unless gb = 0.  Passing to the canonical super-symmetrised
       section SYM absorbs phi exactly and makes sigma vanish identically.

Run:  python3 analyze_scalar_obstruction.py [NMAX]
"""
from fractions import Fraction
import json
import sys

from sympy import Matrix, Rational, zeros

from osp_algebra import ZERO, ONE, const, sym, Lin
from osp_deformation import Deformation

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 3
OUT = {}

for n in range(1, NMAX + 1):
    print("=" * 70)
    print(f"  n = {n}   g = C({n+1}) = osp(2|{2*n})")
    print("=" * 70)
    tmpl = Deformation(n)
    gb_keys = sorted(tmpl.A.gb.keys(), key=lambda t: (t[1], t[0], t[2]))
    rec = {"phi": {}, "sigma_is_coboundary": True, "sigma_SYM_zero": None}

    # undeformed structure constants
    D0 = Deformation(n, gb={k: ZERO for k in tmpl.A.gb}, section="SYM").compute()
    C0 = D0.C
    d = D0.dim

    # SYM section: sigma identically zero?
    Dsym = Deformation(n, section="SYM").compute()
    sym_zero = all(Dsym.sigma[a][b].is_zero() for a in range(d) for b in range(d))
    rec["sigma_SYM_zero"] = sym_zero
    print(f"  SYM section: sigma == 0 identically : {sym_zero}")

    # NAIVE section, one gb parameter switched on at a time
    for key in gb_keys:
        gbv = {k: (ONE if k == key else ZERO) for k in tmpl.A.gb}
        D = Deformation(n, gb=gbv, section="NAIVE").compute()
        # solve  sigma_ab = sum_c C0_ab^c phi_c   for phi
        rows, rhs = [], []
        for a in range(d):
            for b in range(d):
                rows.append([C0[a][b][c].get(None, Fraction(0)) for c in range(d)])
                rhs.append(D.sigma[a][b].get(None, Fraction(0)))
        M = Matrix([[Rational(x) for x in r] for r in rows])
        v = Matrix([Rational(x) for x in rhs])
        aug = M.row_join(v)
        if M.rank() != aug.rank():
            rec["sigma_is_coboundary"] = False
            print(f"  {key}: sigma is NOT of the form phi([X,Y]) -- unexpected")
            continue
        phi = M.solve_least_squares(v)
        assert (M * phi - v).norm() == 0
        support = {D.labels[c]: str(phi[c]) for c in range(d) if phi[c] != 0}
        allodd = all(D.zpar[c] == 1 for c in range(d) if phi[c] != 0)
        rec["phi"][f"gb[{key[0]},{key[1]},{key[2]}]"] = {
            "support": support, "supported_on_g_odd": allodd}
        print(f"  gb[{key[0]},{key[1]},{key[2]}] -> phi = {support}"
              f"   (supported on g_1: {allodd})")

    OUT[f"n={n}"] = rec
    print()

with open("../artifacts/scalar_obstruction.json", "w") as fh:
    json.dump(OUT, fh, indent=2)
print("written to artifacts/scalar_obstruction.json")
