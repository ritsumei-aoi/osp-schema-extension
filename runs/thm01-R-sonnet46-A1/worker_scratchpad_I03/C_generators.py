"""
C_generators.py: Schema 1 generator for C(n+1) = osp(2|2n).

Computes structure constants via oscillator algebra (CAR + CCR) and
outputs Schema 1 JSON files data/C_{n}_structure.json.

Reference: docs/json_schema_specification.md, handover/notation.md
"""

from __future__ import annotations
from fractions import Fraction
from collections import defaultdict
from pathlib import Path
import json
from datetime import date

# ──────────────────────────────────────────────────────────────────
# Oscillator algebra
# ──────────────────────────────────────────────────────────────────

Word = tuple[str, ...]
Elem = dict[Word, Fraction]


def _pbw_index(n: int) -> dict[str, int]:
    """PBW ordering index for each oscillator in C(n+1)."""
    oscs = ['a_1_p', 'a_1_m']
    for k in range(1, n + 1):
        oscs += [f'b_{k}_p', f'b_{k}_m']
    return {o: i for i, o in enumerate(oscs)}


def _osc_parity(label: str) -> int:
    return 1 if label.startswith('a_') else 0


def _is_conj_boson(oi: str, oj: str) -> bool:
    """True iff oi = b_k_m, oj = b_k_p for the same k (b_k_m > b_k_p in PBW)."""
    if not (oi.startswith('b_') and oj.startswith('b_')):
        return False
    pi, pj = oi.split('_'), oj.split('_')
    return pi[1] == pj[1] and pi[2] == 'm' and pj[2] == 'p'


def _one_swap(word: Word, pbw: dict[str, int]) -> tuple[Elem, bool]:
    """
    Find first out-of-order adjacent pair, swap/contract.
    Returns (new_terms dict, changed).
    """
    for i in range(len(word) - 1):
        oi, oj = word[i], word[i + 1]
        pi, pj = _osc_parity(oi), _osc_parity(oj)
        # Fermionic nilpotency: same label adjacent → whole term is zero
        if pi == 1 and oi == oj:
            return {}, True
        if pbw[oi] <= pbw[oj]:
            continue
        # oi > oj in PBW order: swap
        sign = Fraction((-1) ** (pi * pj))
        swapped: Word = word[:i] + (oj, oi) + word[i + 2:]
        rest: Word = word[:i] + word[i + 2:]
        terms: Elem = {swapped: sign}
        if pi == 1 and pj == 1:
            if oi == 'a_1_m' and oj == 'a_1_p':
                # {a_1^-, a_1^+} = 1  ⟹  a_1^- a_1^+ = 1 - a_1^+ a_1^-
                terms[rest] = terms.get(rest, Fraction(0)) + Fraction(1)
        elif pi == 0 and pj == 0 and _is_conj_boson(oi, oj):
            # [b_k^-, b_k^+] = 1  ⟹  b_k^- b_k^+ = b_k^+ b_k^- + 1
            terms[rest] = terms.get(rest, Fraction(0)) + Fraction(1)
        return terms, True
    return {word: Fraction(1)}, False


def _reduce(word: Word, pbw: dict[str, int]) -> Elem:
    """Reduce a word to PBW normal form."""
    terms: Elem = {word: Fraction(1)}
    changed = True
    while changed:
        changed = False
        nxt: defaultdict[Word, Fraction] = defaultdict(Fraction)
        for w, c in terms.items():
            expanded, did = _one_swap(w, pbw)
            if did:
                changed = True
            for w2, c2 in expanded.items():
                nxt[w2] += c * c2
        terms = {k: v for k, v in nxt.items() if v != 0}
    return terms


def _mul(e1: Elem, e2: Elem, pbw: dict[str, int]) -> Elem:
    result: defaultdict[Word, Fraction] = defaultdict(Fraction)
    for w1, c1 in e1.items():
        for w2, c2 in e2.items():
            for w, c in _reduce(w1 + w2, pbw).items():
                result[w] += c1 * c2 * c
    return {k: v for k, v in result.items() if v != 0}


