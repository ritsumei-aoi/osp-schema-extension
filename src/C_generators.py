"""
C_generators.py
Computes structure constants for C(n+1) = osp(2|2n) via oscillator algebra.

Algorithm:
1. Represent each generator as a dict of normal-ordered oscillator monomials -> Fraction coeff.
2. Compute graded brackets [X,Y] = XY - (-1)^{p(X)p(Y)} YX in the oscillator algebra.
3. Normal-order using CCR/CAR (bubble sort with commutation relations).
4. Decompose results into basis generators.
5. Output Schema 1 JSON.

Oscillator algebra CCR/CAR:
  CAR (fermion):  {a_1^-, a_1^+} = 1, (a_1^±)^2 = 0
  CCR (boson):    [b_k^-, b_k^+] = 1, cross-mode commute
  Cross:          a_1^± and b_k^± commute as operators
  PBW order:      a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m
"""

from fractions import Fraction
from collections import defaultdict
import json
import os
import sys
from datetime import date

FERMION_OPS = {'a_1_p', 'a_1_m'}


def build_osc_order(n):
    return ['a_1_p', 'a_1_m'] + [f'b_{k}_{s}' for k in range(1, n + 1) for s in ['p', 'm']]


def has_fermionic_square(word):
    seen = set()
    for op in word:
        if op in FERMION_OPS:
            if op in seen:
                return True
            seen.add(op)
    return False


def normal_order_word(word, osc_idx):
    """
    Normal-order a list of oscillator labels using bubble sort with CCR/CAR.
    Returns dict: word_tuple -> Fraction.

    Rules:
    - Adjacent identical fermion (a_1_p, a_1_p) or (a_1_m, a_1_m) → word is 0.
    - a_1_m * a_1_p (out of PBW order) → -a_1_p * a_1_m + 1  (CAR)
    - b_k_m * b_k_p (out of PBW order) → b_k_p * b_k_m + 1   (CCR)
    - Other out-of-order pairs → free swap (commute).
    """
    current = defaultdict(Fraction)
    current[tuple(word)] = Fraction(1)

    changed = True
    while changed:
        changed = False
        new_current = defaultdict(Fraction)

        for w, c in current.items():
            if c == 0:
                continue

            word_zeroed = False
            swap_done = False

            for i in range(len(w) - 1):
                op_i, op_j = w[i], w[i + 1]
                prefix = w[:i]
                suffix = w[i + 2:]

                # Adjacent fermionic square → zero
                if op_i == op_j and op_i in FERMION_OPS:
                    word_zeroed = True
                    changed = True
                    break

                if osc_idx[op_i] > osc_idx[op_j]:
                    if op_i == 'a_1_m' and op_j == 'a_1_p':
                        # CAR: a_1_m * a_1_p = -a_1_p * a_1_m + 1
                        new_current[prefix + (op_j, op_i) + suffix] += -c
                        new_current[prefix + suffix] += c
                    elif (op_i.startswith('b_') and op_j.startswith('b_') and
                          op_i.endswith('_m') and op_j.endswith('_p') and
                          op_i[:-2] == op_j[:-2]):
                        # CCR: b_k_m * b_k_p = b_k_p * b_k_m + 1
                        new_current[prefix + (op_j, op_i) + suffix] += c
                        new_current[prefix + suffix] += c
                    else:
                        # Free swap (different modes, or boson-fermion)
                        new_current[prefix + (op_j, op_i) + suffix] += c

                    swap_done = True
                    changed = True
                    break

            if not word_zeroed and not swap_done:
                new_current[w] += c

        current = {k: v for k, v in new_current.items() if v != 0}

    return dict(current)


def multiply_elements(elem1, elem2, osc_idx):
    """Multiply two oscillator algebra elements (each: word_tuple -> Fraction)."""
    result = defaultdict(Fraction)
    for w1, c1 in elem1.items():
        for w2, c2 in elem2.items():
            combined = list(w1) + list(w2)
            normed = normal_order_word(combined, osc_idx)
            for w, c in normed.items():
                result[w] += c1 * c2 * c
    return {k: v for k, v in result.items() if v != 0}


