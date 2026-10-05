"""
C(n+1) = osp(2|2n) inhomogeneous deformation (Schema 2).

Computes gamma coefficients arising from the deformed mixed commutator:
  [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa
"""

import json
import sys
from fractions import Fraction
from datetime import date

sys.path.insert(0, '.')
from C_generators import CnAlgebra, OscillatorAlgebra, osc_parity


def gb_label(sigma, j, s):
    return f'gb_{sigma}_{j}_{s}'


def all_gb_labels(n):
    labels = []
    for sigma in ['p', 'm']:
        for j in range(1, n + 1):
            for s in ['p', 'm']:
                labels.append(gb_label(sigma, j, s))
    return labels


def compute_gamma_correction(osc_alg, word, coeff):
    """
    Compute first-order gb corrections from normal-ordering a word
    with the deformed mixed commutator [b^s, a^sigma] = -gb * kappa.
    Returns: dict gb_label -> {word_tuple: Fraction}
    """
    result = {}
    queue = [(list(word), coeff, False, None)]

    while queue:
        w, c, has_gb, tag = queue.pop()
        if c == Fraction(0):
            continue

        found = False
        for i in range(len(w) - 1):
            ia = osc_alg.osc_index[w[i]]
            ib = osc_alg.osc_index[w[i + 1]]

            if ia > ib:
                a, b = w[i], w[i + 1]
                sign, scalar = osc_alg._swap_relation(a, b)

                queue.append((w[:i] + [b, a] + w[i + 2:], c * sign, has_gb, tag))
                if scalar != Fraction(0):
                    queue.append((w[:i] + w[i + 2:], c * scalar, has_gb, tag))

                if not has_gb:
                    pa, pb = osc_parity(a), osc_parity(b)
                    if pa == 0 and pb == 1:
                        sigma = b.split('_')[2]
                        j = a.split('_')[1]
                        s = a.split('_')[2]
                        gl = gb_label(sigma, j, s)
                        contracted = w[:i] + w[i + 2:]
                        queue.append((contracted, c * Fraction(-1), True, gl))

                found = True
                break

            elif ia == ib and osc_parity(w[i]) == 1:
                found = True
                break

        if not found:
            if has_gb and tag is not None:
                key = tuple(w)
                if tag not in result:
                    result[tag] = {}
                result[tag][key] = result[tag].get(key, Fraction(0)) + c

    for gl in list(result.keys()):
        result[gl] = {k: v for k, v in result[gl].items() if v != Fraction(0)}
        if not result[gl]:
            del result[gl]
    return result


def compute_gamma_product(osc_alg, poly_x, poly_y):
    """Compute deformation corrections for the product X*Y."""
    result = {}
    for wx, cx in poly_x.items():
        for wy, cy in poly_y.items():
            corrections = compute_gamma_correction(osc_alg, wx + wy, cx * cy)
            for gl, poly in corrections.items():
                if gl not in result:
                    result[gl] = {}
                for w, c in poly.items():
                    result[gl][w] = result[gl].get(w, Fraction(0)) + c
    for gl in list(result.keys()):
        result[gl] = {k: v for k, v in result[gl].items() if v != Fraction(0)}
        if not result[gl]:
            del result[gl]
    return result


def poly_to_gen_dict_extended(alg, poly):
    """
    Express a polynomial as linear combination of generators.
    Allows K (identity) component for the gamma correction.
    """
    result = {}
    cartan_monos = {}
    for mono, coeff in poly.items():
        assert len(mono) <= 2, f"Degree > 2 monomial {mono}"
        if mono in alg.mono_to_gen:
            gen_name, gen_coeff = alg.mono_to_gen[mono]
            c = coeff / gen_coeff
            result[gen_name] = result.get(gen_name, Fraction(0)) + c
        elif alg._is_cartan_mono(mono):
            cartan_monos[mono] = coeff
        else:
            raise ValueError(f"Unexpected monomial {mono}")

    if cartan_monos:
        n = alg.n
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
        k_coeff = gamma - expected_gamma

        for i in range(1, n + 2):
            if c[i] != Fraction(0):
                result[f'H_{i}'] = result.get(f'H_{i}', Fraction(0)) + c[i]
        if k_coeff != Fraction(0):
            result['K'] = result.get('K', Fraction(0)) + k_coeff

    return {k: v for k, v in result.items() if v != Fraction(0)}


