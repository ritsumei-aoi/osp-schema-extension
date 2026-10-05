#!/usr/bin/env python3
"""
Schema 2: Gamma (Inhomogeneous Deformation) Structure for C(n+1).

Generates deformation parameters and gamma coefficients from Schema 1.
The deformation is defined by exchange relations:
  [b_j^s, a_1^σ] = -gb_{σ,j,s} * κ
where gb parameters have parity 1 (odd).
"""

import json
from typing import Dict, List, Any
from fractions import Fraction


class GammaStructure:
    """Builds Schema 2 gamma structure from Schema 1."""

    def __init__(self, n: int, schema1_data: Dict):
        """Initialize from Schema 1 data."""
        self.n = n
        self.schema1 = schema1_data
        self.m = 1  # Fixed for C(n+1)

    def build_gb_matrix(self) -> Dict[str, Any]:
        """
        Build gb_matrix (4n deformation parameters).

        Parameters indexed by:
        - Fermionic oscillator: a_1^+, a_1^-
        - Bosonic oscillator index j: 1, ..., n
        - Bosonic sign: +, -

        Total: 2 * 2n = 4n parameters
        """
        parameters = []

        for fermion_sign in ['p', 'm']:  # a_1^+ (p), a_1^- (m)
            for boson_idx in range(1, self.n + 1):
                for boson_sign in ['p', 'm']:  # b_k^+ (p), b_k^- (m)
                    label = f"gb_a1{fermion_sign}_b{boson_idx}{boson_sign}"

                    # Symbolic encoding
                    if fermion_sign == 'p':
                        fermi_label = f'a_1_p'
                    else:
                        fermi_label = f'a_1_m'

                    if boson_sign == 'p':
                        bos_label = f'b_{boson_idx}_p'
                    else:
                        bos_label = f'b_{boson_idx}_m'

                    parameters.append({
                        'label': label,
                        'fermion': fermi_label,
                        'boson': bos_label,
                        'parity': 1,  # All gb parameters are odd
                        'index': (fermion_sign, boson_idx, boson_sign)
                    })

        return {
            'description': 'Inhomogeneous deformation parameters',
            'size': [2, 2, self.n],
            'total_count': 4 * self.n,
            'parity': 1,
            'parameters': parameters
        }

    def compute_gamma_coefficients(self) -> List[Dict[str, Any]]:
        """
        Compute gamma coefficients γ_{XYZ} for the 2-cocycle.

        These encode how the bracket [X, Y} = [X, Y]_0 + κ * γ(X, Y).

        For C(n+1), the main non-zero gamma terms arise from:
        1. Cartan-odd generator brackets
        2. Fermionic interactions
        """
        gamma_terms = []

        # Sample gamma terms based on root structure
        # Full computation would require complete bracket algebra

        # Type 1: Cartan elements with ε-roots
        # [H_1, E_eps_del{k}_{...}] may produce gamma contributions

        for k in range(1, self.n + 1):
            for eps_sign in ['p', 'm']:
                for del_sign in ['p', 'm']:
                    odd_gen = f'E_eps_del{k}_{eps_sign}{del_sign}'

                    # [H_1, E_eps_del{k}_{...}]
                    gamma_terms.append({
                        'X': 'H_1',
                        'Y': odd_gen,
                        'gamma_symbolic': f'gb_a1{eps_sign}_b{k}{del_sign}',
                        'gamma_description': f'Deformation from [a_1 interaction with b_{k}]',
                        'involves_kappa': True
                    })

        # Type 2: Odd-odd brackets
        # [E_eps_del{i}_{...}, E_eps_del{j}_{...}] may produce gamma contributions

        for i in range(1, self.n + 1):
            for j in range(i + 1, self.n + 1):
                for i_signs in ['pp', 'pm', 'mp', 'mm']:
                    for j_signs in ['pp', 'pm', 'mp', 'mm']:
                        X = f'E_eps_del{i}_{i_signs}'
                        Y = f'E_eps_del{j}_{j_signs}'

                        # Gamma terms from fermionic interactions
                        # These would involve products of gb parameters
                        # Placeholder: only main interactions

                        if i_signs[0] == 'p' and j_signs[0] == 'm':  # a_1^+ * a_1^-
                            gamma_terms.append({
                                'X': X,
                                'Y': Y,
                                'gamma_symbolic': f'{{gb_a1p_b{i}{i_signs[1]}, gb_a1m_b{j}{j_signs[1]}}}',
                                'gamma_description': f'Anticommutator interaction',
                                'involves_kappa': True
                            })

        return gamma_terms

    def build_schema2(self) -> Dict[str, Any]:
        """Build complete Schema 2 JSON."""
        schema2 = self.schema1.copy()

        # Add deformation-specific fields
        schema2['deformation_parameters'] = {
            'gb_matrix': self.build_gb_matrix()
        }

        schema2['gamma_coefficients'] = {
            'description': '2-cocycle coefficients γ(X, Y) for inhomogeneous deformation',
            'definition': '[X, Y]_γ = [X, Y]_0 + κ · γ(X, Y)',
            'data': self.compute_gamma_coefficients()
        }

        # Update metadata
        schema2['metadata']['schema_type'] = 'Schema 2: Gamma Deformation'
        schema2['metadata']['deformation_type'] = 'inhomogeneous'
        schema2['metadata']['notes'] = f'C({self.n+1}) = osp(2|{2*self.n}) with 4n={4*self.n} deformation parameters'

        return schema2


def generate_schema2_files(output_dir: str = 'data'):
    """Generate Schema 2 JSON files for n=1, 2, 3."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    for n in [1, 2, 3]:
        # Load Schema 1
        schema1_file = f'{output_dir}/C_{n}_structure.json'
        with open(schema1_file, 'r') as f:
            schema1 = json.load(f)

        # Generate Schema 2
        gamma_gen = GammaStructure(n, schema1)
        schema2 = gamma_gen.build_schema2()

        # Save Schema 2
        schema2_file = f'{output_dir}/C_{n}_gamma.json'
        with open(schema2_file, 'w') as f:
            json.dump(schema2, f, indent=2)

        print(f'Generated {schema2_file}')

        # Report gamma structure
        gb_count = len(schema2['deformation_parameters']['gb_matrix']['parameters'])
        gamma_count = len(schema2['gamma_coefficients']['data'])
        print(f'  gb_matrix: {gb_count} parameters')
        print(f'  gamma_coefficients: {gamma_count} terms')


if __name__ == '__main__':
    generate_schema2_files()
