#!/usr/bin/env python3
"""
verify_C_structure.py: Verify C(n+1) structure constants satisfy the
Super Jacobi identity and graded anti-symmetry.

Graded anti-symmetry:
  [X, Y] = -(-1)^{p(X)p(Y)} [Y, X]

Super Jacobi identity (graded):
  (-1)^{p(X)p(Z)} [X,[Y,Z]] + (-1)^{p(Y)p(X)} [Y,[Z,X]] + (-1)^{p(Z)p(Y)} [Z,[X,Y]] = 0
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fractions import Fraction
from collections import defaultdict
from C_generators import CnPlusOne


def verify_antisymmetry(alg):
    """Check graded anti-symmetry: [X,Y] + (-1)^{p(X)p(Y)} [Y,X] = 0."""
    failures = []
    gens = alg.generators
    for i, gx in enumerate(gens):
        for gy in gens[i:]:
            px = alg.gen_parity[gx]
            py = alg.gen_parity[gy]
            sign = Fraction((-1) ** (px * py))

            br_xy = alg.element_to_gens(alg.bracket(gx, gy))
            br_yx = alg.element_to_gens(alg.bracket(gy, gx))

            # Check [X,Y] + sign * [Y,X] = 0
            combined = defaultdict(Fraction)
            for g, c in br_xy.items():
                combined[g] += c
            for g, c in br_yx.items():
                combined[g] += sign * c

            nonzero = {g: c for g, c in combined.items() if c}
            if nonzero:
                failures.append((gx, gy, nonzero))
    return failures


def _add_scaled(acc, d, scale):
    for k, v in d.items():
        acc[k] = acc.get(k, Fraction(0)) + scale * v


def bracket_of_gen_elem(alg, gx, elem_yz):
    """Compute [gx, elem_yz] where elem_yz = {gen: coeff}."""
    result = {}
    for gz, cz in elem_yz.items():
        sub_br = alg.element_to_gens(alg.bracket(gx, gz))
        for g, c in sub_br.items():
            result[g] = result.get(g, Fraction(0)) + cz * c
    return {g: c for g, c in result.items() if c}


def verify_jacobi(alg):
    """
    Check Super Jacobi: sum of cyclic terms = 0.
    (-1)^{p(X)p(Z)}[X,[Y,Z]] + (-1)^{p(Y)p(X)}[Y,[Z,X]] + (-1)^{p(Z)p(Y)}[Z,[X,Y]] = 0
    """
    failures = []
    gens = alg.generators
    total_triples = 0
    for i, gx in enumerate(gens):
        for j, gy in enumerate(gens[i:], i):
            for gz in gens[j:]:
                px = alg.gen_parity[gx]
                py = alg.gen_parity[gy]
                pz = alg.gen_parity[gz]
                total_triples += 1

                # Compute each bracket
                br_yz = alg.element_to_gens(alg.bracket(gy, gz))
                br_zx = alg.element_to_gens(alg.bracket(gz, gx))
                br_xy = alg.element_to_gens(alg.bracket(gx, gy))

                term1 = bracket_of_gen_elem(alg, gx, br_yz)
                term2 = bracket_of_gen_elem(alg, gy, br_zx)
                term3 = bracket_of_gen_elem(alg, gz, br_xy)

                s1 = Fraction((-1) ** (px * pz))
                s2 = Fraction((-1) ** (py * px))
                s3 = Fraction((-1) ** (pz * py))

                combined = defaultdict(Fraction)
                _add_scaled(combined, term1, s1)
                _add_scaled(combined, term2, s2)
                _add_scaled(combined, term3, s3)

                nonzero = {g: c for g, c in combined.items() if c}
                if nonzero:
                    failures.append((gx, gy, gz, nonzero))

    return failures, total_triples


def run_verification(n):
    print(f"\n{'='*60}")
    print(f"Verifying C({n+1}) = osp(2|{2*n})  (n={n})")
    print(f"{'='*60}")
    alg = CnPlusOne(n)
    dim_e = sum(1 for g in alg.generators if alg.gen_parity[g] == 0)
    dim_o = sum(1 for g in alg.generators if alg.gen_parity[g] == 1)
    print(f"Generators: {dim_e} even, {dim_o} odd (total {dim_e+dim_o})")

    # Anti-symmetry
    print("Checking anti-symmetry...")
    asym_failures = verify_antisymmetry(alg)
    if asym_failures:
        print(f"  FAIL: {len(asym_failures)} anti-symmetry violations:")
        for gx, gy, nz in asym_failures[:5]:
            print(f"    [{gx}, {gy}] + sign * [{gy}, {gx}] = {nz}")
    else:
        num_pairs = len(alg.generators) * (len(alg.generators) + 1) // 2
        print(f"  PASS: all {num_pairs} pairs satisfy anti-symmetry.")

    # Jacobi
    print("Checking Super Jacobi identity...")
    jac_failures, total = verify_jacobi(alg)
    if jac_failures:
        print(f"  FAIL: {len(jac_failures)} Jacobi violations (of {total} triples):")
        for gx, gy, gz, nz in jac_failures[:5]:
            print(f"    Jacobi({gx},{gy},{gz}) = {nz}")
    else:
        print(f"  PASS: all {total} triples satisfy Super Jacobi identity.")

    return len(asym_failures) == 0 and len(jac_failures) == 0


if __name__ == '__main__':
    all_pass = True
    for n in [1, 2, 3]:
        ok = run_verification(n)
        all_pass = all_pass and ok

    print(f"\n{'='*60}")
    if all_pass:
        print("ALL CHECKS PASSED for n=1,2,3")
    else:
        print("SOME CHECKS FAILED — review output above")
        sys.exit(1)
