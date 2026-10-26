#!/usr/bin/env python3
"""
compute_gamma.py

Compute the gamma (γ) structure for the C(n+1) inhomogeneous deformation.
Outputs data/C_{n}_gamma.json for n=1,2,3.

Mathematical grounding:
  Deformed oscillator relation (Convention A, as in C_inhomogeneous_definition.md):
    [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa
  i.e., when b_j^s (bosonic, higher PBW) is to the left of a_1^sigma (fermionic, lower PBW),
  swapping them in the PBW reduction contributes -gb_{sigma,j,s} * kappa.

  The gamma 2-cocycle:
    [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)
  where gamma(X, Y) = kappa^1 coefficient in [X,Y]_deformed.
"""

import sys
import json
import datetime
from fractions import Fraction
from collections import defaultdict
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from C_generators import (
    osc_labels, is_fermionic, _comm_value, _swap_sign,
    normalize, poly_add, poly_mul, build_generators, decompose
)

# ---------------------------------------------------------------------------
# Deformed oscillator algebra
# ---------------------------------------------------------------------------

def _parse_boson(lbl: str):
    """Parse 'b_{k}_{s}' -> (k: int, s: str)."""
    parts = lbl.split('_')   # ['b', k, s]
    return int(parts[1]), parts[2]


def normalize_deformed(word: tuple, order: list, sign_convention: int = -1):
    """
    Normalize a word in the deformed oscillator algebra.

    Deformation: when b_j^s (higher PBW) swaps past a_1^sigma (lower PBW),
    the correction is:  sign_convention * gb_{sigma,j,s} * (word_without_pair)

    Convention A (default, sign_convention=-1): [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa
    Convention B (sign_convention=+1): [b_j^s, a_1^sigma] = +gb_{sigma,j,s} * kappa

    Returns:
        main_poly: Poly  (same as undeformed normalize(word, order))
        gamma_dict: dict {gb_label: Poly}  (the kappa^1 corrections, linear in gb)
    """
    idx = {lbl: i for i, lbl in enumerate(order)}
    main_worklist = [(list(word), Fraction(1))]
    result_main = defaultdict(Fraction)
    gamma = defaultdict(lambda: defaultdict(Fraction))

    while main_worklist:
        w, c = main_worklist.pop()
        if c == 0:
            continue
        # Fermionic repeat → word vanishes (in both main and gamma paths)
        if any(w[i] == w[i + 1] and is_fermionic(w[i]) for i in range(len(w) - 1)):
            continue

        swapped = False
        for i in range(len(w) - 1):
            if idx[w[i]] > idx[w[i + 1]]:
                oi, oj = w[i], w[i + 1]
                sign = _swap_sign(oi, oj)
                comm = _comm_value(oi, oj)

                # Deformation correction: bosonic swapping past fermionic
                if not is_fermionic(oi) and is_fermionic(oj):
                    # oi = b_k_s, oj = a_1_sigma
                    k, s = _parse_boson(oi)
                    sigma = oj.split('_')[2]           # 'p' or 'm'
                    gb_label = f'gb_a1{sigma}_b{k}{s}'
                    # Correction word (length reduced by 2)
                    corr_word = tuple(w[:i] + w[i + 2:])
                    # Normalize in UNDEFORMED algebra (kappa^2 = 0)
                    corr_poly = normalize(corr_word, order)
                    for cw, cc in corr_poly.items():
                        gamma[gb_label][cw] += c * Fraction(sign_convention) * cc

                main_worklist.append((w[:i] + [oj, oi] + w[i + 2:], c * sign))
                if comm:
                    main_worklist.append((w[:i] + w[i + 2:], c * comm))
                swapped = True
                break

        if not swapped:
            result_main[tuple(w)] += c

    result_main = {k: v for k, v in result_main.items() if v != 0}
    gamma = {lbl: {k: v for k, v in poly.items() if v != 0}
             for lbl, poly in gamma.items()}
    gamma = {lbl: poly for lbl, poly in gamma.items() if poly}
    return result_main, gamma


# ---------------------------------------------------------------------------
# Gamma bracket computation
# ---------------------------------------------------------------------------

