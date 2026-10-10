#!/usr/bin/env python3
"""
C_generators.py: Structure constant generator for C(n+1) = osp(2|2n).

Computes all non-zero graded brackets [X, Y} for basis pairs X < Y (PBW order)
and outputs Schema 1 JSON files data/C_{n}_structure.json for n=1, 2, 3.
"""

from fractions import Fraction
from itertools import combinations
import json
import os
from datetime import date


# ─── Oscillator algebra ──────────────────────────────────────────────────────

def get_osc_order(n):
    """PBW ordering: a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m"""
    order = ['a_1_p', 'a_1_m']
    for k in range(1, n + 1):
        order.extend([f'b_{k}_p', f'b_{k}_m'])
    return order


def osc_parity(osc):
    """1 if fermionic (a_1_p, a_1_m), 0 if bosonic."""
    return 1 if osc in ('a_1_p', 'a_1_m') else 0


def _elementary_bracket(a, b, n):
    """
    [a, b} for out-of-order pair where osc_idx[a] > osc_idx[b].
    Non-zero cases:
      [a_1_m, a_1_p} = 1   (from {a_1^-, a_1^+} = 1)
      [b_k_m, b_k_p} = 1   (from [b_k^-, b_k^+] = 1)
    """
    if a == 'a_1_m' and b == 'a_1_p':
        return {(): Fraction(1)}
    for k in range(1, n + 1):
        if a == f'b_{k}_m' and b == f'b_{k}_p':
            return {(): Fraction(1)}
    return {}


def _norm_word(word, coeff, osc_idx, n):
    """
    Normalize a single oscillator word to PBW order via bubble sort.
    Returns {word_tuple: Fraction}.
    """
    for i in range(len(word) - 1):
        a, b = word[i], word[i + 1]
        if osc_idx[a] > osc_idx[b]:
            pa, pb = osc_parity(a), osc_parity(b)
            sign = Fraction((-1) ** (pa * pb))
            comm = _elementary_bracket(a, b, n)

            swapped = word[:i] + [b, a] + word[i + 2:]
            result = _norm_word(swapped, coeff * sign, osc_idx, n)

            for cw, cv in comm.items():
                surrounding = word[:i] + list(cw) + word[i + 2:]
                for w, v in _norm_word(surrounding, coeff * cv, osc_idx, n).items():
                    result[w] = result.get(w, Fraction(0)) + v

            return {w: v for w, v in result.items() if v != 0}

    # In PBW order; check fermionic nilpotency
    for i in range(len(word) - 1):
        if word[i] == word[i + 1] and osc_parity(word[i]) == 1:
            return {}

    return {tuple(word): coeff}


def poly_mul(p, q, osc_idx, n):
    """Multiply two oscillator polynomials and normal-order."""
    out = {}
    for w1, c1 in p.items():
        for w2, c2 in q.items():
            for w, v in _norm_word(list(w1 + w2), c1 * c2, osc_idx, n).items():
                out[w] = out.get(w, Fraction(0)) + v
    return {w: v for w, v in out.items() if v != 0}


def graded_bracket(X, Y, px, py, osc_idx, n):
    """[X, Y} = XY - (-1)^{px*py} YX."""
    XY = poly_mul(X, Y, osc_idx, n)
    YX = poly_mul(Y, X, osc_idx, n)
    sign = Fraction((-1) ** (px * py))
    out = dict(XY)
    for w, v in YX.items():
        out[w] = out.get(w, Fraction(0)) - sign * v
    return {w: v for w, v in out.items() if v != 0}


# ─── Generator construction ───────────────────────────────────────────────────

