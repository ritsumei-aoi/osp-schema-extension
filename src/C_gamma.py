"""
C_gamma.py: Schema 2 (gamma structure) generator for C(n+1) = osp(2|2n).

Computes gamma coefficients gamma^c_{ab} from the inhomogeneous deformation:
  [b_j^s, a_1^sigma]_gamma = -gb_{sigma,j,s} * kappa
using the oscillator algebra from C_generators.py.

Output: data/C_n_gamma.json (Schema 2, layer 2, upper-index convention).
"""

from __future__ import annotations
from fractions import Fraction
from collections import defaultdict
from pathlib import Path
import json
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import (
    _pbw_index, _osc_parity, _reduce, make_generators, basis_list,
)

Word = tuple[str, ...]
Elem = dict[Word, Fraction]
GbCoeff = dict[str, Fraction]     # {gb_label: Fraction}
GammaElem = dict[Word, GbCoeff]   # {word: {gb_label: coeff}}


# ──────────────────────────────────────────────────────────────────
# gb label construction
# ──────────────────────────────────────────────────────────────────

def _gb_label(b_osc: str, a_osc: str) -> str:
    """gb_{sigma}_{j}_{s} for deformation coefficient of [b_j^s, a_1^sigma]."""
    sigma = a_osc.split('_')[-1]        # 'p' or 'm'
    parts = b_osc.split('_')            # ['b', j, s]
    return f'gb_{sigma}_{parts[1]}_{parts[2]}'


def gb_labels(n: int) -> list[str]:
    """All gb parameter labels for C(n+1) in canonical order."""
    labels = []
    for sigma in ['p', 'm']:
        for j in range(1, n + 1):
            for s in ['p', 'm']:
                labels.append(f'gb_{sigma}_{j}_{s}')
    return labels


# ──────────────────────────────────────────────────────────────────
# First-order kappa-coefficient computation
# ──────────────────────────────────────────────────────────────────

def _kappa_coeff_product(product: Word, pbw: dict[str, int]) -> GammaElem:
    """
    First-order kappa-coefficient when bringing `product` to PBW normal form.

    For each pair (b at pos i, a_1^sigma at pos j) with i < j:
      contribution = -gb_{sigma,j,s} * N_0(product \\ {i, j})
    where N_0 uses _reduce (CAR/CCR) at zeroth order.

    Returns {normalized_word: {gb_label: Fraction}}.
    b_j^s a_1^sigma = a_1^sigma b_j^s - gb_{sigma,j,s}*kappa → coefficient is -1.
    """
    result: GammaElem = {}
    m = len(product)

    for i in range(m):
        xi = product[i]
        if _osc_parity(xi) != 0 or not xi.startswith('b_'):
            continue
        for j in range(i + 1, m):
            xj = product[j]
            if _osc_parity(xj) != 1 or not xj.startswith('a_'):
                continue

            gb = _gb_label(xi, xj)
            remaining = tuple(product[k] for k in range(m) if k != i and k != j)
            reduced: Elem = _reduce(remaining, pbw)  # may produce () for K

            for word, coeff in reduced.items():
                if word not in result:
                    result[word] = {}
                result[word][gb] = result[word].get(gb, Fraction(0)) - coeff

    return result


def _kappa_coeff_bracket(
    ea: Elem, pa: int,
    eb: Elem, pb: int,
    pbw: dict[str, int],
) -> GammaElem:
    """
    Kappa-coefficient of [ea, eb]_gamma = ea*eb - (-1)^{pa*pb} * eb*ea.
    Returns {word: {gb_label: Fraction}}.
    """
    sign_yx = Fraction((-1) ** (pa * pb))
    total: GammaElem = {}

    def _add(ge: GammaElem, scalar: Fraction) -> None:
        for word, gc in ge.items():
            if word not in total:
                total[word] = {}
            for gb, c in gc.items():
                total[word][gb] = total[word].get(gb, Fraction(0)) + scalar * c

    for mono_a, ca in ea.items():
        for mono_b, cb in eb.items():
            s = ca * cb
            _add(_kappa_coeff_product(mono_a + mono_b, pbw), s)
            _add(_kappa_coeff_product(mono_b + mono_a, pbw), -sign_yx * s)

    return {w: {gb: c for gb, c in gc.items() if c != 0}
            for w, gc in total.items()
            if any(c != 0 for c in gc.values())}


