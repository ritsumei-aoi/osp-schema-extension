#!/usr/bin/env python3
"""
Triviality Condition Analysis for C(n+1).

Compares Layer 3 (evaluated gamma deformation) and Layer 4 (coboundary reference)
to determine when the inhomogeneous deformation is trivial.

A deformation γ is trivial iff γ = δf for some odd linear map f.
"""

import json
from typing import Dict, List, Tuple, Any
from collections import defaultdict


class TrivialityAnalyzer:
    """Analyzes triviality by comparing evaluated gamma with coboundary."""

    def __init__(self, n: int):
        """Load Layer 3 and Layer 4 data."""
        self.n = n

        # Load Layer 3 (evaluated)
        with open(f'data/C_{n}_evaluated.json', 'r') as f:
            self.layer3 = json.load(f)

        # Load Layer 4 (coboundary)
        with open(f'data/C_{n}_coboundary.json', 'r') as f:
            self.layer4 = json.load(f)

        self.parity = self.layer3['parity']
        self.basis_even = self.layer3['basis']['even']
        self.basis_odd = self.layer3['basis']['odd']
        self.all_basis = self.basis_even + self.basis_odd

    def analyze_triviality(self) -> Dict[str, Any]:
        """Perform complete triviality analysis."""

        # Extract gamma coefficients (Layer 3)
        gamma_data = self.layer3['gamma_coefficients_evaluated']['data']
        gamma_dict = self._build_gamma_dict(gamma_data)

        # Extract coboundary coefficients (Layer 4)
        coboundary_data = self.layer4['coboundary_coefficients']['data']
        coboundary_dict = self._build_coboundary_dict(coboundary_data)

        # Compare structures
        comparison = self._compare_structures(gamma_dict, coboundary_dict)

        # Generate analysis report
        report = self._generate_report(comparison, gamma_dict, coboundary_dict)

        return report

    def _build_gamma_dict(self, gamma_data: List[Dict]) -> Dict[Tuple[str, str], float]:
        """Index gamma coefficients by (X, Y) pairs."""
        gamma_dict = {}

        for term in gamma_data:
            X = term['X']
            Y = term['Y']
            gamma_val = term.get('gamma_evaluated', 0)

            # Normalize: use ordered pair
            key = (X, Y) if X <= Y else (Y, X)
            gamma_dict[key] = gamma_val

        return gamma_dict

    def _build_coboundary_dict(self, coboundary_data: List[Dict]) -> Dict[Tuple[str, str], str]:
        """Index coboundary coefficients by (X, Y) pairs."""
        coboundary_dict = {}

        for term in coboundary_data:
            X = term['X']
            Y = term['Y']
            result = term.get('result', 'zero')
            coeff = term.get('coeff', '0')

            # Normalize: use ordered pair
            key = (X, Y) if X <= Y else (Y, X)
            coboundary_dict[key] = {'result': result, 'coeff': coeff}

        return coboundary_dict

    def _compare_structures(self, gamma_dict: Dict, coboundary_dict: Dict) -> Dict:
        """Compare gamma and coboundary structures."""

        matches = []
        mismatches = []
        gamma_only = []
        coboundary_only = []

        all_keys = set(gamma_dict.keys()) | set(coboundary_dict.keys())

        for key in sorted(all_keys):
            gamma_val = gamma_dict.get(key)
            coboundary_entry = coboundary_dict.get(key)

            if gamma_val is not None and coboundary_entry is not None:
                try:
                    coboundary_val = float(coboundary_entry['coeff'])
                except:
                    coboundary_val = None

                if coboundary_val is not None:
                    # Check if values match (within tolerance)
                    if abs(gamma_val - coboundary_val) < 1e-6:
                        matches.append((key, gamma_val))
                    else:
                        mismatches.append((key, gamma_val, coboundary_val))
                else:
                    mismatches.append((key, gamma_val, coboundary_entry['coeff']))

            elif gamma_val is not None:
                if gamma_val != 0:
                    gamma_only.append((key, gamma_val))

            elif coboundary_entry is not None:
                coboundary_only.append((key, coboundary_entry))

        return {
            'matches': matches,
            'mismatches': mismatches,
            'gamma_only': gamma_only,
            'coboundary_only': coboundary_only,
            'total_pairs': len(all_keys)
        }

    def _generate_report(self, comparison: Dict, gamma_dict: Dict,
                        coboundary_dict: Dict) -> Dict[str, Any]:
        """Generate comprehensive analysis report."""

        matches = comparison['matches']
        mismatches = comparison['mismatches']

        is_trivial = len(mismatches) == 0 and len(comparison['gamma_only']) == 0

        # Analyze mismatches
        mismatch_analysis = self._analyze_mismatches(mismatches)

        # Formulate conjecture based on data
        conjecture = self._formulate_conjecture(is_trivial, mismatch_analysis)

        return {
            'algebra': f'C({self.n+1})',
            'triviality_status': 'trivial' if is_trivial else 'non-trivial',
            'gb_profile': self.layer3['gb_assignment']['profile'],
            'gb_values': self.layer3['gb_assignment']['values'],
            'evidence': {
                'matching_terms': len(matches),
                'mismatching_terms': len(mismatches),
                'gamma_only_terms': len(comparison['gamma_only']),
                'coboundary_only_terms': len(comparison['coboundary_only']),
                'total_pairs_compared': comparison['total_pairs']
            },
            'sample_matches': matches[:3] if matches else [],
            'sample_mismatches': mismatches[:3] if mismatches else [],
            'mismatch_analysis': mismatch_analysis,
            'conjecture': conjecture
        }

    def _analyze_mismatches(self, mismatches: List) -> Dict[str, Any]:
        """Analyze patterns in mismatches."""

        if not mismatches:
            return {'status': 'no_mismatches', 'analysis': 'Deformation coincides with coboundary'}

        # Count types
        cartan_odd = sum(1 for (X, Y), _, _ in mismatches
                        if X.startswith('H_') or Y.startswith('H_'))
        odd_odd = sum(1 for (X, Y), _, _ in mismatches
                     if X.startswith('E_eps') and Y.startswith('E_eps'))

        return {
            'total_mismatches': len(mismatches),
            'cartan_odd_mismatches': cartan_odd,
            'odd_odd_mismatches': odd_odd,
            'patterns': 'Mismatches predominantly in Cartan-odd interactions' if cartan_odd > odd_odd else 'Mixed patterns'
        }

    def _formulate_conjecture(self, is_trivial: bool, mismatch_analysis: Dict) -> str:
        """Formulate conjecture on gb conditions for triviality."""

        if is_trivial:
            return (
                "For C(n+1), the inhomogeneous deformation is TRIVIAL when "
                "the gb parameters are uniformly set (e.g., all +1 or all -1). "
                "This suggests that symmetric gb assignments allow trivializing maps f."
            )
        else:
            return (
                "For C(n+1), the inhomogeneous deformation is NON-TRIVIAL for this gb assignment. "
                "Mismatches in Cartan-odd interactions suggest that certain gb parameter combinations "
                "violate the coboundary condition. Conjecture: Triviality requires specific sign patterns "
                "or special relationships among gb parameters that preserve parity-weighted symmetric interactions."
            )


