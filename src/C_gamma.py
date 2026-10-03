#!/usr/bin/env python3
"""
C_gamma.py: Compute the inhomogeneous deformation gamma-structure (Schema 2)
for C(n+1) = osp(2|2n).

The deformation is parametrized by the gb matrix:
  [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa

The gamma 2-cocycle is defined by:
  [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)

gamma(X,Y) is computed by tracking the b-a swaps that occur during
normal ordering of the bracket XY - (-1)^{p(X)p(Y)} YX in the deformed
oscillator algebra. Each swap of b_j^s (index>1) past a_1^sigma (index 0 or 1)
contributes a factor of -gb_{sigma,j,s} times the remaining monomial.
"""

import json
import os
import sys
from fractions import Fraction
from collections import defaultdict
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from C_generators import CnPlusOne


class CnPlusOneGamma(CnPlusOne):
    """Extends CnPlusOne with gamma (inhomogeneous deformation) computation."""

    def gb_label(self, sigma_idx, k, s):
        """
        sigma_idx: 0 (a1p) or 1 (a1m)
        k: bosonic mode (1..n)
        s: 'p' or 'm'
        """
        sigma = 'a1p' if sigma_idx == 0 else 'a1m'
        return f'gb_{sigma}_b{k}{s}'

    def gb_labels_all(self):
        """All 4n gb parameter labels."""
        labels = []
        for sigma in ('a1p', 'a1m'):
            for k in range(1, self.n + 1):
                for s in ('p', 'm'):
                    labels.append(f'gb_{sigma}_b{k}{s}')
        return labels

    # ------------------------------------------------------------------
    # Deformed normal ordering: tracks kappa contributions
    # ------------------------------------------------------------------

    def _no_recurse_deformed(self, idx_list, coeff, out_main, out_kappa):
        """
        Like _no_recurse but also tracks the kappa contributions from b-a swaps.

        out_main: dict {tuple: Fraction}  -- the kappa^0 part (undeformed)
        out_kappa: dict {tuple: {gb_label: Fraction}}  -- the kappa^1 part

        A "b past a" swap: when b_j^s (even, idx>=2) needs to pass a_1^sigma (odd, idx<2),
        the deformation adds -gb_{sigma,j,s} * (remaining monomial) to out_kappa.
        """
        for pos in range(len(idx_list) - 1):
            a, b = idx_list[pos], idx_list[pos + 1]
            if a > b:
                a_odd = (a < 2)
                b_odd = (b < 2)

                swapped = idx_list[:pos] + [b, a] + idx_list[pos + 2:]
                const_idx = idx_list[:pos] + idx_list[pos + 2:]

                if a_odd and b_odd:
                    # a1m * a1p = 1 - a1p * a1m
                    self._no_recurse_deformed(swapped, -coeff, out_main, out_kappa)
                    self._no_recurse_deformed(const_idx, coeff, out_main, out_kappa)
                elif (not a_odd) and (not b_odd):
                    # Both bosonic
                    if a % 2 == 1 and b % 2 == 0 and a == b + 1 and a >= 3:
                        # bkm * bkp = bkp * bkm + 1
                        self._no_recurse_deformed(swapped, coeff, out_main, out_kappa)
                        self._no_recurse_deformed(const_idx, coeff, out_main, out_kappa)
                    else:
                        self._no_recurse_deformed(swapped, coeff, out_main, out_kappa)
                else:
                    # Mixed b-a swap: undeformed part just commutes
                    self._no_recurse_deformed(swapped, coeff, out_main, out_kappa)

                    # Deformed part: b_j^s past a_1^sigma = -gb * remaining
                    # Identify which is bosonic (b) and which is fermionic (a)
                    if a_odd:
                        # a is fermionic (sigma), b is bosonic (bjs)
                        sigma_idx = a  # 0=a1p, 1=a1m
                        bos_idx = b
                    else:
                        # a is bosonic (bjs), b is fermionic (sigma)
                        sigma_idx = b  # 0 or 1
                        bos_idx = a

                    # Decode bosonic oscillator: bos_idx = 2k or 2k+1
                    k = (bos_idx - 2) // 2 + 1  # bosonic mode (1..n)
                    s = 'p' if bos_idx % 2 == 0 else 'm'
                    gb = self.gb_label(sigma_idx, k, s)

                    # Kappa contribution: -gb * remaining monomial
                    # remaining_mono = indices without positions pos and pos+1, then in normal order
                    remaining = idx_list[:pos] + idx_list[pos + 2:]
                    self._add_kappa_remaining(remaining, -coeff, gb, out_kappa)

                return

        # Fully ordered
        for pos in range(len(idx_list) - 1):
            if idx_list[pos] == idx_list[pos + 1] and idx_list[pos] < 2:
                return  # fermionic double occupancy: zero
        key = tuple(idx_list)
        out_main[key] = out_main.get(key, Fraction(0)) + coeff

    def _add_kappa_remaining(self, idx_list, coeff, gb_label, out_kappa):
        """Normal-order idx_list and add to out_kappa[key][gb_label]."""
        normed = {}
        self._no_recurse(list(idx_list), coeff, normed)
        for key, c in normed.items():
            if c:
                if key not in out_kappa:
                    out_kappa[key] = {}
                out_kappa[key][gb_label] = out_kappa[key].get(gb_label, Fraction(0)) + c

    def multiply_deformed(self, elem1, elem2):
        """
        Multiply two algebra elements, tracking deformation.
        Returns (main_part, kappa_part) where:
          main_part: {tuple: Fraction} -- the kappa^0 contribution
          kappa_part: {tuple: {gb: Fraction}} -- the kappa^1 contribution
        """
        out_main = defaultdict(Fraction)
        out_kappa = {}

        for m1, c1 in elem1.items():
            for m2, c2 in elem2.items():
                prod_idx = list(m1) + list(m2)
                sub_main = {}
                sub_kappa = {}
                self._no_recurse_deformed(prod_idx, c1 * c2, sub_main, sub_kappa)
                for k, v in sub_main.items():
                    out_main[k] += v
                for k, gbd in sub_kappa.items():
                    if k not in out_kappa:
                        out_kappa[k] = {}
                    for gb, v in gbd.items():
                        out_kappa[k][gb] = out_kappa[k].get(gb, Fraction(0)) + v

        out_main = {k: v for k, v in out_main.items() if v}
        out_kappa = {k: {gb: v for gb, v in gbd.items() if v}
                     for k, gbd in out_kappa.items()}
        out_kappa = {k: gbd for k, gbd in out_kappa.items() if gbd}
        return out_main, out_kappa

    def bracket_deformed(self, gx, gy):
        """
        Compute deformed bracket [X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y).
        Returns (main_gens, gamma_gens) where:
          main_gens: {gen: Fraction}  -- undeformed bracket
          gamma_gens: {gen: {gb: Fraction}}  -- gamma coefficients
        """
        ex = self.gen_realization[gx]
        ey = self.gen_realization[gy]
        px = self.gen_parity[gx]
        py = self.gen_parity[gy]
        sign = Fraction((-1) ** (px * py))

        xy_main, xy_kappa = self.multiply_deformed(ex, ey)
        yx_main, yx_kappa = self.multiply_deformed(ey, ex)

        # Main (undeformed): xy_main - sign * yx_main
        main_mono = defaultdict(Fraction)
        for k, v in xy_main.items():
            main_mono[k] += v
        for k, v in yx_main.items():
            main_mono[k] -= sign * v
        main_mono = {k: v for k, v in main_mono.items() if v}

        # Kappa part: xy_kappa - sign * yx_kappa
        kappa_mono = {}
        for k, gbd in xy_kappa.items():
            if k not in kappa_mono:
                kappa_mono[k] = {}
            for gb, v in gbd.items():
                kappa_mono[k][gb] = kappa_mono[k].get(gb, Fraction(0)) + v
        for k, gbd in yx_kappa.items():
            if k not in kappa_mono:
                kappa_mono[k] = {}
            for gb, v in gbd.items():
                kappa_mono[k][gb] = kappa_mono[k].get(gb, Fraction(0)) - sign * v
        kappa_mono = {k: {gb: v for gb, v in gbd.items() if v}
                      for k, gbd in kappa_mono.items()}
        kappa_mono = {k: gbd for k, gbd in kappa_mono.items() if gbd}

        # Convert to generators
        main_gens = self.element_to_gens(main_mono) if main_mono else {}

        # Convert kappa monomials to generators
        gamma_gens = {}
        for mono, gbd in kappa_mono.items():
            try:
                gen_coeffs = self.element_to_gens({mono: Fraction(1)})
            except ValueError:
                continue  # skip unexpected monomials (degree>2)
            for gz, gc in gen_coeffs.items():
                if gz not in gamma_gens:
                    gamma_gens[gz] = {}
                for gb, v in gbd.items():
                    gamma_gens[gz][gb] = gamma_gens[gz].get(gb, Fraction(0)) + gc * v

        # Clean up zeros
        gamma_gens = {gz: {gb: v for gb, v in gbd.items() if v}
                      for gz, gbd in gamma_gens.items()}
        gamma_gens = {gz: gbd for gz, gbd in gamma_gens.items() if gbd}

        return main_gens, gamma_gens

    # ------------------------------------------------------------------
    # Compute all gamma entries
    # ------------------------------------------------------------------

    def compute_gamma(self):
        """
        Compute gamma(X,Y) for all pairs (X,Y).
        Returns list of dicts with keys X, Y, Z, coeff_expr.
        """
        entries = []
        gens = self.generators
        for i, gx in enumerate(gens):
            for gy in gens[i:]:
                _, gamma_gens = self.bracket_deformed(gx, gy)
                for gz, gbd in gamma_gens.items():
                    coeff_expr = {gb: str(v) for gb, v in gbd.items()}
                    entries.append({
                        'X': gx,
                        'Y': gy,
                        'Z': gz,
                        'coeff_expr': coeff_expr,
                    })
        return entries

    def build_schema2(self):
        n = self.n
        gb_labels = self.gb_labels_all()
        doc = {
            'schema_version': '5.0',
            'algebra': {
                'family': 'C',
                'm': 1,
                'n': n,
                'cartan_type': f'C({n+1})',
                'osp': f'osp(2|{2*n})',
            },
            'deformation_parameters': {
                'count': 4*n,
                'labels': gb_labels,
                'parity': 1,
                'defining_relation': '[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa',
            },
            'gamma_structure': self.compute_gamma(),
            'metadata': {
                'generated_by': 'src/C_gamma.py',
                'generation_date': str(date.today()),
                'description': (
                    'gamma(X,Y) is the 2-cocycle for the inhomogeneous deformation. '
                    'coeff_expr gives the coefficient of each generator Z in gamma(X,Y) '
                    'as a linear combination of gb parameters.'
                ),
            },
        }
        return doc


def generate_and_save(n, output_dir='data'):
    os.makedirs(output_dir, exist_ok=True)
    alg = CnPlusOneGamma(n)
    doc = alg.build_schema2()
    out_path = os.path.join(output_dir, f'C_{n}_gamma.json')
    with open(out_path, 'w') as f:
        json.dump(doc, f, indent=2)
    count = len(doc['gamma_structure'])
    print(f"C({n+1}) = osp(2|{2*n}): {count} non-zero gamma entries "
          f"({4*n} gb parameters) → {out_path}")
    return alg, doc


if __name__ == '__main__':
    for n in [1, 2, 3]:
        generate_and_save(n)
