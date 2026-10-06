"""
Independent verification of the C(n+1) Schema-1 structure constants (Issue I04).

This script does NOT use the oscillator engine. It loads C_{n}_structure.json and reconstructs
the graded bracket purely from the stored structure constants, then checks:

  (A) graded antisymmetry   [X,Y} = -(-1)^{p(X)p(Y)} [Y,X}
  (B) super-Jacobi identity
        (-1)^{p(X)p(Z)} [[X,Y},Z} + (-1)^{p(Y)p(X)} [[Y,Z},X} + (-1)^{p(Z)p(Y)} [[Z,X},Y} = 0
      for every ordered triple of basis generators.

Because the constants were generated as graded commutators in an associative superalgebra these
identities must hold; verifying them here catches any bookkeeping/decomposition error independently.

Run:  python3 src/verify_C_structure.py
"""

from __future__ import annotations
import json
import os
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")


def load(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as f:
        return json.load(f)


def _add(dst, Z, c):
    if c == 0:
        return
    v = dst.get(Z, Fraction(0)) + c
    if v == 0:
        dst.pop(Z, None)
    else:
        dst[Z] = v


class Algebra:
    def __init__(self, data):
        self.parity = dict(data["parity"])
        self.parity["K"] = 0
        self.basis = list(data["basis"]["even"]) + list(data["basis"]["odd"])
        self.stored = {}            # (X,Y) -> {Z: Fraction}
        for r in data["structure_constants"]:
            key = (r["X"], r["Y"])
            self.stored.setdefault(key, {})
            _add(self.stored[key], r["Z"], Fraction(r["coeff"]))

    def p(self, X):
        return self.parity[X]

    def bracket(self, X, Y):
        """[X,Y} as {Z: Fraction}, from stored (X<=Y) records + graded antisymmetry."""
        if X == "K" or Y == "K":
            return {}
        if (X, Y) in self.stored:
            return dict(self.stored[(X, Y)])
        if (Y, X) in self.stored:
            sign = -1 if (self.p(X) * self.p(Y)) % 2 else 1
            return {Z: (-sign) * c for Z, c in self.stored[(Y, X)].items()}
        return {}

    def bracket_vec(self, vec, Z):
        """[ sum c_W W , Z }."""
        out = {}
        for W, c in vec.items():
            for Zz, cc in self.bracket(W, Z).items():
                _add(out, Zz, c * cc)
        return out

    # ---- checks ----
    def check_antisymmetry(self):
        failures = []
        for X in self.basis:
            for Y in self.basis:
                lhs = self.bracket(X, Y)
                sign = -1 if (self.p(X) * self.p(Y)) % 2 else 1
                rhs = {Z: -sign * c for Z, c in self.bracket(Y, X).items()}
                diff = dict(lhs)
                for Z, c in rhs.items():
                    _add(diff, Z, -c)
                if diff:
                    failures.append((X, Y, diff))
        return failures

    def check_jacobi(self):
        failures = []
        count = 0
        B = self.basis
        for X in B:
            for Y in B:
                for Z in B:
                    count += 1
                    t1 = self.bracket_vec(self.bracket(X, Y), Z)
                    s1 = -1 if (self.p(X) * self.p(Z)) % 2 else 1
                    t2 = self.bracket_vec(self.bracket(Y, Z), X)
                    s2 = -1 if (self.p(Y) * self.p(X)) % 2 else 1
                    t3 = self.bracket_vec(self.bracket(Z, X), Y)
                    s3 = -1 if (self.p(Z) * self.p(Y)) % 2 else 1
                    total = {}
                    for s, t in ((s1, t1), (s2, t2), (s3, t3)):
                        for W, c in t.items():
                            _add(total, W, s * c)
                    if total:
                        failures.append((X, Y, Z, total))
        return count, failures


def main():
    print("=" * 70)
    print("C(n+1) Schema-1 verification (antisymmetry + super-Jacobi)")
    print("=" * 70)
    all_ok = True
    for n in (1, 2, 3):
        data = load(n)
        alg = Algebra(data)
        anti = alg.check_antisymmetry()
        count, jac = alg.check_jacobi()
        ok = not anti and not jac
        all_ok = all_ok and ok
        print(f"\nC({n+1})  (n={n}, dim={len(alg.basis)}):")
        print(f"  antisymmetry : {'PASS' if not anti else f'FAIL ({len(anti)})'} "
              f"over {len(alg.basis)**2} ordered pairs")
        print(f"  super-Jacobi : {'PASS' if not jac else f'FAIL ({len(jac)})'} "
              f"over {count} ordered triples")
        if anti:
            for f in anti[:5]:
                print("    antisym fail:", f)
        if jac:
            for f in jac[:5]:
                print("    jacobi  fail:", f)
    print("\n" + "=" * 70)
    print("OVERALL:", "ALL CHECKS PASS" if all_ok else "FAILURES PRESENT")
    print("=" * 70)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
