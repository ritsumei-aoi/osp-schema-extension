"""
verify_C_structure.py
Verifies that C(n+1) structure constants satisfy:
  1. Graded anti-symmetry: [X,Y} = -(-1)^{p(X)p(Y)} [Y,X}
  2. Super Jacobi identity: (-1)^{p(X)p(Z)} [X,[Y,Z}} + cyclic = 0
"""

import json
import sys
import os
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_generators import build_basis, build_parity, bracket


def load_structure_constants(n):
    fname = f"data/C_{n}_structure.json"
    with open(fname) as f:
        d = json.load(f)
    sc = {}
    for entry in d["structure_constants"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        coeff = Fraction(entry["coeff"])
        sc[(X, Y, Z)] = coeff
    return sc


def bracket_from_sc(X, Y, sc, parity, all_basis):
    """Compute [X, Y} as dict using structure constants (for [X,Y] with X < Y in basis order)."""
    result = {}
    idx = {g: i for i, g in enumerate(all_basis)}
    px = parity[X]
    py = parity[Y]

    if idx[X] < idx[Y]:
        for Z in all_basis:
            c = sc.get((X, Y, Z), Fraction(0))
            if c != 0:
                result[Z] = c
    else:
        # [Y, X} = -(-1)^{p(Y)p(X)} [X, Y}  → [X, Y} = -(-1)^{px*py} [Y, X}
        for Z in all_basis:
            c = sc.get((Y, X, Z), Fraction(0))
            if c != 0:
                result[Z] = -Fraction((-1) ** (px * py)) * c

    return result


def verify_antisymmetry(n, all_basis, parity, sc, verbose=False):
    """Check [X,Y} = -(-1)^{p(X)p(Y)} [Y,X} using computed brackets."""
    failures = 0
    for i, X in enumerate(all_basis):
        for j, Y in enumerate(all_basis):
            if j <= i:
                continue
            res_xy = bracket(X, Y, n, parity)
            res_yx = bracket(Y, X, n, parity)
            px, py = parity[X], parity[Y]
            sign = (-1) ** (px * py)

            for Z in set(list(res_xy.keys()) + list(res_yx.keys())):
                lhs = res_xy.get(Z, Fraction(0))
                rhs = -Fraction(sign) * res_yx.get(Z, Fraction(0))
                if lhs != rhs:
                    if verbose:
                        print(f"ANTISYMMETRY FAIL: [{X},{Y}]_Z={Z}: {lhs} != {rhs}")
                    failures += 1

    return failures


def compose(res_1, gen2, n, parity):
    """Compute sum_W c_{1W} * [W, gen2} = [[X,Y}, Z}."""
    result = {}
    for W, c_w in res_1.items():
        sub = bracket(W, gen2, n, parity)
        for Z2, c_z in sub.items():
            result[Z2] = result.get(Z2, Fraction(0)) + c_w * c_z
    return {k: v for k, v in result.items() if v != 0}


def act_on(inner_bracket, gen, inner_parity, n, parity):
    """
    Compute [gen, inner}_g = -(-1)^{p(gen)*p_inner} * compose(inner_bracket, gen).
    This gives [gen, sum_W c_W W} using compose([[inner},gen}) then converting.
    """
    p_inner = inner_parity % 2
    p_gen = parity[gen]
    sign = -(-1) ** (p_gen * p_inner)
    raw = compose(inner_bracket, gen, n, parity)  # = [[inner}, gen}
    return {W: Fraction(sign) * c for W, c in raw.items()}


def verify_super_jacobi(n, all_basis, parity, verbose=False):
    """
    Check Super Jacobi identity for all triples (X,Y,Z):
    (-1)^{p(X)p(Z)} [X,[Y,Z}} + (-1)^{p(Y)p(X)} [Y,[Z,X}} + (-1)^{p(Z)p(Y)} [Z,[X,Y}} = 0

    Note: [A, B}_g = -(-1)^{p(A)p(B)} [B, A}_g.
    So [X, [Y,Z}} = -(-1)^{p(X)*(py+pz)} * [[Y,Z}, X}.
    """
    failures = 0
    total_triples = 0

    for i, X in enumerate(all_basis):
        for j, Y in enumerate(all_basis):
            for k, Z in enumerate(all_basis):
                if not (i < j < k):
                    continue
                total_triples += 1
                px, py, pz = parity[X], parity[Y], parity[Z]

                yz = bracket(Y, Z, n, parity)
                zx = bracket(Z, X, n, parity)
                xy = bracket(X, Y, n, parity)

                p_yz = (py + pz) % 2
                p_zx = (pz + px) % 2
                p_xy = (px + py) % 2

                # [X, [Y,Z}} = -(-1)^{px*p_yz} * compose(yz, X)
                t1 = act_on(yz, X, p_yz, n, parity)
                t2 = act_on(zx, Y, p_zx, n, parity)
                t3 = act_on(xy, Z, p_xy, n, parity)

                s1 = (-1) ** (px * pz)
                s2 = (-1) ** (py * px)
                s3 = (-1) ** (pz * py)

                jacobiW = {}
                for W in set(list(t1.keys()) + list(t2.keys()) + list(t3.keys())):
                    val = (Fraction(s1) * t1.get(W, Fraction(0))
                           + Fraction(s2) * t2.get(W, Fraction(0))
                           + Fraction(s3) * t3.get(W, Fraction(0)))
                    if val != 0:
                        jacobiW[W] = val

                if jacobiW:
                    failures += 1
                    if verbose:
                        print(f"JACOBI FAIL ({X},{Y},{Z}): {jacobiW}")

    return failures, total_triples


def main():
    for n in [1, 2, 3]:
        print(f"\n=== C({n+1}) (n={n}) ===")
        even, odd = build_basis(n)
        all_basis = even + odd
        parity = build_parity(even, odd)

        print("  Checking anti-symmetry...")
        asym_fails = verify_antisymmetry(n, all_basis, parity, sc=None)
        if asym_fails == 0:
            print("  Anti-symmetry: PASS")
        else:
            print(f"  Anti-symmetry: FAIL ({asym_fails} failures)")

        print("  Checking Super Jacobi identity...")
        jac_fails, total = verify_super_jacobi(n, all_basis, parity)
        if jac_fails == 0:
            print(f"  Super Jacobi: PASS ({total} triples checked)")
        else:
            print(f"  Super Jacobi: FAIL ({jac_fails}/{total} triples failed)")

    print("\nDone.")


if __name__ == "__main__":
    main()