def _graded_bracket(e1: Elem, p1: int, e2: Elem, p2: int, pbw: dict[str, int]) -> Elem:
    """[e1, e2} = e1*e2 - (-1)^{p1*p2} e2*e1."""
    xy = _mul(e1, e2, pbw)
    yx = _mul(e2, e1, pbw)
    sign = Fraction((-1) ** (p1 * p2))
    result: defaultdict[Word, Fraction] = defaultdict(Fraction)
    for w, c in xy.items():
        result[w] += c
    for w, c in yx.items():
        result[w] -= sign * c
    return {k: v for k, v in result.items() if v != 0}


# ──────────────────────────────────────────────────────────────────
# Generator definitions for C(n+1)
# ──────────────────────────────────────────────────────────────────

GenEntry = tuple[Elem, int]    # (oscillator element, parity)


def make_generators(n: int) -> dict[str, GenEntry]:
    """Build all basis generators for C(n+1) = osp(2|2n)."""
    def E(*pairs) -> Elem:
        d: defaultdict[Word, Fraction] = defaultdict(Fraction)
        for word, c in pairs:
            d[tuple(word)] += Fraction(c)
        return {k: v for k, v in d.items() if v != 0}

    g: dict[str, GenEntry] = {}

    # Cartan generators
    g['H_1'] = (E((['a_1_p', 'a_1_m'], 1), (['b_1_p', 'b_1_m'], 1)), 0)
    for k in range(2, n + 1):
        g[f'H_{k}'] = (E(([f'b_{k-1}_p', f'b_{k-1}_m'], 1),
                         ([f'b_{k}_p',   f'b_{k}_m'],   -1)), 0)
    g[f'H_{n+1}'] = (E(([f'b_{n}_p', f'b_{n}_m'], -1), ([], Fraction(-1, 2))), 0)

    # Odd generators: E_eps1_del{k}_{ss}
    for k in range(1, n + 1):
        for ao, bo, ss in [('a_1_p', f'b_{k}_p', 'pp'),
                           ('a_1_p', f'b_{k}_m', 'pm'),
                           ('a_1_m', f'b_{k}_p', 'mp'),
                           ('a_1_m', f'b_{k}_m', 'mm')]:
            g[f'E_eps1_del{k}_{ss}'] = (E(([ao, bo], 1)), 1)

    # Even root generators
    for k in range(1, n + 1):
        g[f'E_2del{k}_p'] = (E(([f'b_{k}_p', f'b_{k}_p'], 1)), 0)
        g[f'E_2del{k}_m'] = (E(([f'b_{k}_m', f'b_{k}_m'], 1)), 0)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            g[f'E_del{i}_del{j}_pp'] = (E(([f'b_{i}_p', f'b_{j}_p'], 1)), 0)
            g[f'E_del{i}_del{j}_mm'] = (E(([f'b_{i}_m', f'b_{j}_m'], 1)), 0)
            g[f'E_del{i}_del{j}_pm'] = (E(([f'b_{i}_p', f'b_{j}_m'], 1)), 0)
            g[f'E_del{i}_del{j}_mp'] = (E(([f'b_{i}_m', f'b_{j}_p'], 1)), 0)

    return g


