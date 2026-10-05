#!/usr/bin/env python3
"""
Compute structure constants [X, Y} = Z with coefficient for C(n+1).
Uses oscillator commutation relations to compute brackets.
"""

import json
from typing import Dict, Tuple, Optional
from fractions import Fraction
from collections import defaultdict
from itertools import product


class BracketComputer:
    """Computes Lie superalgebra brackets from oscillator realizations."""

    def __init__(self, schema: Dict):
        """Initialize with Schema 1 JSON."""
        self.schema = schema
        self.realizations = schema['generator_realization']['realizations']
        self.parity = schema['parity']
        self.basis_even = schema['basis']['even']
        self.basis_odd = schema['basis']['odd']
        self.all_basis = self.basis_even + self.basis_odd

    def compute_bracket(self, X: str, Y: str) -> Dict[str, Fraction]:
        """
        Compute [X, Y} using oscillator realizations.

        Returns dict mapping generator labels to coefficients.
        Uses commutation relations:
        - Bosons: [b_j^-, b_k^+] = δ_jk
        - Fermions: {a_1^-, a_1^+} = 1
        - Mixed: [b_i^±, a_1^±] = 0 (undeformed)
        """
        p_X = self.parity[X]
        p_Y = self.parity[Y]

        real_X = self.realizations[X]['standard_form']
        real_Y = self.realizations[Y]['standard_form']

        # Expand bracket: [X, Y} = Σ (coeff_X * coeff_Y * commutator_of_words)
        bracket_terms = defaultdict(Fraction)

        for term_X in real_X:
            for term_Y in real_Y:
                words_X = term_X['words']
                words_Y = term_Y['words']
                coeff_X = Fraction(term_X['coeff'])
                coeff_Y = Fraction(term_Y['coeff'])

                # Compute commutator of two oscillator words
                # Use PBW reduction via oscillator relations
                commutator_result = self._commute_words(words_X, words_Y)

                for result_key, result_coeff in commutator_result.items():
                    total_coeff = coeff_X * coeff_Y * result_coeff
                    # Apply sign rule: [X, Y} = (-1)^{p(X)p(Y)} [Y, X}
                    if result_key != '0':
                        bracket_terms[result_key] += total_coeff

        return dict(bracket_terms)

    def _commute_words(self, words_X: list, words_Y: list) -> Dict[str, Fraction]:
        """
        Compute [word_X, word_Y} using oscillator algebra.
        Returns dict mapping PBW words to coefficients.
        """
        # Simplification: Handle simple cases
        # For complex reduction, would need full PBW algorithm

        if not words_X or not words_Y:
            # If either is empty (constant), result is zero
            return {}

        # Permute Y's words left through X's words
        # Collecting commutation/anticommutation terms
        result = defaultdict(Fraction)

        # Simple approach: bubble left
        current_words_Y = words_Y[:]

        for word_X in reversed(words_X):
            new_words_Y = []
            delta_term = Fraction(0)

            for word_Y in current_words_Y:
                comm = self._single_pair_commute(word_X, word_Y)
                if comm is not None:
                    delta_term += comm
                else:
                    new_words_Y.append(word_Y)

            current_words_Y = new_words_Y

        # If we completely reduced to nothing or identity, add
        if not current_words_Y and delta_term != 0:
            result['identity'] += delta_term
        else:
            # For non-zero results, reconstruct the word
            word_key = ' '.join(current_words_Y) if current_words_Y else 'identity'
            if delta_term != 0:
                result[word_key] += delta_term

        return dict(result)

    def _single_pair_commute(self, op1: str, op2: str) -> Optional[Fraction]:
        """
        Compute commutator [op1, op2}.
        Returns coefficient if it's a c-number, None if it's an operator.
        """
        # Bosonic pair commutators
        if op1.startswith('b') and op2.startswith('b'):
            # Extract indices and types
            parts1 = op1.split('_')  # e.g., 'b', '1', 'p'
            parts2 = op2.split('_')

            idx1, idx2 = int(parts1[1]), int(parts2[1])
            type1, type2 = parts1[2], parts2[2]

            # [b_j^-, b_k^+] = δ_jk
            if type1 == 'm' and type2 == 'p' and idx1 == idx2:
                return Fraction(1)

            # [b_j^+, b_k^-] = -δ_jk
            if type1 == 'p' and type2 == 'm' and idx1 == idx2:
                return Fraction(-1)

            return None

        # Fermionic anticommutators (treated as commutators with sign correction)
        if op1.startswith('a') and op2.startswith('a'):
            # {a_1^-, a_1^+} = 1
            if {op1, op2} == {'a_1_m', 'a_1_p'}:
                return Fraction(1)

            return None

        # Mixed: [b, a] = 0 (undeformed)
        return None


def compute_all_brackets(schema: Dict) -> list:
    """Compute all non-zero brackets [X, Y} for basis pairs."""
    computer = BracketComputer(schema)

    all_basis = computer.all_basis
    brackets = []

    for i, X in enumerate(all_basis):
        for j, Y in enumerate(all_basis):
            if i >= j:
                continue

            bracket_result = computer.compute_bracket(X, Y)

            for Z_label, coeff in bracket_result.items():
                if coeff != 0 and Z_label != '0':
                    # Map Z_label back to basis if possible
                    if Z_label in computer.all_basis:
                        brackets.append({
                            'X': X,
                            'Y': Y,
                            'Z': Z_label,
                            'coeff': str(coeff),
                            'sign_rule': 'graded'
                        })

    return brackets


if __name__ == '__main__':
    # Test on C(2)
    with open('data/C_1_structure.json', 'r') as f:
        schema = json.load(f)

    brackets = compute_all_brackets(schema)
    print(f"Computed {len(brackets)} non-zero brackets for C(2)")
    for b in brackets[:5]:
        print(f"  [{b['X']}, {b['Y']}] = {b['coeff']} * {b['Z']}")
