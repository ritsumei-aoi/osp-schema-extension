#!/usr/bin/env python3
"""
C(n+1) = osp(2|2n) structure constant generator.

Computes all non-zero graded brackets [X,Y} = XY - (-1)^{p(X)p(Y)} YX
via the oscillator algebra, outputs Schema 1 JSON.

Monomial tuple format: (e_a1p, e_a1m, b1p, b1m, b2p, b2m, ..., bnp, bnm)
- e_a1p, e_a1m in {0,1} (fermionic)
- bkp, bkm >= 0 (bosonic)
Normal ordering: a1+ before a1-, bk+ before bk- for each k.
"""

from fractions import Fraction
from collections import defaultdict
import math
import json
import os
from datetime import date

# ---------------------------------------------------------------------------
# Fermionic multiplication table (pre-computed)
# key: (e1p, e1m, f1p, f1m), value: dict {(r1p, r1m): coeff}
# ---------------------------------------------------------------------------
_FERM_TABLE = {
    (0,0,0,0): {(0,0): Fraction(1)},
    (0,0,1,0): {(1,0): Fraction(1)},
    (0,0,0,1): {(0,1): Fraction(1)},
    (0,0,1,1): {(1,1): Fraction(1)},
    (1,0,0,0): {(1,0): Fraction(1)},
    (1,0,1,0): {},
    (1,0,0,1): {(1,1): Fraction(1)},
    (1,0,1,1): {},
    (0,1,0,0): {(0,1): Fraction(1)},
    (0,1,1,0): {(0,0): Fraction(1), (1,1): Fraction(-1)},
    (0,1,0,1): {},
    (0,1,1,1): {(0,1): Fraction(1)},
    (1,1,0,0): {(1,1): Fraction(1)},
    (1,1,1,0): {(1,0): Fraction(1)},
    (1,1,0,1): {},
    (1,1,1,1): {},
}


def _bos_single_mult(p, q, r, s):
    """Normal-order (b+)^p (b-)^q * (b+)^r (b-)^s.

    Formula: (b-)^q (b+)^r = sum_{j=0}^{min(q,r)} j! C(q,j) C(r,j) (b+)^{r-j} (b-)^{q-j}
    Full product: (b+)^{p+r-j} (b-)^{q-j+s} with coefficient j! C(q,j) C(r,j)
    """
    result = {}
    for j in range(min(q, r) + 1):
        c = Fraction(math.factorial(j) * math.comb(q, j) * math.comb(r, j))
        key = (p + r - j, q - j + s)
        result[key] = result.get(key, Fraction(0)) + c
    return [(k, v) for k, v in result.items() if v != 0]


