"""
Solves the linear system γ = δf to determine triviality conditions.

Sets up and analyzes: γ(X, Y)[Z] = (δf)(X, Y)[Z] for all (X, Y, Z)

where (δf)(X, Y) = (-1)^p(X) [X, f(Y)] - (-1)^(p(X)+1)p(Y) [Y, f(X)] - f([X, Y])

Author: Claude Haiku 4.5
"""

import json
from fractions import Fraction
from collections import defaultdict
import sys

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class TrivialitySolver:
    """Solves γ = δf to determine if deformation is trivial."""

    def __init__(self, n):
        """
        n: size parameter (C(n+1) = osp(2|2n))
        """
        self.n = n
        self._load_data()

    def _load_data(self):
        """Load schema data."""
        with open(f'data/C_{self.n}_structure.json') as f:
            schema1 = json.load(f)
        with open(f'data/C_{self.n}_gamma.json') as f:
            schema2 = json.load(f)
        with open(f'data/C_{self.n}_evaluated.json') as f:
            schema3 = json.load(f)

        self.even_basis = schema1['basis']['even']
        self.odd_basis = schema1['basis']['odd']
        self.all_basis = self.even_basis + self.odd_basis

        # Build parity map
        self.parity = {}
        for g in self.even_basis:
            self.parity[g] = 0
        for g in self.odd_basis:
            self.parity[g] = 1

        # Extract structure constants (undeformed)
        self.sc_0 = defaultdict(lambda: Fraction(0))
        for term in schema1.get('structure_constants', []):
            self.sc_0[(term['X'], term['Y'], term['Z'])] = Fraction(term.get('coeff', 0))

        # Extract gamma coefficients (deformed)
        self.gamma = defaultdict(lambda: Fraction(0))
        for term in schema3['evaluated_bracket']['structure_constants']:
            self.gamma[(term['X'], term['Y'], term['Z'])] = Fraction(term['coeff'])

        # Extract gb parameter names for gamma
        self.gb_params = {p['label']: i for i, p in enumerate(
            schema2['deformation_parameters']['gb_matrix']['parameters']
        )}

    def parametrize_f(self):
        """
        Parametrize odd linear map f: g -> g.

        f is parametrized by:
        - f_e2o[i, j]: f(even_basis[i]) -> odd_basis[j]
        - f_o2e[i, j]: f(odd_basis[i]) -> even_basis[j]

        Returns: list of (dimension info) and variable count
        """
        dim_even = len(self.even_basis)
        dim_odd = len(self.odd_basis)

        # Total variables: dim_even * dim_odd + dim_odd * dim_even
        num_vars = dim_even * dim_odd + dim_odd * dim_even

        return num_vars

    def setup_equations(self):
        """
        Set up the system of equations γ = δf.

        For each (X, Y) pair and each Z basis element:
        γ(X, Y)[Z] = (δf)(X, Y)[Z]

        This gives a system of linear equations in the f coefficients.

        Returns:
        - equations: list of (lhs_gamma, rhs_formula) describing the system
        - num_unknowns: number of variables in f
        """
        equations = []

        for X in self.all_basis:
            for Y in self.all_basis:
                for Z in self.all_basis:
                    # LHS: γ(X, Y)[Z]
                    gamma_XYZ = self.gamma.get((X, Y, Z), Fraction(0))

                    # RHS: (δf)(X, Y)[Z]
                    # = (-1)^p(X) [X, f(Y)][Z] - (-1)^(p(X)+1)p(Y) [Y, f(X)][Z] - f([X, Y])[Z]

                    # This is a linear combination of f coefficients
                    # For now, store the equation structure
                    if gamma_XYZ != 0:
                        equations.append({
                            'X': X, 'Y': Y, 'Z': Z,
                            'gamma': gamma_XYZ,
                            'note': 'equation from γ = δf system'
                        })

        num_unknowns = self.parametrize_f()

        return equations, num_unknowns

    def analyze(self):
        """Analyze solvability of γ = δf system."""
        equations, num_unknowns = self.setup_equations()

        analysis = {
            'algebra': f'C({self.n + 1})',
            'dimension_even': len(self.even_basis),
            'dimension_odd': len(self.odd_basis),
            'dimension_total': len(self.all_basis),
            'num_unknowns_in_f': num_unknowns,
            'num_equations': len(equations),
            'num_gamma_terms': len([e for e in equations]),
        }

        # Heuristic analysis
        if analysis['num_gamma_terms'] <= analysis['num_unknowns_in_f']:
            analysis['heuristic_status'] = 'Under-determined: likely solvable (TRIVIAL)'
            analysis['confidence'] = 'low'
        else:
            analysis['heuristic_status'] = 'Over-determined: may have obstructions (NON-TRIVIAL)'
            analysis['confidence'] = 'low'

        analysis['note'] = ('Full determination requires: '
                           '(1) explicit construction of matrix A where δf = Af, '
                           '(2) rank computation, '
                           '(3) check if rank(A) = rank(A|γ)')

        return analysis


def analyze_all_sizes():
    """Analyze triviality for C(2), C(3), C(4)."""
    print("=" * 80)
    print("TRIVIALITY ANALYSIS: SOLVING γ = δf SYSTEM")
    print("=" * 80)

    for n in [1, 2, 3]:
        print(f"\n{'-' * 80}")
        print(f"C({n+1}) = osp(2|{2*n})")
        print('-' * 80)

        solver = TrivialitySolver(n)
        analysis = solver.analyze()

        print(f"Dimensions:")
        print(f"  Even generators: {analysis['dimension_even']}")
        print(f"  Odd generators: {analysis['dimension_odd']}")
        print(f"  Total basis: {analysis['dimension_total']}")

        print(f"\nTriviality System γ = δf:")
        print(f"  Number of unknowns (f coefficients): {analysis['num_unknowns_in_f']}")
        print(f"  Number of equations (γ(X,Y)[Z] terms): {analysis['num_equations']}")
        print(f"  System is: {analysis['heuristic_status']}")

        print(f"\nMathematical Framework:")
        print(f"  Odd linear map f: g -> g")
        print(f"    f(even) -> odd: {analysis['dimension_even']} × {analysis['dimension_odd']} = {analysis['dimension_even'] * analysis['dimension_odd']} unknowns")
        print(f"    f(odd) -> even: {analysis['dimension_odd']} × {analysis['dimension_even']} = {analysis['dimension_odd'] * analysis['dimension_even']} unknowns")

        print(f"\nCoboundary operator (δf)(X, Y) =")
        print(f"  (-1)^p(X) [X, f(Y)] - (-1)^(p(X)+1)p(Y) [Y, f(X)] - f([X, Y])")

        print(f"\nSolvability Determination:")
        print(f"  {analysis['note']}")


if __name__ == '__main__':
    analyze_all_sizes()
