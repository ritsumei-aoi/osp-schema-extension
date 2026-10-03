"""
C_gamma.py
Computes the gamma (inhomogeneous deformation) coefficients for C(n+1) = osp(2|2n).

The deformation is parametrized by the gb matrix:
  [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa

where sigma in {p,m} (for a_1^+/-) and s in {p,m} (for b_j^+/-).

This gives a deformed oscillator algebra. The gamma 2-cocycle gamma: g x g -> g
is defined by:
  [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)

where [X, Y]_0 is the undeformed bracket.

To compute gamma(X, Y):
  Substitute the deformed oscillator relations into the bracket computation
  and collect terms proportional to kappa.

  The deformation modifies the cross commutator:
    [b_j_s, a_1_sigma] = -gb_{sigma,j,s} * kappa

  In the standard (undeformed) algebra, [b_j_s, a_1_sigma] = 0 (they commute).
  The deformation introduces a kappa-proportional correction.

Computation strategy:
  gamma(X, Y) is non-zero when the bracket computation in the deformed algebra
  produces a kappa-proportional term. This happens when one of the "free swap"
  steps between a fermion and a boson from different sectors is modified.

  Specifically: when we compute [X, Y] in the deformed algebra and encounter
  a b_j_s · a_1_sigma adjacency (needing to pass the boson past the fermion),
  the deformed rule gives: b_j_s · a_1_sigma = a_1_sigma · b_j_s - gb_{sigma,j,s} * kappa.

  This kappa term is the source of gamma.

Implementation:
  We compute the "kappa correction" by tracking how many times a (b, a_1) swap
  occurs and what gb coefficient it introduces. We keep the kappa terms separate.
"""

import os
import sys
import json
from fractions import Fraction
from collections import defaultdict
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
from C_generators import CnPlus1, FERMION_OPS, build_osc_order


def build_gb_labels(n):
    """Build gb parameter labels: gb_{sigma}_{j}_{s}."""
    labels = []
    for sigma in ['p', 'm']:
        for j in range(1, n + 1):
            for s in ['p', 'm']:
                labels.append(f'gb_{sigma}_{j}_{s}')
    return labels


