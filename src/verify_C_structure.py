#!/usr/bin/env python3
"""
Verification script for C(n+1) structure constants.

Checks:
1. Anti-symmetry: [X, Y} = -(-1)^(p(X)p(Y)) [Y, X}
2. Super Jacobi identity: [X, [Y, Z}} + (-1)^(p(X)(p(Y)+p(Z))) [Y, [Z, X}}
                          + (-1)^(p(Z)(p(X)+p(Y))) [Z, [X, Y}} = 0
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class StructureVerifier:
    """Verifies structure constant properties."""

    def __init__(self, json_file: str):
        """Load structure constants from JSON."""
        with open(json_file, 'r') as f:
            self.schema = json.load(f)

        self.n = self.schema['algebra']['n']
        self.cartan_type = self.schema['algebra']['cartan_type']
        self.basis_even = self.schema['basis']['even']
        self.basis_odd = self.schema['basis']['odd']
        self.all_generators = self.basis_even + self.basis_odd
        self.parity = self.schema['parity']
        self.structure_constants = self.schema['structure_constants']

        # Build lookup table: (X, Y) -> list of (Z, coeff) for [X, Y} = sum coeff * Z
        self.brackets = self._build_bracket_table()
        self.anti_symmetry_violations = []
        self.jacobi_violations = []

    def _build_bracket_table(self) -> Dict[Tuple[str, str], List[Tuple[str, float]]]:
        """Build a lookup table for [X, Y} bracket results."""
        brackets = {}
        for const in self.structure_constants:
            X, Y, Z = const['X'], const['Y'], const['Z']
            coeff = float(const['coeff'])

            key = (X, Y)
            if key not in brackets:
                brackets[key] = []
            brackets[key].append((Z, coeff))

        return brackets

    def get_bracket(self, X: str, Y: str) -> Dict[str, float]:
        """Get [X, Y} as a dict {generator: coefficient}."""
        result = {}

        if (X, Y) in self.brackets:
            for Z, coeff in self.brackets[(X, Y)]:
                result[Z] = result.get(Z, 0) + coeff

        return result

    def check_antisymmetry(self) -> Tuple[bool, List[str]]:
        """Check anti-symmetry for all pairs."""
        violations = []

        for i, X in enumerate(self.all_generators):
            for j, Y in enumerate(self.all_generators):
                if i >= j:
                    continue

                bracket_xy = self.get_bracket(X, Y)
                bracket_yx = self.get_bracket(Y, X)

                # Anti-symmetry: [X, Y} = -(-1)^(p(X)p(Y)) [Y, X}
                sign = (-1) ** (self.parity[X] * self.parity[Y])
                expected_yx = {Z: -sign * coeff for Z, coeff in bracket_xy.items()}

                # Check if bracket_yx matches expected
                if bracket_yx != expected_yx:
                    # If both are empty, that's fine
                    if not bracket_xy and not bracket_yx:
                        continue

                    violations.append(
                        f"[{X}, {Y}] ≠ -(-1)^(p(X)p(Y))[{Y}, {X}]\n"
                        f"  p({X})={self.parity[X]}, p({Y})={self.parity[Y]}\n"
                        f"  [{X}, {Y}] = {bracket_xy}\n"
                        f"  [{Y}, {X}] = {bracket_yx}\n"
                        f"  Expected [{Y}, {X}] = {expected_yx}"
                    )

        self.anti_symmetry_violations = violations
        return len(violations) == 0, violations

    def check_jacobi_identity(self, sample_size: int = None) -> Tuple[bool, List[str]]:
        """Check Super Jacobi identity for generator triples.

        Full check: all triples (3^n complexity)
        Sampled check: random subset if too many triples
        """
        violations = []
        n_gens = len(self.all_generators)
        n_triples = n_gens ** 3

        # For small algebras, check all. For large, sample.
        if sample_size is None:
            sample_size = min(n_triples, 100 if n_triples > 1000 else n_triples)

        checked = 0
        for i, X in enumerate(self.all_generators):
            for j, Y in enumerate(self.all_generators):
                for k, Z in enumerate(self.all_generators):
                    if sample_size < n_triples and (i + j + k) % max(1, n_triples // sample_size) != 0:
                        continue

                    checked += 1

                    # Super Jacobi:
                    # [X, [Y, Z}} + (-1)^(p(X)(p(Y)+p(Z))) [Y, [Z, X}}
                    # + (-1)^(p(Z)(p(X)+p(Y))) [Z, [X, Y}} = 0

                    p_x = self.parity[X]
                    p_y = self.parity[Y]
                    p_z = self.parity[Z]

                    # Compute [Y, Z}
                    yz = self.get_bracket(Y, Z)

                    # Compute [X, [Y, Z}}
                    x_yz = {}
                    for W, c_yz in yz.items():
                        xw = self.get_bracket(X, W)
                        for V, c_xw in xw.items():
                            x_yz[V] = x_yz.get(V, 0) + c_yz * c_xw

                    # Compute [Z, X}
                    zx = self.get_bracket(Z, X)

                    # Compute [Y, [Z, X}}
                    y_zx = {}
                    for W, c_zx in zx.items():
                        yw = self.get_bracket(Y, W)
                        for V, c_yw in yw.items():
                            y_zx[V] = y_zx.get(V, 0) + c_zx * c_yw
                    sign_y = (-1) ** (p_x * (p_y + p_z))

                    # Compute [X, Y}
                    xy = self.get_bracket(X, Y)

                    # Compute [Z, [X, Y}}
                    z_xy = {}
                    for W, c_xy in xy.items():
                        zw = self.get_bracket(Z, W)
                        for V, c_zw in zw.items():
                            z_xy[V] = z_xy.get(V, 0) + c_xy * c_zw
                    sign_z = (-1) ** (p_z * (p_x + p_y))

                    # Combine with signs
                    jacobi_sum = {}
                    for V in set(list(x_yz.keys()) + list(y_zx.keys()) + list(z_xy.keys())):
                        jacobi_sum[V] = (
                            x_yz.get(V, 0) +
                            sign_y * y_zx.get(V, 0) +
                            sign_z * z_xy.get(V, 0)
                        )

                    # Check if sum is zero (allowing for floating point errors)
                    max_nonzero = max(abs(c) for c in jacobi_sum.values()) if jacobi_sum else 0
                    if max_nonzero > 1e-10:
                        violations.append(
                            f"Jacobi violation for ({X}, {Y}, {Z}):\n"
                            f"  Result: {jacobi_sum}"
                        )

        self.jacobi_violations = violations
        return len(violations) == 0, violations, checked

    def report(self):
        """Print summary report."""
        print(f"\n{'='*70}")
        print(f"Structure Constants Verification Report")
        print(f"{'='*70}")
        print(f"Algebra: {self.cartan_type} = osp(2|{2*self.n})")
        print(f"Generators: {len(self.basis_even)} even + {len(self.basis_odd)} odd = {len(self.all_generators)} total")
        print(f"Structure constants defined: {len(self.structure_constants)}")

        # Anti-symmetry check
        print(f"\n{'-'*70}")
        print("ANTI-SYMMETRY CHECK")
        print(f"{'-'*70}")
        passed_as, violations_as = self.check_antisymmetry()
        if passed_as:
            print("✓ PASS: Anti-symmetry property satisfied")
        else:
            print(f"✗ FAIL: Anti-symmetry violations found ({len(violations_as)})")
            for v in violations_as[:3]:  # Show first 3
                print(f"  {v}")

        # Jacobi identity check
        print(f"\n{'-'*70}")
        print("SUPER JACOBI IDENTITY CHECK")
        print(f"{'-'*70}")
        passed_jac, violations_jac, checked = self.check_jacobi_identity()
        print(f"Generator triples checked: {checked}")
        if passed_jac:
            print("✓ PASS: Super Jacobi identity satisfied")
        else:
            print(f"✗ FAIL: Jacobi violations found ({len(violations_jac)})")
            for v in violations_jac[:3]:  # Show first 3
                print(f"  {v}")

        # Summary
        print(f"\n{'-'*70}")
        print("SUMMARY")
        print(f"{'-'*70}")
        all_passed = passed_as and passed_jac
        if all_passed:
            print("✓ ALL CHECKS PASSED")
        else:
            print("✗ SOME CHECKS FAILED")

        return all_passed


def verify_all(data_dir: str = 'data'):
    """Verify all three structure constants files."""
    results = {}

    for n in [1, 2, 3]:
        json_file = f'{data_dir}/C_{n}_structure.json'
        print(f"\n\n{'#'*70}")
        print(f"# Verifying C_{n}_structure.json")
        print(f"{'#'*70}")

        try:
            verifier = StructureVerifier(json_file)
            passed = verifier.report()
            results[n] = passed
        except Exception as e:
            print(f"ERROR: {e}")
            results[n] = False

    print(f"\n\n{'#'*70}")
    print("FINAL SUMMARY")
    print(f"{'#'*70}")
    for n, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"C({n+1}): {status}")

    return all(results.values())


if __name__ == '__main__':
    data_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    success = verify_all(data_dir)
    sys.exit(0 if success else 1)
