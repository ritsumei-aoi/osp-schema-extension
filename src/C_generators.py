"""
C(n+1) = osp(2|2n) structure constant generator (Schema 1).

Computes the complete v5.0 JSON for C(n+1) with bosonic rank n=1,2,3
using the oscillator realization from Frappat et al. (2000).
"""

import json
import sys
from fractions import Fraction
from datetime import date


def osc_parity(label):
    return 1 if label.startswith('a_') else 0


class OscillatorAlgebra:
    def __init__(self, n):
        self.n = n
        self.osc_labels = ['a_1_p', 'a_1_m']
        for k in range(1, n + 1):
            self.osc_labels.extend([f'b_{k}_p', f'b_{k}_m'])
        self.osc_index = {lab: i for i, lab in enumerate(self.osc_labels)}

    def _swap_relation(self, a, b):
        """a * b = sign * b * a + scalar"""
        pa, pb = osc_parity(a), osc_parity(b)
        if pa == 1 and pb == 1:
            sign = Fraction(-1)
            scalar = Fraction(1) if {a, b} == {'a_1_p', 'a_1_m'} else Fraction(0)
        elif pa == 0 and pb == 0:
            sign = Fraction(1)
            scalar = Fraction(0)
            ka, ta = int(a.split('_')[1]), a.split('_')[2]
            kb, tb = int(b.split('_')[1]), b.split('_')[2]
            if ka == kb and ta != tb:
                scalar = Fraction(-1) if (ta == 'p' and tb == 'm') else Fraction(1)
        else:
            sign = Fraction(1)
            scalar = Fraction(0)
        return sign, scalar

    def normal_order(self, word, coeff=None):
        if coeff is None:
            coeff = Fraction(1)
        result = {}
        queue = [(list(word), coeff)]
        while queue:
            w, c = queue.pop()
            if c == Fraction(0):
                continue
            found = False
            for i in range(len(w) - 1):
                ia = self.osc_index[w[i]]
                ib = self.osc_index[w[i + 1]]
                if ia > ib:
                    a, b = w[i], w[i + 1]
                    sign, scalar = self._swap_relation(a, b)
                    queue.append((w[:i] + [b, a] + w[i + 2:], c * sign))
                    if scalar != Fraction(0):
                        queue.append((w[:i] + w[i + 2:], c * scalar))
                    found = True
                    break
                elif ia == ib and osc_parity(w[i]) == 1:
                    found = True
                    break
            if not found:
                key = tuple(w)
                result[key] = result.get(key, Fraction(0)) + c
        return {k: v for k, v in result.items() if v != Fraction(0)}

    def multiply_polys(self, p1, p2):
        result = {}
        for w1, c1 in p1.items():
            for w2, c2 in p2.items():
                for w, c in self.normal_order(w1 + w2, c1 * c2).items():
                    result[w] = result.get(w, Fraction(0)) + c
        return {k: v for k, v in result.items() if v != Fraction(0)}

    def graded_bracket(self, p1, par1, p2, par2):
        xy = self.multiply_polys(p1, p2)
        yx = self.multiply_polys(p2, p1)
        sign = Fraction(-1) ** (par1 * par2)
        result = dict(xy)
        for w, c in yx.items():
            result[w] = result.get(w, Fraction(0)) - sign * c
        return {k: v for k, v in result.items() if v != Fraction(0)}


