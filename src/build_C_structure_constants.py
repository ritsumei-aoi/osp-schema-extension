#!/usr/bin/env python3
"""
build_C_structure_constants.py
Compute C(n+1) = osp(2|2n) structure constants and output Schema 1 JSON.

Usage: python src/build_C_structure_constants.py
Output: data/C_1_structure.json, data/C_2_structure.json, data/C_3_structure.json

Oscillator index convention (for bosonic rank n):
  0      a_1_p   fermionic (parity 1)
  1      a_1_m   fermionic (parity 1)
  2k     b_k_p   bosonic   (parity 0), k = 1..n
  2k+1   b_k_m   bosonic   (parity 0)

CAR: {a_1^-, a_1^+} = 1,  (a_1^+)^2 = (a_1^-)^2 = 0
CCR: [b_k^-, b_l^+] = delta_{kl},  [b_k^pm, b_l^pm] = 0
Mixed: [b_k^pm, a_1^pm] = 0
"""

from fractions import Fraction
from collections import OrderedDict
import json
import sys
import os
from datetime import date


# ── Oscillator algebra ────────────────────────────────────────────────────────

def is_fermionic(idx: int) -> bool:
    return idx < 2


def reduce_word(word: tuple) -> dict:
    """
    Reduce a word (tuple of oscillator indices) to PBW normal form.
    PBW order: a_1_p(0) < a_1_m(1) < b_1_p(2) < b_1_m(3) < b_2_p(4) < ...
    Returns {word_tuple: Fraction}.
    Uses an iterative stack to avoid recursion depth issues.
    """
    stack = [(list(word), Fraction(1))]
    result = {}

    while stack:
        w, coeff = stack.pop()

        reduced = True
        for i in range(len(w) - 1):
            a, b = w[i], w[i + 1]

            # Same fermionic oscillator squared: vanishes
            if a == b and is_fermionic(a):
                reduced = False
                break

            if a > b:
                pre = w[:i]
                suf = w[i + 2:]
                af = is_fermionic(a)
                bf = is_fermionic(b)

                if af and bf:
                    # {a_1_m, a_1_p} = 1; all other fermionic anticommutators = 0
                    acomm = Fraction(1) if (a == 1 and b == 0) else Fraction(0)
                    # a * b = {a,b} - b * a
                    stack.append((pre + [b, a] + suf, -coeff))
                    if acomm:
                        stack.append((pre + suf, acomm * coeff))

                elif not af and not bf:
                    # [b_k_m, b_k_p] = 1 for same k; all other bosonic commutators = 0
                    # a = 2k+1 (odd, >= 3), b = 2k = a-1
                    comm = (Fraction(1)
                            if (a % 2 == 1 and a >= 3 and b == a - 1)
                            else Fraction(0))
                    # a * b = b * a + [a, b]
                    stack.append((pre + [b, a] + suf, coeff))
                    if comm:
                        stack.append((pre + suf, comm * coeff))

                else:
                    # Mixed boson-fermion: commute freely
                    stack.append((pre + [b, a] + suf, coeff))

                reduced = False
                break

        if reduced:
            key = tuple(w)
            result[key] = result.get(key, Fraction(0)) + coeff

    return {w: c for w, c in result.items() if c}


def add_polys(p1: dict, p2: dict) -> dict:
    res = dict(p1)
    for w, c in p2.items():
        res[w] = res.get(w, Fraction(0)) + c
    return {w: c for w, c in res.items() if c}


def scale_poly(p: dict, s) -> dict:
    s = Fraction(s)
    if s == 0:
        return {}
    return {w: c * s for w, c in p.items()}


def multiply_polys(p1: dict, p2: dict) -> dict:
    res = {}
    for w1, c1 in p1.items():
        for w2, c2 in p2.items():
            for w, c in reduce_word(w1 + w2).items():
                v = c1 * c2 * c
                if v:
                    res[w] = res.get(w, Fraction(0)) + v
    return {w: c for w, c in res.items() if c}


def graded_bracket(X: dict, Y: dict, pX: int, pY: int) -> dict:
    """[X, Y} = XY - (-1)^{pX pY} YX"""
    XY = multiply_polys(X, Y)
    YX = multiply_polys(Y, X)
    return add_polys(XY, scale_poly(YX, -(-1) ** (pX * pY)))


# ── Generator construction ────────────────────────────────────────────────────