def build_algebra(n):
    """
    Build C(n+1) = osp(2|2n) generators.

    Returns (basis_odd, basis_even, parity, gen_poly, osc_idx) where:
      basis_odd, basis_even  – lists of labels in PBW order
      parity                 – {label: 0 or 1}
      gen_poly               – {label: {word_tuple: Fraction}}
      osc_idx                – {osc_label: int}
    """
    osc_order = get_osc_order(n)
    osc_idx = {o: i for i, o in enumerate(osc_order)}
    gen_poly = {}
    parity = {}
    basis_odd = []
    basis_even = []

    # Odd generators – PBW: pp-group < pm-group < mp-group < mm-group, k=1..n within
    for suffix, a_osc, b_suf in [('pp', 'a_1_p', 'p'), ('pm', 'a_1_p', 'm'),
                                   ('mp', 'a_1_m', 'p'), ('mm', 'a_1_m', 'm')]:
        for k in range(1, n + 1):
            lbl = f'E_eps1_del{k}_{suffix}'
            b_osc = f'b_{k}_{b_suf}'
            basis_odd.append(lbl)
            parity[lbl] = 1
            gen_poly[lbl] = {(a_osc, b_osc): Fraction(1)}

    # Even generators

    # Cartan: H_1, ..., H_{n+1}
    gen_poly['H_1'] = {('a_1_p', 'a_1_m'): Fraction(1),
                       ('b_1_p', 'b_1_m'): Fraction(1)}
    parity['H_1'] = 0
    basis_even.append('H_1')

    for k in range(2, n + 1):
        lbl = f'H_{k}'
        gen_poly[lbl] = {(f'b_{k-1}_p', f'b_{k-1}_m'): Fraction(1),
                         (f'b_{k}_p', f'b_{k}_m'): Fraction(-1)}
        parity[lbl] = 0
        basis_even.append(lbl)

    hn1 = f'H_{n+1}'
    gen_poly[hn1] = {(f'b_{n}_p', f'b_{n}_m'): Fraction(-1),
                     (): Fraction(-1, 2)}
    parity[hn1] = 0
    basis_even.append(hn1)

    # Positive even: E_2del{k}_p, then E_del{i}_del{j}_pp (i<j)
    for k in range(1, n + 1):
        lbl = f'E_2del{k}_p'
        gen_poly[lbl] = {(f'b_{k}_p', f'b_{k}_p'): Fraction(1, 2)}
        parity[lbl] = 0
        basis_even.append(lbl)

    for i, j in combinations(range(1, n + 1), 2):
        lbl = f'E_del{i}_del{j}_pp'
        gen_poly[lbl] = {(f'b_{i}_p', f'b_{j}_p'): Fraction(1)}
        parity[lbl] = 0
        basis_even.append(lbl)

    # Negative even: E_2del{k}_m, then E_del{i}_del{j}_mm (i<j)
    for k in range(1, n + 1):
        lbl = f'E_2del{k}_m'
        gen_poly[lbl] = {(f'b_{k}_m', f'b_{k}_m'): Fraction(1, 2)}
        parity[lbl] = 0
        basis_even.append(lbl)

    for i, j in combinations(range(1, n + 1), 2):
        lbl = f'E_del{i}_del{j}_mm'
        gen_poly[lbl] = {(f'b_{i}_m', f'b_{j}_m'): Fraction(1)}
        parity[lbl] = 0
        basis_even.append(lbl)

    # Mixed: E_del{i}_del{j}_pm (i<j), then E_del{i}_del{j}_mp (i<j)
    for i, j in combinations(range(1, n + 1), 2):
        lbl = f'E_del{i}_del{j}_pm'
        gen_poly[lbl] = {(f'b_{i}_p', f'b_{j}_m'): Fraction(1)}
        parity[lbl] = 0
        basis_even.append(lbl)

    for i, j in combinations(range(1, n + 1), 2):
        lbl = f'E_del{i}_del{j}_mp'
        gen_poly[lbl] = {(f'b_{i}_m', f'b_{j}_p'): Fraction(1)}
        parity[lbl] = 0
        basis_even.append(lbl)

    return basis_odd, basis_even, parity, gen_poly, osc_idx


# ─── Decomposition ────────────────────────────────────────────────────────────

def build_word_map(gen_poly, basis_odd, basis_even):
    """
    Map each non-Cartan oscillator word to (generator_label, coefficient).
    Every non-Cartan generator has exactly one oscillator word.
    """
    word_map = {}
    for lbl in basis_odd + basis_even:
        if lbl.startswith('H_'):
            continue
        gp = gen_poly[lbl]
        for word, coeff in gp.items():
            if word == ():
                continue
            assert word not in word_map, f"Duplicate word {word}: {lbl} vs {word_map[word][0]}"
            word_map[word] = (lbl, coeff)
    return word_map