def basis_list(n: int) -> tuple[list[str], list[str]]:
    """
    Returns (odd_basis, even_basis) following the PBW convention in notation.md.
    Odd: _pp block, _pm block, _mp block, _mm block.
    Even: Cartans, pos-sym, neg-sym, mixed.
    """
    odd: list[str] = []
    for ss in ['pp', 'pm', 'mp', 'mm']:
        for k in range(1, n + 1):
            odd.append(f'E_eps1_del{k}_{ss}')

    cartans = [f'H_{k}' for k in range(1, n + 2)]
    pos_sym: list[str] = [f'E_2del{k}_p' for k in range(1, n + 1)]
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            pos_sym.append(f'E_del{i}_del{j}_pp')
    neg_sym: list[str] = [f'E_2del{k}_m' for k in range(1, n + 1)]
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            neg_sym.append(f'E_del{i}_del{j}_mm')
    mixed: list[str] = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            mixed.append(f'E_del{i}_del{j}_pm')
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            mixed.append(f'E_del{i}_del{j}_mp')
    even = cartans + pos_sym + neg_sym + mixed
    return odd, even


def sc_ordering(n: int) -> list[str]:
    """
    Canonical ordering for structure constant pairs (X before Y).
    Cartans first, then even roots, then odd generators.
    """
    cartans = [f'H_{k}' for k in range(1, n + 2)]
    pos_sym: list[str] = [f'E_2del{k}_p' for k in range(1, n + 1)]
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            pos_sym.append(f'E_del{i}_del{j}_pp')
    neg_sym: list[str] = [f'E_2del{k}_m' for k in range(1, n + 1)]
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            neg_sym.append(f'E_del{i}_del{j}_mm')
    mixed: list[str] = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            mixed.append(f'E_del{i}_del{j}_pm')
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            mixed.append(f'E_del{i}_del{j}_mp')
    odd: list[str] = []
    for ss in ['pp', 'pm', 'mp', 'mm']:
        for k in range(1, n + 1):
            odd.append(f'E_eps1_del{k}_{ss}')
    return cartans + pos_sym + neg_sym + mixed + odd


# ──────────────────────────────────────────────────────────────────
# Identify bracket result as linear combination of basis generators
# ──────────────────────────────────────────────────────────────────

def identify(word_poly: Elem, gens: dict[str, GenEntry], n: int) -> dict[str, Fraction]:
    """
    Express word_poly (output of _graded_bracket) as Σ c_i gen_i.
    Raises ValueError if the result is not in the span of generators.
    """
    # Map each root-generator word to (label, coeff_in_gen)
    word_to_root: dict[Word, tuple[str, Fraction]] = {}
    for label, (elem, _) in gens.items():
        if not label.startswith('H_'):
            for word, coeff in elem.items():
                if word in word_to_root:
                    raise AssertionError(f"Word collision: {word} in {label} and {word_to_root[word][0]}")
                word_to_root[word] = (label, coeff)

    result: defaultdict[str, Fraction] = defaultdict(Fraction)
    rem: defaultdict[Word, Fraction] = defaultdict(Fraction, word_poly)

    # Step 1: identify root (non-Cartan) generators
    for word in list(rem.keys()):
        c = rem[word]
        if c == 0:
            continue
        if word in word_to_root:
            label, gen_coeff = word_to_root[word]
            contrib = c / gen_coeff
            result[label] += contrib
            for w2, c2 in gens[label][0].items():
                rem[w2] -= contrib * c2
    rem = defaultdict(Fraction, {k: v for k, v in rem.items() if v != 0})

    # Step 2: identify Cartan generators from remaining oscillator words
    if rem:
        n1_word: Word = ('a_1_p', 'a_1_m')
        const_word: Word = ()

        c_n1 = rem.pop(n1_word, Fraction(0))
        c_const = rem.pop(const_word, Fraction(0))
        c_N = {k: rem.pop((f'b_{k}_p', f'b_{k}_m'), Fraction(0)) for k in range(1, n + 1)}

        if rem:
            raise ValueError(f"Unidentified oscillator words remaining: {dict(rem)}")

        # Solve for alpha_k (coefficient of H_k in the Cartan combination)
        #   H_1 = n_1 + N_1
        #   H_k = N_{k-1} - N_k   (2 <= k <= n)
        #   H_{n+1} = -N_n - 1/2
        # Equations:
        #   alpha_1 = c_n1
        #   alpha_{n+1} = -2 * c_const
        #   For n>=2: alpha_2 = c_N[1] - alpha_1
        #             alpha_{j+1} = c_N[j] + alpha_j  (j=2,...,n-1)
        #   For n==1: alpha_2 already determined by const; N_1 check: alpha_1 - alpha_2 == c_N[1]

        alpha: dict[int, Fraction] = {}
        alpha[1] = c_n1
        alpha[n + 1] = Fraction(-2) * c_const
        if n >= 2:
            alpha[2] = c_N[1] - alpha[1]
            for j in range(2, n):
                alpha[j + 1] = c_N[j] + alpha[j]

        for k in range(1, n + 2):
            if alpha.get(k, Fraction(0)) != 0:
                result[f'H_{k}'] += alpha[k]

    return {k: v for k, v in result.items() if v != 0}