def bp(k: int) -> int:
    """Oscillator index for b_k^+"""
    return 2 * k


def bm(k: int) -> int:
    """Oscillator index for b_k^-"""
    return 2 * k + 1


def osc_labels_for(n: int) -> list:
    labels = ['a_1_p', 'a_1_m']
    for k in range(1, n + 1):
        labels += [f'b_{k}_p', f'b_{k}_m']
    return labels


def build_generators(n: int) -> OrderedDict:
    """
    Build C(n+1) = osp(2|2n) generators as OrderedDict:
        name -> (poly: dict{word_tuple: Fraction}, parity: int)

    Insertion order follows schema basis ordering (schema spec §basis):
      Even:  Cartans H_1..H_{n+1},
             positive roots E_2del{k}_p / E_del{i}_del{j}_pp,
             negative roots E_2del{k}_m / E_del{i}_del{j}_mm,
             mixed roots E_del{i}_del{j}_pm / E_del{i}_del{j}_mp
      Odd:   a_1^+ block (E_eps1_del{k}_pp, then E_eps1_del{k}_pm, k=1..n)
             a_1^- block (E_eps1_del{k}_mp, then E_eps1_del{k}_mm, k=1..n)
    """
    gens = OrderedDict()

    # ── Even: Cartans ──
    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    gens['H_1'] = (
        {(0, 1): Fraction(1), (bp(1), bm(1)): Fraction(1)}, 0)
    # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-  (k = 2..n)
    for k in range(2, n + 1):
        gens[f'H_{k}'] = (
            {(bp(k - 1), bm(k - 1)): Fraction(1),
             (bp(k), bm(k)): Fraction(-1)}, 0)
    # H_{n+1} = -b_n^+ b_n^- - 1/2
    gens[f'H_{n+1}'] = (
        {(bp(n), bm(n)): Fraction(-1), (): Fraction(-1, 2)}, 0)

    # ── Even: positive roots ──
    for k in range(1, n + 1):
        gens[f'E_2del{k}_p'] = ({(bp(k), bp(k)): Fraction(1)}, 0)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            gens[f'E_del{i}_del{j}_pp'] = ({(bp(i), bp(j)): Fraction(1)}, 0)

    # ── Even: negative roots ──
    for k in range(1, n + 1):
        gens[f'E_2del{k}_m'] = ({(bm(k), bm(k)): Fraction(1)}, 0)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            gens[f'E_del{i}_del{j}_mm'] = ({(bm(i), bm(j)): Fraction(1)}, 0)

    # ── Even: mixed roots ──
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            gens[f'E_del{i}_del{j}_pm'] = ({(bp(i), bm(j)): Fraction(1)}, 0)
            gens[f'E_del{i}_del{j}_mp'] = ({(bm(i), bp(j)): Fraction(1)}, 0)

    # ── Odd: a_1^+ block ──
    for k in range(1, n + 1):
        gens[f'E_eps1_del{k}_pp'] = ({(0, bp(k)): Fraction(1)}, 1)
    for k in range(1, n + 1):
        gens[f'E_eps1_del{k}_pm'] = ({(0, bm(k)): Fraction(1)}, 1)

    # ── Odd: a_1^- block ──
    for k in range(1, n + 1):
        gens[f'E_eps1_del{k}_mp'] = ({(1, bp(k)): Fraction(1)}, 1)
    for k in range(1, n + 1):
        gens[f'E_eps1_del{k}_mm'] = ({(1, bm(k)): Fraction(1)}, 1)

    return gens


# ── Decomposition ─────────────────────────────────────────────────────────────