def _solve_cartan(r_a, r_b, r_0, n):
    """
    Solve for Cartan coefficients c[1..n+1] from:
      c[1]                              = r_a          (from (a_1_p, a_1_m))
      c[n+1]                            = -2 * r_0     (from () in H_{n+1})
      n=1: c[1] - c[2] = r_b[0]
      n>=2: c[1]+c[2]=r_b[0]; -c[k]+c[k+1]=r_b[k-1] for k=2..n-1; -c[n]-c[n+1]=r_b[n-1]
    Returns list c (1-indexed, c[0] unused).
    """
    c = [Fraction(0)] * (n + 2)
    c[1] = r_a
    c[n + 1] = Fraction(-2) * r_0

    if n == 1:
        # H_2 = -b_1^+ b_1^- - 1/2: coefficient of (b_1_p, b_1_m) is -1
        # c[1]*1 + c[2]*(-1) = r_b[0]  =>  c[2] = c[1] - r_b[0]
        c[2] = c[1] - r_b[0]
    else:
        # H_2 = b_1^+ b_1^- - b_2^+ b_2^-: coeff of (b_1_p,b_1_m) is +1
        c[2] = r_b[0] - c[1]
        for k in range(2, n):        # propagate c[3]..c[n]
            c[k + 1] = r_b[k - 1] + c[k]
        # c[n+1] already set from (); consistency: -c[n] - c[n+1] = r_b[n-1]

    return c


def decompose(poly, gen_poly, basis_odd, basis_even, n, word_map):
    """
    Express a normal-ordered polynomial as a linear combination of generators.
    Returns [(label, Fraction), ...] for non-zero terms.
    Raises ValueError if poly contains unexpected terms.
    """
    remaining = dict(poly)
    result = []

    # Step 1: match non-Cartan words (each word → exactly one generator)
    for word in list(remaining.keys()):
        if word in word_map:
            lbl, gen_coeff = word_map[word]
            c = remaining[word] / gen_coeff
            if c != 0:
                result.append((lbl, c))
                for w, v in gen_poly[lbl].items():
                    remaining[w] = remaining.get(w, Fraction(0)) - c * v
                    if remaining[w] == 0:
                        remaining.pop(w, None)

    # Step 2: solve Cartan system for remaining words
    r_a = remaining.pop(('a_1_p', 'a_1_m'), Fraction(0))
    r_b = [remaining.pop((f'b_{k}_p', f'b_{k}_m'), Fraction(0)) for k in range(1, n + 1)]
    r_0 = remaining.pop((), Fraction(0))

    if r_a != 0 or any(r != 0 for r in r_b) or r_0 != 0:
        c = _solve_cartan(r_a, r_b, r_0, n)
        for k in range(1, n + 2):
            if c[k] != 0:
                result.append((f'H_{k}', c[k]))

    if remaining:
        raise ValueError(f"Bracket produced terms not in algebra span: {remaining}")

    return [(lbl, c) for lbl, c in result if c != 0]


# ─── Frappat human-readable forms ────────────────────────────────────────────

def frappat_form(lbl, n):
    """Return a human-readable Frappat-style string for a generator label."""
    if lbl == 'H_1':
        return 'a_1^+ a_1^- + b_1^+ b_1^-'
    if lbl == f'H_{n+1}':
        return f'-b_{n}^+ b_{n}^- - 1/2'
    if lbl.startswith('H_'):
        k = int(lbl[2:])
        return f'b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-'
    if lbl.startswith('E_eps1_del'):
        rest = lbl[len('E_eps1_del'):]          # e.g. "1_pp"
        k_str, suffix = rest.rsplit('_', 1)
        a_sign = '^+' if suffix[0] == 'p' else '^-'
        b_sign = '^+' if suffix[1] == 'p' else '^-'
        return f'a_1{a_sign} b_{k_str}{b_sign}'
    if lbl.startswith('E_2del'):
        rest = lbl[len('E_2del'):]              # e.g. "1_p"
        k_str, sign = rest.rsplit('_', 1)
        b_sign = '^+' if sign == 'p' else '^-'
        return f'(1/2)(b_{k_str}{b_sign})^2'
    if lbl.startswith('E_del'):
        rest = lbl[len('E_del'):]               # e.g. "1_del2_pp"
        idx = rest.find('_del')
        i_str = rest[:idx]
        rest2 = rest[idx + len('_del'):]        # e.g. "2_pp"
        j_str, suffix = rest2.rsplit('_', 1)
        b1_sign = '^+' if suffix[0] == 'p' else '^-'
        b2_sign = '^+' if suffix[1] == 'p' else '^-'
        return f'b_{i_str}{b1_sign} b_{j_str}{b2_sign}'
    return lbl


# ─── Schema assembly ─────────────────────────────────────────────────────────

