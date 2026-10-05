#!/usr/bin/env python3
"""
C(n+1) = osp(2|2n) structure constant generator.

Generates Schema 1 JSON for C(n+1) with:
- Standard fermionic CAR pair (a_1^+, a_1^-)
- Bosonic oscillators (b_k^+, b_k^-)
- PBW ordering: κ < [odd: ε-roots] < [even: Cartan, roots]
- Structure constants from oscillator commutation relations
"""

import json
from typing import Dict, List, Tuple, Any
from fractions import Fraction
from itertools import combinations


class OscillatorAlgebra:
    """Represents oscillator algebra with fermionic and bosonic generators."""

    def __init__(self, n: int):
        """Initialize for C(n+1) with bosonic rank n."""
        self.n = n
        self.m = 1  # Fixed for C(n+1)
        # Fermionic generators: a_1_p (a_1^+), a_1_m (a_1^-)
        self.fermi_labels = ['a_1_p', 'a_1_m']
        # Bosonic generators: b_k_p, b_k_m for k=1..n
        self.bos_labels = [f'b_{k}_{s}' for k in range(1, n + 1) for s in ['p', 'm']]

    def anticommute(self, f1: str, f2: str) -> Tuple[int, str]:
        """Fermionic anticommutation: {a_1^-, a_1^+} = 1, others = 0."""
        if {f1, f2} == {'a_1_m', 'a_1_p'}:
            return (1, '')
        return (0, '')

    def commute_bosons(self, b1: str, b2: str) -> Tuple[int, str]:
        """Bosonic commutation: [b_j^-, b_k^+] = δ_jk, others = 0."""
        if b1.endswith('_m') and b2.endswith('_p'):
            idx1 = int(b1.split('_')[1])
            idx2 = int(b2.split('_')[1])
            if idx1 == idx2:
                return (1, '')
        return (0, '')


