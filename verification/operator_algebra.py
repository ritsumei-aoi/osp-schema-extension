#!/usr/bin/env python3
"""
Compute all gamma values from the deformed oscillator algebra for C(2) = osp(2|2).

Normal-ordered monomials: c * (a+)^n_ap (a-)^n_am (b+)^m_bp (b-)^m_bm kappa^k
with n_ap, n_am in {0,1}, m_bp, m_bm >= 0, k in {0,1}.
"""
from fractions import Fraction as F


class DeformedOscillator:
    def __init__(self, gb_pp, gb_pm, gb_mp, gb_mm):
        self.gb = {('+','+'): F(gb_pp), ('+','-'): F(gb_pm),
                   ('-','+'): F(gb_mp), ('-','-'): F(gb_mm)}

    def _add(self, terms, n_ap, n_am, m_bp, m_bm, k, c):
        if c == 0 or n_ap > 1 or n_am > 1 or k > 1 or n_ap < 0 or n_am < 0 or m_bp < 0 or m_bm < 0:
            return
        ky = (n_ap, n_am, m_bp, m_bm, k)
        terms[ky] = terms.get(ky, F(0)) + c
        if terms[ky] == 0:
            del terms[ky]

    def mul_right_ap(self, terms):
        """Right-multiply by a+ in deformed algebra.

        For monomial M = (a+)^n (a-)^m (b+)^p (b-)^q kappa^k, compute M * a+.

        a+ bubbles left through kappa, b-, b+, a- in sequence.
        At each b-step, correction term absorbs a+ (no further bubbling).
        """
        result = {}
        for (n_ap, n_am, m_bp, m_bm, k), c in terms.items():
            s = F((-1)**k)  # sign from passing kappa

            # Corrections where a+ is absorbed by b- or b+
            if k == 0:  # corrections produce k+1=1; if k already 1, k+1=2 -> kappa^2=0
                if m_bm > 0:
                    self._add(result, n_ap, n_am, m_bp, m_bm - 1, 1,
                              c * s * (-m_bm) * self.gb[('+', '-')])
                if m_bp > 0:
                    self._add(result, n_ap, n_am, m_bp - 1, m_bm, 1,
                              c * s * (-m_bp) * self.gb[('+', '+')])

            # Main term: a+ passes all b's, reaches a- position
            if n_am == 0:
                self._add(result, n_ap + 1, 0, m_bp, m_bm, k, c * s)
            else:  # n_am == 1: a- a+ = 1 - a+a-
                self._add(result, n_ap, 0, m_bp, m_bm, k, c * s)        # "1" part
                self._add(result, n_ap + 1, 1, m_bp, m_bm, k, -c * s)   # "-a+a-" part
        return result

    def mul_right_am(self, terms):
        """Right-multiply by a- in deformed algebra."""
        result = {}
        for (n_ap, n_am, m_bp, m_bm, k), c in terms.items():
            s = F((-1)**k)

            if k == 0:
                if m_bm > 0:
                    self._add(result, n_ap, n_am, m_bp, m_bm - 1, 1,
                              c * s * (-m_bm) * self.gb[('-', '-')])
                if m_bp > 0:
                    self._add(result, n_ap, n_am, m_bp - 1, m_bm, 1,
                              c * s * (-m_bp) * self.gb[('-', '+')])

            if n_am == 0:
                self._add(result, n_ap, 1, m_bp, m_bm, k, c * s)
            # n_am == 1: a- a- = 0, main term vanishes
        return result

    def mul_right_bp(self, terms):
        """Right-multiply by b+. b+ passes kappa (trivially) then b-'s."""
        result = {}
        for (n_ap, n_am, m_bp, m_bm, k), c in terms.items():
            self._add(result, n_ap, n_am, m_bp + 1, m_bm, k, c)
            if m_bm > 0:
                self._add(result, n_ap, n_am, m_bp, m_bm - 1, k, c * m_bm)
        return result

    def mul_right_bm(self, terms):
        """Right-multiply by b-. Already rightmost in normal order."""
        result = {}
        for (n_ap, n_am, m_bp, m_bm, k), c in terms.items():
            self._add(result, n_ap, n_am, m_bp, m_bm + 1, k, c)
        return result

    def mul_right_kappa(self, terms):
        result = {}
        for (n_ap, n_am, m_bp, m_bm, k), c in terms.items():
            if k == 0:
                self._add(result, n_ap, n_am, m_bp, m_bm, 1, c)
        return result

    def build_product(self, ops):
        """Build normal-ordered product from left-to-right operator sequence."""
        result = {(0, 0, 0, 0, 0): F(1)}
        dispatch = {
            'a+': self.mul_right_ap, 'a-': self.mul_right_am,
            'b+': self.mul_right_bp, 'b-': self.mul_right_bm,
            'kappa': self.mul_right_kappa,
        }
        for op in ops:
            result = dispatch[op](result)
        return result

    def scale(self, terms, s):
        return {k: v * s for k, v in terms.items() if v * s != 0}

    def add_terms(self, t1, t2):
        r = dict(t1)
        for k, v in t2.items():
            r[k] = r.get(k, F(0)) + v
            if r[k] == 0:
                del r[k]
        return r

    def sub_terms(self, t1, t2):
        return self.add_terms(t1, self.scale(t2, F(-1)))