class CnAlgebra:
    """Oscillator algebra for C(n+1) = osp(2|2n)."""

    def __init__(self, n):
        self.n = n
        self._dim_mon = 2 + 2 * n
        self._zero = (0,) * self._dim_mon

    def _ferm_mult(self, f1, f2):
        """Multiply two fermionic parts: f = (e_a1p, e_a1m)."""
        return list(_FERM_TABLE.get(f1 + f2, {}).items())

    def _bos_mult(self, bos1, bos2):
        """Multiply two bosonic parts, each of length 2n."""
        n = self.n
        current = {(): Fraction(1)}
        for k in range(n):
            p, q = bos1[2*k], bos1[2*k+1]
            r, s = bos2[2*k], bos2[2*k+1]
            singles = _bos_single_mult(p, q, r, s)
            new_cur = {}
            for pk, pv in current.items():
                for (np_, nq_), c in singles:
                    key = pk + (np_, nq_)
                    new_cur[key] = new_cur.get(key, Fraction(0)) + pv * c
            current = new_cur
        return [(k, v) for k, v in current.items() if v != 0]

    def multiply(self, e1, e2):
        """Multiply two algebra elements (dicts of monomial -> Fraction)."""
        result = defaultdict(Fraction)
        for m1, c1 in e1.items():
            for m2, c2 in e2.items():
                f1, b1 = m1[:2], m1[2:]
                f2, b2 = m2[:2], m2[2:]
                for fr, fc in self._ferm_mult(f1, f2):
                    for br, bc in self._bos_mult(b1, b2):
                        result[fr + br] += c1 * c2 * fc * bc
        return {k: v for k, v in result.items() if v != 0}

    def super_comm(self, X, pX, Y, pY):
        """Compute graded bracket [X,Y} = XY - (-1)^{pX*pY} YX."""
        XY = self.multiply(X, Y)
        YX = self.multiply(Y, X)
        sign = -1 if (pX * pY) % 2 == 1 else 1
        result = defaultdict(Fraction)
        for m, c in XY.items():
            result[m] += c
        for m, c in YX.items():
            result[m] -= Fraction(sign) * c
        return {k: v for k, v in result.items() if v != 0}

    def make_mon(self, **kw):
        """Build a monomial tuple from oscillator names and powers."""
        m = list(self._zero)
        for key, val in kw.items():
            if key == 'a1p':
                m[0] = val
            elif key == 'a1m':
                m[1] = val
            elif len(key) >= 3 and key[0] == 'b':
                # Format: b{k}p or b{k}m
                pm = key[-1]
                idx = int(key[1:-1])
                offset = 2 + 2*(idx-1) + (0 if pm == 'p' else 1)
                m[offset] = val
        return tuple(m)

    def build_generators(self):
        """Build all generators as oscillator algebra elements.

        Returns: (generators dict, parities dict, basis_order list)
        """
        n = self.n
        gens = {}
        pars = {}

        # H_1 = a1+a1- + b1+b1-
        gens['H_1'] = {
            self.make_mon(a1p=1, a1m=1): Fraction(1),
            self.make_mon(b1p=1, b1m=1): Fraction(1),
        }
        pars['H_1'] = 0

        # H_k = b_{k-1}+b_{k-1}- - bk+bk- for k=2,...,n
        for k in range(2, n+1):
            gens[f'H_{k}'] = {
                self.make_mon(**{f'b{k-1}p': 1, f'b{k-1}m': 1}): Fraction(1),
                self.make_mon(**{f'b{k}p': 1, f'b{k}m': 1}): Fraction(-1),
            }
            pars[f'H_{k}'] = 0

        # H_{n+1} = -bn+bn- - 1/2
        gens[f'H_{n+1}'] = {
            self.make_mon(**{f'b{n}p': 1, f'b{n}m': 1}): Fraction(-1),
            self._zero: Fraction(-1, 2),
        }
        pars[f'H_{n+1}'] = 0

        # E_{2δ_k} = (bk+)^2
        for k in range(1, n+1):
            gens[f'E_2del{k}_p'] = {self.make_mon(**{f'b{k}p': 2}): Fraction(1)}
            pars[f'E_2del{k}_p'] = 0

        # E_{-2δ_k} = (bk-)^2
        for k in range(1, n+1):
            gens[f'E_2del{k}_m'] = {self.make_mon(**{f'b{k}m': 2}): Fraction(1)}
            pars[f'E_2del{k}_m'] = 0

        # E_{δi+δj} = bi+bj+ (i<j)
        for i in range(1, n+1):
            for j in range(i+1, n+1):
                gens[f'E_del{i}_del{j}_pp'] = {
                    self.make_mon(**{f'b{i}p': 1, f'b{j}p': 1}): Fraction(1)
                }
                pars[f'E_del{i}_del{j}_pp'] = 0

        # E_{δi-δj} = bi+bj- (i<j)
        for i in range(1, n+1):
            for j in range(i+1, n+1):
                gens[f'E_del{i}_del{j}_pm'] = {
                    self.make_mon(**{f'b{i}p': 1, f'b{j}m': 1}): Fraction(1)
                }
                pars[f'E_del{i}_del{j}_pm'] = 0

        # E_{-(δi-δj)} = bi-bj+ (i<j)
        for i in range(1, n+1):
            for j in range(i+1, n+1):
                gens[f'E_del{i}_del{j}_mp'] = {
                    self.make_mon(**{f'b{i}m': 1, f'b{j}p': 1}): Fraction(1)
                }
                pars[f'E_del{i}_del{j}_mp'] = 0

        # E_{-(δi+δj)} = bi-bj- (i<j)
        for i in range(1, n+1):
            for j in range(i+1, n+1):
                gens[f'E_del{i}_del{j}_mm'] = {
                    self.make_mon(**{f'b{i}m': 1, f'b{j}m': 1}): Fraction(1)
                }
                pars[f'E_del{i}_del{j}_mm'] = 0

        # Odd generators: E_eps1_del{k}_{sign1}{sign2}
        for k in range(1, n+1):
            gens[f'E_eps1_del{k}_pp'] = {
                self.make_mon(a1p=1, **{f'b{k}p': 1}): Fraction(1)
            }
            pars[f'E_eps1_del{k}_pp'] = 1
            gens[f'E_eps1_del{k}_pm'] = {
                self.make_mon(a1p=1, **{f'b{k}m': 1}): Fraction(1)
            }
            pars[f'E_eps1_del{k}_pm'] = 1
            gens[f'E_eps1_del{k}_mp'] = {
                self.make_mon(a1m=1, **{f'b{k}p': 1}): Fraction(1)
            }
            pars[f'E_eps1_del{k}_mp'] = 1
            gens[f'E_eps1_del{k}_mm'] = {
                self.make_mon(a1m=1, **{f'b{k}m': 1}): Fraction(1)
            }
            pars[f'E_eps1_del{k}_mm'] = 1

        # Build PBW basis order: κ < [odd] < [even]
        odd_labels = []
        for k in range(1, n+1):
            odd_labels += [
                f'E_eps1_del{k}_pp', f'E_eps1_del{k}_pm',
                f'E_eps1_del{k}_mp', f'E_eps1_del{k}_mm'
            ]

        even_cartan = [f'H_{k}' for k in range(1, n+2)]
        even_pos = (
            [f'E_2del{k}_p' for k in range(1, n+1)] +
            [f'E_del{i}_del{j}_pp' for i in range(1, n+1) for j in range(i+1, n+1)]
        )
        even_neg = (
            [f'E_2del{k}_m' for k in range(1, n+1)] +
            [f'E_del{i}_del{j}_mm' for i in range(1, n+1) for j in range(i+1, n+1)]
        )
        even_mixed = (
            [f'E_del{i}_del{j}_pm' for i in range(1, n+1) for j in range(i+1, n+1)] +
            [f'E_del{i}_del{j}_mp' for i in range(1, n+1) for j in range(i+1, n+1)]
        )
        even_labels = even_cartan + even_pos + even_neg + even_mixed

        basis_order = odd_labels + even_labels
        return gens, pars, basis_order

    def decompose(self, element, gens, pars, basis_order):
        """Express element as a linear combination of basis generators.

        Returns: dict {gen_label: Fraction_coeff}
        """
        n = self.n
        result = {}
        remaining = dict(element)

        # Step 1: extract non-Cartan generators (each has a unique monomial)
        for label in basis_order:
            if label.startswith('H_'):
                continue
            gen = gens[label]
            for m, gc in gen.items():
                if m in remaining and remaining[m] != 0:
                    c = remaining[m] / gc
                    if c != 0:
                        result[label] = result.get(label, Fraction(0)) + c
                        for gm, gv in gen.items():
                            remaining[gm] = remaining.get(gm, Fraction(0)) - c * gv
                    break

        # Step 2: extract Cartan generators from remaining
        # Cartan monomials: a1+a1-, b1+b1-, ..., bn+bn-, constant
        # Cartan generators H_1,...,H_{n+1} satisfy the matrix equation below.
        #
        # Coefficient of a1+a1- in sum cj Hj: only H_1 contributes => c_1
        # Coefficient of bk+bk-:
        #   k=1: c_1 (from H_1) + c_2 (from H_2 if n>=2) or c_1 - c_2 (from H_{n+1} if n=1)
        #   k=2..n-1: c_{k+1} - c_k
        #   k=n: -c_n - c_{n+1}
        # Constant: -c_{n+1}/2

        def bk_mon(k):
            m = list(self._zero)
            m[2 + 2*(k-1)] = 1
            m[2 + 2*(k-1) + 1] = 1
            return tuple(m)

        ferm_mon = self.make_mon(a1p=1, a1m=1)
        alpha = remaining.get(ferm_mon, Fraction(0))
        beta = [remaining.get(bk_mon(k), Fraction(0)) for k in range(1, n+1)]
        gamma = remaining.get(self._zero, Fraction(0))

        # Solve for c_1,...,c_{n+1}
        c = [Fraction(0)] * (n + 2)  # c[j] = c_j, 1-indexed (c[0] unused)
        c[1] = alpha

        # c_{n+1} from constant: -c_{n+1}/2 = gamma
        c[n+1] = -2 * gamma if gamma != 0 else Fraction(0)

        if n == 1:
            # coefficient of b1+b1-: c_1 - c_2 = beta[0]
            # => c_2 = c_1 - beta[0]
            # Also c_2 = -2*gamma (already set); use if gamma nonzero, else compute from beta
            c2_from_beta = c[1] - beta[0]
            if c[n+1] == 0 and gamma == 0:
                c[n+1] = c2_from_beta
            # (consistency: c2_from_beta should equal -2*gamma for valid elements)
        else:
            # n >= 2
            # c_2 = beta[0] - c_1  (from c_1 + c_2 = beta[0])
            c[2] = beta[0] - c[1]
            # c_{k+1} = beta[k-1] + c[k] for k=2,...,n-1
            for k in range(2, n):
                c[k+1] = beta[k-1] + c[k]
            # c_{n+1} already set from constant term
            # (consistency: -c[n] - c[n+1] should equal beta[n-1])

        for j in range(1, n+2):
            if c[j] != 0:
                label = f'H_{j}'
                result[label] = result.get(label, Fraction(0)) + c[j]

        return {k: v for k, v in result.items() if v != 0}