# ──────────────────────────────────────────────────────────────────
# Extended identification: basis generators + K
# ──────────────────────────────────────────────────────────────────

def _solve_cartan_K(
    c_n1: Fraction,
    c_N: dict[int, Fraction],
    c_const: Fraction,
    n: int,
) -> tuple[dict[int, Fraction], Fraction]:
    """
    Solve the linear system for Cartan coefficients alpha[1..n+1] and K coefficient.

    Realization structure (from make_generators):
      H_1:     (a_1_p,a_1_m)=1, (b_1_p,b_1_m)=1
      H_k(2<=k<=n): (b_{k-1}_p,b_{k-1}_m)=1, (b_k_p,b_k_m)=-1
      H_{n+1}: (b_n_p,b_n_m)=-1, ()=-1/2
      K:       ()=1

    Returns (alpha, alpha_K).
    """
    alpha: dict[int, Fraction] = {1: c_n1}

    if n == 1:
        # eq(m_1): alpha[1]*1 + alpha[2]*(-1) = c_N[1]  (H_2=H_{n+1} has m_1 coeff -1)
        alpha[2] = alpha[1] - c_N[1]
    else:
        # eq(m_1): alpha[1] + alpha[2] = c_N[1]  (H_1 and H_2 both contribute +1)
        alpha[2] = c_N[1] - alpha[1]
        # eq(m_k) for k=2..n-1: -alpha[k] + alpha[k+1] = c_N[k]
        for k in range(2, n):
            alpha[k + 1] = c_N[k] + alpha[k]
        # eq(m_n): -alpha[n] - alpha[n+1] = c_N[n]  (H_n and H_{n+1} both have m_n=-1)
        alpha[n + 1] = -c_N[n] - alpha[n]

    # eq(m_{n+1}=()): -1/2 * alpha[n+1] + alpha_K = c_const
    alpha_K = c_const + Fraction(1, 2) * alpha[n + 1]
    return alpha, alpha_K


def identify_extended(
    word_poly: Elem,
    gens: dict,
    n: int,
) -> dict[str, Fraction]:
    """
    Express word_poly as linear combination of basis generators and possibly K.

    Returns {gen_label_or_'K': Fraction}.
    K is the even central element (= scalar 1 in representations).
    """
    # Build word→root map for non-Cartan generators
    word_to_root: dict[Word, tuple[str, Fraction]] = {}
    for label, (elem, _) in gens.items():
        if not label.startswith('H_'):
            for word, coeff in elem.items():
                word_to_root[word] = (label, coeff)

    result: defaultdict[str, Fraction] = defaultdict(Fraction)
    rem: defaultdict[Word, Fraction] = defaultdict(Fraction, word_poly)

    # Step 1: identify non-Cartan generators
    for word in list(rem.keys()):
        c = rem[word]
        if c == 0 or word not in word_to_root:
            continue
        label, gen_coeff = word_to_root[word]
        contrib = c / gen_coeff
        result[label] += contrib
        for w2, c2 in gens[label][0].items():
            rem[w2] -= contrib * c2
    rem = defaultdict(Fraction, {k: v for k, v in rem.items() if v != 0})

    if not rem:
        return {k: v for k, v in result.items() if v != 0}

    # Step 2: solve extended Cartan + K system
    n1_word: Word = ('a_1_p', 'a_1_m')
    const_word: Word = ()
    c_n1 = rem.pop(n1_word, Fraction(0))
    c_const = rem.pop(const_word, Fraction(0))
    c_N = {k: rem.pop((f'b_{k}_p', f'b_{k}_m'), Fraction(0)) for k in range(1, n + 1)}

    if rem:
        raise ValueError(f'Unidentified oscillator words: {dict(rem)}')

    alpha, alpha_K = _solve_cartan_K(c_n1, c_N, c_const, n)
    for k, v in alpha.items():
        if v != 0:
            result[f'H_{k}'] += v
    if alpha_K != 0:
        result['K'] += alpha_K

    return {k: v for k, v in result.items() if v != 0}


# ──────────────────────────────────────────────────────────────────
# Gamma computation
# ──────────────────────────────────────────────────────────────────

def _coeff_str(c: Fraction) -> str:
    return str(c.numerator) if c.denominator == 1 else f'{c.numerator}/{c.denominator}'