def graded_bracket(elem1, elem2, p1, p2, osc_idx):
    """Graded bracket [X, Y] = XY - (-1)^{p1*p2} YX."""
    xy = multiply_elements(elem1, elem2, osc_idx)
    yx = multiply_elements(elem2, elem1, osc_idx)
    sign = Fraction((-1) ** (p1 * p2))
    result = defaultdict(Fraction)
    for w, c in xy.items():
        result[w] += c
    for w, c in yx.items():
        result[w] -= sign * c
    return {k: v for k, v in result.items() if v != 0}


class CnPlus1:
    """C(n+1) = osp(2|2n) structure constant computer."""

    def __init__(self, n):
        self.n = n
        self.osc_order = build_osc_order(n)
        self.osc_idx = {op: i for i, op in enumerate(self.osc_order)}
        self._setup_basis()
        self._setup_realizations()

    def _setup_basis(self):
        n = self.n
        cartan = [f'H_{k}' for k in range(1, n + 2)]

        even_nc = []
        for k in range(1, n + 1):
            even_nc.append(f'E_2del{k}_p')
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                even_nc.append(f'E_del{i}_del{j}_pp')
        for k in range(1, n + 1):
            even_nc.append(f'E_2del{k}_m')
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                even_nc.append(f'E_del{i}_del{j}_mm')
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                even_nc.append(f'E_del{i}_del{j}_pm')
                even_nc.append(f'E_del{i}_del{j}_mp')

        odd = []
        for s1, s2 in [('p', 'p'), ('p', 'm'), ('m', 'p'), ('m', 'm')]:
            for k in range(1, n + 1):
                odd.append(f'E_eps1_del{k}_{s1}{s2}')

        self.even_basis = cartan + even_nc
        self.odd_basis = odd
        self.basis = self.even_basis + self.odd_basis
        self.parity_map = {g: 0 for g in self.even_basis}
        self.parity_map.update({g: 1 for g in self.odd_basis})

    def _setup_realizations(self):
        n = self.n
        R = {}

        # Cartan generators
        R['H_1'] = {('a_1_p', 'a_1_m'): Fraction(1),
                    ('b_1_p', 'b_1_m'): Fraction(1)}
        for k in range(2, n + 1):
            R[f'H_{k}'] = {(f'b_{k-1}_p', f'b_{k-1}_m'): Fraction(1),
                           (f'b_{k}_p', f'b_{k}_m'): Fraction(-1)}
        R[f'H_{n+1}'] = {(f'b_{n}_p', f'b_{n}_m'): Fraction(-1),
                         (): Fraction(-1, 2)}

        # Even non-Cartan
        for k in range(1, n + 1):
            R[f'E_2del{k}_p'] = {(f'b_{k}_p', f'b_{k}_p'): Fraction(1)}
            R[f'E_2del{k}_m'] = {(f'b_{k}_m', f'b_{k}_m'): Fraction(1)}
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                R[f'E_del{i}_del{j}_pp'] = {(f'b_{i}_p', f'b_{j}_p'): Fraction(1)}
                R[f'E_del{i}_del{j}_mm'] = {(f'b_{i}_m', f'b_{j}_m'): Fraction(1)}
                R[f'E_del{i}_del{j}_pm'] = {(f'b_{i}_p', f'b_{j}_m'): Fraction(1)}
                R[f'E_del{i}_del{j}_mp'] = {(f'b_{i}_m', f'b_{j}_p'): Fraction(1)}

        # Odd generators
        for k in range(1, n + 1):
            R[f'E_eps1_del{k}_pp'] = {('a_1_p', f'b_{k}_p'): Fraction(1)}
            R[f'E_eps1_del{k}_pm'] = {('a_1_p', f'b_{k}_m'): Fraction(1)}
            R[f'E_eps1_del{k}_mp'] = {('a_1_m', f'b_{k}_p'): Fraction(1)}
            R[f'E_eps1_del{k}_mm'] = {('a_1_m', f'b_{k}_m'): Fraction(1)}

        self.realizations = R

    def decompose(self, osc_expr):
        """
        Decompose a normal-ordered oscillator expression into basis generator coefficients.
        Returns dict: generator_label -> Fraction.
        """
        n = self.n
        result = {}
        remaining = dict(osc_expr)

        # 1. Odd generators (a_1 + b_k monomials)
        for k in range(1, n + 1):
            for s1, s2 in [('p', 'p'), ('p', 'm'), ('m', 'p'), ('m', 'm')]:
                a_op = f'a_1_{s1}'
                b_op = f'b_{k}_{s2}'
                mono = (a_op, b_op)
                if mono in remaining and remaining[mono] != 0:
                    result[f'E_eps1_del{k}_{s1}{s2}'] = remaining.pop(mono)

        # 2. Even non-Cartan (two-boson monomials)
        for k in range(1, n + 1):
            mono = (f'b_{k}_p', f'b_{k}_p')
            if mono in remaining and remaining[mono] != 0:
                result[f'E_2del{k}_p'] = remaining.pop(mono)
            mono = (f'b_{k}_m', f'b_{k}_m')
            if mono in remaining and remaining[mono] != 0:
                result[f'E_2del{k}_m'] = remaining.pop(mono)

        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                for s1, s2, suffix in [('p', 'p', 'pp'), ('m', 'm', 'mm'),
                                        ('p', 'm', 'pm'), ('m', 'p', 'mp')]:
                    mono = (f'b_{i}_{s1}', f'b_{j}_{s2}')
                    if mono in remaining and remaining[mono] != 0:
                        result[f'E_del{i}_del{j}_{suffix}'] = remaining.pop(mono)

        # 3. Remaining: Cartan monomials + scalar
        c_a = remaining.pop(('a_1_p', 'a_1_m'), Fraction(0))
        c_b = [remaining.pop((f'b_{k}_p', f'b_{k}_m'), Fraction(0)) for k in range(1, n + 1)]
        scalar = remaining.pop((), Fraction(0))

        if remaining:
            raise ValueError(f"Unrecognized monomials in decompose (n={n}): {dict(remaining)}")

        # Express Cartan part as H coefficients using:
        # H_1 coeff:     c_a
        # H_j (2<=j<=n): -c_a + sum_{k=1}^{j-1} c_b[k-1]
        # H_{n+1} coeff: c_a - sum c_b
        # Scalar check:  (c_a - sum c_b)/2 + scalar == 0

        total_c_b = sum(c_b)

        h1 = c_a
        if h1 != 0:
            result['H_1'] = result.get('H_1', Fraction(0)) + h1

        for j in range(2, n + 1):
            hj = -c_a + sum(c_b[:j - 1])
            if hj != 0:
                result[f'H_{j}'] = result.get(f'H_{j}', Fraction(0)) + hj

        h_n1 = c_a - total_c_b
        if h_n1 != 0:
            result[f'H_{n+1}'] = result.get(f'H_{n+1}', Fraction(0)) + h_n1

        # Scalar check (should be 0 for valid Lie bracket)
        const_check = (c_a - total_c_b) * Fraction(1, 2) + scalar
        if const_check != 0:
            raise ValueError(f"Non-zero scalar residual {const_check} in bracket decomposition "
                             f"(c_a={c_a}, c_b={c_b}, scalar={scalar})")

        return {k: v for k, v in result.items() if v != 0}

    def compute_structure_constants(self):
        """Compute all non-zero structure constants [X, Y] = sum coeff * Z."""
        brackets = []
        basis = self.basis
        parity = self.parity_map
        R = self.realizations
        osc_idx = self.osc_idx

        for i in range(len(basis)):
            for j in range(i + 1, len(basis)):
                X, Y = basis[i], basis[j]
                p_X, p_Y = parity[X], parity[Y]

                bracket = graded_bracket(R[X], R[Y], p_X, p_Y, osc_idx)
                if not bracket:
                    continue

                decomp = self.decompose(bracket)
                for Z, coeff in sorted(decomp.items()):
                    brackets.append({
                        'X': X, 'Y': Y, 'Z': Z,
                        'coeff': str(coeff),
                        'sign_rule': 'graded'
                    })

        return brackets

    def _dim_formula(self):
        n = self.n
        return {
            'total': 2 * n * n + 5 * n + 1,
            'even': 2 * n * n + n + 1,
            'odd': 4 * n
        }

    def to_schema1_json(self):
        """Produce the full Schema 1 JSON dict."""
        n = self.n
        dim = self._dim_formula()
        brackets = self.compute_structure_constants()

        osc_labels = [f'b_{k}_{s}' for k in range(1, n + 1) for s in ['p', 'm']]
        boson_count = 2 * n

        # Build parity dict for JSON
        parity_json = {}
        for g in self.even_basis:
            parity_json[g] = 0
        for g in self.odd_basis:
            parity_json[g] = 1

        # Build generator realization for JSON
        def realization_json(label):
            entries = []
            for mono, coeff in sorted(self.realizations[label].items(),
                                      key=lambda x: len(x[0])):
                entries.append({'words': list(mono), 'coeff': str(coeff)})
            return {'standard_form': entries, 'parity': self.parity_map[label]}

        gen_real = {g: realization_json(g) for g in self.basis}

        schema = {
            'schema_version': '5.0',
            'algebra': {
                'family': 'C',
                'm': 1,
                'n': n,
                'cartan_type': f'C({n+1})',
                'alternative_notation': {
                    'osp': f'osp(2|{2*n})',
                    'dimension_formula': 'osp(2m|2n) with m=1'
                },
                'dimension': dim
            },
            'central_elements': {
                'kappa': {
                    'label': 'kappa', 'parity': 1,
                    'property': 'kappa^2 = 0',
                    'description': 'Odd nilpotent central element for inhomogeneous deformation'
                },
                'K': {
                    'label': 'K', 'parity': 0,
                    'property': 'central identity = scalar 1',
                    'description': 'Even central element; excluded from basis'
                }
            },
            'oscillator_generators': {
                'fermions': {
                    'm': 1,
                    'labels': ['a_1_p', 'a_1_m'],
                    'parity': 1,
                    'description': 'Standard CAR pair a_1^+, a_1^-; {a_1^-, a_1^+} = 1'
                },
                'bosons': {
                    'count': boson_count,
                    'n': n,
                    'labels': osc_labels,
                    'description': f'Bosonic oscillators b_k^± with k=1,...,{n}'
                }
            },
            'oscillator_relations': {
                'standard_fermion_anticommutators': {
                    'relations': {
                        'cross': '{a_1^-, a_1^+} = 1',
                        'square_p': 'a_1^+ * a_1^+ = 0',
                        'square_m': 'a_1^- * a_1^- = 0'
                    }
                },
                'bosonic_commutators': {
                    'relations': {
                        'same_sign': '[b_i^±, b_j^±] = 0',
                        'conjugate_pair': '[b_i^-, b_j^+] = delta_{ij}'
                    }
                },
                'mixed_commutators': {'fermion_boson': '[a_1^±, b_k^±] = 0'}
            },
            'basis': {
                'even': self.even_basis,
                'odd': self.odd_basis,
                'ordering_convention': 'PBW: kappa < [odd] < [even]; K excluded'
            },
            'parity': parity_json,
            'generator_realization': {
                'description': 'Normal-ordered oscillator words in PBW order',
                'ordering': self.osc_order,
                'realizations': gen_real
            },
            'structure_constants': brackets,
            'metadata': {
                'generated_by': 'src/C_generators.py',
                'generation_date': str(date.today()),
                'references': [
                    'Frappat, Sciarrino, Sorba, Dictionary on Lie Algebras and Superalgebras (2000)',
                    'docs/math/Cn1_definition.md',
                    'docs/json_schema_specification.md'
                ]
            }
        }
        return schema


def generate_all(output_dir='data'):
    os.makedirs(output_dir, exist_ok=True)
    results = {}
    for n in range(1, 4):
        print(f"Computing C({n+1}) = osp(2|{2*n}), n={n}...")
        alg = CnPlus1(n)
        schema = alg.to_schema1_json()
        fname = os.path.join(output_dir, f'C_{n}_structure.json')
        with open(fname, 'w') as f:
            json.dump(schema, f, indent=2)
        sc = schema['structure_constants']
        print(f"  dim={schema['algebra']['dimension']}, "
              f"non-zero brackets: {len(sc)}")
        results[n] = schema
    return results


if __name__ == '__main__':
    output_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    generate_all(output_dir)
    print("Done. JSON files written to", output_dir)