def build_algebra(n):
    """Build C(n+1) algebra structure and compute all structure constants."""
    alg = CnAlgebra(n)
    gens, pars, basis_order = alg.build_generators()

    structure_constants = []
    labels = basis_order

    for i, xi in enumerate(labels):
        for j, xj in enumerate(labels):
            bracket = alg.super_comm(gens[xi], pars[xi], gens[xj], pars[xj])
            if not bracket:
                continue
            decomp = alg.decompose(bracket, gens, pars, basis_order)
            for z, coeff in sorted(decomp.items()):
                if coeff != 0:
                    structure_constants.append({
                        'X': xi,
                        'Y': xj,
                        'Z': z,
                        'coeff': str(coeff),
                        'sign_rule': 'graded',
                    })

    return gens, pars, basis_order, structure_constants


def build_schema1_json(n):
    """Build the full Schema 1 JSON dict for C(n+1) with bosonic rank n."""
    gens, pars, basis_order, sc = build_algebra(n)

    dim_total = 2*n*n + 5*n + 1
    dim_even = 2*n*n + n + 1
    dim_odd = 4*n

    odd_labels = [l for l in basis_order if pars[l] == 1]
    even_labels = [l for l in basis_order if pars[l] == 0]

    # Generator realizations
    realizations = {}
    for label, gen in gens.items():
        words_list = []
        for mon, coeff in gen.items():
            osc_names = _mon_to_osc_names(mon, n)
            words_list.append({'words': osc_names, 'coeff': str(coeff)})
        realizations[label] = {
            'standard_form': words_list,
            'parity': pars[label],
        }

    # Boson labels
    bos_labels = []
    for k in range(1, n+1):
        bos_labels += [f'b_{k}_p', f'b_{k}_m']

    schema = {
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
                'total': dim_total,
                'even': dim_even,
                'odd': dim_odd,
                'formula_even': '2*n^2 + n + 1',
                'formula_odd': '4*n',
                'formula_total': '2*n^2 + 5*n + 1',
            },
        },
        'central_elements': {
            'K': {'label': 'K', 'parity': 0,
                  'description': 'Even central identity; K=1 in all current applications.'},
            'kappa': {'label': 'kappa', 'parity': 1,
                      'description': 'Odd nilpotent central element; kappa^2=0.',
                      'relation': 'kappa^2 = 0'},
        },
        'oscillator_generators': {
            'fermions': {
                'm': 1,
                'labels': ['a_1_p', 'a_1_m'],
                'description': 'Standard fermionic CAR pair a_1^+, a_1^-',
            },
            'bosons': {
                'count': 2*n,
                'n': n,
                'labels': bos_labels,
                'description': f'Bosonic oscillators b_k^+/- with k=1,...,{n}',
            },
        },
        'oscillator_relations': {
            'standard_fermion_anticommutators': {
                'description': 'CAR for standard fermionic pair',
                'relations': {
                    'anticommutator': '{a_1^-, a_1^+} = 1',
                    'nilpotency_p': '(a_1^+)^2 = 0',
                    'nilpotency_m': '(a_1^-)^2 = 0',
                },
            },
            'bosonic_commutators': {
                'description': 'CCR for bosonic oscillators',
                'relations': {
                    'same_type': '[b_i^pm, b_j^pm] = 0',
                    'conjugate_pair': '[b_i^-, b_j^+] = delta_{ij}',
                },
            },
            'mixed_commutators': {
                'boson_fermion': '[b_k^pm, a_1^pm] = 0 (undeformed)',
            },
        },
        'basis': {
            'even': even_labels,
            'odd': odd_labels,
            'ordering_convention': 'PBW: kappa < [odd] < [even]',
        },
        'parity': {label: pars[label] for label in basis_order},
        'generator_realization': {
            'description': 'Standard normal-ordered oscillator form',
            'ordering': 'a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m',
            'realizations': realizations,
        },
        'structure_constants': sc,
        'metadata': {
            'generated_by': 'src/C_generators.py',
            'generation_date': str(date.today()),
            'references': [
                'Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras',
                'Bakalov and Sullivan (2017)',
                'docs/math/Cn1_definition.md',
            ],
        },
    }
    return schema


def _mon_to_osc_names(mon, n):
    """Convert a monomial tuple to a list of oscillator name strings."""
    names = []
    if mon[0] > 0:
        names.extend(['a_1_p'] * mon[0])
    if mon[1] > 0:
        names.extend(['a_1_m'] * mon[1])
    for k in range(n):
        if mon[2 + 2*k] > 0:
            names.extend([f'b_{k+1}_p'] * mon[2 + 2*k])
        if mon[2 + 2*k + 1] > 0:
            names.extend([f'b_{k+1}_m'] * mon[2 + 2*k + 1])
    return names


def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(out_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f'Building C({n+1}) structure (n={n})...')
        schema = build_schema1_json(n)
        fname = os.path.join(out_dir, f'C_{n}_structure.json')
        with open(fname, 'w') as f:
            json.dump(schema, f, indent=2)
        sc_count = len(schema['structure_constants'])
        dim = schema['algebra']['dimension']['total']
        print(f'  dim={dim}, structure_constants={sc_count}')
        print(f'  Written: {fname}')


if __name__ == '__main__':
    main()