class CnAlgebra:
    def __init__(self, n):
        self.n = n
        self.osc = OscillatorAlgebra(n)
        self._build_generators()
        self._build_mono_map()

    def _build_generators(self):
        self.generators = {}
        self.gen_parity = {}
        self.even_basis = []
        self.odd_basis = []
        n = self.n

        self.generators['H_1'] = {
            ('a_1_p', 'a_1_m'): Fraction(1),
            ('b_1_p', 'b_1_m'): Fraction(1)
        }
        self.gen_parity['H_1'] = 0
        self.even_basis.append('H_1')

        for k in range(2, n + 1):
            name = f'H_{k}'
            self.generators[name] = {
                (f'b_{k-1}_p', f'b_{k-1}_m'): Fraction(1),
                (f'b_{k}_p', f'b_{k}_m'): Fraction(-1)
            }
            self.gen_parity[name] = 0
            self.even_basis.append(name)

        hname = f'H_{n+1}'
        self.generators[hname] = {
            (f'b_{n}_p', f'b_{n}_m'): Fraction(-1),
            (): Fraction(-1, 2)
        }
        self.gen_parity[hname] = 0
        self.even_basis.append(hname)

        for k in range(1, n + 1):
            name = f'E_2del{k}_p'
            self.generators[name] = {(f'b_{k}_p', f'b_{k}_p'): Fraction(1)}
            self.gen_parity[name] = 0
            self.even_basis.append(name)

        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                name = f'E_del{i}_del{j}_pp'
                self.generators[name] = {(f'b_{i}_p', f'b_{j}_p'): Fraction(1)}
                self.gen_parity[name] = 0
                self.even_basis.append(name)

        for k in range(1, n + 1):
            name = f'E_2del{k}_m'
            self.generators[name] = {(f'b_{k}_m', f'b_{k}_m'): Fraction(1)}
            self.gen_parity[name] = 0
            self.even_basis.append(name)

        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                name = f'E_del{i}_del{j}_mm'
                self.generators[name] = {(f'b_{i}_m', f'b_{j}_m'): Fraction(1)}
                self.gen_parity[name] = 0
                self.even_basis.append(name)

        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                name = f'E_del{i}_del{j}_pm'
                self.generators[name] = {(f'b_{i}_p', f'b_{j}_m'): Fraction(1)}
                self.gen_parity[name] = 0
                self.even_basis.append(name)

        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                name = f'E_del{i}_del{j}_mp'
                self.generators[name] = {(f'b_{i}_m', f'b_{j}_p'): Fraction(1)}
                self.gen_parity[name] = 0
                self.even_basis.append(name)

        for k in range(1, n + 1):
            for sa, sb in [('p', 'p'), ('p', 'm'), ('m', 'p'), ('m', 'm')]:
                name = f'E_eps1_del{k}_{sa}{sb}'
                self.generators[name] = {(f'a_1_{sa}', f'b_{k}_{sb}'): Fraction(1)}
                self.gen_parity[name] = 1
                self.odd_basis.append(name)

        self.all_basis = self.odd_basis + self.even_basis

    def _build_mono_map(self):
        self.mono_to_gen = {}
        for name, poly in self.generators.items():
            if name.startswith('H_'):
                continue
            for mono, coeff in poly.items():
                self.mono_to_gen[mono] = (name, coeff)

    def _is_cartan_mono(self, mono):
        if mono == ():
            return True
        if mono == ('a_1_p', 'a_1_m'):
            return True
        if len(mono) == 2 and mono[0].startswith('b_') and mono[1].startswith('b_'):
            k0, t0 = int(mono[0].split('_')[1]), mono[0].split('_')[2]
            k1, t1 = int(mono[1].split('_')[1]), mono[1].split('_')[2]
            if k0 == k1 and t0 == 'p' and t1 == 'm':
                return True
        return False

    def _solve_cartan(self, cartan_monos):
        n = self.n
        alpha = [Fraction(0)] * (n + 1)
        alpha[0] = cartan_monos.get(('a_1_p', 'a_1_m'), Fraction(0))
        for k in range(1, n + 1):
            alpha[k] = cartan_monos.get((f'b_{k}_p', f'b_{k}_m'), Fraction(0))
        gamma = cartan_monos.get((), Fraction(0))

        c = [Fraction(0)] * (n + 2)
        c[1] = alpha[0]
        if n >= 2:
            c[2] = alpha[1] - c[1]
        else:
            c[2] = c[1] - alpha[1]

        for k in range(2, n):
            c[k + 1] = alpha[k] + c[k]

        if n >= 2:
            c[n + 1] = -alpha[n] - c[n]

        expected_gamma = -c[n + 1] * Fraction(1, 2)
        assert expected_gamma == gamma, \
            f"Cartan inconsistency: expected {expected_gamma}, got {gamma}"

        return {f'H_{i}': c[i] for i in range(1, n + 2) if c[i] != Fraction(0)}

    def poly_to_gen_dict(self, poly):
        result = {}
        cartan_monos = {}
        for mono, coeff in poly.items():
            assert len(mono) <= 2, f"Degree > 2 monomial {mono} in bracket result"
            if mono in self.mono_to_gen:
                gen_name, gen_coeff = self.mono_to_gen[mono]
                c = coeff / gen_coeff
                result[gen_name] = result.get(gen_name, Fraction(0)) + c
            elif self._is_cartan_mono(mono):
                cartan_monos[mono] = coeff
            else:
                raise ValueError(f"Unexpected monomial {mono}")
        if cartan_monos:
            for name, c in self._solve_cartan(cartan_monos).items():
                result[name] = result.get(name, Fraction(0)) + c
        return {k: v for k, v in result.items() if v != Fraction(0)}

    def compute_bracket(self, x_name, y_name):
        px = self.gen_parity[x_name]
        py = self.gen_parity[y_name]
        bracket = self.osc.graded_bracket(
            self.generators[x_name], px,
            self.generators[y_name], py
        )
        if not bracket:
            return {}
        return self.poly_to_gen_dict(bracket)

    def compute_structure_constants(self):
        constants = []
        basis = self.all_basis
        for i, x_name in enumerate(basis):
            for j, y_name in enumerate(basis):
                if i >= j:
                    continue
                gen_dict = self.compute_bracket(x_name, y_name)
                for z_name, coeff in sorted(gen_dict.items()):
                    constants.append({
                        'X': x_name,
                        'Y': y_name,
                        'Z': z_name,
                        'coeff': str(coeff),
                        'sign_rule': 'graded'
                    })
        return constants

    def to_json(self):
        n = self.n
        sc = self.compute_structure_constants()

        parity = {name: self.gen_parity[name] for name in self.all_basis}

        realizations = {}
        for name, poly in self.generators.items():
            std_form = []
            for mono, coeff in poly.items():
                std_form.append({'words': list(mono), 'coeff': str(coeff)})
            realizations[name] = {
                'standard_form': std_form,
                'parity': self.gen_parity[name]
            }

        boson_labels = []
        for k in range(1, n + 1):
            boson_labels.extend([f'b_{k}_p', f'b_{k}_m'])

        even_dim = 2 * n * n + n + 1
        odd_dim = 4 * n

        return {
            'schema_version': '5.0',
            'algebra': {
                'family': 'C',
                'm': 1,
                'n': n,
                'cartan_type': f'C({n + 1})',
                'alternative_notation': {
                    'osp': f'osp(2|{2 * n})',
                    'dimension_formula': 'osp(2m|2n) with m=1'
                },
                'dimension': {
                    'total': even_dim + odd_dim,
                    'even': even_dim,
                    'odd': odd_dim
                }
            },
            'oscillator_generators': {
                'fermions': {
                    'type': 'standard_pair',
                    'm': 1,
                    'labels': ['a_1_p', 'a_1_m'],
                    'parity': 1,
                    'description': 'Standard fermionic pair a_1^+/- with CAR {a_1^-, a_1^+} = 1'
                },
                'bosons': {
                    'count': 2 * n,
                    'n': n,
                    'labels': boson_labels,
                    'description': f'Bosonic oscillators b_k^+/- with k=1,...,{n}'
                }
            },
            'oscillator_relations': {
                'standard_fermion_anticommutators': {
                    'description': 'Canonical anticommutation relations',
                    'relations': {
                        'canonical': '{a_1^-, a_1^+} = 1',
                        'nilpotent': '{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0'
                    }
                },
                'bosonic_commutators': {
                    'description': 'Canonical commutation relations',
                    'relations': {
                        'same_type': '[b_i^s, b_j^s] = 0 for all i, j',
                        'conjugate_pair': '[b_i^-, b_j^+] = delta_{ij}'
                    }
                },
                'mixed_commutators': {
                    'boson_fermion': '[b_i^s, a_1^t] = 0 (undeformed)'
                }
            },
            'central_elements': {
                'K': {
                    'parity': 0,
                    'description': 'Even central identity (= scalar 1). Excluded from PBW basis.'
                },
                'kappa': {
                    'parity': 1,
                    'description': 'Odd nilpotent central element (kappa^2 = 0).'
                }
            },
            'basis': {
                'even': self.even_basis,
                'odd': self.odd_basis,
                'ordering_convention': 'PBW: kappa < [odd] < [even] (K = 1 excluded)'
            },
            'parity': parity,
            'generator_realization': {
                'description': 'Standard form with PBW ordering',
                'ordering': ', '.join(self.osc.osc_labels),
                'realizations': realizations
            },
            'structure_constants': sc,
            'metadata': {
                'generated_by': 'C_generators.py',
                'generation_date': str(date.today()),
                'references': [
                    'Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras',
                    'Bakalov and Sullivan (2017)'
                ]
            }
        }


def main():
    for n in [1, 2, 3]:
        print(f"Generating C({n+1}) = osp(2|{2*n}) (n={n})...")
        alg = CnAlgebra(n)
        schema = alg.to_json()
        filename = f'data/C_{n}_structure.json'
        with open(filename, 'w') as f:
            json.dump(schema, f, indent=2)
        print(f"  {filename}: even={len(alg.even_basis)}, odd={len(alg.odd_basis)}, "
              f"total={len(alg.all_basis)}, sc_entries={len(schema['structure_constants'])}")


if __name__ == '__main__':
    main()