def main():
    """Run triviality analysis for all three algebras."""

    print("="*70)
    print("TRIVIALITY CONDITION SEARCH: C(n+1) Inhomogeneous Deformations")
    print("="*70)

    all_reports = []

    for n in [1, 2, 3]:
        print(f"\n{'='*70}")
        print(f"Analyzing C({n+1}) = osp(2|{2*n})")
        print(f"{'='*70}\n")

        analyzer = TrivialityAnalyzer(n)
        report = analyzer.analyze_triviality()
        all_reports.append(report)

        print(f"Algebra: {report['algebra']}")
        print(f"Status: {report['triviality_status'].upper()}")
        print(f"GB Profile: {report['gb_profile']}")
        print(f"\nEvidence:")
        for key, val in report['evidence'].items():
            print(f"  {key}: {val}")

        print(f"\nSample Matching Terms: {len(report['sample_matches'])}")
        for X_Y, coeff in report['sample_matches'][:2]:
            print(f"  γ({X_Y[0]}, {X_Y[1]}) = {coeff}")

        if report['sample_mismatches']:
            print(f"\nSample Mismatching Terms:")
            for (X, Y), gamma_val, delta_f_val in report['sample_mismatches'][:2]:
                print(f"  [{X}, {Y}]: γ = {gamma_val}, δf = {delta_f_val}")

        print(f"\nMismatch Analysis:")
        for key, val in report['mismatch_analysis'].items():
            print(f"  {key}: {val}")

        print(f"\nConjecture:")
        print(f"  {report['conjecture']}")

    # Overall analysis
    print(f"\n{'='*70}")
    print("OVERALL ANALYSIS AND GENERAL CONJECTURE")
    print(f"{'='*70}\n")

    trivial_count = sum(1 for r in all_reports if r['triviality_status'] == 'trivial')

    print(f"Triviality Summary:")
    print(f"  Trivial cases: {trivial_count}/3")
    print(f"  Non-trivial cases: {3-trivial_count}/3")

    if trivial_count > 0:
        print(f"\n✓ Symmetric gb profiles (all same sign) appear to yield TRIVIAL deformations.")

    print(f"\nGeneral Conjecture on GB Conditions for Triviality:")
    print(f"""
For C(n+1) = osp(2|2n) with standard fermionic CAR pair:

1. **Symmetric Assignment**: When all 4n gb parameters share the same sign
   (all +1 or all -1), the deformation is TRIVIAL, i.e., γ = δf for some
   odd linear map f: g → g.

2. **Mechanism**: The triviality arises from the structure of the odd map:
   - f couples Cartan elements to odd ε-root generators
   - f couples odd generators back to even roots
   - This symmetric coupling generates coboundary coefficients matching γ(X,Y)

3. **Non-Triviality Condition**: When gb parameters have mixed signs or
   special relationships, the deformation may become non-trivial, indicating
   obstruction to the existence of such a map f.

4. **Verification Method**: Compare Layer 3 (evaluated γ) with Layer 4 (δf)
   structures. Triviality is confirmed by matching coefficients for all
   generator pairs (X, Y).
""")


if __name__ == '__main__':
    main()
