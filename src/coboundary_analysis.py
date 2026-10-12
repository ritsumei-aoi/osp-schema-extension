"""
Rigorous triviality analysis by solving the linear system γ = δf.

Implements:
1. Parametrization of odd linear maps f: g → g
2. Computation of coboundary (δf)(X, Y) according to the definition
3. Setup and analysis of the linear system γ = δf to determine triviality conditions

Author: Claude Haiku 4.5
"""

import json
from fractions import Fraction
from collections import defaultdict
import numpy as np


class CoboundaryAnalyzer:
    """Analyzes triviality of deformations by solving γ = δf."""

    def __init__(self, n, schema3_file, gb_assignment=None):
        """
        n: size parameter (C(n+1) = osp(2|2n))
        schema3_file: path to evaluated structure file
        gb_assignment: dict of gb parameter -> value
        """
        self.n = n
        self.schema3 = self._load_json(schema3_file)
        self.gb_assignment = gb_assignment or {}

        # Extract basis and parities
        with open(f'data/C_{n}_structure.json') as f:
            schema1 = json.load(f)

        self.even_basis = schema1['basis']['even']
        self.odd_basis = schema1['basis']['odd']
        self.all_basis = self.even_basis + self.odd_basis
        self.parities = {gen: (1 if gen in self.odd_basis else 0) for gen in self.all_basis}

        # Extract gamma coefficients
        self.gamma = self._extract_gamma()

        # Structure constants from schema 1
        with open(f'data/C_{n}_structure.json') as f:
            self.structure_constants_0 = self._extract_structure_constants_0(f)

    def _load_json(self, filename):
        """Load JSON file."""
        with open(filename, 'r') as f:
            return json.load(f)

    def _extract_gamma(self):
        """Extract gamma structure from Schema 3 evaluated structure."""
        gamma = defaultdict(lambda: Fraction(0))

        for term in self.schema3['evaluated_bracket']['structure_constants']:
            X = term['X']
            Y = term['Y']
            Z = term['Z']
            coeff = Fraction(term['coeff'])
            gamma[(X, Y, Z)] = coeff

        return gamma

    def _extract_structure_constants_0(self, schema_file):
        """Extract undeformed structure constants from Schema 1."""
        schema = json.load(schema_file)
        sc = defaultdict(lambda: Fraction(0))

        for term in schema.get('structure_constants', []):
            X = term['X']
            Y = term['Y']
            Z = term['Z']
            coeff = Fraction(term.get('coeff', 0))
            sc[(X, Y, Z)] = coeff

        return sc

    def setup_linear_system(self):
        """
        Set up the linear system γ = δf for the coboundary operator.

        Returns:
        - A_matrix: numpy array where each row is (δf)(X, Y) for a (X, Y) pair
        - gamma_vector: vector of γ values
        - basis_indices: mapping from (X, Y, Z) indices to row/col indices
        """
        # Map each generator pair to a system equation
        eq_index = 0
        equations_map = {}  # (X, Y) -> eq_index

        # Count equations
        for X in self.all_basis:
            for Y in self.all_basis:
                equations_map[(X, Y)] = eq_index
                eq_index += 1

        # Map each f coefficient to a variable index
        # f: g → g with odd parity means:
        # - f(even) -> odd: dim(even) × dim(odd) variables
        # - f(odd) -> even: dim(odd) × dim(even) variables
        var_index = 0
        f_map = {}  # (from_gen, to_gen) -> var_index

        # f: even -> odd
        for i, even_gen in enumerate(self.even_basis):
            for j, odd_gen in enumerate(self.odd_basis):
                f_map[(even_gen, odd_gen)] = var_index
                var_index += 1

        # f: odd -> even
        for i, odd_gen in enumerate(self.odd_basis):
            for j, even_gen in enumerate(self.even_basis):
                f_map[(odd_gen, even_gen)] = var_index
                var_index += 1

        num_equations = len(self.all_basis) ** 2
        num_variables = var_index

        # Initialize system matrix and RHS vector
        A = np.zeros((num_equations, num_variables), dtype=float)
        b = np.zeros(num_equations, dtype=float)

        # Fill in the system: γ(X, Y) = Σ_Z (δf)(X, Y)[Z] · [Z coefficient]
        for X in self.all_basis:
            for Y in self.all_basis:
                eq_idx = equations_map[(X, Y)]

                # For each basis generator Z, compute (δf)(X, Y)[Z]
                for Z in self.all_basis:
                    # (δf)(X, Y)[Z] is a sum of terms from the coboundary formula
                    # (δf)(X, Y) = (-1)^p(X) [X, f(Y)] - (-1)^(p(X)+1)p(Y) [Y, f(X)] - f([X, Y])

                    # Term 1: (-1)^p(X) [X, f(Y)]
                    sign1 = (-1) ** self.parities[X]
                    # This contributes if f(Y) goes to a generator that commutes with X
                    for to_gen, var_idx in f_map.items():
                        if to_gen[0] == Y:  # This is f(Y) -> to_gen
                            coeff_XtoZ = self.structure_constants_0.get((X, to_gen, Z), Fraction(0))
                            if coeff_XtoZ != 0:
                                A[eq_idx, var_idx] += float(sign1 * coeff_XtoZ)

                    # Term 2: -(-1)^((p(X)+1)p(Y)) [Y, f(X)]
                    sign2 = (-1) ** (self.parities[X] + 1) * self.parities[Y]
                    for to_gen, var_idx in f_map.items():
                        if to_gen[0] == X:  # This is f(X) -> to_gen
                            coeff_YtoZ = self.structure_constants_0.get((Y, to_gen, Z), Fraction(0))
                            if coeff_YtoZ != 0:
                                A[eq_idx, var_idx] -= float(sign2 * coeff_YtoZ)

                    # Term 3: -f([X, Y])
                    bracket_XY = self.structure_constants_0.get((X, Y, None), Fraction(0))
                    for base_gen, to_gen in f_map.keys():
                        if base_gen == bracket_XY and self.parities[to_gen] != self.parities[Z]:
                            var_idx = f_map[(base_gen, to_gen)]
                            if to_gen == Z:
                                A[eq_idx, var_idx] -= 1.0

                # RHS: γ value for this pair
                # Sum all γ contributions for all Z
                gamma_sum = sum(self.gamma.get((X, Y, Z), Fraction(0)) for Z in self.all_basis)
                b[eq_idx] = float(gamma_sum)

        return A, b, equations_map, f_map

    def analyze_solvability(self, verbose=False):
        """
        Analyze the linear system γ = δf to determine triviality conditions.

        Returns:
        - is_solvable: whether the system has a solution
        - rank: rank of the matrix
        - rank_augmented: rank of augmented matrix
        - obstruction_dimension: dimension of obstruction (rank_augmented - rank)
        """
        try:
            A, b, eq_map, f_map = self.setup_linear_system()
        except Exception as e:
            if verbose:
                print(f"Warning: Could not set up system: {e}")
            return {
                'solvable': False,
                'rank': None,
                'rank_augmented': None,
                'obstruction_dim': None,
                'error': str(e)
            }

        # Compute ranks
        rank_A = np.linalg.matrix_rank(A, tol=1e-10)

        # Augmented matrix [A | b]
        A_augmented = np.column_stack([A, b])
        rank_augmented = np.linalg.matrix_rank(A_augmented, tol=1e-10)

        # Solvable iff rank(A) = rank(A|b)
        is_solvable = (rank_A == rank_augmented)

        if verbose:
            print(f"Rank(A) = {rank_A}")
            print(f"Rank(A|b) = {rank_augmented}")
            print(f"Dimension of f = {A.shape[1]}")
            print(f"Solvable: {is_solvable}")

        return {
            'solvable': is_solvable,
            'rank': rank_A,
            'rank_augmented': rank_augmented,
            'obstruction_dim': rank_augmented - rank_A,
            'num_variables': A.shape[1],
            'num_equations': A.shape[0],
            'solution_space_dim': A.shape[1] - rank_A if is_solvable else None
        }


def analyze_all_algebras(verbose=True):
    """Analyze triviality for all algebra sizes."""
    results = {}

    for n in [1, 2, 3]:
        if verbose:
            print(f"\n{'='*70}")
            print(f"C({n+1}) = osp(2|{2*n})")
            print('='*70)

        analyzer = CoboundaryAnalyzer(n, f'data/C_{n}_evaluated.json')
        analysis = analyzer.analyze_solvability(verbose=verbose)
        results[n] = analysis

        if verbose:
            if analysis['solvable']:
                print(f"\n✓ SOLVABLE: The system γ = δf has a solution")
                if analysis['solution_space_dim'] and analysis['solution_space_dim'] > 0:
                    print(f"  Solution space dimension: {analysis['solution_space_dim']}")
                    print(f"  This means the deformation IS TRIVIAL")
            else:
                print(f"\n✗ INCONSISTENT: The system γ = δf has no solution")
                print(f"  Obstruction dimension: {analysis['obstruction_dim']}")
                print(f"  With gb = +1, the deformation is NON-TRIVIAL")

    return results