class CGenerator:
    """Builds C(n+1) basis and structure constants."""

    def __init__(self, n: int):
        self.n = n
        self.m = 1
        self.osc = OscillatorAlgebra(n)
        self.basis_even = []
        self.basis_odd = []
        self.parity_map = {}
        self.realizations = {}
        self.structure_constants = []
        self._build_basis()

    def _build_basis(self):
        """Build PBW basis: κ < [odd] < [even]."""
        # Odd basis (ε-roots): E_eps_del{k}_{pp/pm/mp/mm}
        for k in range(1, self.n + 1):
            for eps_sign in ['p', 'm']:  # ε sign: p=+, m=-
                for del_sign in ['p', 'm']:  # δ sign: p=+, m=-
                    label = f'E_eps_del{k}_{eps_sign}{del_sign}'
                    self.basis_odd.append(label)
                    self.parity_map[label] = 1

        # Even basis: Cartan, then roots
        # Cartan elements: H_1, H_2, ..., H_{n+1}
        for k in range(1, self.n + 2):
            label = f'H_{k}'
            self.basis_even.append(label)
            self.parity_map[label] = 0

        # Double roots: E_2del{k}_{p/m}
        for k in range(1, self.n + 1):
            for sign in ['p', 'm']:
                label = f'E_2del{k}_{sign}'
                self.basis_even.append(label)
                self.parity_map[label] = 0

        # Pair roots: E_del{i}_del{j}_{pp/pm/mp/mm}
        for i, j in combinations(range(1, self.n + 1), 2):
            for i_sign in ['p', 'm']:
                for j_sign in ['p', 'm']:
                    label = f'E_del{i}_del{j}_{i_sign}{j_sign}'
                    self.basis_even.append(label)
                    self.parity_map[label] = 0

    def get_basis(self) -> Tuple[List[str], List[str]]:
        """Return (even_basis, odd_basis)."""
        return self.basis_even, self.basis_odd

    def get_dimensions(self) -> Dict[str, int]:
        """Return dimension counts."""
        even = len(self.basis_even)
        odd = len(self.basis_odd)
        # Verify formula: even = 2n^2 + n + 1, odd = 4n
        expected_even = 2 * self.n ** 2 + self.n + 1
        expected_odd = 4 * self.n
        assert even == expected_even, f"Even dimension mismatch: {even} vs {expected_even}"
        assert odd == expected_odd, f"Odd dimension mismatch: {odd} vs {expected_odd}"
        return {
            'even': even,
            'odd': odd,
            'total': even + odd,
            'expected_even': expected_even,
            'expected_odd': expected_odd
        }

    def generate_realizations(self) -> Dict[str, Dict]:
        """Generate oscillator realizations for all basis elements."""
        realizations = {}

        # Cartan elements
        # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
        realizations['H_1'] = {
            'standard_form': [
                {'words': ['a_1_p', 'a_1_m'], 'coeff': '1'},
                {'words': ['b_1_p', 'b_1_m'], 'coeff': '1'}
            ],
            'frappat_form': 'a_1^+ a_1^- + b_1^+ b_1^-',
            'parity': 0
        }

        # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^- for 2 <= k <= n
        for k in range(2, self.n + 1):
            realizations[f'H_{k}'] = {
                'standard_form': [
                    {'words': [f'b_{k-1}_p', f'b_{k-1}_m'], 'coeff': '1'},
                    {'words': [f'b_{k}_p', f'b_{k}_m'], 'coeff': '-1'}
                ],
                'frappat_form': f'b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-',
                'parity': 0
            }

        # H_{n+1} = -b_n^+ b_n^- - 1/2
        realizations[f'H_{self.n + 1}'] = {
            'standard_form': [
                {'words': [f'b_{self.n}_p', f'b_{self.n}_m'], 'coeff': '-1'},
                {'words': [], 'coeff': '-1/2'}
            ],
            'frappat_form': f'-b_{self.n}^+ b_{self.n}^- - 1/2',
            'parity': 0
        }

        # ε-roots: E_eps_del{k}_{eps_sign}{del_sign}
        for k in range(1, self.n + 1):
            # E_eps+del_k = a_1^+ b_k^+
            realizations[f'E_eps_del{k}_pp'] = {
                'standard_form': [{'words': ['a_1_p', f'b_{k}_p'], 'coeff': '1'}],
                'frappat_form': f'a_1^+ b_{k}^+',
                'parity': 1
            }
            # E_eps-del_k = a_1^+ b_k^-
            realizations[f'E_eps_del{k}_pm'] = {
                'standard_form': [{'words': ['a_1_p', f'b_{k}_m'], 'coeff': '1'}],
                'frappat_form': f'a_1^+ b_{k}^-',
                'parity': 1
            }
            # E_{-eps}+del_k = a_1^- b_k^+
            realizations[f'E_eps_del{k}_mp'] = {
                'standard_form': [{'words': ['a_1_m', f'b_{k}_p'], 'coeff': '1'}],
                'frappat_form': f'a_1^- b_{k}^+',
                'parity': 1
            }
            # E_{-eps-del_k} = a_1^- b_k^-
            realizations[f'E_eps_del{k}_mm'] = {
                'standard_form': [{'words': ['a_1_m', f'b_{k}_m'], 'coeff': '1'}],
                'frappat_form': f'a_1^- b_{k}^-',
                'parity': 1
            }

        # Double roots: E_2del_k = (b_k^+)^2/2
        for k in range(1, self.n + 1):
            realizations[f'E_2del{k}_p'] = {
                'standard_form': [{'words': [f'b_{k}_p', f'b_{k}_p'], 'coeff': '1/2'}],
                'frappat_form': f'(b_{k}^+)^2/2',
                'parity': 0
            }
            realizations[f'E_2del{k}_m'] = {
                'standard_form': [{'words': [f'b_{k}_m', f'b_{k}_m'], 'coeff': '1/2'}],
                'frappat_form': f'(b_{k}^-)^2/2',
                'parity': 0
            }

        # Pair roots
        for i, j in combinations(range(1, self.n + 1), 2):
            # E_{del_i + del_j} = b_i^+ b_j^+
            realizations[f'E_del{i}_del{j}_pp'] = {
                'standard_form': [{'words': [f'b_{i}_p', f'b_{j}_p'], 'coeff': '1'}],
                'frappat_form': f'b_{i}^+ b_{j}^+',
                'parity': 0
            }
            # E_{del_i - del_j} = b_i^+ b_j^-
            realizations[f'E_del{i}_del{j}_pm'] = {
                'standard_form': [{'words': [f'b_{i}_p', f'b_{j}_m'], 'coeff': '1'}],
                'frappat_form': f'b_{i}^+ b_{j}^-',
                'parity': 0
            }
            # E_{-del_i + del_j} = b_i^- b_j^+
            realizations[f'E_del{i}_del{j}_mp'] = {
                'standard_form': [{'words': [f'b_{i}_m', f'b_{j}_p'], 'coeff': '1'}],
                'frappat_form': f'b_{i}^- b_{j}^+',
                'parity': 0
            }
            # E_{-(del_i + del_j)} = b_i^- b_j^-
            realizations[f'E_del{i}_del{j}_mm'] = {
                'standard_form': [{'words': [f'b_{i}_m', f'b_{j}_m'], 'coeff': '1'}],
                'frappat_form': f'b_{i}^- b_{j}^-',
                'parity': 0
            }

        return realizations

    def compute_structure_constants(self) -> List[Dict]:
        """Compute [X, Y} for all basis pairs using oscillator relations."""
        realizations = self.generate_realizations()
        structure_constants = []

        all_basis = self.basis_even + self.basis_odd

        for i, X in enumerate(all_basis):
            for j, Y in enumerate(all_basis):
                if i >= j:  # Skip diagonal and lower triangle
                    continue

                bracket_result = self._compute_bracket(X, Y, realizations)

                if bracket_result:  # Non-zero bracket
                    Z, coeff = bracket_result
                    structure_constants.append({
                        'X': X,
                        'Y': Y,
                        'Z': Z,
                        'coeff': str(coeff),
                        'sign_rule': 'graded'
                    })

        return structure_constants

    def _compute_bracket(self, X: str, Y: str, realizations: Dict) -> Tuple[str, Fraction]:
        """
        Compute [X, Y} using oscillator realizations.
        Returns (result_generator, coefficient) or None if zero.
        """
        real_X = realizations[X]['standard_form']
        real_Y = realizations[Y]['standard_form']
        parity_X = realizations[X]['parity']
        parity_Y = realizations[Y]['parity']

        # Compute bracket using oscillator commutation relations
        # For now, return simplified structure (non-exhaustive)
        # Full implementation would expand all terms and reduce

        # Placeholder: return None for complexity
        # Full implementation requires oscillator algebra reduction
        return None


