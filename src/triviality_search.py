"""
Triviality search and analysis for C(n+1) inhomogeneous deformation.

Compares Layer 3 (evaluated structure with gamma) and Layer 4 (coboundary structure)
to determine conditions for triviality.

Author: Claude Haiku 4.5
"""

import json
from fractions import Fraction
from collections import defaultdict


class TrivialityAnalyzer:
    """Analyzes triviality conditions for C(n+1) deformations."""

    def __init__(self, n):
        self.n = n
        self.schema3_file = f"data/C_{n}_evaluated.json"
        self.schema4_file = f"data/C_{n}_coboundary.json"
        self.schema1_file = f"data/C_{n}_structure.json"

        self.schema3 = self._load_json(self.schema3_file)
        self.schema4 = self._load_json(self.schema4_file)
        self.schema1 = self._load_json(self.schema1_file)

        self.gamma_coefficients = self._extract_gamma()
        self.coboundary_coefficients = self._extract_coboundary()

    def _load_json(self, filename):
        """Load JSON file."""
        with open(filename, "r") as f:
            return json.load(f)

    def _extract_gamma(self):
        """Extract gamma structure from Layer 3."""
        gamma = {}
        for entry in self.schema3.get("evaluated_bracket", {}).get("structure_constants", []):
            X = entry["X"]
            Y = entry["Y"]
            Z = entry["Z"]
            coeff = Fraction(entry["coeff"])

            key = (X, Y, Z)
            gamma[key] = coeff

        return gamma

    def _extract_coboundary(self):
        """Extract coboundary structure from Layer 4."""
        coboundary = {}
        for entry in self.schema4.get("coboundary_operator", {}).get("coboundary_terms", []):
            X = entry["X"]
            Y = entry["Y"]
            Z = entry["Z"]
            coeff = Fraction(entry["coeff"])

            key = (X, Y, Z)
            coboundary[key] = coeff

        return coboundary

    def compare_structures(self):
        """Compare gamma and coboundary structures."""
        all_keys = set(self.gamma_coefficients.keys()) | set(self.coboundary_coefficients.keys())

        matches = []
        discrepancies = []

        for key in all_keys:
            gamma_val = self.gamma_coefficients.get(key, Fraction(0))
            coboundary_val = self.coboundary_coefficients.get(key, Fraction(0))

            if gamma_val == coboundary_val:
                matches.append((key, gamma_val))
            else:
                discrepancies.append({
                    "X": key[0],
                    "Y": key[1],
                    "Z": key[2],
                    "gamma": gamma_val,
                    "coboundary": coboundary_val,
                    "difference": gamma_val - coboundary_val
                })

        return {
            "matches": matches,
            "discrepancies": discrepancies,
            "total_gamma_terms": len(self.gamma_coefficients),
            "total_coboundary_terms": len(self.coboundary_coefficients),
            "matching_terms": len(matches)
        }

    def analyze_triviality(self):
        """
        Analyze triviality based on comparison with f=0 (test point, not exhaustive).

        IMPORTANT: This analysis only tests f=0. Finding γ ≠ (δ0) shows f=0 is
        insufficient but does NOT prove non-triviality. Full triviality determination
        requires solving the linear system γ = δf for all possible f coefficients.
        """
        comparison = self.compare_structures()

        analysis = {
            "total_terms": comparison["total_gamma_terms"],
            "matching_terms": comparison["matching_terms"],
            "discrepancies": comparison["discrepancies"],
            "match_percentage": 100 * comparison["matching_terms"] / max(comparison["total_gamma_terms"], 1),
            "test_scope": "f=0 only (single point in parameter space)"
        }

        if comparison["matching_terms"] == comparison["total_gamma_terms"]:
            test_result = "MATCHES_f=0"
            test_reason = "All gamma coefficients match δf with f=0 (deformation is trivial)"
        elif comparison["matching_terms"] == 0:
            test_result = "DOES_NOT_MATCH_f=0"
            test_reason = "No gamma coefficients match δf with f=0 (f=0 is insufficient)"
        else:
            test_result = "PARTIAL_MATCH_f=0"
            test_reason = "Some gamma terms match δf with f=0, others do not"

        analysis["test_result"] = test_result
        analysis["test_reason"] = test_reason
        analysis["triviality_status"] = "UNDETERMINED (requires solving full linear system γ = δf)"

        return analysis

    def analyze_gb_patterns(self):
        """Analyze patterns in gb parameters that affect triviality."""
        gb_assignment = self.schema3.get("gb_assignment", {}).get("values", {})

        analysis = {
            "gb_count": len(gb_assignment),
            "gb_assignment": gb_assignment,
            "notes": [
                "Current assignment: all gb = +1 (symmetric point in parameter space)",
                "Deformation depends linearly on gb parameters",
                "Triviality analysis would require solving linear equations in gb space"
            ]
        }

        return analysis

    def generate_conjecture(self):
        """Generate conjecture on triviality conditions."""
        triviality = self.analyze_triviality()
        gb_analysis = self.analyze_gb_patterns()

        conjecture = {
            "statement": "The inhomogeneous deformation of C(n+1) is trivial iff the gb parameters satisfy the linear system γ(X,Y) = (δf)(X,Y) for some odd linear map f.",
            "basis": [
                "The gamma coefficients are linear in the gb parameters",
                "The coboundary (δf) is linear in f coefficients",
                "Triviality requires solving γ = δf for f coefficients",
                "Solvability depends on the gb values (constraint manifold in parameter space)"
            ],
            "current_test_result": triviality["test_result"],
            "current_test_reason": triviality["test_reason"],
            "key_observation": "With f=0, the coboundary is zero, but γ ≠ 0 with gb=+1. This shows f=0 insufficient, not non-triviality.",
            "next_steps": [
                "Parametrize f by its matrix entries in the basis of g",
                "Compute δf symbolically in terms of f coefficients",
                "Solve the linear system γ = δf for all generator pairs",
                "Determine gb constraints that make the system solvable",
                "Identify obstruction cohomology classes"
            ]
        }

        return conjecture

    def to_report(self):
        """Generate comprehensive triviality report."""
        comparison = self.compare_structures()
        triviality = self.analyze_triviality()
        gb_analysis = self.analyze_gb_patterns()
        conjecture = self.generate_conjecture()

        report = {
            "algebra": f"C({self.n+1}) = osp(2|{2*self.n})",
            "comparison": comparison,
            "triviality_analysis": triviality,
            "gb_analysis": gb_analysis,
            "conjecture": conjecture,
            "summary": self._generate_summary(triviality, comparison)
        }

        return report

    def _generate_summary(self, triviality, comparison):
        """Generate executive summary."""
        return f"""
Test Scope: {triviality['test_scope']}
Test Result: {triviality['test_result']}
Reason: {triviality['test_reason']}
Triviality Status: {triviality['triviality_status']}

Evidence:
- Deformation has {comparison['total_gamma_terms']} non-zero terms
- Coboundary with f=0 has {comparison['total_coboundary_terms']} terms
- Matching terms with f=0: {comparison['matching_terms']} ({triviality['match_percentage']:.1f}%)

Interpretation:
With gb=+1, the deformation γ does not match the coboundary from f=0.
This shows f=0 is insufficient but does NOT prove non-triviality.
A non-zero linear map f may exist that satisfies γ = δf.
The full triviality determination requires solving the system γ = δf for f coefficients.
"""