def generate_schema(n):
    """Generate Schema 1 dict for C(n+1) = osp(2|2n)."""
    basis_odd, basis_even, parity, gen_poly, osc_idx = build_algebra(n)
    all_basis = basis_odd + basis_even
    word_map = build_word_map(gen_poly, basis_odd, basis_even)

    # Compute structure constants (upper triangle: i < j in PBW order)
    structure_constants = []
    for i in range(len(all_basis)):
        for j in range(i + 1, len(all_basis)):
            X, Y = all_basis[i], all_basis[j]
            px, py = parity[X], parity[Y]
            br = graded_bracket(gen_poly[X], gen_poly[Y], px, py, osc_idx, n)
            if not br:
                continue
            terms = decompose(br, gen_poly, basis_odd, basis_even, n, word_map)
            for Z, c in terms:
                structure_constants.append({
                    'X': X, 'Y': Y, 'Z': Z,
                    'coeff': str(c),
                    'sign_rule': 'graded'
                })

    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n

    osc_labels_bosons = []
    for k in range(1, n + 1):
        osc_labels_bosons.extend([f'b_{k}_p', f'b_{k}_m'])

    realizations = {}
    for lbl in all_basis:
        gp = gen_poly[lbl]
        std_form = [{'words': list(w), 'coeff': str(c)} for w, c in gp.items()]
        realizations[lbl] = {
            'standard_form': std_form,
            'frappat_form': frappat_form(lbl, n),
            'parity': parity[lbl]
        }

    return {
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
            'dimension_formula': {
                'even': '2*n^2 + n + 1',
                'odd': '4*n',
                'total': '2*n^2 + 5*n + 1'
            },
            'dimension': {
                'total': even_dim + odd_dim,
                'even': even_dim,
                'odd': odd_dim
            }
        },
        'oscillator_generators': {
            'fermions': {
                'm': 1,
                'labels': ['a_1_p', 'a_1_m'],
                'parity': 1,
                'relation': '{a_1^-, a_1^+} = 1',
                'description': 'Standard fermionic CAR pair; m=1 fermionic degree of freedom.'
            },
            'bosons': {
                'n': n,
                'count': 2 * n,
                'labels': osc_labels_bosons,
                'description': f'Bosonic oscillators b_k^± with k=1,...,{n}.'
            }
        },
        'oscillator_relations': {
            'standard_fermion_anticommutators': {
                'description': 'Standard CAR for fermionic pair a_1^±',
                'relations': {
                    'anticommutator': '{a_1^-, a_1^+} = 1',
                    'nilpotency': '{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0'
                }
            },
            'bosonic_commutators': {
                'description': 'CCR for bosonic oscillators',
                'relations': {
                    'same_type': '[b_i^±, b_j^±] = 0 for all i, j',
                    'conjugate_pair': '[b_i^-, b_j^+] = delta_{ij}'
                }
            },
            'mixed_commutators': {
                'boson_fermion': '[b_i^±, a_1^±] = 0'
            }
        },
        'central_elements': {
            'kappa': {
                'parity': 1,
                'description': 'Odd central extension element; nilpotent: kappa^2 = 0.',
                'note': 'Formal extension symbol; appears in deformed oscillator exchange relations.'
            },
            'K': {
                'parity': 0,
                'description': 'Even central element; identified with scalar 1 in all current applications.',
                'note': 'Not an independent basis element; excluded from PBW ordering and basis lists.'
            }
        },
        'basis': {
            'odd': basis_odd,
            'even': basis_even,
            'ordering_convention': (
                'PBW (epsilon-grouped): [odd,+eps,+del] < [odd,+eps,-del] '
                '< [odd,-eps,+del] < [odd,-eps,-del] < [even]; '
                'kappa and K are excluded as independent basis elements.'
            )
        },
        'parity': parity,
        'generator_realization': {
            'description': 'Standard form with PBW oscillator ordering',
            'ordering': ', '.join(get_osc_order(n)),
            'realizations': realizations
        },
        'structure_constants': structure_constants,
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
    import argparse
    parser = argparse.ArgumentParser(description='Generate C(n+1) Schema 1 JSON')
    parser.add_argument('--n', type=int, nargs='+', default=[1, 2, 3])
    parser.add_argument('--output-dir', default='data')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    for n in args.n:
        print(f'Generating C({n+1}) = osp(2|{2*n})...')
        schema = generate_schema(n)
        fname = os.path.join(args.output_dir, f'C_{n}_structure.json')
        with open(fname, 'w') as f:
            json.dump(schema, f, indent=2)
        dim = schema['algebra']['dimension']
        nsc = len(schema['structure_constants'])
        print(f'  Written: {fname}')
        print(f'  Dimensions: even={dim["even"]}, odd={dim["odd"]}, total={dim["total"]}')
        print(f'  Non-zero structure constants: {nsc}')


if __name__ == '__main__':
    main()