# ──────────────────────────────────────────────────────────────────
# Structure constant computation
# ──────────────────────────────────────────────────────────────────

def compute_structure_constants(n: int) -> list[dict]:
    """
    Compute all non-zero structure constants [X, Y} = sum c_i Z_i for C(n+1).
    Returns list of {X, Y, terms, parity_X, parity_Y} entries.
    terms = [(label, coeff_str)] — usually a single term.
    """
    gens = make_generators(n)
    pbw = _pbw_index(n)
    order = sc_ordering(n)

    sc_list: list[dict] = []

    for i, lx in enumerate(order):
        ex, px = gens[lx]
        for ly in order[i + 1:]:
            ey, py = gens[ly]
            br = _graded_bracket(ex, px, ey, py, pbw)
            if not br:
                continue
            result = identify(br, gens, n)
            if result:
                terms = [(lbl, coeff) for lbl, coeff in sorted(result.items())]
                sc_list.append({
                    'X': lx, 'Y': ly,
                    'parity_X': px, 'parity_Y': py,
                    'terms': terms
                })

    return sc_list


# ──────────────────────────────────────────────────────────────────
# Schema 1 JSON builder
# ──────────────────────────────────────────────────────────────────

def _coeff_str(c: Fraction) -> str:
    if c.denominator == 1:
        return str(c.numerator)
    return f"{c.numerator}/{c.denominator}"


def _realization_entry(label: str, elem: Elem, parity: int) -> dict:
    std = [
        {'words': list(w), 'coeff': _coeff_str(c)}
        for w, c in elem.items()
    ]
    return {'standard_form': std, 'parity': parity}


def _frappat_label(label: str) -> str:
    """Return a LaTeX-style description for the Frappat reference."""
    if label.startswith('H_'):
        k = label[2:]
        return f"H_{{{k}}}"
    if label.startswith('E_eps1_del'):
        parts = label.split('_')
        k = parts[3].replace('del', '')
        ss = parts[4]
        se = '+' if ss[0] == 'p' else '-'
        sd = '+' if ss[1] == 'p' else '-'
        return f"E_{{\\varepsilon{se}\\delta_{{{k}}}}}"
    if label.startswith('E_2del'):
        k = label[6]
        sign = '+' if label.endswith('_p') else '-'
        return f"E_{{{sign}2\\delta_{{{k}}}}}"
    if label.startswith('E_del'):
        parts = label.split('_')
        i, j = parts[1].replace('del', ''), parts[2].replace('del', '')
        ss = parts[3]
        si = '+' if ss[0] == 'p' else '-'
        sj = '+' if ss[1] == 'p' else '-'
        return f"E_{{{si}\\delta_{{{i}}}{sj}\\delta_{{{j}}}}}"
    return label


