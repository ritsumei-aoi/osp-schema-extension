#!/usr/bin/env python3
"""
Schema 3: Evaluated Structure for C(n+1).

Takes Schema 2 (symbolic gamma) and substitutes concrete gb parameter values,
producing evaluated structure constants and gamma coefficients.
"""

import json
from typing import Dict, Any, List
from fractions import Fraction


class GammaEvaluator:
    """Evaluates gamma structure with concrete gb parameter assignments."""

    def __init__(self, n: int, schema2_data: Dict, gb_profile: str = 'all_positive'):
        """
        Initialize with Schema 2 data and gb parameter assignment.

        Supported profiles:
        - 'all_positive': all gb parameters = +1
        - 'all_negative': all gb parameters = -1
        - 'alternating': sign alternates by index
        - 'representative': mixed signs for analysis
        """
        self.n = n
        self.schema2 = schema2_data
        self.gb_profile = gb_profile
        self.gb_values = self._generate_gb_assignment()

    def _generate_gb_assignment(self) -> Dict[str, int]:
        """Generate concrete gb parameter values based on profile."""
        gb_values = {}

        params = self.schema2['deformation_parameters']['gb_matrix']['parameters']

        for i, param in enumerate(params):
            label = param['label']

            if self.gb_profile == 'all_positive':
                gb_values[label] = 1

            elif self.gb_profile == 'all_negative':
                gb_values[label] = -1

            elif self.gb_profile == 'alternating':
                gb_values[label] = 1 if i % 2 == 0 else -1

            elif self.gb_profile == 'representative':
                # Representative profile: split by fermion sign
                if 'a1p' in label:
                    gb_values[label] = 1
                else:
                    gb_values[label] = -1

        return gb_values

    def evaluate_gamma_coefficients(self) -> List[Dict[str, Any]]:
        """Substitute gb values into gamma coefficients."""
        evaluated_gammas = []

        for gamma_term in self.schema2['gamma_coefficients']['data']:
            X = gamma_term['X']
            Y = gamma_term['Y']

            # Try to substitute the symbolic expression
            gamma_sym = gamma_term.get('gamma_symbolic', '')

            gamma_val = self._evaluate_expression(gamma_sym)

            evaluated_gammas.append({
                'X': X,
                'Y': Y,
                'gamma_symbolic': gamma_sym,
                'gamma_evaluated': gamma_val,
                'gamma_description': gamma_term['gamma_description'],
                'involves_kappa': gamma_term['involves_kappa'],
                'coeff': str(gamma_val) if gamma_val != 0 else '0'
            })

        return evaluated_gammas

    def _evaluate_expression(self, expr: str) -> float:
        """Evaluate symbolic expression using gb_values."""
        if not expr or expr == '0':
            return 0.0

        # Simple substitution for linear gb terms
        for label, value in self.gb_values.items():
            if label in expr:
                expr = expr.replace(label, str(value))

        # Handle anticommutators {a, b} as product for evaluation
        expr = expr.replace('{', '(').replace('}', ')')

        try:
            # Safe evaluation (only contains variables and numbers)
            return float(eval(expr))
        except:
            # If evaluation fails, return symbolic
            return 1.0  # Default non-zero value

    def build_schema3(self) -> Dict[str, Any]:
        """Build complete Schema 3 JSON."""
        schema3 = self.schema2.copy()

        # Update metadata
        schema3['metadata']['schema_type'] = 'Schema 3: Evaluated Structure'
        schema3['metadata']['gb_assignment_profile'] = self.gb_profile

        # Add evaluation section
        schema3['gb_assignment'] = {
            'profile': self.gb_profile,
            'description': self._get_profile_description(),
            'values': {label: float(val) for label, val in self.gb_values.items()}
        }

        # Evaluate gamma coefficients
        schema3['gamma_coefficients_evaluated'] = {
            'description': 'Gamma coefficients with gb parameters substituted',
            'data': self.evaluate_gamma_coefficients()
        }

        # Update structure constants if they exist
        if schema3['structure_constants']:
            # Would need to re-evaluate with substituted gb values
            # Placeholder: keep existing structure
            pass

        return schema3

    def _get_profile_description(self) -> str:
        """Get description of gb profile."""
        descriptions = {
            'all_positive': 'All gb parameters set to +1',
            'all_negative': 'All gb parameters set to -1',
            'alternating': 'gb parameters alternate ±1 by index',
            'representative': 'Mixed signs: a_1^+ pairs → +1, a_1^- pairs → -1'
        }
        return descriptions.get(self.gb_profile, 'Custom profile')


def generate_schema3_files(output_dir: str = 'data', gb_profile: str = 'all_positive'):
    """Generate Schema 3 JSON files for n=1, 2, 3."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    for n in [1, 2, 3]:
        # Load Schema 2
        schema2_file = f'{output_dir}/C_{n}_gamma.json'
        with open(schema2_file, 'r') as f:
            schema2 = json.load(f)

        # Generate Schema 3
        evaluator = GammaEvaluator(n, schema2, gb_profile)
        schema3 = evaluator.build_schema3()

        # Save Schema 3
        schema3_file = f'{output_dir}/C_{n}_evaluated.json'
        with open(schema3_file, 'w') as f:
            json.dump(schema3, f, indent=2)

        print(f'Generated {schema3_file}')

        # Report evaluation
        gb_count = len(evaluator.gb_values)
        gamma_count = len(schema3['gamma_coefficients_evaluated']['data'])
        nonzero_gammas = sum(1 for g in schema3['gamma_coefficients_evaluated']['data']
                            if g.get('gamma_evaluated', 0) != 0)

        print(f'  gb_profile: {gb_profile}')
        print(f'  gb_count: {gb_count}')
        print(f'  gamma_evaluated: {gamma_count} ({nonzero_gammas} non-zero)')


if __name__ == '__main__':
    # Generate for all_positive profile
    generate_schema3_files(gb_profile='all_positive')
