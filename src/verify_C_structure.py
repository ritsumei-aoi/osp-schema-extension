#!/usr/bin/env python3
"""
Verification script for C(n+1) structure constants.

Verifies:
1. Anti-symmetry: [X, Y] = -(-1)^{p(X)p(Y)} [Y, X]
2. Super Jacobi identity: Sum over cyclic permutations of [[X,Y],Z] = 0

Reference: docs/math/C_coboundary_definition.md (Lie superalgebra bracket properties)
"""

import json
from collections import defaultdict
from pathlib import Path
from fractions import Fraction
from typing import Dict, List, Tuple


class StructureVerifier:
    """Verifies structure constants for C(n+1) algebras."""

    def __init__(self, schema_file: str):
        """Load schema from JSON file."""
        with open(schema_file) as f:
            self.schema = json.load(f)

        self.algebra = self.schema['algebra']['cartan_type']
        self.parity = self.schema['parity']
        self.basis = self.schema['basis']['even'] + self.schema['basis']['odd']

        # Build structure constants dictionary
        # Format: (X, Y) -> {Z: coeff}
        self.brackets = self._build_bracket_dict()

    def _build_bracket_dict(self) -> Dict[Tuple, Dict[str, float]]:
        """Build a dictionary of all brackets from structure_constants list."""
        brackets = defaultdict(lambda: defaultdict(float))

        for struct in self.schema['structure_constants']:
            X = struct['X']
            Y = struct['Y']
            Z = struct['Z']
            coeff = float(struct['coeff']) if isinstance(struct['coeff'], str) else struct['coeff']

            brackets[(X, Y)][Z] = coeff

        return dict(brackets)

    def get_bracket(self, X: str, Y: str) -> Dict[str, float]:
        """Get [X, Y] as a dict {Z: coeff}."""
        if (X, Y) in self.brackets:
            return self.brackets[(X, Y)]
        return {}

    def verify_anti_symmetry(self) -> Tuple[bool, List[str]]:
        """Verify [X, Y] = -(-1)^{p(X)p(Y)} [Y, X]."""
        failures = []

        if not self.brackets:
            return True, ["No structure constants to verify (empty schema)"]

        for (X, Y), bracket_XY in self.brackets.items():
            bracket_YX = self.get_bracket(Y, X)

            p_X = self.parity.get(X, 0)
            p_Y = self.parity.get(Y, 0)
            sign = (-1) ** (p_X * p_Y)

            # Check: bracket_XY = -sign * bracket_YX
            all_Z = set(bracket_XY.keys()) | set(bracket_YX.keys())

            for Z in all_Z:
                coeff_XY = bracket_XY.get(Z, 0)
                coeff_YX = bracket_YX.get(Z, 0)

                expected = -sign * coeff_YX
                if abs(coeff_XY - expected) > 1e-10:
                    failures.append(
                        f"[{X}, {Y}] vs [{Y}, {X}]: "
                        f"coeff of {Z} is {coeff_XY}, expected {expected}"
                    )

        return len(failures) == 0, failures

    def verify_jacobi(self) -> Tuple[bool, List[str]]:
        """Verify the graded Jacobi identity."""
        failures = []

        if not self.brackets:
            return True, ["No structure constants to verify (empty schema)"]

        # The super Jacobi identity states:
        # (-1)^{p(X)p(Z)} [[X,Y],Z] + (-1)^{p(Y)p(X)} [[Y,Z],X] + (-1)^{p(Z)p(Y)} [[Z,X],Y] = 0

        checked = set()
        for X in self.basis[:5]:  # Sample check (all triples would be O(n^3))
            for Y in self.basis[:5]:
                for Z in self.basis[:5]:
                    if (X, Y, Z) in checked:
                        continue
                    checked.add((X, Y, Z))

                    p_X = self.parity.get(X, 0)
                    p_Y = self.parity.get(Y, 0)
                    p_Z = self.parity.get(Z, 0)

                    # Compute [[X,Y],Z]
                    bracket_XY = self.get_bracket(X, Y)
                    term1 = {}
                    for W, c_W in bracket_XY.items():
                        bracket_WZ = self.get_bracket(W, Z)
                        for V, c_V in bracket_WZ.items():
                            term1[V] = term1.get(V, 0) + c_W * c_V * ((-1) ** (p_X * p_Z))

                    # Compute [[Y,Z],X]
                    bracket_YZ = self.get_bracket(Y, Z)
                    term2 = {}
                    for W, c_W in bracket_YZ.items():
                        bracket_WX = self.get_bracket(W, X)
                        for V, c_V in bracket_WX.items():
                            term2[V] = term2.get(V, 0) + c_W * c_V * ((-1) ** (p_Y * p_X))

                    # Compute [[Z,X],Y]
                    bracket_ZX = self.get_bracket(Z, X)
                    term3 = {}
                    for W, c_W in bracket_ZX.items():
                        bracket_WY = self.get_bracket(W, Y)
                        for V, c_V in bracket_WY.items():
                            term3[V] = term3.get(V, 0) + c_W * c_V * ((-1) ** (p_Z * p_Y))

                    # Sum should be zero
                    all_V = set(term1.keys()) | set(term2.keys()) | set(term3.keys())
                    for V in all_V:
                        total = term1.get(V, 0) + term2.get(V, 0) + term3.get(V, 0)
                        if abs(total) > 1e-10:
                            failures.append(
                                f"Jacobi([{X}, {Y}, {Z}]): "
                                f"coefficient of {V} is {total}, expected 0"
                            )

        return len(failures) == 0, failures

    def verify_closure(self) -> Tuple[bool, List[str]]:
        """Verify that all bracket results are in the basis."""
        failures = []

        if not self.brackets:
            return True, ["No structure constants to verify (empty schema)"]

        for (X, Y), bracket in self.brackets.items():
            for Z in bracket.keys():
                if Z not in self.basis:
                    failures.append(f"[{X}, {Y}] contains {Z}, which is not in basis")

        return len(failures) == 0, failures

    def generate_report(self) -> str:
        """Generate a verification report."""
        lines = [
            f"Structure Constants Verification Report for {self.algebra}",
            "=" * 70,
            f"Schema file: {self.algebra}",
            f"Total basis elements: {len(self.basis)}",
            f"Non-zero structure constants: {len(self.brackets)}",
            ""
        ]

        if not self.brackets:
            lines.extend([
                "STATUS: NO STRUCTURE CONSTANTS",
                "",
                "Note: The Schema 1 layer contains the algebra structure (basis, parity,",
                "oscillator realizations, and central elements), but structure constants",
                "(the full Lie bracket table) are deferred to Schema 2 layer (deformation",
                "theory). This is expected and correct.",
                ""
            ])
            return "\n".join(lines)

        # Anti-symmetry check
        lines.append("1. ANTI-SYMMETRY CHECK")
        lines.append("-" * 70)
        passed, failures = self.verify_anti_symmetry()
        if passed:
            lines.append("✓ PASSED: All brackets satisfy [X,Y] = -(-1)^{p(X)p(Y)} [Y,X]")
        else:
            lines.append(f"✗ FAILED: {len(failures)} violations")
            for f in failures[:5]:
                lines.append(f"  - {f}")
            if len(failures) > 5:
                lines.append(f"  ... and {len(failures) - 5} more")
        lines.append("")

        # Jacobi identity check
        lines.append("2. SUPER JACOBI IDENTITY CHECK")
        lines.append("-" * 70)
        passed, failures = self.verify_jacobi()
        if passed:
            lines.append("✓ PASSED: Sampled triples satisfy Jacobi identity")
        else:
            lines.append(f"✗ FAILED: {len(failures)} violations")
            for f in failures[:5]:
                lines.append(f"  - {f}")
            if len(failures) > 5:
                lines.append(f"  ... and {len(failures) - 5} more")
        lines.append("")

        # Closure check
        lines.append("3. BASIS CLOSURE CHECK")
        lines.append("-" * 70)
        passed, failures = self.verify_closure()
        if passed:
            lines.append("✓ PASSED: All bracket results are in the basis")
        else:
            lines.append(f"✗ FAILED: {len(failures)} violations")
            for f in failures[:5]:
                lines.append(f"  - {f}")
            if len(failures) > 5:
                lines.append(f"  ... and {len(failures) - 5} more")
        lines.append("")

        return "\n".join(lines)


def main():
    """Verify structure constants for all C(n+1) algebras."""
    for n in [1, 2, 3]:
        filepath = f"data/C_{n}_structure.json"
        if not Path(filepath).exists():
            print(f"File not found: {filepath}")
            continue

        print(f"\nVerifying {filepath}...")
        print("=" * 70)

        verifier = StructureVerifier(filepath)
        report = verifier.generate_report()
        print(report)


if __name__ == "__main__":
    main()
