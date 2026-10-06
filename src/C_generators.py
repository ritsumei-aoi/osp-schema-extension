"""
C_generators.py: Schema 1 v5.0 generator for C(n+1) = osp(2|2n).

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
    """True iff oi = b_k_m, oj = b_k_p for the same k."""
    if not (oi.startswith('b_') and oj.startswith('b_')):
        return False
    pi, pj = oi.split('_'), oj.split('_')
    return pi[1] == pj[1] and pi[2] == 'm' and pj[2] == 'p'


def _one_swap(word: Word, pbw: dict[str, int]) -> tuple[Elem, bool]:
    """
    Find first out-of-order (or nilpotent) adjacent pair, apply rule.
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
                # {a_1^-, a_1^+} = 1
                terms[rest] = terms.get(rest, Fraction(0)) + Fraction(1)
        elif pi == 0 and pj == 0 and _is_conj_boson(oi, oj):
            # [b_k^-, b_k^+] = 1
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
    Odd: _pp block, _pm block, _mp block, _mm block (within each: k=1..n).
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
    Returns dict {gen_label: Fraction}.
    Raises ValueError if the result is not in the span.
    """
    word_to_root: dict[Word, tuple[str, Fraction]] = {}
    for label, (elem, _) in gens.items():
        if not label.startswith('H_'):
            for word, coeff in elem.items():
                if word in word_to_root:
                    raise AssertionError(f"Word collision: {word}")
                word_to_root[word] = (label, coeff)

    result: defaultdict[str, Fraction] = defaultdict(Fraction)
    rem: defaultdict[Word, Fraction] = defaultdict(Fraction, word_poly)

    # Step 1: identify root (non-Cartan) generators
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

    # Step 2: identify Cartan generators from remaining oscillator words
    if rem:
        n1_word: Word = ('a_1_p', 'a_1_m')
        const_word: Word = ()

        c_n1 = rem.pop(n1_word, Fraction(0))
        c_const = rem.pop(const_word, Fraction(0))
        c_N = {k: rem.pop((f'b_{k}_p', f'b_{k}_m'), Fraction(0)) for k in range(1, n + 1)}

        if rem:
            raise ValueError(f"Unidentified oscillator words remaining: {dict(rem)}")

        # Solve linear system for alpha_k (coefficient of H_k):
        #   H_1 = n_1 + N_1  → alpha[1] = c_n1
        #   H_{n+1} = -N_n - 1/2  → alpha[n+1] = -2*c_const
        #   For n>=2:  N_1 eq: alpha[1]+alpha[2]=c_N[1] → alpha[2]=c_N[1]-alpha[1]
        #              N_j eq (2<=j<=n-1): -alpha[j]+alpha[j+1]=c_N[j] → alpha[j+1]=c_N[j]+alpha[j]
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
    Compute all non-zero structure constants for C(n+1).
    Returns list of {X, Y, terms, parity_X, parity_Y} where
    terms = [(Z_label, Fraction_coeff)].
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
                terms = sorted(result.items())   # [(label, coeff)]
                sc_list.append({
                    'X': lx, 'Y': ly,
                    'parity_X': px, 'parity_Y': py,
                    'terms': terms,
                })
    return sc_list


# ──────────────────────────────────────────────────────────────────
# Schema 1 v5.0 JSON builder — 10 exact top-level keys
# ──────────────────────────────────────────────────────────────────

def _coeff_str(c: Fraction) -> str:
    return str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"


def _frappat(label: str, n: int) -> str:
    """Human-readable oscillator expression for a generator."""
    if label == 'H_1':
        return 'a_1^+ a_1^- + b_1^+ b_1^-'
    if label.startswith('H_'):
        k = int(label[2:])
        if k == n + 1:
            return f'-b_{n}^+ b_{n}^- - 1/2'
        return f'b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-'
    if label.startswith('E_eps1_del'):
        parts = label.split('_')   # E, eps1, del{k}, {ss}
        k = parts[2].replace('del', '')
        ss = parts[3]
        ae = f'a_1^{"+" if ss[0]=="p" else "-"}'
        be = f'b_{k}^{"+" if ss[1]=="p" else "-"}'
        return f'{ae} {be}'
    if label.startswith('E_2del'):
        k = label[6]
        sign = '+' if label.endswith('_p') else '-'
        return f'(b_{k}^{sign})^2'
    if label.startswith('E_del'):
        parts = label.split('_')   # E, del{i}, del{j}, {ss}
        i = parts[1].replace('del', '')
        j = parts[2].replace('del', '')
        ss = parts[3]
        bi = f'b_{i}^{"+" if ss[0]=="p" else "-"}'
        bj = f'b_{j}^{"+" if ss[1]=="p" else "-"}'
        return f'{bi} {bj}'
    return label


def _realization_entry(label: str, elem: Elem, parity: int, n: int) -> dict:
    std = [{'words': list(w), 'coeff': _coeff_str(c)} for w, c in elem.items()]
    entry: dict = {
        'standard_form': std,
        'frappat_form': _frappat(label, n),
        'parity': parity,
    }
    if label == 'H_1':
        entry['note'] = 'Dual to simple root alpha_1 = epsilon - delta_1 (odd, isotropic)'
    elif label.startswith('H_'):
        k = int(label[2:])
        if k == n + 1:
            entry['note'] = (f'Terminal Cartan H_{{n+1}}; dual to alpha_{{n+1}} = 2*delta_{n}; '
                             'constant -1/2 from oscillator algebra')
        else:
            entry['note'] = f'Dual to simple root alpha_{k} = delta_{k-1} - delta_{k}'
    return entry


def generate_schema1(n: int) -> dict:
    """
    Build Schema 1 v5.0 JSON for C(n+1) with the exact 10 top-level keys
    defined in docs/json_schema_specification.md Section 2.
    """
    gens = make_generators(n)
    odd_basis, even_basis = basis_list(n)
    sc_raw = compute_structure_constants(n)

    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n

    # ── 1. schema_version ─────────────────────────────────────────
    schema_version = '5.0'

    # ── 2. algebra ────────────────────────────────────────────────
    algebra = {
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
        },
    }

    # ── 3. oscillator_generators ──────────────────────────────────
    boson_labels = []
    for k in range(1, n + 1):
        boson_labels += [f'b_{k}_p', f'b_{k}_m']
    oscillator_generators = {
        'fermions': {
            'm': 1,
            'labels': ['a_1_p', 'a_1_m'],
            'parity': 1,
            'relation': '{a_1^-, a_1^+} = 1',
            'description': 'Standard CAR fermionic pair; m=1 pair in total',
        },
        'bosons': {
            'count': 2 * n,
            'n': n,
            'labels': boson_labels,
            'description': f'Bosonic oscillators b_i^± with i=1,...,{n}',
        },
    }

    # ── 4. oscillator_relations ───────────────────────────────────
    oscillator_relations = {
        'standard_fermion_anticommutators': {
            'description': 'Canonical anticommutation relations for the standard fermionic pair',
            'relations': {
                'nilpotency_p': 'a_1_p * a_1_p = 0',
                'nilpotency_m': 'a_1_m * a_1_m = 0',
                'anticommutator': '{a_1_m, a_1_p} = 1',
            },
        },
        'bosonic_commutators': {
            'description': 'Canonical commutation relations for bosonic oscillators',
            'relations': {
                'same_type': '[b_i^±, b_j^±] = 0 for all i, j',
                'conjugate_pair': '[b_i^-, b_j^+] = delta_{ij}',
            },
        },
        'mixed_commutators': {
            'description': 'Fermionic and bosonic oscillators commute (undeformed)',
            'relation': '[b_i^±, a_1^±] = 0',
        },
    }

    # ── 5. central_elements ───────────────────────────────────────
    central_elements = {
        'kappa': {
            'label': 'kappa',
            'parity': 1,
            'properties': ['nilpotent: kappa^2 = 0', 'central', 'parity-odd'],
            'description': ('Odd nilpotent central element; appears in deformed bracket '
                            '[X,Y]_γ = [X,Y]_0 + kappa·γ(X,Y)'),
        },
        'K': {
            'label': 'K',
            'parity': 0,
            'properties': ['central', 'even', 'identified with scalar 1 in all applications'],
            'description': 'Even central identity; excluded from PBW basis and basis lists',
        },
    }

    # ── 6. basis ──────────────────────────────────────────────────
    basis = {
        'even': even_basis,
        'odd': odd_basis,
        'ordering_convention': (
            'PBW: kappa < [odd: _pp<_pm<_mp<_mm] < '
            '[even: H\'s<pos-sym<neg-sym<mixed]  (K=1 excluded)'
        ),
    }

    # ── 7. parity ─────────────────────────────────────────────────
    parity = {lbl: p for lbl, (_, p) in gens.items()}

    # ── 8. generator_realization ──────────────────────────────────
    pbw_order_str = ', '.join(['a_1_p', 'a_1_m'] + boson_labels)
    realizations = {}
    for lbl in even_basis + odd_basis:
        elem, p = gens[lbl]
        realizations[lbl] = _realization_entry(lbl, elem, p, n)

    generator_realization = {
        'description': 'Standard form with PBW ordering',
        'ordering': pbw_order_str,
        'realizations': realizations,
    }

    # ── 9. structure_constants ────────────────────────────────────
    # Format: one {X,Y,Z,coeff,sign_rule} entry per (X,Y,Z) triple.
    # Multi-term brackets (Cartan combinations) produce multiple entries.
    structure_constants = []
    for entry in sc_raw:
        for z_label, coeff in entry['terms']:
            structure_constants.append({
                'X': entry['X'],
                'Y': entry['Y'],
                'Z': z_label,
                'coeff': _coeff_str(coeff),
                'sign_rule': 'graded',
            })

    # ── 10. metadata ──────────────────────────────────────────────
    metadata = {
        'generated_by': 'src/C_generators.py',
        'generation_date': str(date.today()),
        'references': [
            'Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras',
            'Aoi (2026), docs/math/Cn1_definition.md',
            'Issue I02-1 specification: docs/json_schema_specification.md',
            'Notation: handover/notation.md',
        ],
    }

    return {
        'schema_version': schema_version,
        'algebra': algebra,
        'oscillator_generators': oscillator_generators,
        'oscillator_relations': oscillator_relations,
        'central_elements': central_elements,
        'basis': basis,
        'parity': parity,
        'generator_realization': generator_realization,
        'structure_constants': structure_constants,
        'metadata': metadata,
    }


def main():
    out_dir = Path('data')
    out_dir.mkdir(exist_ok=True)
    for n in [1, 2, 3]:
        schema = generate_schema1(n)
        out_path = out_dir / f'C_{n}_structure.json'
        with open(out_path, 'w') as f:
            json.dump(schema, f, indent=2)
        dim = schema['algebra']['dimension']
        sc_count = len(schema['structure_constants'])
        print(f'C({n+1}): dim={dim["even"]}|{dim["odd"]}={dim["total"]}, '
              f'SC entries={sc_count} → {out_path}')


if __name__ == '__main__':
    main()
