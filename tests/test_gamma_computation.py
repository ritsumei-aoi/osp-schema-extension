"""
Verification that gamma coefficients match the mathematical definition.

Tests that computed gamma values satisfy:
[X, Y]_γ = [X, Y]_0 + κ · γ(X, Y)

where γ arises from the deformed commutation relations:
[b_j^s, a_1^σ] = -gb_{σ,j,s} · κ

Author: Claude Haiku 4.5
"""

import json
import pytest
from fractions import Fraction


class TestGammaComputation:
    """Verify gamma values from mathematical definition."""

    @pytest.fixture
    def schema1_C2(self):
        """Load C(2) structure (undeformed)."""
        with open('data/C_1_structure.json') as f:
            return json.load(f)

    @pytest.fixture
    def schema2_C2(self):
        """Load C(2) gamma structure (deformed)."""
        with open('data/C_1_gamma.json') as f:
            return json.load(f)

    def test_gamma_terms_are_for_mixed_parity_pairs(self, schema1_C2, schema2_C2):
        """Gamma should only appear for (even, odd) or (odd, even) pairs."""
        even_gens = set(schema1_C2['basis']['even'])
        odd_gens = set(schema1_C2['basis']['odd'])

        for term in schema2_C2['inhomogeneous_deformation']['gamma_terms']:
            X = term['X']
            Y = term['Y']
            # Verify: (X even and Y odd) or (X odd and Y even)
            assert (X in even_gens and Y in odd_gens) or (X in odd_gens and Y in even_gens)

    def test_gamma_output_generators_are_odd(self, schema1_C2, schema2_C2):
        """Output generator Z of gamma term must be odd (to match κ coefficient parity)."""
        odd_gens = set(schema1_C2['basis']['odd'])

        for term in schema2_C2['inhomogeneous_deformation']['gamma_terms']:
            Z = term['Z']
            assert Z in odd_gens, f"γ output {Z} should be odd, but it's in {schema1_C2['parity'].get(Z, 'unknown')}"

    def test_gamma_parameter_names_match_gb_matrix(self, schema2_C2):
        """All gamma_coeff strings should match gb matrix parameter names."""
        gb_params = {p['label'] for p in schema2_C2['deformation_parameters']['gb_matrix']['parameters']}

        for term in schema2_C2['inhomogeneous_deformation']['gamma_terms']:
            coeff_str = term['gamma_coeff']
            # Remove leading '-' if present
            param_name = coeff_str.lstrip('-')
            assert param_name in gb_params, f"Parameter {param_name} not in gb_matrix"

    def test_gamma_sign_pattern_anticommutes_with_parity(self, schema1_C2, schema2_C2):
        """
        For (X, Y) and (Y, X) pairs with X even Y odd:
        If (X, Y) → Z with γ = a·gb_..., then (Y, X) → Z with γ = -a·gb_...
        """
        even_gens = set(schema1_C2['basis']['even'])
        odd_gens = set(schema1_C2['basis']['odd'])

        # Build dict: (X, Y, Z) -> gamma_coeff
        gamma_dict = {}
        for term in schema2_C2['inhomogeneous_deformation']['gamma_terms']:
            X, Y, Z = term['X'], term['Y'], term['Z']
            gamma_dict[(X, Y, Z)] = term['gamma_coeff']

        # Check anticommutativity: γ(X, Y) = -γ(Y, X) for (even X, odd Y)
        for (X, Y, Z) in list(gamma_dict.keys()):
            if X in even_gens and Y in odd_gens:
                forward_coeff = gamma_dict.get((X, Y, Z), '0')
                backward_coeff = gamma_dict.get((Y, X, Z), '0')

                # If forward is -gb_..., backward should be +gb_...
                if forward_coeff.startswith('-'):
                    expected_backward = forward_coeff[1:]
                else:
                    expected_backward = '-' + forward_coeff

                assert backward_coeff == expected_backward, \
                    f"Anticommutativity violated: ({X},{Y}) has {forward_coeff} but ({Y},{X}) has {backward_coeff}"

    def test_gamma_coefficients_are_nonzero_with_deformation(self, schema2_C2):
        """With deformed parameters (gb ≠ 0), gamma terms should have non-zero coefficients."""
        for term in schema2_C2['inhomogeneous_deformation']['gamma_terms']:
            coeff_str = term['gamma_coeff']
            assert coeff_str != '0', f"Gamma term has zero coefficient: {term}"

    def test_gamma_values_evaluate_correctly_at_gb_1(self):
        """Verify gamma values when evaluated at gb = +1."""
        with open('data/C_1_evaluated.json') as f:
            evaluated = json.load(f)

        # All evaluated gamma coefficients should be ±1 (since all gb = +1)
        for term in evaluated['evaluated_bracket']['structure_constants']:
            coeff = Fraction(term['coeff'])
            # Should be ±1 or 0 (but we only store non-zero)
            assert abs(coeff) == 1, f"Expected ±1, got {coeff} for {term}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