def compute_gamma_bracket(alg, x_name, y_name):
    """
    Compute gamma(X, Y) for [X,Y]_gamma = [X,Y]_0 + kappa*gamma(X,Y).
    Returns: dict gb_label -> {gen_name: Fraction}
    """
    px, py = alg.gen_parity[x_name], alg.gen_parity[y_name]
    sign = Fraction(-1) ** (px * py)

    gxy = compute_gamma_product(alg.osc, alg.generators[x_name], alg.generators[y_name])
    gyx = compute_gamma_product(alg.osc, alg.generators[y_name], alg.generators[x_name])

    result = {}
    all_gl = set(list(gxy.keys()) + list(gyx.keys()))

    for gl in all_gl:
        poly = {}
        if gl in gxy:
            for w, c in gxy[gl].items():
                poly[w] = poly.get(w, Fraction(0)) + c
        if gl in gyx:
            for w, c in gyx[gl].items():
                poly[w] = poly.get(w, Fraction(0)) - sign * c
        poly = {k: v for k, v in poly.items() if v != Fraction(0)}
        if poly:
            gen_dict = poly_to_gen_dict_extended(alg, poly)
            if gen_dict:
                result[gl] = gen_dict

    return result


def compute_all_gamma(alg):
    """Compute all gamma coefficients for C(n+1)."""
    basis = alg.all_basis
    entries = []

    for i, x in enumerate(basis):
        for j, y in enumerate(basis):
            if i >= j:
                continue
            gamma = compute_gamma_bracket(alg, x, y)
            for gl, gen_dict in gamma.items():
                for z, coeff in sorted(gen_dict.items()):
                    entries.append({
                        'X': x,
                        'Y': y,
                        'Z': z,
                        'gb_param': gl,
                        'coeff': str(coeff)
                    })

    return entries


def build_gb_matrix(n):
    params = []
    for sigma in ['p', 'm']:
        for j in range(1, n + 1):
            for s in ['p', 'm']:
                params.append({
                    'label': gb_label(sigma, j, s),
                    'fermionic': f'a_1_{sigma}',
                    'bosonic': f'b_{j}_{s}',
                })
    return {
        'description': 'Inhomogeneous deformation parameters for C(n+1)',
        'parameters': params,
        'total_count': 4 * n
    }


def generate_schema2(n):
    print(f"Computing gamma for C({n+1}) = osp(2|{2*n}) (n={n})...")
    alg = CnAlgebra(n)
    gamma_entries = compute_all_gamma(alg)

    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n

    schema = {
        'schema_version': '5.0',
        'layer': 2,
        'algebra': {
            'family': 'C',
            'm': 1,
            'n': n,
            'cartan_type': f'C({n + 1})',
            'alternative_notation': {
                'osp': f'osp(2|{2 * n})'
            },
            'dimension': {
                'total': even_dim + odd_dim,
                'even': even_dim,
                'odd': odd_dim
            }
        },
        'gb_matrix': build_gb_matrix(n),
        'gamma_coefficients': gamma_entries,
        'metadata': {
            'generated_by': 'C_gamma.py',
            'generation_date': str(date.today()),
            'description': 'Inhomogeneous deformation gamma structure for C(n+1)',
            'references': [
                'Frappat et al. (2000)',
                'Bakalov and Sullivan (2017)'
            ]
        }
    }
    return schema


def main():
    for n in [1, 2, 3]:
        schema = generate_schema2(n)
        filename = f'data/C_{n}_gamma.json'
        with open(filename, 'w') as f:
            json.dump(schema, f, indent=2)
        print(f"  {filename}: {len(schema['gamma_coefficients'])} gamma entries, "
              f"{schema['gb_matrix']['total_count']} gb params")


if __name__ == '__main__':
    main()
