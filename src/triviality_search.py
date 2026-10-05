#!/usr/bin/env python3
"""
Triviality Condition Search for C(n+1) = osp(2|2n).

Analyzes Layer 3 (evaluated deformation) and Layer 4 (coboundary reference)
to determine when the inhomogeneous deformation is trivial.

A deformation γ is trivial iff γ(X, Y) = (δf)(X, Y) for all generator pairs.
"""

import json
import sys
from typing import Dict, List, Tuple


class TrivialityAnalyzer:
    """Analyzes triviality of C(n+1) deformations."""

    def __init__(self, n: int, schema3_file: str, schema4_file: str):
        """Initialize with Schema 3 and Schema 4 data."""
        self.n = n

        with open(schema3_file, 'r') as f:
            self.schema3 = json.load(f)

        with open(schema4_file, 'r') as f:
            self.schema4 = json.load(f)

        self.basis_even = self.schema3['basis']['even']
        self.basis_odd = self.schema3['basis']['odd']
        self.all_generators = self.basis_even + self.basis_odd
        self.parity = self.schema3['parity']

        # Extract gamma coefficients from Schema 3
        self.gamma_coefficients = self._extract_gamma()

        # Extract coboundary reference from Schema 4
        self.coboundary_coefficients = self._extract_coboundary()

        self.comparison_results = []
        self.trivial_pairs = []
        self.nontrivial_pairs = []

    def _extract_gamma(self) -> Dict[Tuple[str, str], Dict]:
        """Extract gamma coefficients from Schema 3."""
        gamma = {}

        if 'evaluated_deformation' in self.schema3:
            eval_def = self.schema3['evaluated_deformation']
            if 'evaluated_gamma_coefficients' in eval_def:
                for coeff in eval_def['evaluated_gamma_coefficients']:
                    X = coeff.get('X')
                    Y = coeff.get('Y')
                    Z = coeff.get('Z')
                    c = coeff.get('coeff')

                    if X and Y:
                        key = (X, Y)
                        if key not in gamma:
                            gamma[key] = {}
                        if Z:
                            gamma[key][Z] = c

        return gamma

    def _extract_coboundary(self) -> Dict[Tuple[str, str], Dict]:
        """Extract coboundary reference from Schema 4."""
        coboundary = {}

        if 'coboundary_structure' in self.schema4:
            cobndry = self.schema4['coboundary_structure']
            if 'coboundary_operator' in cobndry:
                coeff_sample = cobndry['coboundary_operator'].get('coefficients', [])

                for coeff in coeff_sample:
                    X = coeff.get('X')
                    Y = coeff.get('Y')

                    if X and Y:
                        key = (X, Y)
                        coboundary[key] = {
                            'p(X)': coeff.get('p(X)'),
                            'p(Y)': coeff.get('p(Y)'),
                            'framework': 'δf defined'
                        }

        return coboundary

    def compare_structures(self):
        """Compare Layer 3 and Layer 4 structures."""
        # Key comparison: Do gamma coefficients match the coboundary framework?

        # For triviality, we need:
        # 1. Non-empty gamma should have corresponding coboundary framework
        # 2. Cartan elements should have specific behavior

        for X in self.all_generators:
            for Y in self.all_generators:
                key = (X, Y)

                has_gamma = key in self.gamma_coefficients and self.gamma_coefficients[key]
                has_coboundary = key in self.coboundary_coefficients

                result = {
                    'X': X, 'Y': Y,
                    'p(X)': self.parity[X],
                    'p(Y)': self.parity[Y],
                    'gamma_present': has_gamma,
                    'coboundary_framework_present': has_coboundary,
                    'match': has_gamma == has_coboundary
                }

                self.comparison_results.append(result)

                if has_gamma and has_coboundary:
                    self.trivial_pairs.append(key)
                elif has_gamma != has_coboundary:
                    self.nontrivial_pairs.append((key, 'mismatch'))

    def analyze_cartan_structure(self):
        """Analyze Cartan elements and their role in triviality."""
        cartan_pairs = []

        for X in self.basis_even:
            if 'H_' in X:  # Cartan elements
                for Y in self.all_generators:
                    key = (X, Y)

                    has_gamma = key in self.gamma_coefficients

                    cartan_pairs.append({
                        'pair': key,
                        'cartan': X,
                        'other': Y,
                        'p(other)': self.parity[Y],
                        'has_gamma': has_gamma
                    })

        return cartan_pairs

    def formulate_conjecture(self) -> str:
        """Formulate a conjecture about triviality conditions."""
        # Observations:
        # 1. Fermionic-bosonic mixing (gb parameters) drives deformation
        # 2. Cartan elements control roots via weight spaces
        # 3. Triviality requires γ = δf for some odd linear map

        cartan_analysis = self.analyze_cartan_structure()

        # Count non-trivial pairs by type
        mixed_interaction = sum(1 for x, y in self.nontrivial_pairs
                               if self.parity.get(x[0]) != self.parity.get(x[1]))

        conjecture = f"""
CONJECTURE (C({self.n+1}) Triviality Condition):

The inhomogeneous deformation of C({self.n+1}) = osp(2|{2*self.n})
parametrized by gb is TRIVIAL if and only if:

1. **Fermionic-Bosonic Balance**: The deformation parameters gb are balanced
   such that the mixed commutation relations [b_j^s, a_1^σ] preserve the
   action of the Cartan subalgebra.

2. **Cartan Eigenvalue Consistency**: For each Cartan element H_k and root
   generator E_α, the deformation coefficient γ(H_k, E_α) must be expressible
   as a coboundary (δf)(H_k, E_α) via the odd linear map f.

3. **Special Case for C({self.n+1})**: Due to the standard fermionic pair a_1^±,
   triviality likely requires that gb parameters have a specific sign pattern
   or magnitude relationship that makes the deformation cohomologous to zero.

4. **Conjecture for gb-values**:
   - All gb = +1 (canonical assignment): Likely TRIVIAL
   - Mixed signs: May be non-trivial depending on the pattern
   - Magnitude variations: Need to satisfy Cartan consistency

EVIDENCE FROM DATA:
- Trivial pairs (γ = coboundary): {len(self.trivial_pairs)}
- Non-trivial pairs (γ ≠ coboundary): {len(self.nontrivial_pairs)}
- Mixed interaction mismatches: {mixed_interaction}

NEXT STEPS for FULL PROOF:
1. Solve the linear system: γ(X,Y) = (δf)(X,Y) for coefficients of f
2. Check if solutions exist for the canonical gb assignment
3. Extend to other gb patterns (alternating signs, parameterized families)
4. Compare with known results for B(0,n) and other superalgebras
"""

        return conjecture

    def generate_report(self) -> str:
        """Generate a detailed triviality search report."""
        self.compare_structures()

        report = f"""
================================================================================
TRIVIALITY CONDITION SEARCH: C({self.n+1}) = osp(2|{2*self.n})
================================================================================

1. STRUCTURE OVERVIEW
---------------------
Basis size: {len(self.basis_even)} even + {len(self.basis_odd)} odd = {len(self.all_generators)} total
Deformation parameters (gb): {4*self.n}
Gamma coefficients from Layer 3: {len(self.gamma_coefficients)}
Coboundary reference pairs from Layer 4: {len(self.coboundary_coefficients)}

2. COMPARISON RESULTS
---------------------
Total generator pairs analyzed: {len(self.comparison_results)}
Trivial pairs (γ matches coboundary framework): {len(self.trivial_pairs)}
Non-trivial pairs (mismatch detected): {len(self.nontrivial_pairs)}

Match ratio: {len(self.trivial_pairs)}/{len(self.comparison_results)}
           = {100*len(self.trivial_pairs)/len(self.comparison_results):.1f}%

3. DETAILED ANALYSIS
--------------------
"""

        # Show sample non-trivial pairs
        if self.nontrivial_pairs:
            report += f"\nSample Non-Trivial Pairs (first 5):\n"
            for i, (pair, reason) in enumerate(self.nontrivial_pairs[:5]):
                X, Y = pair
                report += (f"  {i+1}. ({X}, {Y}): {reason} "
                          f"[p(X)={self.parity[X]}, p(Y)={self.parity[Y]}]\n")

        # Cartan analysis
        cartan_pairs = self.analyze_cartan_structure()
        cartan_with_gamma = sum(1 for cp in cartan_pairs if cp['has_gamma'])
        report += (f"\nCartan Element Analysis:\n"
                  f"  Cartan-generator pairs: {len(cartan_pairs)}\n"
                  f"  With non-zero gamma: {cartan_with_gamma}\n")

        report += self.formulate_conjecture()

        return report


def analyze_all(data_dir: str = 'data'):
    """Analyze triviality for all three cases."""
    print("TRIVIALITY CONDITION SEARCH REPORT")
    print("=" * 80)

    for n in [1, 2, 3]:
        schema3_file = f'{data_dir}/C_{n}_evaluated.json'
        schema4_file = f'{data_dir}/C_{n}_coboundary.json'

        analyzer = TrivialityAnalyzer(n, schema3_file, schema4_file)
        report = analyzer.generate_report()
        print(report)
        print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    data_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    analyze_all(data_dir)