def poly_mul_deformed(p1, p2, order, sign_convention):
    """
    Multiply two polynomials in the deformed oscillator algebra.
    Returns (main_poly, gamma_dict).
    """
    result_main = defaultdict(Fraction)
    result_gamma = defaultdict(lambda: defaultdict(Fraction))

    for w1, c1 in p1.items():
        for w2, c2 in p2.items():
            main, gamma = normalize_deformed(w1 + w2, order, sign_convention)
            for w, c in main.items():
                result_main[w] += c1 * c2 * c
            for gb_lbl, poly in gamma.items():
                for w, c in poly.items():
                    result_gamma[gb_lbl][w] += c1 * c2 * c

    result_main = {k: v for k, v in result_main.items() if v != 0}
    result_gamma = {lbl: {k: v for k, v in poly.items() if v != 0}
                    for lbl, poly in result_gamma.items()}
    result_gamma = {lbl: poly for lbl, poly in result_gamma.items() if poly}
    return result_main, result_gamma


def graded_bracket_deformed(X, Y, pX, pY, order, sign_convention):
    """
    [X, Y]_gamma = X*Y - (-1)^{pX*pY} * Y*X  in deformed algebra.
    Returns (main_poly, gamma_dict).
    """
    sgn = Fraction((-1) ** (pX * pY))

    xy_main, xy_gamma = poly_mul_deformed(X, Y, order, sign_convention)
    yx_main, yx_gamma = poly_mul_deformed(Y, X, order, sign_convention)

    # Main part: [X,Y]_0
    bracket_main = defaultdict(Fraction, xy_main)
    for w, c in yx_main.items():
        bracket_main[w] -= sgn * c
    bracket_main = {k: v for k, v in bracket_main.items() if v != 0}

    # Gamma part: kappa^1 coefficient
    bracket_gamma = defaultdict(lambda: defaultdict(Fraction))
    for gb_lbl, poly in xy_gamma.items():
        for w, c in poly.items():
            bracket_gamma[gb_lbl][w] += c
    for gb_lbl, poly in yx_gamma.items():
        for w, c in poly.items():
            bracket_gamma[gb_lbl][w] -= sgn * c

    bracket_gamma = {lbl: {k: v for k, v in poly.items() if v != 0}
                     for lbl, poly in bracket_gamma.items()}
    bracket_gamma = {lbl: poly for lbl, poly in bracket_gamma.items() if poly}
    return bracket_main, bracket_gamma


# ---------------------------------------------------------------------------
# Schema 2 builder
# ---------------------------------------------------------------------------

def gb_labels(n: int) -> list:
    """Return all gb parameter labels for C(n+1) with bosonic rank n (4n total)."""
    labels = []
    for sigma in ('p', 'm'):
        for k in range(1, n + 1):
            for s in ('p', 'm'):
                labels.append(f'gb_a1{sigma}_b{k}{s}')
    return labels


def compute_gamma_entries(n: int, sign_convention: int = -1) -> list:
    """
    Compute gamma(X, Y) for all pairs (X, Y) with index_X <= index_Y.
    Returns list of {X, Y, gb_label, Z, coeff}.

    gamma(X, Y) is decomposed into the basis generators PLUS the central
    element K (= scalar 1, the even central identity), since the κ^1 correction
    may contain a constant term κ·K = κ.
    """
    even_labels, odd_labels, gens = build_generators(n)
    all_labels = even_labels + odd_labels
    order = osc_labels(n)

    # Include K = {(): 1} as an additional basis element for decomposition
    gens_ext = dict(gens)
    gens_ext['K'] = ({(): Fraction(1)}, 0)
    all_labels_ext = all_labels + ['K']

    entries = []
    for idx_i, lbl_i in enumerate(all_labels):
        poly_i, par_i = gens[lbl_i]
        for lbl_j in all_labels[idx_i:]:
            poly_j, par_j = gens[lbl_j]
            _, gamma = graded_bracket_deformed(poly_i, poly_j, par_i, par_j,
                                               order, sign_convention)
            if not gamma:
                continue
            for gb_lbl, corr_poly in gamma.items():
                if not corr_poly:
                    continue
                coeffs = decompose(corr_poly, all_labels_ext, gens_ext)
                for lbl_z, c in coeffs.items():
                    if c != 0:
                        entries.append({
                            'X': lbl_i,
                            'Y': lbl_j,
                            'gb_label': gb_lbl,
                            'Z': lbl_z,
                            'coeff': str(c),
                        })
    return entries