def compute_gamma_entries(n: int) -> list[dict]:
    """
    Compute all non-zero gamma^c_{ab} for C(n+1).
    Returns list of {'a', 'b', 'c', 'coeff_gb'} dicts.
    c is a generator label or 'K'.
    coeff_gb: {gb_label: coeff_str}.
    """
    gens = make_generators(n)
    pbw = _pbw_index(n)
    odd_basis, even_basis = basis_list(n)
    all_basis = even_basis + odd_basis

    entries: list[dict] = []

    for la in all_basis:
        ea, pa = gens[la]
        for lb in all_basis:
            eb, pb_val = gens[lb]

            kc = _kappa_coeff_bracket(ea, pa, eb, pb_val, pbw)
            if not kc:
                continue

            # Convert GammaElem to gen-basis representation
            gen_gb: dict[str, GbCoeff] = defaultdict(lambda: defaultdict(Fraction))

            for word, gb_coeffs in kc.items():
                single = {word: Fraction(1)}
                identified = identify_extended(single, gens, n)
                for gen_label, gen_coeff in identified.items():
                    for gb, c in gb_coeffs.items():
                        gen_gb[gen_label][gb] += gen_coeff * c

            for gen_label, gb_dict in gen_gb.items():
                nonzero = {gb: c for gb, c in gb_dict.items() if c != 0}
                if nonzero:
                    entries.append({
                        'a': la,
                        'b': lb,
                        'c': gen_label,
                        'coeff_gb': {gb: _coeff_str(c) for gb, c in nonzero.items()},
                    })

    return entries


# ──────────────────────────────────────────────────────────────────
# Schema 2 JSON builder
# ──────────────────────────────────────────────────────────────────

def generate_schema2(n: int) -> dict:
    """Build Schema 2 v5.0 JSON for C(n+1)."""
    odd_basis, even_basis = basis_list(n)
    all_basis = even_basis + odd_basis

    gamma_entries = compute_gamma_entries(n)

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels += [f'b_{k}_p', f'b_{k}_m']

    gb_rows = {'a_1_p': {}, 'a_1_m': {}}
    for sigma in ['a_1_p', 'a_1_m']:
        sig = sigma.split('_')[-1]
        for k in range(1, n + 1):
            for s in ['p', 'm']:
                b_label = f'b_{k}_{s}'
                gb_rows[sigma][b_label] = f'gb_{sig}_{k}_{s}'

    return {
        'schema_version': '5.0',
        'schema_layer': 2,
        'algebra': {
            'family': 'C',
            'n': n,
            'cartan_type': f'C({n + 1})',
            'alternative_notation': {'osp': f'osp(2|{2 * n})'},
            'schema1_file': f'C_{n}_structure.json',
        },
        'deformation_parameters': {
            'description': (
                'gb_{sigma,j,s}: coefficient of kappa in '
                '[b_j^s, a_1^sigma]_gamma = -gb_{sigma,j,s}*kappa'
            ),
            'count': 4 * n,
            'gb_matrix': {
                'rows': ['a_1_p', 'a_1_m'],
                'cols': boson_labels,
                'entries': gb_rows,
            },
        },
        'index_convention': 'upper_c',
        'gamma_cocycle': gamma_entries,
        'gram_matrix': None,
        'metadata': {
            'generated_by': 'src/C_gamma.py',
            'generation_date': str(date.today()),
            'notes': (
                "gamma^c_{ab}: coefficient of e_c in gamma(e_a, e_b). "
                "K = even central element (scalar 1). "
                "Gram matrix deferred to Schema 4."
            ),
            'references': [
                'docs/math/C_inhomogeneous_definition.md',
                'docs/math/B0n_schema_v5.md',
                'Issue I05-1',
            ],
        },
    }


def main() -> None:
    out_dir = Path('data')
    out_dir.mkdir(exist_ok=True)
    for n in [1, 2, 3]:
        schema = generate_schema2(n)
        out_path = out_dir / f'C_{n}_gamma.json'
        with open(out_path, 'w') as f:
            json.dump(schema, f, indent=2)
        count = len(schema['gamma_cocycle'])
        print(f'C({n + 1}): {count} gamma entries → {out_path}')


if __name__ == '__main__':
    main()