class DeformedOscillatorUndeformed(DeformedOscillator):
    """Undeformed version (gb=0)."""
    def __init__(self):
        super().__init__(0, 0, 0, 0)


def compute_all_gammas(gb_pp, gb_pm, gb_mp, gb_mm):
    alg_def = DeformedOscillator(gb_pp, gb_pm, gb_mp, gb_mm)
    alg_undef = DeformedOscillatorUndeformed()

    gen_specs = {
        'e1': [(['a+', 'a-'], F(1)), (['b+', 'b-'], F(1))],
        'e2': [(['b+', 'b-'], F(-1))],
        'e3': [(['b+', 'b+'], F(1, 2))],
        'e4': [(['b-', 'b-'], F(1, 2))],
        'o1': [(['a+', 'b+'], F(1))],
        'o2': [(['a+', 'b-'], F(1))],
        'o3': [(['a-', 'b+'], F(1))],
        'o4': [(['a-', 'b-'], F(1))],
    }

    def build_gen(alg, label):
        result = {}
        for ops, coeff in gen_specs[label]:
            t = alg.build_product(ops)
            result = alg.add_terms(result, alg.scale(t, coeff))
        return result

    def compute_product(alg, label_x, label_y):
        result = {}
        for x_ops, x_coeff in gen_specs[label_x]:
            for y_ops, y_coeff in gen_specs[label_y]:
                t = alg.build_product(x_ops + y_ops)
                result = alg.add_terms(result, alg.scale(t, x_coeff * y_coeff))
        return result

    def compute_bracket(alg, label_x, label_y):
        px = 1 if label_x.startswith('o') else 0
        py = 1 if label_y.startswith('o') else 0
        sign = F((-1)**(px * py))
        xy = compute_product(alg, label_x, label_y)
        yx = compute_product(alg, label_y, label_x)
        return alg.sub_terms(xy, alg.scale(yx, sign))

    def extract_kappa_part(terms):
        result = {}
        for (n_ap, n_am, m_bp, m_bm, k), c in terms.items():
            if k == 1:
                result[(n_ap, n_am, m_bp, m_bm)] = c
        return result

    def express_in_basis(kappa_terms):
        result = {}
        for osc_key, label in [((1,0,1,0), 'o1'), ((1,0,0,1), 'o2'),
                                ((0,1,1,0), 'o3'), ((0,1,0,1), 'o4')]:
            c = kappa_terms.get(osc_key, F(0))
            if c != 0:
                result[label] = c

        c_bp2 = kappa_terms.get((0,0,2,0), F(0))
        c_bm2 = kappa_terms.get((0,0,0,2), F(0))
        c_Na = kappa_terms.get((1,1,0,0), F(0))
        c_Nb = kappa_terms.get((0,0,1,1), F(0))

        if c_bp2 != 0:
            result['e3'] = result.get('e3', F(0)) + 2 * c_bp2
        if c_bm2 != 0:
            result['e4'] = result.get('e4', F(0)) + 2 * c_bm2
        if c_Na != 0:
            result['e1'] = result.get('e1', F(0)) + c_Na
            result['e2'] = result.get('e2', F(0)) + c_Na
        if c_Nb != 0:
            result['e2'] = result.get('e2', F(0)) - c_Nb

        for osc_key, c in kappa_terms.items():
            if osc_key not in [(1,0,1,0),(1,0,0,1),(0,1,1,0),(0,1,0,1),
                               (0,0,2,0),(0,0,0,2),(1,1,0,0),(0,0,1,1),(0,0,0,0)]:
                if c != 0:
                    print(f"WARNING: unexpected monomial {osc_key} with coeff {c}")

        return {k: v for k, v in result.items() if v != 0}

    basis = ['e1', 'e2', 'e3', 'e4', 'o1', 'o2', 'o3', 'o4']
    gammas = {}

    for i, x in enumerate(basis):
        for j, y in enumerate(basis):
            if j <= i:
                continue
            br_def = compute_bracket(alg_def, x, y)
            br_undef = compute_bracket(alg_undef, x, y)
            diff = alg_def.sub_terms(br_def, br_undef)
            kp = extract_kappa_part(diff)
            if kp:
                gamma = express_in_basis(kp)
                if gamma:
                    gammas[(x, y)] = gamma

    return gammas


if __name__ == '__main__':
    gammas = compute_all_gammas(1, 2, 3, 4)
    print("All gamma(X,Y) for C(2) with gb=(1,2,3,4):")
    print()
    for (x, y), gamma in sorted(gammas.items()):
        terms = ' + '.join(f'{v}*{k}' for k, v in sorted(gamma.items()))
        print(f"  gamma({x},{y}) = {terms}")

    print()
    print("Verification: [H_1, o1] should have gamma = -1*e1 - 4*e3")
    print(f"  gamma(e1,o1) = {gammas.get(('e1','o1'), 'NOT FOUND')}")
