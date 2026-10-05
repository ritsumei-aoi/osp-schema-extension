#!/usr/bin/env python3
"""
C(n+1) = osp(2|2n) evaluated structure (Schema 3) generator.

Substitutes concrete values into the gb parameters and produces
evaluated structure constants.

Reference: Layer 3 (Evaluated Structure) in the 4-layer architecture.
"""

import json
from typing import Dict, List, Tuple


class CnEvaluatedGenerator:
    """Generator for C(n+1) Schema 3 with evaluated parameters."""

    def __init__(self, n: int, schema2_data: Dict = None, gb_values: Dict = None):
        """Initialize from Schema 2 data with optional gb values.

        Args:
            n: Rank parameter
            schema2_data: Schema 2 JSON data (gamma structure)
            gb_values: Dict mapping parameter names to numeric values (parity encoded as ±1)
        """
        self.n = n
        if schema2_data:
            self.schema2 = schema2_data
        else:
            # Would load from C_n_gamma.json
            raise ValueError("schema2_data required")

        # Use provided gb_values or default assignment
        if gb_values:
            self.gb_values = gb_values
        else:
            self.gb_values = self._default_gb_assignment()

        self.evaluated_structure_constants = []
        self._evaluate_gamma()

    def _default_gb_assignment(self) -> Dict[str, int]:
        """Generate a representative gb parameter assignment.

        Default: All gb parameters = +1 (parity-preserving choice).
        This represents a canonical evaluation of the deformation.
        """
        gb_values = {}

        for sigma in ['p', 'm']:
            for j in range(1, self.n + 1):
                for s in ['p', 'm']:
                    param_name = f'gb_a1_{sigma}_b{j}_{s}'
                    gb_values[param_name] = 1  # +1 for parity preservation

        return gb_values

    def _evaluate_gamma(self):
        """Substitute gb values into gamma structure and evaluate.

        Creates evaluated_structure_constants by substituting
        concrete values for the symbolic deformation parameters.
        """
        if 'gamma_structure' not in self.schema2:
            return

        gamma_struct = self.schema2['gamma_structure']

        # For each gamma coefficient, substitute gb values
        if 'gamma_coefficients' in gamma_struct:
            for gamma_coeff in gamma_struct['gamma_coefficients']:
                # Clone the coefficient
                eval_coeff = dict(gamma_coeff)

                # Substitute gb values in the coefficient expression
                coeff_expr = eval_coeff.get('coeff', '')

                # Simple substitution (in production, use symbolic algebra)
                for gb_param, gb_val in self.gb_values.items():
                    gb_val_sign = '+1' if gb_val == 1 else '-1'
                    coeff_expr = coeff_expr.replace(gb_param, gb_val_sign)

                eval_coeff['coeff'] = coeff_expr
                eval_coeff['evaluated'] = True

                self.evaluated_structure_constants.append(eval_coeff)

    def to_json(self) -> Dict:
        """Generate complete Schema 3 JSON (evaluated structure)."""
        # Start with Schema 2
        schema3 = json.loads(json.dumps(self.schema2))
        schema3['schema_version'] = '5.0'

        # Add evaluated deformation section
        schema3['evaluated_deformation'] = {
            'description': 'Evaluated structure constants with gb parameter substitution',
            'gb_assignment': {
                'strategy': 'Representative/canonical assignment',
                'note': 'All gb parameters set to +1 (parity-preserving)',
                'values': self.gb_values
            },
            'evaluated_gamma_coefficients': self.evaluated_structure_constants,
            'evaluation_note': 'Gamma coefficients computed with concrete gb values'
        }

        # Update metadata
        schema3['metadata']['generated_by'] = 'src/C_evaluated_generator.py'
        schema3['metadata']['schema_layer'] = 'Schema 3 (Evaluated Structure)'
        schema3['metadata']['evaluation_date'] = '2026-10-05'

        return schema3


def generate_all(schema2_dir: str = 'data', output_dir: str = 'data'):
    """Generate Schema 3 (evaluated) JSON files for n=1, 2, 3."""
    for n in [1, 2, 3]:
        # Load Schema 2
        schema2_file = f'{schema2_dir}/C_{n}_gamma.json'
        with open(schema2_file, 'r') as f:
            schema2_data = json.load(f)

        # Generate Schema 3
        generator = CnEvaluatedGenerator(n, schema2_data)
        schema3 = generator.to_json()

        # Write output
        output_file = f'{output_dir}/C_{n}_evaluated.json'
        with open(output_file, 'w') as f:
            json.dump(schema3, f, indent=2)

        print(f"Generated {output_file}")
        print(f"  Evaluated gamma coefficients: {len(generator.evaluated_structure_constants)}")
        print(f"  GB assignment: canonical (+1 for all parameters)")


if __name__ == '__main__':
    import sys
    schema2_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'data'
    generate_all(schema2_dir, output_dir)