def normal_order_with_kappa(word, osc_idx, n):
    """
    Normal-order a word in the DEFORMED oscillator algebra.
    When a b_j_s passes over a_1_sigma (free swap in undeformed algebra),
    it now introduces a kappa term: b_j_s * a_1_sigma = a_1_sigma * b_j_s - gb_{sigma,j,s} * kappa.

    Returns:
      main_terms: dict word_tuple -> Fraction  (kappa-free part)
      kappa_terms: dict word_tuple -> {gb_label: Fraction}  (kappa-proportional part, symbolic)
    """
    # Represent as (word_tuple, coeff_frac, kappa_coeff_dict)
    # kappa_coeff_dict maps gb_label -> Fraction coefficient
    # The full expression is: sum_i coeff_i * word_i + kappa * sum_i gb_expr_i * word_i

    initial = [(tuple(word), Fraction(1), {})]

    changed = True
    while changed:
        changed = False
        new_terms = []

        for w, c, kappa_c in initial:
            if c == 0 and not kappa_c:
                continue

            word_zeroed = False
            swap_done = False

            for i in range(len(w) - 1):
                op_i, op_j = w[i], w[i + 1]
                prefix = w[:i]
                suffix = w[i + 2:]

                # Adjacent fermionic square -> zero
                if op_i == op_j and op_i in FERMION_OPS:
                    word_zeroed = True
                    changed = True
                    break

                if osc_idx[op_i] > osc_idx[op_j]:
                    if op_i == 'a_1_m' and op_j == 'a_1_p':
                        # CAR: a_1_m * a_1_p = -a_1_p * a_1_m + 1
                        new_w1 = prefix + (op_j, op_i) + suffix
                        new_w2 = prefix + suffix
                        new_terms.append((new_w1, -c, {k: -v for k, v in kappa_c.items()}))
                        new_terms.append((new_w2, c, dict(kappa_c)))
                    elif (op_i.startswith('b_') and op_j.startswith('b_') and
                          op_i.endswith('_m') and op_j.endswith('_p') and
                          op_i[:-2] == op_j[:-2]):
                        # CCR same mode: b_k_m * b_k_p = b_k_p * b_k_m + 1
                        new_w1 = prefix + (op_j, op_i) + suffix
                        new_w2 = prefix + suffix
                        new_terms.append((new_w1, c, dict(kappa_c)))
                        new_terms.append((new_w2, c, dict(kappa_c)))
                    elif (op_i.startswith('b_') and op_j in FERMION_OPS):
                        # Deformed swap: b_j_s * a_1_sigma = a_1_sigma * b_j_s - gb_{sigma,j,s} * kappa
                        # Parse: op_i = 'b_{j}_{s}', op_j = 'a_1_{sigma}'
                        parts_i = op_i.split('_')  # ['b', j, s]
                        j_idx = parts_i[1]
                        s = parts_i[2]
                        sigma = op_j.split('_')[2]  # a_1_{sigma}
                        gb_label = f'gb_{sigma}_{j_idx}_{s}'

                        # Main term (free swap)
                        new_w_main = prefix + (op_j, op_i) + suffix
                        new_terms.append((new_w_main, c, dict(kappa_c)))

                        # Kappa correction term: -gb_{sigma,j,s} * kappa * (prefix + suffix)
                        new_w_kappa = prefix + suffix
                        new_kappa_c = dict(kappa_c)
                        new_kappa_c[gb_label] = new_kappa_c.get(gb_label, Fraction(0)) - c
                        if any(v != 0 for v in new_kappa_c.values()):
                            new_terms.append((new_w_kappa, Fraction(0), new_kappa_c))
                    elif (op_i in FERMION_OPS and op_j.startswith('b_')):
                        # Deformed swap: a_1_sigma * b_j_s -> but in PBW, a_1 < b_j
                        # So this case (a_1 out of order = a_1_m before a_1_p handled above,
                        # or b before a_1) means this would be b after a_1 in PBW.
                        # Actually if op_i is a_1_m (idx 1) and op_j is b_k_p (idx 2), then 1 < 2 → in order.
                        # If op_i is b_k_s and op_j is a_1_p, then b_k > a_1_p → out of order → handled above.
                        # This branch shouldn't be reached for standard cases.
                        new_w = prefix + (op_j, op_i) + suffix
                        new_terms.append((new_w, c, dict(kappa_c)))
                    else:
                        # Free swap (boson-boson different modes)
                        new_w = prefix + (op_j, op_i) + suffix
                        new_terms.append((new_w, c, dict(kappa_c)))

                    swap_done = True
                    changed = True
                    break

            if not word_zeroed and not swap_done:
                new_terms.append((w, c, kappa_c))

        initial = new_terms

    # Collapse
    main_result = defaultdict(Fraction)
    kappa_result = defaultdict(lambda: defaultdict(Fraction))

    for w, c, kappa_c in initial:
        if c != 0:
            main_result[w] += c
        for gb_label, gb_coeff in kappa_c.items():
            if gb_coeff != 0:
                kappa_result[w][gb_label] += gb_coeff

    main_result = {k: v for k, v in main_result.items() if v != 0}
    kappa_result = {k: dict(v) for k, v in kappa_result.items() if any(x != 0 for x in v.values())}
    return main_result, kappa_result


def multiply_with_kappa(elem1, elem2, osc_idx, n):
    """Multiply two elements in deformed algebra. Returns (main, kappa) dicts."""
    main_result = defaultdict(Fraction)
    kappa_result = defaultdict(lambda: defaultdict(Fraction))

    for w1, c1 in elem1.items():
        for w2, c2 in elem2.items():
            combined = list(w1) + list(w2)
            main_terms, kappa_terms = normal_order_with_kappa(combined, osc_idx, n)
            for w, c in main_terms.items():
                main_result[w] += c1 * c2 * c
            for w, gb_dict in kappa_terms.items():
                for gb_label, gb_c in gb_dict.items():
                    kappa_result[w][gb_label] += c1 * c2 * gb_c

    main_result = {k: v for k, v in main_result.items() if v != 0}
    kappa_result = {k: dict(v) for k, v in kappa_result.items()
                    if any(x != 0 for x in v.values())}
    return dict(main_result), dict(kappa_result)