def decompose(poly: dict, gens: OrderedDict, n: int) -> dict:
    """
    Express poly as a linear combination of generators.
    Returns {gen_name: Fraction}, raises AssertionError if not expressible.

    Strategy:
      1. Generators with a PBW word unique to them are identified first.
      2. Remaining words (shared among Cartan generators) are solved by
         Gaussian elimination over Fraction.
    """
    if not poly:
        return {}

    # Map: word -> set of generator names that have it
    word_to_gens: dict = {}
    for name, (gpoly, _) in gens.items():
        for w in gpoly:
            word_to_gens.setdefault(w, set()).add(name)

    remaining = dict(poly)
    coeffs: dict = {}

    def subtract(name: str, c: Fraction):
        gpoly, _ = gens[name]
        for w, gc in gpoly.items():
            v = remaining.get(w, Fraction(0)) - c * gc
            if v:
                remaining[w] = v
            else:
                remaining.pop(w, None)

    # Step 1: generators whose PBW word appears in no other generator
    changed = True
    while changed and remaining:
        changed = False
        for name, (gpoly, _) in gens.items():
            for w, gc in gpoly.items():
                if w in remaining and word_to_gens.get(w) == {name}:
                    c = remaining[w] / gc
                    coeffs[name] = coeffs.get(name, Fraction(0)) + c
                    subtract(name, c)
                    changed = True
                    break

    if not remaining:
        return {k: v for k, v in coeffs.items() if v}

    # Step 2: Cartan system (words shared among H_1..H_{n+1})
    cartan_names = [f'H_{k}' for k in range(1, n + 2)]
    cartan_words_set = set(w for nm in cartan_names for w in gens[nm][0])
    assert all(w in cartan_words_set for w in remaining), (
        f'Unidentifiable words after unique extraction: '
        f'{set(remaining.keys()) - cartan_words_set}')

    all_words = sorted(cartan_words_set, key=lambda w: (len(w), w))
    nc = len(cartan_names)
    nw = len(all_words)

    # Build augmented matrix [M | rhs] over Fraction
    aug = [
        [gens[cartan_names[j]][0].get(w, Fraction(0)) for j in range(nc)]
        + [remaining.get(w, Fraction(0))]
        for w in all_words
    ]

    # Row-reduced echelon form
    pivot_col_to_row: dict = {}
    row = 0
    for col in range(nc):
        pr = next((r for r in range(row, nw) if aug[r][col] != 0), None)
        if pr is None:
            continue
        aug[pr], aug[row] = aug[row], aug[pr]
        pv = aug[row][col]
        aug[row] = [x / pv for x in aug[row]]
        for r in range(nw):
            if r != row and aug[r][col] != 0:
                f = aug[r][col]
                aug[r] = [aug[r][c2] - f * aug[row][c2] for c2 in range(nc + 1)]
        pivot_col_to_row[col] = row
        row += 1

    # Consistency check
    for r in range(row, nw):
        assert all(aug[r][c2] == 0 for c2 in range(nc)), (
            f'Inconsistent Cartan system at row {r}')
        assert aug[r][-1] == 0, (
            f'Inconsistent rhs at row {r}: {aug[r][-1]}')

    for col, r in pivot_col_to_row.items():
        c = aug[r][-1]
        if c:
            coeffs[cartan_names[col]] = (
                coeffs.get(cartan_names[col], Fraction(0)) + c)

    return {k: v for k, v in coeffs.items() if v}


# ── Schema 1 builder ──────────────────────────────────────────────────────────

def basis_lists(gens: OrderedDict) -> tuple:
    """Return (basis_even, basis_odd) in schema ordering (dict insertion order)."""
    even = [name for name, (_, p) in gens.items() if p == 0]
    odd  = [name for name, (_, p) in gens.items() if p == 1]
    return even, odd


def coeff_str(c: Fraction) -> str:
    if c.denominator == 1:
        return str(c.numerator)
    return f'{c.numerator}/{c.denominator}'