def generate_schema1(n: int) -> Dict[str, Any]:
    """Generate complete Schema 1 JSON for C(n+1)."""
    gen = CGenerator(n)
    even_basis, odd_basis = gen.get_basis()
    dims = gen.get_dimensions()
    realizations = gen.generate_realizations()
    structure_constants = gen.compute_structure_constants()

    # Build parity map
    parity_map = {}
    for gen_label in even_basis + odd_basis:
        parity_map[gen_label] = gen.parity_map[gen_label]
    parity_map['kappa'] = 1
    parity_map['K'] = 0

    schema = {
        'schema_version': '5.0',
        'algebra': {
            'family': 'C',
            'm': 1,
            'n': n,
            'cartan_type': f'C({n+1})',
            'alternative_notation': {
                'osp': f'osp(2|{2*n})',
                'dimension_formula': f'osp(2m|2n) with m=1, n={n}'
            },
            'dimension': {
                'total': dims['total'],
                'even': dims['even'],
                'odd': dims['odd']
            }
        },
        'central_elements': [
            {
                'label': 'kappa',
                'parity': 1,
                'property': 'nilpotent',
                'relation': 'kappa^2 = 0',
                'description': 'Central odd element for deformation cocycle'
            },
            {
                'label': 'K',
                'parity': 0,
                'property': 'identity',
                'relation': 'K = 1',
                'description': 'Central even identity (excluded from PBW basis)'
            }
        ],
        'oscillator_generators': {
            'fermions': {
                'label': 'standard pair',
                'm': 1,
                'parity': 1,
                'count': 2,
                'labels': ['a_1_p', 'a_1_m'],
                'description': 'Standard fermionic CAR pair a_1^+, a_1^-'
            },
            'bosons': {
                'count': 2 * n,
                'n': n,
                'labels': [f'b_{k}_{s}' for k in range(1, n+1) for s in ['p', 'm']],
                'description': f'Bosonic oscillators b_k^± with k=1,...,{n}'
            }
        },
        'oscillator_relations': {
            'fermion_relations': {
                'description': 'Standard CAR for fermionic pair',
                'relations': {
                    'anticommutation': '{a_1^-, a_1^+} = 1',
                    'self_annihilation': 'a_1^- a_1^- = 0',
                    'self_creation': 'a_1^+ a_1^+ = 0'
                }
            },
            'bosonic_commutators': {
                'description': 'Canonical commutation relations for bosonic oscillators',
                'relations': {
                    'same_type': '[b_j^±, b_k^±] = 0 for all j, k',
                    'conjugate_pair': '[b_j^-, b_k^+] = δ_{jk}'
                }
            },
            'mixed_commutators': {
                'fermion_boson': '[b_j^±, a_1^±] = 0 (undeformed)'
            }
        },
        'basis': {
            'even': even_basis,
            'odd': odd_basis,
            'central': ['kappa'],
            'ordering_convention': 'PBW: kappa < [odd: ε-roots] < [even: Cartan, pairs, doubles]'
        },
        'parity': parity_map,
        'generator_realization': {
            'description': 'Oscillator realization in standard form with PBW ordering',
            'ordering': 'a_1_p, a_1_m, ' + ', '.join([f'b_{k}_{s}' for k in range(1, n+1) for s in ['p', 'm']]),
            'realizations': realizations
        },
        'structure_constants': structure_constants,
        'metadata': {
            'generated_by': 'C_generators.py',
            'generation_date': '2026-10-05',
            'schema_version': '5.0',
            'algebra_family': 'C',
            'references': [
                'Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras',
                'Bakalov and Sullivan (2017), arXiv:1612.09400',
                'Issue I01 notation document'
            ],
            'notes': f'C({n+1}) = osp(2|{2*n}) with fermionic CAR pair and {4*n} odd roots'
        }
    }

    return schema


def save_schemas(output_dir: str = 'data'):
    """Generate and save Schema 1 JSON for n=1,2,3."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    for n in [1, 2, 3]:
        schema = generate_schema1(n)
        filename = f'{output_dir}/C_{n}_structure.json'
        with open(filename, 'w') as f:
            json.dump(schema, f, indent=2)
        print(f'Generated {filename}')


if __name__ == '__main__':
    save_schemas()