def analyze_all(n_values=[1, 2, 3]):
    """Perform triviality analysis for all algebra sizes."""
    print("="*70)
    print("TRIVIALITY SEARCH AND ANALYSIS FOR C(n+1)")
    print("="*70)

    reports = {}

    for n in n_values:
        print(f"\n{'='*70}")
        print(f"C({n+1}) = osp(2|{2*n})")
        print('='*70)

        analyzer = TrivialityAnalyzer(n)
        report = analyzer.to_report()
        reports[n] = report

        print(f"\nComparison Results:")
        print(f"  Deformation terms (gamma): {report['comparison']['total_gamma_terms']}")
        print(f"  Coboundary terms (δf): {report['comparison']['total_coboundary_terms']}")
        print(f"  Matching terms: {report['comparison']['matching_terms']}")

        print(f"\nTest Result (f=0): {report['triviality_analysis']['test_result']}")
        print(f"  {report['triviality_analysis']['test_reason']}")
        print(f"\nTriviality Status: {report['triviality_analysis']['triviality_status']}")

        if report['comparison']['discrepancies']:
            print(f"\nDiscrepancies: {len(report['comparison']['discrepancies'])} generator triples")
            for disc in report['comparison']['discrepancies'][:3]:
                print(f"  ({disc['X']}, {disc['Y']}) → {disc['Z']}: γ={disc['gamma']}, δf={disc['coboundary']}")
            if len(report['comparison']['discrepancies']) > 3:
                print(f"  ... and {len(report['comparison']['discrepancies']) - 3} more")

        print(f"\nGB Assignment:")
        print(f"  Count: {report['gb_analysis']['gb_count']}")
        print(f"  Type: Canonical (all parameters = +1)")

        print(f"\nConjecture: {report['conjecture']['statement']}")

    print(f"\n{'='*70}")
    print("GENERAL FINDINGS")
    print('='*70)
    print("""
1. CURRENT TEST STATUS (f=0 only):
   All three algebras (C(2), C(3), C(4)) have γ ≠ (δ0) when gb=+1.
   This shows f=0 is insufficient but does NOT determine actual triviality.

2. EVIDENCE:
   - Gamma coefficients from Schema 3 are non-zero (from deformed relations)
   - Coboundary operator with f=0 yields zeros (by definition)
   - No match between γ and δ0 at this test point

3. MATHEMATICAL INTERPRETATION:
   The deformation γ(X,Y) encodes [b_j^s, a_1^σ] = -gb_{σ,j,s} · κ.
   The coboundary (δ0) = 0 trivially.
   Therefore γ ≠ (δ0), confirming that f=0 cannot account for the deformation.

   However, this is EXPECTED and DOES NOT PROVE NON-TRIVIALITY.
   A non-zero odd linear map f may exist that solves γ = δf.

4. FRAMEWORK FOR TRIVIALITY DETERMINATION:

   For C(n+1) = osp(2|2n) with gb parameters {gb_{a_1^σ, b_j^s}}:

   The deformation is trivial ⟺ ∃ odd linear map f: g → g such that γ = δf

   This requires solving the linear system:
   γ(X,Y) = (δf)(X,Y) for all pairs (X,Y)

   where the unknowns are the matrix entries of f.

5. NEXT STEPS FOR COMPLETE ANALYSIS:
   - Parametrize f with dim(g_even) × dim(g_odd) coefficients
   - Compute δf symbolically in terms of f coefficients
   - Set up system: γ(X,Y,Z) = (δf)(X,Y,Z) for all triples
   - Analyze solvability: rank, kernel, obstruction classes
   - Determine which gb values lead to trivial deformations
""")


if __name__ == "__main__":
    analyze_all()
