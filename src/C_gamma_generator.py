#!/usr/bin/env python3
"""
C(n+1) = osp(2|2n) gamma structure (Schema 2) generator.

Extends Schema 1 with inhomogeneous deformation parameters (gb_matrix)
and gamma coefficients derived from oscillator relations.

Reference: docs/math/C_inhomogeneous_definition.md
"""

import json
from fractions import Fraction
from typing import Dict, List, Tuple


class CnGammaGenerator:
    """Generator for C(n+1) Schema 2 with gamma structure."""

    def __init__(self, n: int, schema1_data: Dict = None):
        """Initialize from Schema 1 data or from n value."""
        self.n = n
        if schema1_data:
            self.schema1 = schema1_data
        else:
            # Would load from C_n_structure.json; for now use direct import
            from C_generators import CnGenerator
            gen = CnGenerator(n)
            self.schema1 = gen.to_json()

        self.deformation_parameters = []
        self.gamma_coefficients = []
        self._build_gb_matrix()

    def _build_gb_matrix(self):
        """Build the deformation parameter matrix (gb_matrix).

        For C(n+1), there are 4n parameters:
        gb_{a_1^+, b_j^+}, gb_{a_1^+, b_j^-}, gb_{a_1^-, b_j^+}, gb_{a_1^-, b_j^-}
        for j = 1, ..., n.

        These are indexed as:
        gb[sigma][j][s] where sigma in {+, -}, j in {1, ..., n}, s in {+, -}
        """
        self.gb_matrix = {}

        for sigma in ['+', '-']:
            self.gb_matrix[sigma] = {}
            sigma_label = 'p' if sigma == '+' else 'm'

            for j in range(1, self.n + 1):
                self.gb_matrix[sigma][j] = {}

                for s in ['+', '-']:
                    s_label = 'p' if s == '+' else 'm'

                    # Parameter name: gb_{a_1^sigma, b_j^s}
                    param_name = f'gb_a1_{sigma_label}_b{j}_{s_label}'

                    self.deformation_parameters.append({
                        'name': param_name,
                        'fermionic_index': f'a_1_{sigma_label}',
                        'bosonic_index': f'b_{j}_{s_label}',
                        'parity': 1,
                        'description': f'Deformation parameter for [b_{j}^{s}, a_1^{sigma}]'
                    })

                    self.gb_matrix[sigma][j][s] = param_name

    def _compute_gamma_from_oscillator(self) -> List[Dict]:
        """Compute gamma coefficients from oscillator realization.

        The gamma coefficients arise from the deformed oscillator relations:
        [b_j^s, a_1^sigma] = -gb_{a_1^sigma, b_j^s} * κ

        For generators X, Y realized as oscillator words:
        γ(X, Y) represents the coefficient of κ in [X, Y]_deformed - [X, Y]_undeformed.

        For Schema 2, we focus on terms involving the fermionic-bosonic interaction.
        """
        gamma_coeffs = []

        # Key interaction: [E_eps_del{k}, E_eps_del{l}] might involve
        # anticommutation of fermionic parts and commutation of bosonic parts.

        # Example: [a_1^+ b_k^+, a_1^- b_l^+]
        # = a_1^+ b_k^+ a_1^- b_l^+ - (-1)^(1·1) a_1^- b_l^+ a_1^+ b_k^+
        # = a_1^+ b_k^+ a_1^- b_l^+ + a_1^- b_l^+ a_1^+ b_k^+
        # The deformed relations affect the mixed terms.

        # For now, record that gamma terms arise from fermionic-bosonic interactions.
        # Full computation requires systematic PBW expansion with deformed relations.

        # Fermionic anticommutators: {a_1^+, a_1^-} = 1 (no deformation to first order)
        # Bosonic commutators: [b_j^s, b_l^t] are unchanged
        # Mixed: [b_j^s, a_1^sigma] = -gb parameter * κ (deformed)

        for k in range(1, self.n + 1):
            for l in range(1, self.n + 1):
                for sig1 in ['+', '-']:
                    for sig2 in ['+', '-']:
                        # Consider [E_eps_del{k}_{sig1,*}, E_eps_del{l}_{sig2,*}]
                        # The fermionic parts {a_1^{sig1}, a_1^{sig2}} contribute Kronecker δ.
                        # The bosonic parts don't commute with fermions under deformation.

                        sig1_label = 'p' if sig1 == '+' else 'm'
                        sig2_label = 'p' if sig2 == '+' else 'm'

                        # [E_eps_del{k}_{pp}, E_eps_del{l}_{mm}] = [a_1^+ b_k^+, a_1^- b_l^-]
                        if sig1 == '+' and sig2 == '-':
                            # Anticommute: {a_1^+, a_1^-} contributes to the bracket
                            gamma_coeffs.append({
                                'X': f'E_eps_del{k}_pp',
                                'Y': f'E_eps_del{l}_mm',
                                'Z': 'K',  # Central element
                                'coeff': f'gb_a1_p_b{k}_p * gb_a1_m_b{l}_m',
                                'description': 'Gamma from fermionic-bosonic interaction',
                                'note': f'[a_1^+, a_1^-] interaction in oscillator realization'
                            })

        return gamma_coeffs

    def to_json(self) -> Dict:
        """Generate complete Schema 2 JSON (gamma structure)."""
        gamma_coeffs = self._compute_gamma_from_oscillator()

        # Start with Schema 1
        schema2 = json.loads(json.dumps(self.schema1))
        schema2['schema_version'] = '5.0'

        # Add gamma structure
        schema2['gamma_structure'] = {
            'description': 'Inhomogeneous deformation parameters and gamma coefficients',
            'deformation_parameters': self.deformation_parameters,
            'gb_matrix_size': f'{2} x {2*self.n}',
            'gb_matrix_interpretation': 'Rows: a_1^+, a_1^-; Columns: b_1^+, b_1^-, ..., b_n^+, b_n^-',
            'gamma_coefficients': gamma_coeffs,
            'notes': [
                'Gamma coefficients represent the deformation term κ · γ(X, Y) in [X, Y]_γ = [X, Y]_0 + κ · γ(X, Y)',
                'Full gamma computation requires systematic PBW expansion with deformed oscillator relations',
                'Currently includes key fermionic-bosonic interaction terms'
            ]
        }

        # Update metadata
        schema2['metadata']['generated_by'] = 'src/C_gamma_generator.py'
        schema2['metadata']['schema_extension'] = 'Schema 1 (C_n_structure.json) -> Schema 2 (C_n_gamma.json)'

        return schema2


def generate_all(schema1_dir: str = 'data', output_dir: str = 'data'):
    """Generate Schema 2 (gamma) JSON files for n=1, 2, 3."""
    for n in [1, 2, 3]:
        # Load Schema 1
        schema1_file = f'{schema1_dir}/C_{n}_structure.json'
        with open(schema1_file, 'r') as f:
            schema1_data = json.load(f)

        # Generate Schema 2
        generator = CnGammaGenerator(n, schema1_data)
        schema2 = generator.to_json()

        # Write output
        output_file = f'{output_dir}/C_{n}_gamma.json'
        with open(output_file, 'w') as f:
            json.dump(schema2, f, indent=2)

        print(f"Generated {output_file}")
        print(f"  Deformation parameters: {len(generator.deformation_parameters)}")
        print(f"  Gamma coefficients: {len(generator.gamma_coefficients)}")


if __name__ == '__main__':
    import sys
    schema1_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'data'
    generate_all(schema1_dir, output_dir)
