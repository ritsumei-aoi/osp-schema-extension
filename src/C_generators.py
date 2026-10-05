#!/usr/bin/env python3
"""
C(n+1) = osp(2|2n) structure constant generator.

Generates Schema 1 JSON files for C(n+1) based on oscillator realization.
Following the notation and PBW ordering defined in handover/notation.md.
"""

import json
from fractions import Fraction
from typing import Dict, List, Tuple, Set
from collections import defaultdict


class OscillatorWord:
    """Represents a product of oscillator generators in PBW order."""

    def __init__(self, factors: List[str] = None):
        """factors: list of oscillator labels like ['a_1_p', 'b_1_m', ...]"""
        self.factors = factors if factors else []
        self.normalize()

    def normalize(self):
        """Normalize to PBW order: a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m"""
        # PBW ordering priority
        priority = {
            'a_1_p': 0, 'a_1_m': 1,
        }
        for i in range(1, 10):  # support up to n=9
            priority[f'b_{i}_p'] = 2 + 2*(i-1)
            priority[f'b_{i}_m'] = 2 + 2*(i-1) + 1

        self.factors.sort(key=lambda x: priority.get(x, 100))

    def __eq__(self, other):
        return isinstance(other, OscillatorWord) and self.factors == other.factors

    def __hash__(self):
        return hash(tuple(self.factors))

    def __repr__(self):
        return 'OscillatorWord(' + ' '.join(self.factors) + ')'

    def commute_pair(self, other: 'OscillatorWord') -> Tuple['OscillatorWord', Fraction]:
        """Anticommute two words and return (result, coefficient)."""
        # This is a simplified version; full PBW expansion would be needed for production
        return other, Fraction(1)