def generate_schema1(n: int) -> dict:
    """Build the complete Schema 1 JSON object for C(n+1)."""
    gens = make_generators(n)
    odd_basis, even_basis = basis_list(n)
    sc_list = compute_structure_constants(n)

    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n
    dim_total = dim_even + dim_odd

    # Parity assignment
    parity_assignment = {
        lbl: parity for lbl, (_, parity) in gens.items()
    }

    # CAR relations for the standard fermionic pair
    car_relations = [
        {'relation': '{a_1_m, a_1_p} = 1', 'type': 'CAR'},
        {'relation': '(a_1_p)^2 = 0', 'type': 'nilpotency'},
        {'relation': '(a_1_m)^2 = 0', 'type': 'nilpotency'},
    ]

    # Generator realizations
    gen_realizations = {}
    for lbl, (elem, parity) in gens.items():
        gen_realizations[lbl] = _realization_entry(lbl, elem, parity)

    # Structure constants in schema format
    structure_constants = []
    for entry in sc_list:
        terms = entry['terms']
        if len(terms) == 1:
            lbl, coeff = terms[0]
            structure_constants.append({
                'X': entry['X'],
                'Y': entry['Y'],
                'Z': lbl,
                'coeff': _coeff_str(coeff),
                'sign_rule': 'graded',
            })
        else:
            # Multi-term result (Cartan combination)
            structure_constants.append({
                'X': entry['X'],
                'Y': entry['Y'],
                'Z': 'linear_combination',
                'terms': [{'Z': lbl, 'coeff': _coeff_str(c)} for lbl, c in terms],
                'sign_rule': 'graded',
            })

    # Central elements
    central_elements = [
        {
            'label': 'kappa',
            'parity': 1,
            'property': 'nilpotent odd central; kappa^2 = 0; lowest in PBW order',
        },
        {
            'label': 'K',
            'parity': 0,
            'property': 'central identity; identified with scalar 1 in all applications',
        },
    ]

    # Deformation parameters
    gb_params = []
    for k in range(1, n + 1):
        for se in ['p', 'm']:
            for sb in ['p', 'm']:
                gb_params.append(f'gb_a1{se}_b{k}{sb}')

    schema = {
        'schema_version': '5.0',
        'algebra': f'C({n+1})',
        'isomorphism': f'osp(2|{2*n})',
        'bosonic_rank': n,
        'generated_date': str(date.today()),
        'dimensions': {
            'even': dim_even,
            'odd': dim_odd,
            'total': dim_total,
            'formula': {
                'even': '2n^2+n+1',
                'odd': '4n',
                'total': '2n^2+5n+1',
            },
        },
        'basis': {
            'odd': odd_basis,
            'even': even_basis,
        },
        'parity_assignment': parity_assignment,
        'car_relations': car_relations,
        'cartan_eigenvalues': {
            'description': (
                'Eigenvalue of H_k on generator E with oscillator content '
                '(s_eps, s_1, ..., s_n) where s_j = (#b_j^+ - #b_j^-), s_eps = (#a_1^+ - #a_1^-).'
            ),
            'formulas': {
                'H_1': 's_eps + s_1',
                'H_k (2<=k<=n)': 's_{k-1} - s_k',
                f'H_{n+1}': '-s_n',
            },
        },
        'generator_realizations': gen_realizations,
        'central_elements': central_elements,
        'deformation_parameters': {
            'count': 4 * n,
            'parity': 1,
            'labels': gb_params,
        },
        'structure_constants': structure_constants,
    }
    return schema


def main():
    out_dir = Path('data')
    out_dir.mkdir(exist_ok=True)
    for n in [1, 2, 3]:
        schema = generate_schema1(n)
        out_path = out_dir / f'C_{n}_structure.json'
        with open(out_path, 'w') as f:
            json.dump(schema, f, indent=2)
        dim = schema['dimensions']
        sc_count = len(schema['structure_constants'])
        print(f'C({n+1}): dim={dim["even"]}|{dim["odd"]}={dim["total"]}, '
              f'SC entries={sc_count} → {out_path}')


if __name__ == '__main__':
    main()
