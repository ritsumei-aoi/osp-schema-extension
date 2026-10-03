#!/usr/bin/env python3
"""
C_generators.py: Generate C(n+1) = osp(2|2n) structure constants and output Schema 1 JSON.

Oscillator convention:
  Indices: 0=a1p, 1=a1m, 2=b1p, 3=b1m, 4=b2p, 5=b2m, ..., 2k=bkp, 2k+1=bkm
  PBW order: a1p < a1m < b1p < b1m < b2p < b2m < ...

Relations:
  {a1p, a1m} = 1,  a1p^2 = 0,  a1m^2 = 0
  [bkm, bkp] = 1  (i.e. bkm*bkp = bkp*bkm + 1)
  [a1pm, bkpm] = 0  (mixed boson-fermion commute)
"""

import json
import os
from fractions import Fraction
from itertools import combinations
from collections import defaultdict
from datetime import date


class CnPlusOne:
    """Oscillator algebra realization of C(n+1) = osp(2|2n)."""

    def __init__(self, n):
        self.n = n
        # Build oscillator label list: a1p(0), a1m(1), b1p(2), b1m(3), ...
        self.osc_labels = ['a1p', 'a1m']
        for k in range(1, n + 1):
            self.osc_labels.append(f'b{k}p')
            self.osc_labels.append(f'b{k}m')
        self.num_osc = len(self.osc_labels)
        # Parity: index 0,1 are fermionic; rest are bosonic
        self.osc_parity = [1, 1] + [0, 0] * n

        # Build all generators with their oscillator realizations
        self.generators = []        # ordered list of generator names
        self.gen_realization = {}   # name -> {tuple_of_osc_indices: Fraction}
        self.gen_parity = {}        # name -> int (0 or 1)
        self._build_generators()

        # Maps for inverse lookup: monomial -> (gen_name, coefficient)
        self.mono_to_gen = {}
        self._build_mono_to_gen_map()

    # ------------------------------------------------------------------
    # Generator construction
    # ------------------------------------------------------------------

    def _build_generators(self):
        n = self.n

        # -- Even: Cartan H_1, ..., H_{n+1} --
        # H_1 = a1p*a1m + b1p*b1m
        self.gen_realization['H_1'] = {(0, 1): Fraction(1), (2, 3): Fraction(1)}
        self.gen_parity['H_1'] = 0
        self.generators.append('H_1')

        for k in range(2, n + 1):
            # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-
            self.gen_realization[f'H_{k}'] = {
                (2*(k-1), 2*(k-1)+1): Fraction(1),
                (2*k, 2*k+1): Fraction(-1),
            }
            self.gen_parity[f'H_{k}'] = 0
            self.generators.append(f'H_{k}')

        # H_{n+1} = -b_n^+ b_n^- - 1/2
        self.gen_realization[f'H_{n+1}'] = {
            (2*n, 2*n+1): Fraction(-1),
            (): Fraction(-1, 2),
        }
        self.gen_parity[f'H_{n+1}'] = 0
        self.generators.append(f'H_{n+1}')

        # -- Even: sp(2n) root generators --
        for k in range(1, n + 1):
            self.gen_realization[f'E_2del{k}_p'] = {(2*k, 2*k): Fraction(1)}
            self.gen_parity[f'E_2del{k}_p'] = 0
            self.generators.append(f'E_2del{k}_p')

            self.gen_realization[f'E_2del{k}_m'] = {(2*k+1, 2*k+1): Fraction(1)}
            self.gen_parity[f'E_2del{k}_m'] = 0
            self.generators.append(f'E_2del{k}_m')

        for i, j in combinations(range(1, n + 1), 2):  # i < j
            # E_{delta_i + delta_j} = b_i^+ b_j^+  (pp)
            self.gen_realization[f'E_del{i}_del{j}_pp'] = {(2*i, 2*j): Fraction(1)}
            self.gen_parity[f'E_del{i}_del{j}_pp'] = 0
            self.generators.append(f'E_del{i}_del{j}_pp')

            # E_{-delta_i - delta_j} = b_i^- b_j^-  (mm)
            self.gen_realization[f'E_del{i}_del{j}_mm'] = {(2*i+1, 2*j+1): Fraction(1)}
            self.gen_parity[f'E_del{i}_del{j}_mm'] = 0
            self.generators.append(f'E_del{i}_del{j}_mm')

            # E_{delta_i - delta_j} = b_i^+ b_j^-  (pm); i<j => 2i < 2j+1 ✓
            self.gen_realization[f'E_del{i}_del{j}_pm'] = {(2*i, 2*j+1): Fraction(1)}
            self.gen_parity[f'E_del{i}_del{j}_pm'] = 0
            self.generators.append(f'E_del{i}_del{j}_pm')

            # E_{-delta_i + delta_j} = b_i^- b_j^+  (mp); i<j => 2i+1 < 2j ✓
            self.gen_realization[f'E_del{i}_del{j}_mp'] = {(2*i+1, 2*j): Fraction(1)}
            self.gen_parity[f'E_del{i}_del{j}_mp'] = 0
            self.generators.append(f'E_del{i}_del{j}_mp')

        # -- Odd: eps-root generators --
        for k in range(1, n + 1):
            self.gen_realization[f'E_eps1_del{k}_pp'] = {(0, 2*k): Fraction(1)}
            self.gen_parity[f'E_eps1_del{k}_pp'] = 1
            self.generators.append(f'E_eps1_del{k}_pp')

            self.gen_realization[f'E_eps1_del{k}_pm'] = {(0, 2*k+1): Fraction(1)}
            self.gen_parity[f'E_eps1_del{k}_pm'] = 1
            self.generators.append(f'E_eps1_del{k}_pm')

            self.gen_realization[f'E_eps1_del{k}_mp'] = {(1, 2*k): Fraction(1)}
            self.gen_parity[f'E_eps1_del{k}_mp'] = 1
            self.generators.append(f'E_eps1_del{k}_mp')

            self.gen_realization[f'E_eps1_del{k}_mm'] = {(1, 2*k+1): Fraction(1)}
            self.gen_parity[f'E_eps1_del{k}_mm'] = 1
            self.generators.append(f'E_eps1_del{k}_mm')

    def _build_mono_to_gen_map(self):
        """Map each single-term (non-Cartan) generator monomial to its generator."""
        for gen, real in self.gen_realization.items():
            if len(real) == 1 and not gen.startswith('H_'):
                (mono, coeff), = real.items()
                self.mono_to_gen[mono] = (gen, coeff)

    # ------------------------------------------------------------------
    # Normal ordering in the oscillator algebra
    # ------------------------------------------------------------------

    def _no_recurse(self, idx_list, coeff, out):
        """Recursively bring idx_list to PBW order; accumulate in out dict."""
        for pos in range(len(idx_list) - 1):
            a, b = idx_list[pos], idx_list[pos + 1]
            if a > b:
                # Out-of-order pair at (pos, pos+1)
                a_odd = (a < 2)
                b_odd = (b < 2)

                swapped = idx_list[:pos] + [b, a] + idx_list[pos + 2:]
                const = idx_list[:pos] + idx_list[pos + 2:]

                if a_odd and b_odd:
                    # a1m (1) before a1p (0): a1m * a1p = 1 - a1p * a1m
                    self._no_recurse(swapped, -coeff, out)
                    self._no_recurse(const, coeff, out)
                elif (not a_odd) and (not b_odd):
                    # Both bosonic. Check same-mode: bkm(2k+1) * bkp(2k)
                    if a % 2 == 1 and b % 2 == 0 and a == b + 1 and a >= 3:
                        # bkm * bkp = bkp * bkm + 1
                        self._no_recurse(swapped, coeff, out)
                        self._no_recurse(const, coeff, out)
                    else:
                        # Different bosonic modes — just commute
                        self._no_recurse(swapped, coeff, out)
                else:
                    # Mixed boson-fermion: commute without constant
                    self._no_recurse(swapped, coeff, out)
                return  # processed first inversion; recurse handles the rest

        # Fully ordered: check fermionic double occupancy
        for pos in range(len(idx_list) - 1):
            if idx_list[pos] == idx_list[pos + 1] and idx_list[pos] < 2:
                return  # (a1p)^2 = 0 or (a1m)^2 = 0
        key = tuple(idx_list)
        out[key] = out.get(key, Fraction(0)) + coeff

    def normal_order(self, idx_list, coeff=Fraction(1)):
        """Return {tuple: Fraction} for the normally-ordered product."""
        out = {}
        self._no_recurse(list(idx_list), coeff, out)
        return {k: v for k, v in out.items() if v}

    # ------------------------------------------------------------------
    # Algebra element multiplication and brackets
    # ------------------------------------------------------------------

    def multiply(self, elem1, elem2):
        """Multiply two algebra elements (dicts {mono: Fraction})."""
        out = defaultdict(Fraction)
        for m1, c1 in elem1.items():
            for m2, c2 in elem2.items():
                prod = self.normal_order(list(m1) + list(m2), c1 * c2)
                for k, v in prod.items():
                    out[k] += v
        return {k: v for k, v in out.items() if v}

    def bracket(self, gx, gy):
        """Compute [gx, gy] (graded Lie superalgebra bracket)."""
        ex = self.gen_realization[gx]
        ey = self.gen_realization[gy]
        px = self.gen_parity[gx]
        py = self.gen_parity[gy]
        sign = Fraction((-1) ** (px * py))

        xy = self.multiply(ex, ey)
        yx = self.multiply(ey, ex)

        out = defaultdict(Fraction)
        for k, v in xy.items():
            out[k] += v
        for k, v in yx.items():
            out[k] -= sign * v
        return {k: v for k, v in out.items() if v}

    # ------------------------------------------------------------------
    # Cartan coefficient extraction via Gaussian elimination
    # ------------------------------------------------------------------

    def _solve_cartan(self, elem):
        """
        Express an element (dict of Cartan-type monomials) as a linear
        combination of H_1,...,H_{n+1}.  Returns {gen_name: Fraction}.
        """
        n = self.n
        cartan_monos = [(0, 1)] + [(2*k, 2*k+1) for k in range(1, n+1)] + [()]
        h_gens = [f'H_{k}' for k in range(1, n+2)]
        num_eq = len(cartan_monos)
        num_var = len(h_gens)

        # Augmented matrix [M | b]
        aug = [[Fraction(0)] * (num_var + 1) for _ in range(num_eq)]
        for j, hg in enumerate(h_gens):
            for mono, c in self.gen_realization[hg].items():
                if mono in cartan_monos:
                    aug[cartan_monos.index(mono)][j] = c
        for i, mono in enumerate(cartan_monos):
            aug[i][num_var] = elem.get(mono, Fraction(0))

        # Forward Gaussian elimination
        pivot_rows = {}
        row = 0
        for col in range(num_var):
            pivot = next((r for r in range(row, num_eq) if aug[r][col]), None)
            if pivot is None:
                continue
            aug[row], aug[pivot] = aug[pivot], aug[row]
            pv = aug[row][col]
            aug[row] = [x / pv for x in aug[row]]
            for r in range(num_eq):
                if r != row and aug[r][col]:
                    f = aug[r][col]
                    aug[r] = [aug[r][c] - f * aug[row][c] for c in range(num_var + 1)]
            pivot_rows[col] = row
            row += 1

        sol = [Fraction(0)] * num_var
        for col, r in pivot_rows.items():
            sol[col] = aug[r][num_var]
        return {h_gens[j]: sol[j] for j in range(num_var) if sol[j]}

    # ------------------------------------------------------------------
    # Convert monomial dict to generator coefficients
    # ------------------------------------------------------------------

    def element_to_gens(self, elem):
        """Express elem (dict {mono: Fraction}) as {gen_name: Fraction}."""
        result = defaultdict(Fraction)
        remaining = dict(elem)

        # Non-Cartan generators: direct monomial lookup
        for mono in list(remaining.keys()):
            if mono in self.mono_to_gen:
                gen, mono_c = self.mono_to_gen[mono]
                c = remaining.pop(mono) / mono_c
                if c:
                    result[gen] += c

        # Cartan part
        cartan_set = {(0, 1)} | {(2*k, 2*k+1) for k in range(1, self.n+1)} | {()}
        cartan_part = {}
        bad = {}
        for k, v in remaining.items():
            if k in cartan_set:
                cartan_part[k] = v
            else:
                bad[k] = v

        if bad:
            raise ValueError(f"Unexpected monomials in bracket result (degree>2 or unrecognized): {bad}")

        if cartan_part:
            for gen, c in self._solve_cartan(cartan_part).items():
                if c:
                    result[gen] += c

        return {k: v for k, v in result.items() if v}

    # ------------------------------------------------------------------
    # Compute all structure constants
    # ------------------------------------------------------------------

    def compute_structure_constants(self):
        """
        Compute all non-zero [X, Y] = sum_Z f_XYZ * Z.
        Returns list of dicts with keys X, Y, Z, coeff, sign_rule.
        """
        sc = []
        gens = self.generators
        for i, gx in enumerate(gens):
            for gy in gens[i:]:
                br = self.bracket(gx, gy)
                if not br:
                    continue
                gen_coeffs = self.element_to_gens(br)
                for gz, c in gen_coeffs.items():
                    sc.append({
                        'X': gx,
                        'Y': gy,
                        'Z': gz,
                        'coeff': str(c),
                        'sign_rule': 'graded',
                    })
        return sc

    # ------------------------------------------------------------------
    # Build Schema 1 JSON document
    # ------------------------------------------------------------------

    def build_schema1(self):
        n = self.n
        even_basis = [g for g in self.generators if self.gen_parity[g] == 0]
        odd_basis  = [g for g in self.generators if self.gen_parity[g] == 1]
        dim_even = len(even_basis)
        dim_odd  = len(odd_basis)

        osc_labels_str = ', '.join(self.osc_labels)

        # Oscillator realization for generator_realization field
        realizations = {}
        for gen in self.generators:
            terms = []
            for mono, c in self.gen_realization[gen].items():
                words = [self.osc_labels[i] for i in mono]
                terms.append({'words': words, 'coeff': str(c)})
            realizations[gen] = {
                'standard_form': terms,
                'parity': self.gen_parity[gen],
            }

        # gb_labels for Schema 2+ reference
        gb_labels = []
        for sigma in ('a1p', 'a1m'):
            for k in range(1, n + 1):
                for s in ('p', 'm'):
                    gb_labels.append(f'gb_{sigma}_b{k}{s}')

        doc = {
            'schema_version': '5.0',
            'algebra': {
                'family': 'C',
                'm': 1,
                'n': n,
                'cartan_type': f'C({n+1})',
                'alternative_notation': {
                    'osp': f'osp(2|{2*n})',
                    'dimension_formula': 'osp(2m|2n) with m=1',
                },
                'dimension': {
                    'total': dim_even + dim_odd,
                    'even': dim_even,
                    'odd': dim_odd,
                    'even_formula': '2*n^2 + n + 1',
                    'odd_formula': '4*n',
                },
            },
            'oscillator_generators': {
                'fermions': {
                    'm': 1,
                    'labels': ['a1p', 'a1m'],
                    'parity': 1,
                    'description': 'Standard fermionic pair a_1^+, a_1^- with CAR',
                },
                'bosons': {
                    'count': 2*n,
                    'n': n,
                    'labels': self.osc_labels[2:],
                    'description': 'Bosonic oscillators b_k^+/- with CCR',
                },
            },
            'oscillator_relations': {
                'fermionic_anticommutators': {
                    'a1m_a1p': '{a1^-, a1^+} = K = 1',
                    'a1p_squared': '(a1^+)^2 = 0',
                    'a1m_squared': '(a1^-)^2 = 0',
                },
                'bosonic_commutators': {
                    'same_type': '[b_i^+/-, b_j^+/-] = 0 for same sign',
                    'conjugate_pair': '[b_i^-, b_j^+] = delta_ij',
                },
                'mixed_commutators': {
                    'boson_fermion': '[b_k^+/-, a_1^+/-] = 0',
                },
            },
            'central_elements': {
                'K': {
                    'parity': 0,
                    'description': 'Even central identity; K = 1 in all realizations',
                },
                'kappa': {
                    'parity': 1,
                    'description': 'Odd nilpotent central element; kappa^2 = 0',
                },
            },
            'basis': {
                'even': even_basis,
                'odd': odd_basis,
                'ordering_convention': 'PBW: kappa < [odd: eps-roots] < [even: Cartan, positive, negative, mixed]',
            },
            'parity': {g: self.gen_parity[g] for g in self.generators},
            'generator_realization': {
                'description': f'Oscillator PBW order: {osc_labels_str}',
                'ordering': osc_labels_str,
                'realizations': realizations,
            },
            'structure_constants': self.compute_structure_constants(),
            'metadata': {
                'generated_by': 'src/C_generators.py',
                'generation_date': str(date.today()),
                'references': [
                    'Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras',
                    'docs/math/Cn1_definition.md',
                    'docs/json_schema_specification.md',
                ],
            },
        }
        return doc


def generate_and_save(n, output_dir='data'):
    os.makedirs(output_dir, exist_ok=True)
    alg = CnPlusOne(n)
    doc = alg.build_schema1()
    out_path = os.path.join(output_dir, f'C_{n}_structure.json')
    with open(out_path, 'w') as f:
        json.dump(doc, f, indent=2)
    sc_count = len(doc['structure_constants'])
    dim = doc['algebra']['dimension']
    print(f"C({n+1}) = osp(2|{2*n}): dim {dim['even']}|{dim['odd']}, "
          f"{sc_count} non-zero brackets → {out_path}")
    return alg, doc


if __name__ == '__main__':
    for n in [1, 2, 3]:
        generate_and_save(n)