def deformed_bracket(elem1, elem2, p1, p2, osc_idx, n):
    """
    Compute [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y) in deformed algebra.
    Returns (main, kappa) where main = [X,Y]_0 and kappa = gamma(X,Y) as symbolic dict.
    """
    xy_main, xy_kappa = multiply_with_kappa(elem1, elem2, osc_idx, n)
    yx_main, yx_kappa = multiply_with_kappa(elem2, elem1, osc_idx, n)

    sign = Fraction((-1) ** (p1 * p2))

    # main part
    main = defaultdict(Fraction)
    for w, c in xy_main.items():
        main[w] += c
    for w, c in yx_main.items():
        main[w] -= sign * c
    main = {k: v for k, v in main.items() if v != 0}

    # kappa part (symbolic: each entry is {gb_label: Fraction})
    kappa = defaultdict(lambda: defaultdict(Fraction))
    for w, gb_dict in xy_kappa.items():
        for gb, c in gb_dict.items():
            kappa[w][gb] += c
    for w, gb_dict in yx_kappa.items():
        for gb, c in gb_dict.items():
            kappa[w][gb] -= sign * c
    kappa = {k: {g: v for g, v in d.items() if v != 0}
             for k, d in kappa.items() if any(x != 0 for x in d.values())}

    return dict(main), dict(kappa)


def compute_gamma(n):
    """Compute all gamma coefficients for C(n+1)."""
    alg = CnPlus1(n)
    osc_idx = alg.osc_idx
    basis = alg.basis
    parity = alg.parity_map
    R = alg.realizations

    gamma_entries = []

    for i in range(len(basis)):
        for j in range(i + 1, len(basis)):
            X, Y = basis[i], basis[j]
            p_X = parity[X]
            p_Y = parity[Y]

            main, kappa = deformed_bracket(R[X], R[Y], p_X, p_Y, osc_idx, n)

            if not kappa:
                continue

            # Decompose kappa into basis generators
            # kappa: word_tuple -> {gb_label: Fraction}
            # First, group all monomial contributions by basis generator
            gen_gb = defaultdict(lambda: defaultdict(Fraction))

            # Collect all monomials that are non-Cartan (direct mapping)
            kappa_expr = defaultdict(lambda: defaultdict(Fraction))
            for mono, gb_dict in kappa.items():
                for gb, c in gb_dict.items():
                    kappa_expr[mono][gb] += c

            # Decompose each mono contribution to a generator
            # Use same logic as alg.decompose but for symbolic coefficients
            # First handle non-Cartan monomials
            remaining_kappa = dict(kappa_expr)
            n_ = n

            # Odd generators
            for k in range(1, n_ + 1):
                for s1, s2 in [('p', 'p'), ('p', 'm'), ('m', 'p'), ('m', 'm')]:
                    a_op = f'a_1_{s1}'
                    b_op = f'b_{k}_{s2}'
                    mono = (a_op, b_op)
                    if mono in remaining_kappa:
                        label = f'E_eps1_del{k}_{s1}{s2}'
                        for gb, c in remaining_kappa.pop(mono).items():
                            gen_gb[label][gb] += c

            # Even non-Cartan
            for k in range(1, n_ + 1):
                for suffix2, s1s2 in [('p', ('p', 'p')), ('m', ('m', 'm'))]:
                    mono = (f'b_{k}_{s1s2[0]}', f'b_{k}_{s1s2[1]}')
                    lbl = f'E_2del{k}_{suffix2}'
                    if mono in remaining_kappa:
                        for gb, c in remaining_kappa.pop(mono).items():
                            gen_gb[lbl][gb] += c

            for i2 in range(1, n_ + 1):
                for j2 in range(i2 + 1, n_ + 1):
                    for s1, s2, suffix2 in [('p', 'p', 'pp'), ('m', 'm', 'mm'),
                                             ('p', 'm', 'pm'), ('m', 'p', 'mp')]:
                        mono = (f'b_{i2}_{s1}', f'b_{j2}_{s2}')
                        lbl = f'E_del{i2}_del{j2}_{suffix2}'
                        if mono in remaining_kappa:
                            for gb, c in remaining_kappa.pop(mono).items():
                                gen_gb[lbl][gb] += c

            # Cartan: N_a and N_{b_k}
            c_a_gb = remaining_kappa.pop(('a_1_p', 'a_1_m'), {})
            c_b_gb = [remaining_kappa.pop((f'b_{k}_p', f'b_{k}_m'), {}) for k in range(1, n_ + 1)]
            scalar_gb = remaining_kappa.pop((), {})

            # Ignore remaining (should be empty)
            # Express Cartan as H_k coefficients
            # H_1 coeff: c_a
            # H_j (2<=j<=n): -c_a + sum_{k=1}^{j-1} c_b[k-1]
            # H_{n+1}: c_a - sum c_b

            # For each gb label, compute the H coefficients
            all_gbs = set()
            for d in [c_a_gb] + c_b_gb + [scalar_gb]:
                all_gbs.update(d.keys())

            for gb_l in all_gbs:
                ca = c_a_gb.get(gb_l, Fraction(0))
                cb = [c_b_gb[k].get(gb_l, Fraction(0)) for k in range(n_)]

                h1 = ca
                if h1 != 0:
                    gen_gb['H_1'][gb_l] += h1

                for jj in range(2, n_ + 1):
                    hj = -ca + sum(cb[:jj - 1])
                    if hj != 0:
                        gen_gb[f'H_{jj}'][gb_l] += hj

                h_n1 = ca - sum(cb)
                if h_n1 != 0:
                    gen_gb[f'H_{n_+1}'][gb_l] += h_n1

            # Build entries
            for Z, gb_dict in gen_gb.items():
                gb_dict = {k: v for k, v in gb_dict.items() if v != 0}
                if gb_dict:
                    # Build symbolic expression string
                    terms = []
                    for gb_lbl, coeff in sorted(gb_dict.items()):
                        if coeff == 1:
                            terms.append(gb_lbl)
                        elif coeff == -1:
                            terms.append(f'-{gb_lbl}')
                        else:
                            terms.append(f'{coeff}*{gb_lbl}')
                    coeff_expr = ' + '.join(terms).replace('+ -', '- ')
                    gamma_entries.append({
                        'X': X, 'Y': Y, 'Z': Z,
                        'coeff_expr': coeff_expr,
                        'gb_coeffs': {k: str(v) for k, v in gb_dict.items()}
                    })

    return gamma_entries