def build_gamma_schema(n: int, sign_convention: int = -1) -> dict:
    even_labels, odd_labels, gens = build_generators(n)
    all_labels = even_labels + odd_labels
    order = osc_labels(n)

    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n

    gbs = gb_labels(n)
    gb_defs = []
    for lbl in gbs:
        # lbl = 'gb_a1{sigma}_b{k}{s}'
        parts = lbl.split('_')   # ['gb', 'a1p', 'bks']
        sigma = parts[1][2]       # 'p' or 'm'
        rest = parts[2]           # 'b{k}{s}'
        k = int(rest[1:-1])
        s = rest[-1]
        gb_defs.append({
            'label': lbl,
            'fermionic_oscillator': f'a_1_{sigma}',
            'bosonic_oscillator': f'b_{k}_{s}',
            'sigma': sigma,
            'k': k,
            's': s,
            'parity': 1,
            'description': f'Deformation parameter for [b_{k}^{s}, a_1^{sigma}]',
        })

    if sign_convention == -1:
        rel_str = '[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa'
        conv_name = 'A'
    else:
        rel_str = '[b_j^s, a_1^sigma] = +gb_{sigma,j,s} * kappa'
        conv_name = 'B'

    entries = compute_gamma_entries(n, sign_convention)

    return {
        'schema_version': '5.0',
        'algebra': {
            'family': 'C',
            'm': 1,
            'n': n,
            'cartan_type': f'C({n + 1})',
            'alternative_notation': {'osp': f'osp(2|{2 * n})'},
            'dimension': {
                'even': even_dim,
                'odd': odd_dim,
                'total': even_dim + odd_dim,
            },
        },
        'gb_matrix': {
            'description': (
                f'Deformation parameters for C({n+1}) inhomogeneous deformation. '
                f'4n = {4*n} parameters total (2 fermionic x 2n bosonic oscillator pairs).'
            ),
            'count': 4 * n,
            'parameters': gb_defs,
        },
        'sign_convention': {
            'name': f'Convention {conv_name}',
            'deformation_relation': rel_str,
            'sign': str(sign_convention),
            'parity_note': 'kappa is odd (parity 1); gb parameters must be odd (parity 1)',
        },
        'gamma': entries,
        'metadata': {
            'generated_by': 'src/compute_gamma.py',
            'generation_date': datetime.date.today().isoformat(),
            'n': n,
            'sign_convention': f'Convention {conv_name}',
            'references': [
                'Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras',
                'C_inhomogeneous_definition.md',
            ],
        },
    }


# ---------------------------------------------------------------------------
# Dry-run / main
# ---------------------------------------------------------------------------

def main():
    dry_run = '--dry-run' in sys.argv
    show_sample = '--sample' in sys.argv
    conv_b = '--convention-b' in sys.argv
    sign_convention = +1 if conv_b else -1
    conv_name = 'B' if conv_b else 'A'

    data_dir = Path(__file__).parent.parent / 'data'
    if not dry_run:
        data_dir.mkdir(exist_ok=True)

    for n in [1, 2, 3]:
        print(f'\nBuilding gamma for C({n + 1}) = osp(2|{2 * n}), n={n} '
              f'(Convention {conv_name})...', flush=True)
        schema = build_gamma_schema(n, sign_convention)
        n_gb = len(schema['gb_matrix']['parameters'])
        n_entries = len(schema['gamma'])
        print(f'  gb parameters: {n_gb}')
        print(f'  gamma entries: {n_entries}')

        if show_sample and n == 1:
            print(f'  Sample gamma entries (n=1):')
            for e in schema['gamma'][:8]:
                print(f'    gamma({e["X"]}, {e["Y"]})[{e["gb_label"]}] -> {e["Z"]} : {e["coeff"]}')

        if dry_run:
            print(f'  [dry-run] would write data/C_{n}_gamma.json')
        else:
            out = data_dir / f'C_{n}_gamma.json'
            with open(out, 'w') as f:
                json.dump(schema, f, indent=2)
            print(f'  written: {out}')


if __name__ == '__main__':
    main()