class CnGenerator:
    """Generator for C(n+1) = osp(2|2n) structure constants."""

    def __init__(self, n: int):
        self.n = n
        self.basis_even = []
        self.basis_odd = []
        self.parity = {}
        self.realizations = {}
        self.structure_constants = []
        self._build_basis()

    def _build_basis(self):
        """Build the basis following PBW ordering from handover/notation.md."""
        # Even basis: Cartan elements and even roots
        self.basis_even = []

        # Cartan elements: H_1, ..., H_{n+1}
        for k in range(1, self.n + 2):
            gen = f"H_{k}"
            self.basis_even.append(gen)
            self.parity[gen] = 0

        # Even roots: E_{±2δ_k}
        for k in range(1, self.n + 1):
            for sign in ['p', 'm']:
                gen = f"E_2del{k}_{sign}"
                self.basis_even.append(gen)
                self.parity[gen] = 0

        # Even roots: E_{±(δ_i ± δ_j)} for i < j
        for i in range(1, self.n + 1):
            for j in range(i + 1, self.n + 1):
                for sign_i in ['p', 'm']:
                    for sign_j in ['p', 'm']:
                        gen = f"E_del{i}_del{j}_{sign_i}{sign_j}"
                        self.basis_even.append(gen)
                        self.parity[gen] = 0

        # Odd basis: E_{±ε ± δ_k}
        self.basis_odd = []
        for k in range(1, self.n + 1):
            for sign_eps in ['p', 'm']:
                for sign_delta in ['p', 'm']:
                    gen = f"E_eps_del{k}_{sign_eps}{sign_delta}"
                    self.basis_odd.append(gen)
                    self.parity[gen] = 1

    def _build_realizations(self):
        """Build oscillator realizations for all generators."""
        # Cartan H_1
        self.realizations['H_1'] = {
            'standard_form': [
                {'words': ['a_1_p', 'a_1_m'], 'coeff': '1'},
                {'words': ['b_1_p', 'b_1_m'], 'coeff': '1'}
            ],
            'frappat_form': 'a_1^+ a_1^- + b_1^+ b_1^-',
            'parity': 0
        }

        # Cartan H_k for 2 <= k <= n
        for k in range(2, self.n + 1):
            self.realizations[f'H_{k}'] = {
                'standard_form': [
                    {'words': [f'b_{k-1}_p', f'b_{k-1}_m'], 'coeff': '1'},
                    {'words': [f'b_{k}_p', f'b_{k}_m'], 'coeff': '-1'}
                ],
                'frappat_form': f'b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-',
                'parity': 0
            }

        # Cartan H_{n+1} (terminal)
        self.realizations[f'H_{self.n+1}'] = {
            'standard_form': [
                {'words': [f'b_{self.n}_p', f'b_{self.n}_m'], 'coeff': '-1'},
                {'words': [], 'coeff': '-1/2'}
            ],
            'frappat_form': f'-b_{self.n}^+ b_{self.n}^- - 1/2',
            'parity': 0,
            'note': 'Terminal Cartan; includes constant term'
        }

        # Even roots E_{±2δ_k}
        for k in range(1, self.n + 1):
            coeff = '1/2' if k == self.n else '1'
            self.realizations[f'E_2del{k}_p'] = {
                'standard_form': [
                    {'words': [f'b_{k}_p', f'b_{k}_p'], 'coeff': coeff}
                ],
                'frappat_form': f'({coeff})(b_{k}^+)^2',
                'parity': 0
            }
            self.realizations[f'E_2del{k}_m'] = {
                'standard_form': [
                    {'words': [f'b_{k}_m', f'b_{k}_m'], 'coeff': coeff}
                ],
                'frappat_form': f'({coeff})(b_{k}^-)^2',
                'parity': 0
            }

        # Even roots E_{±(δ_i ± δ_j)} for i < j
        for i in range(1, self.n + 1):
            for j in range(i + 1, self.n + 1):
                self.realizations[f'E_del{i}_del{j}_pp'] = {
                    'standard_form': [
                        {'words': [f'b_{i}_p', f'b_{j}_p'], 'coeff': '1'}
                    ],
                    'frappat_form': f'b_{i}^+ b_{j}^+',
                    'parity': 0
                }
                self.realizations[f'E_del{i}_del{j}_pm'] = {
                    'standard_form': [
                        {'words': [f'b_{i}_p', f'b_{j}_m'], 'coeff': '1'}
                    ],
                    'frappat_form': f'b_{i}^+ b_{j}^-',
                    'parity': 0
                }
                self.realizations[f'E_del{i}_del{j}_mp'] = {
                    'standard_form': [
                        {'words': [f'b_{i}_m', f'b_{j}_p'], 'coeff': '1'}
                    ],
                    'frappat_form': f'b_{i}^- b_{j}^+',
                    'parity': 0
                }
                self.realizations[f'E_del{i}_del{j}_mm'] = {
                    'standard_form': [
                        {'words': [f'b_{i}_m', f'b_{j}_m'], 'coeff': '1'}
                    ],
                    'frappat_form': f'b_{i}^- b_{j}^-',
                    'parity': 0
                }

        # Odd roots E_{±ε ± δ_k}
        for k in range(1, self.n + 1):
            self.realizations[f'E_eps_del{k}_pp'] = {
                'standard_form': [
                    {'words': ['a_1_p', f'b_{k}_p'], 'coeff': '1'}
                ],
                'frappat_form': f'a_1^+ b_{k}^+',
                'parity': 1
            }
            self.realizations[f'E_eps_del{k}_pm'] = {
                'standard_form': [
                    {'words': ['a_1_p', f'b_{k}_m'], 'coeff': '1'}
                ],
                'frappat_form': f'a_1^+ b_{k}^-',
                'parity': 1
            }
            self.realizations[f'E_eps_del{k}_mp'] = {
                'standard_form': [
                    {'words': ['a_1_m', f'b_{k}_p'], 'coeff': '1'}
                ],
                'frappat_form': f'a_1^- b_{k}^+',
                'parity': 1
            }
            self.realizations[f'E_eps_del{k}_mm'] = {
                'standard_form': [
                    {'words': ['a_1_m', f'b_{k}_m'], 'coeff': '1'}
                ],
                'frappat_form': f'a_1^- b_{k}^-',
                'parity': 1
            }

    def _compute_structure_constants(self):
        """Compute basic structure constants for verification.

        For now, compute key Cartan-root relations.
        Full computation will be in Schema 2 with deformation parameters.
        """
        self.structure_constants = []

        # Key Cartan-root relations for verification
        # [H_1, E_eps_del{k}_{pp}] = E_eps_del{k}_{pp}  (eps weight +1)
        # [H_1, E_eps_del{k}_{pm}] = E_eps_del{k}_{pm}
        # [H_1, E_eps_del{k}_{mp}] = -E_eps_del{k}_{mp}  (eps weight -1)
        # [H_1, E_eps_del{k}_{mm}] = -E_eps_del{k}_{mm}

        for k in range(1, self.n + 1):
            # H_1 acting on fermionic generators (forward)
            self.structure_constants.append({
                'X': 'H_1',
                'Y': f'E_eps_del{k}_pp',
                'Z': f'E_eps_del{k}_pp',
                'coeff': '1',
                'sign_rule': 'graded'
            })
            self.structure_constants.append({
                'X': 'H_1',
                'Y': f'E_eps_del{k}_pm',
                'Z': f'E_eps_del{k}_pm',
                'coeff': '1',
                'sign_rule': 'graded'
            })
            self.structure_constants.append({
                'X': 'H_1',
                'Y': f'E_eps_del{k}_mp',
                'Z': f'E_eps_del{k}_mp',
                'coeff': '-1',
                'sign_rule': 'graded'
            })
            self.structure_constants.append({
                'X': 'H_1',
                'Y': f'E_eps_del{k}_mm',
                'Z': f'E_eps_del{k}_mm',
                'coeff': '-1',
                'sign_rule': 'graded'
            })

            # Inverse relations: [E_eps_del{k}_*, H_1]
            # By graded anti-symmetry: [E, H} = -(-1)^(p(E)p(H))[H, E}
            # Since p(E)=1, p(H)=0: [E, H} = -[H, E}
            self.structure_constants.append({
                'X': f'E_eps_del{k}_pp',
                'Y': 'H_1',
                'Z': f'E_eps_del{k}_pp',
                'coeff': '-1',
                'sign_rule': 'graded'
            })
            self.structure_constants.append({
                'X': f'E_eps_del{k}_pm',
                'Y': 'H_1',
                'Z': f'E_eps_del{k}_pm',
                'coeff': '-1',
                'sign_rule': 'graded'
            })
            self.structure_constants.append({
                'X': f'E_eps_del{k}_mp',
                'Y': 'H_1',
                'Z': f'E_eps_del{k}_mp',
                'coeff': '1',
                'sign_rule': 'graded'
            })
            self.structure_constants.append({
                'X': f'E_eps_del{k}_mm',
                'Y': 'H_1',
                'Z': f'E_eps_del{k}_mm',
                'coeff': '1',
                'sign_rule': 'graded'
            })

    def _get_dimension(self) -> Tuple[int, int, int]:
        """Get dimensions: (even, odd, total)."""
        even = 2 * self.n * self.n + self.n + 1
        odd = 4 * self.n
        total = even + odd
        return even, odd, total

    def to_json(self) -> Dict:
        """Generate complete Schema 1 JSON structure."""
        self._build_realizations()
        self._compute_structure_constants()

        even_dim, odd_dim, total_dim = self._get_dimension()

        return {
            'schema_version': '5.0',
            'algebra': {
                'family': 'C',
                'm': 1,
                'n': self.n,
                'cartan_type': f'C({self.n + 1})',
                'alternative_notation': {
                    'osp': f'osp(2|{2*self.n})',
                    'dimension_formula': 'osp(2m|2n) with m=1'
                },
                'dimension': {
                    'total': total_dim,
                    'even': even_dim,
                    'odd': odd_dim
                }
            },
            'oscillator_generators': {
                'fermions': {
                    'count': 2,
                    'm': 1,
                    'labels': ['a_1_p', 'a_1_m'],
                    'parity': 1,
                    'relation': '{a_1^-, a_1^+} = 1',
                    'description': 'Standard fermionic pair under CAR'
                },
                'bosons': {
                    'count': 2 * self.n,
                    'n': self.n,
                    'labels': [f'b_{k}_{s}' for k in range(1, self.n + 1) for s in ['p', 'm']],
                    'description': f'Bosonic oscillators b_i^± with i=1,...,{self.n}'
                }
            },
            'oscillator_relations': {
                'standard_fermion_anticommutators': {
                    'description': 'CAR for fermionic pair',
                    'relations': {
                        'standard_car': '{a_1^-, a_1^+} = 1',
                        'self': '{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0'
                    }
                },
                'bosonic_commutators': {
                    'description': 'CCR for bosonic oscillators',
                    'relations': {
                        'same_type': '[b_i^+, b_j^+] = 0, [b_i^-, b_j^-] = 0',
                        'conjugate_pair': '[b_i^-, b_j^+] = δ_{ij}'
                    }
                },
                'mixed_commutators': {
                    'boson_fermion': '[b_i^±, a_1^±] = 0'
                }
            },
            'central_elements': {
                'kappa': {
                    'symbol': 'κ',
                    'parity': 1,
                    'nilpotency': 'κ² = 0',
                    'description': 'Odd central element for deformation'
                },
                'K': {
                    'symbol': 'K',
                    'parity': 0,
                    'description': 'Even central identity'
                }
            },
            'basis': {
                'even': self.basis_even,
                'odd': self.basis_odd,
                'ordering_convention': 'PBW: κ < [odd generators] < [even generators]'
            },
            'parity': self.parity,
            'generator_realization': {
                'description': 'Oscillator realization in standard PBW form',
                'ordering': 'a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m',
                'realizations': self.realizations
            },
            'structure_constants': self.structure_constants,
            'metadata': {
                'generated_by': 'src/C_generators.py',
                'generation_date': '2026-10-05',
                'references': [
                    'Frappat, Sciarrino, Sorba (2000)',
                    'docs/math/Cn1_definition.md'
                ]
            }
        }


def generate_all(output_dir: str = 'data'):
    """Generate Schema 1 JSON files for n=1, 2, 3."""
    for n in [1, 2, 3]:
        generator = CnGenerator(n)
        schema = generator.to_json()

        filename = f'{output_dir}/C_{n}_structure.json'
        with open(filename, 'w') as f:
            json.dump(schema, f, indent=2)

        print(f"Generated {filename}")
        print(f"  Dimensions: even={schema['algebra']['dimension']['even']}, " +
              f"odd={schema['algebra']['dimension']['odd']}, " +
              f"total={schema['algebra']['dimension']['total']}")


if __name__ == '__main__':
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    generate_all(output_dir)