def generate_gamma_json(n, output_dir='data'):
    alg = CnPlus1(n)
    dim = {
        'total': 2 * n * n + 5 * n + 1,
        'even': 2 * n * n + n + 1,
        'odd': 4 * n
    }
    gb_labels = build_gb_labels(n)
    gamma_entries = compute_gamma(n)

    schema = {
        'schema_version': '5.0',
        'algebra': {
            'family': 'C', 'm': 1, 'n': n,
            'cartan_type': f'C({n+1})',
            'alternative_notation': {'osp': f'osp(2|{2*n})'},
            'dimension': dim
        },
        'deformation_parameters': {
            'gb_matrix': {
                'description': f'4n={4*n} parity-1 parameters for C({n+1})',
                'count': 4 * n,
                'labels': gb_labels,
                'indexing': 'gb_{sigma}_{j}_{s}: sigma in {p,m}, j=1..n, s in {p,m}'
            }
        },
        'gamma_coefficients': gamma_entries,
        'metadata': {
            'generated_by': 'src/C_gamma.py',
            'generation_date': str(date.today()),
            'description': ('gamma(X,Y) computed from deformed oscillator relations: '
                            '[b_j_s, a_1_sigma] = -gb_{sigma,j,s} * kappa')
        }
    }

    os.makedirs(output_dir, exist_ok=True)
    fname = os.path.join(output_dir, f'C_{n}_gamma.json')
    with open(fname, 'w') as f:
        json.dump(schema, f, indent=2)
    print(f"C({n+1}): {len(gamma_entries)} gamma entries -> {fname}")
    return schema


def main():
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    for n in range(1, 4):
        generate_gamma_json(n, output_dir)
    print("Done.")


if __name__ == '__main__':
    main()