def build_schema1(n: int) -> dict:
    gens = build_generators(n)
    basis_even, basis_odd = basis_lists(gens)
    osc_labels = osc_labels_for(n)

    dim_even = 2 * n * n + n + 1
    dim_odd  = 4 * n
    assert len(basis_even) == dim_even, (
        f'n={n}: even dim {len(basis_even)} != expected {dim_even}')
    assert len(basis_odd) == dim_odd, (
        f'n={n}: odd dim {len(basis_odd)} != expected {dim_odd}')

    parity = {name: p for name, (_, p) in gens.items()}

    # generator_realization
    realizations = {}
    for name, (gpoly, par) in gens.items():
        std_form = [
            {'words': [osc_labels[idx] for idx in word],
             'coeff': coeff_str(c)}
            for word, c in sorted(gpoly.items(), key=lambda x: (len(x[0]), x[0]))
        ]
        realizations[name] = {'standard_form': std_form, 'parity': par}

    # structure constants: combined ordering = even then odd
    combined = basis_even + basis_odd
    sc = []
    for xi, Xname in enumerate(combined):
        for yi in range(xi, len(combined)):
            Yname = combined[yi]
            Xpoly, pX = gens[Xname]
            Ypoly, pY = gens[Yname]
            bracket = graded_bracket(Xpoly, Ypoly, pX, pY)
            if not bracket:
                continue
            comps = decompose(bracket, gens, n)
            for Zname, coeff in comps.items():
                sc.append({
                    'X': Xname, 'Y': Yname, 'Z': Zname,
                    'coeff': coeff_str(coeff),
                    'sign_rule': 'graded',
                })

    return {
        'schema_version': '5.0',
        'algebra': {
            'family': 'C',
            'm': 1,
            'n': n,
            'cartan_type': f'C({n + 1})',
            'alternative_notation': {
                'osp': f'osp(2|{2 * n})',
                'dimension_formula': 'osp(2m|2n) with m=1',
            },
            'dimension': {
                'total': dim_even + dim_odd,
                'even': dim_even,
                'odd': dim_odd,
                'formulas': {
                    'even': '2*n^2 + n + 1',
                    'odd': '4*n',
                    'total': '2*n^2 + 5*n + 1',
                },
            },
        },
        'oscillator_generators': {
            'fermions': {
                'm': 1,
                'count': 2,
                'labels': ['a_1_p', 'a_1_m'],
                'description': 'Standard fermionic pair; CAR {a_1^-, a_1^+} = 1',
            },
            'bosons': {
                'n': n,
                'count': 2 * n,
                'labels': [f'b_{k}_{s}'
                           for k in range(1, n + 1) for s in ('p', 'm')],
                'description': (f'Bosonic oscillators b_k^pm for k=1..{n}; '
                                f'CCR [b_k^-, b_l^+] = delta_{{kl}}'),
            },
        },
        'oscillator_relations': {
            'fermionic_anticommutators': {
                'description': 'CAR for standard fermionic pair',
                'relations': {
                    'main': '{a_1^-, a_1^+} = 1',
                    'same_sign_p': '{a_1^+, a_1^+} = 0',
                    'same_sign_m': '{a_1^-, a_1^-} = 0',
                },
            },
            'bosonic_commutators': {
                'description': 'CCR for bosonic oscillators',
                'relations': {
                    'same_type': '[b_k^pm, b_l^pm] = 0',
                    'conjugate_pair': '[b_k^-, b_l^+] = delta_{kl}',
                },
            },
            'mixed_commutators': {
                'description': 'Fermion-boson (undeformed)',
                'fermion_boson': '[b_k^pm, a_1^pm] = 0',
            },
        },
        'central_elements': {
            'kappa': {
                'label': 'kappa',
                'parity': 1,
                'properties': ['kappa^2 = 0', 'central in g-tilde'],
                'description': ('Odd nilpotent central element; '
                                'coefficient in deformed brackets (Schema 2)'),
            },
            'K': {
                'label': 'K',
                'parity': 0,
                'properties': ['even central element', 'K = 1'],
                'description': 'Even central identity; excluded from PBW basis',
            },
        },
        'basis': {
            'even': basis_even,
            'odd': basis_odd,
            'ordering_convention': (
                'PBW: kappa < '
                '[a_1^+ block: E_eps1_del{k}_pp (k=1..n), E_eps1_del{k}_pm (k=1..n)] '
                '< [a_1^- block: E_eps1_del{k}_mp (k=1..n), E_eps1_del{k}_mm (k=1..n)] '
                '< [even: H_k, positive roots, negative roots, mixed roots]  (K=1 excluded)'
            ),
        },
        'parity': parity,
        'generator_realization': {
            'description': 'PBW-ordered oscillator words',
            'ordering': ', '.join(osc_labels),
            'realizations': realizations,
        },
        'structure_constants': sc,
        'metadata': {
            'generated_by': 'build_C_structure_constants.py',
            'generation_date': str(date.today()),
            'references': [
                'Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras',
                'arXiv:hep-th/9607161',
            ],
        },
    }


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root, 'data')
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f'Building C({n+1}) = osp(2|{2*n}), n={n} ...', file=sys.stderr)
        schema = build_schema1(n)
        fname = os.path.join(data_dir, f'C_{n}_structure.json')
        with open(fname, 'w') as f:
            json.dump(schema, f, indent=2)
        sc_count = len(schema['structure_constants'])
        dim = schema['algebra']['dimension']
        print(
            f'  -> {fname}  '
            f'dim={dim["even"]}|{dim["odd"]}  '
            f'{sc_count} SC entries',
            file=sys.stderr,
        )


if __name__ == '__main__':
    main()
