#!/usr/bin/env python3
"""
build_C_gamma.py
Compute Schema 2 (inhomogeneous deformation / gamma structure) for C(n+1) = osp(2|2n).

Generates data/C_{n}_gamma.json for n = 1, 2, 3.

Deformation convention (from C_inhomogeneous_definition.md, Option A columns):
    [b_j^s, a_1^σ]_γ = −gb_{σ,j,s} · κ       (deformed oscillator relation)
    [X,Y]_γ = [X,Y]_0 + κ · γ(X,Y)             (deformed Lie bracket)

γ is first-order in gb and is computed by tracing every b·a crossing during
PBW reduction of the product XY − (−1)^{pXpY} YX in the deformed algebra.

Each crossing of a bosonic b_j^s (from the left factor) past a fermionic a_1^σ
(from the right factor) contributes, at first order in gb:

    (−1)^{f_L + 1} × gb_{σ,j,s} × reduce_word(remaining)

where f_L = number of fermionic oscillators in the left monomial that lie
strictly to the left of b_j^s (these are already in the stack and commuting
κ past them generates the sign).

Schema 2 JSON stores inhomogeneous_deformation as a flat list of entries:
    {X, Y, Z, gb, coeff, sign_rule}
meaning γ(X,Y) ∋ coeff × gb × Z.
Z = "K" denotes the even central element K=1 (from CCR constant terms).
"""

from __future__ import annotations
import json, os, sys
from fractions import Fraction
from collections import OrderedDict
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_C_structure_constants import (
    reduce_word, build_generators, decompose, is_fermionic,
)


# ── GB parameter labelling (Option A: interleaved columns) ────────────────────

def _gb_label(fermion_idx: int, boson_idx: int) -> str:
    """
    gb label for the crossing b_j^s past a_1^σ.
    fermion_idx: 0 → σ=p (a_1^+),  1 → σ=m (a_1^-)
    boson_idx:   2k  → s=p (b_k^+), 2k+1 → s=m (b_k^-)   (k ≥ 1)
    """
    σ = 'p' if fermion_idx == 0 else 'm'
    k = boson_idx // 2              # site index, 1-based
    s = 'p' if boson_idx % 2 == 0 else 'm'
    return f'gb_{σ}_{k}_{s}'


def gb_labels_all(n: int) -> list[str]:
    """
    All 4n gb labels in column-major Option-A order:
    columns = b_1^+, b_1^-, b_2^+, b_2^-, ..., b_n^+, b_n^-
    within each column: row σ=p first, then σ=m.
    """
    labels = []
    for j in range(1, n + 1):
        for s in ('p', 'm'):
            labels.append(f'gb_p_{j}_{s}')
            labels.append(f'gb_m_{j}_{s}')
    return labels


# ── First-order κ contributions from a single monomial product ────────────────

def _kappa_product(m_X: tuple, m_Y: tuple) -> dict[str, dict[tuple, Fraction]]:
    """
    First-order κ-coefficient of the associative product m_X · m_Y.

    Enumerates every (boson from m_X, fermion from m_Y) crossing pair.
    Each pair contributes:
        (−1)^{f_L + 1} × gb_{σ,j,s} × reduce_word(remaining)
    where f_L = # fermionic oscillators in m_X strictly left of the boson.

    Returns {gb_label: {word_tuple: Fraction}}
    """
    result: dict[str, dict[tuple, Fraction]] = {}

    for i, osc_b in enumerate(m_X):
        if is_fermionic(osc_b):
            continue                          # only bosons generate crossings

        f_L = sum(1 for j in range(i) if is_fermionic(m_X[j]))
        sign = Fraction((-1) ** (f_L + 1))

        for fi, osc_f in enumerate(m_Y):
            if not is_fermionic(osc_f):
                continue                      # only fermions from m_Y are crossed

            gb = _gb_label(osc_f, osc_b)
            remaining = m_X[:i] + m_X[i + 1:] + m_Y[:fi] + m_Y[fi + 1:]
            reduced = reduce_word(remaining)

            entry = result.setdefault(gb, {})
            for word, c in reduced.items():
                v = entry.get(word, Fraction(0)) + sign * c
                if v:
                    entry[word] = v
                else:
                    entry.pop(word, None)

    return {k: v for k, v in result.items() if v}


# ── γ polynomial for a generator pair ─────────────────────────────────────────

def _gamma_poly(
    X_poly: dict[tuple, Fraction],
    Y_poly: dict[tuple, Fraction],
    pX: int, pY: int,
) -> dict[tuple, dict[str, Fraction]]:
    """
    Compute γ(X,Y) = κ-coefficient of [X,Y]_γ = XY − (−1)^{pXpY} YX.

    Returns {word_tuple: {gb_label: Fraction}}
    where the sum Σ_{word,gb} coeff·gb·word equals γ(X,Y).
    """
    bracket_sign = Fraction((-1) ** (pX * pY))
    acc: dict[tuple, dict[str, Fraction]] = {}

    def _add(word_dict: dict[tuple, Fraction], gb: str, scale: Fraction) -> None:
        for word, c in word_dict.items():
            entry = acc.setdefault(word, {})
            v = entry.get(gb, Fraction(0)) + scale * c
            if v:
                entry[gb] = v
            else:
                entry.pop(gb, None)
        for word in [w for w, d in list(acc.items()) if not d]:
            del acc[word]

    for m_X, cx in X_poly.items():
        for m_Y, cy in Y_poly.items():
            # κ-coefficient of m_X · m_Y
            for gb, wd in _kappa_product(m_X, m_Y).items():
                _add(wd, gb, cx * cy)
            # κ-coefficient of m_Y · m_X  (subtracted with bracket sign)
            for gb, wd in _kappa_product(m_Y, m_X).items():
                _add(wd, gb, -bracket_sign * cy * cx)

    return acc


# ── Decompose γ polynomial into named generators ──────────────────────────────

def _decompose_with_K(poly: dict, gens: OrderedDict, n: int) -> dict:
    """
    Like decompose() from build_C_structure_constants but also solves for K.

    The empty word () appears in:
      • the γ polynomial (from CCR constant [b_k^−, b_k^+] = 1)
      • H_{n+1}'s polynomial (coefficient −1/2)
    So () is shared between K and H_{n+1} and is NOT unique.  Including K in
    the Cartan system (columns) makes the augmented matrix full rank.

    Returns {gen_name: Fraction} where gen_name may be 'K'.
    """
    if not poly:
        return {}

    # Build generator set that includes K
    gens_ext = OrderedDict([('K', ({(): Fraction(1)}, 0))])
    gens_ext.update(gens)

    # Map word → set of generators that contain it
    word_to_gens: dict = {}
    for name, (gpoly, _) in gens_ext.items():
        for w in gpoly:
            word_to_gens.setdefault(w, set()).add(name)

    remaining = dict(poly)
    coeffs: dict = {}

    def subtract(name: str, c: Fraction) -> None:
        gpoly, _ = gens_ext[name]
        for w, gc in gpoly.items():
            v = remaining.get(w, Fraction(0)) - c * gc
            if v:
                remaining[w] = v
            else:
                remaining.pop(w, None)

    # Step 1: generators with a PBW word unique to them
    changed = True
    while changed and remaining:
        changed = False
        for name, (gpoly, _) in gens_ext.items():
            for w, gc in gpoly.items():
                if w in remaining and word_to_gens.get(w) == {name}:
                    c = remaining[w] / gc
                    coeffs[name] = coeffs.get(name, Fraction(0)) + c
                    subtract(name, c)
                    changed = True
                    break

    if not remaining:
        return {k: v for k, v in coeffs.items() if v}

    # Step 2: Cartan system — K plus H_1 … H_{n+1}
    cartan_names = ['K'] + [f'H_{k}' for k in range(1, n + 2)]
    cartan_words_set = set(w for nm in cartan_names for w in gens_ext[nm][0])
    assert all(w in cartan_words_set for w in remaining), (
        f'Unidentifiable words after unique extraction: '
        f'{set(remaining.keys()) - cartan_words_set}')

    all_words = sorted(cartan_words_set, key=lambda w: (len(w), w))
    nc = len(cartan_names)
    nw = len(all_words)

    aug = [
        [gens_ext[cartan_names[j]][0].get(w, Fraction(0)) for j in range(nc)]
        + [remaining.get(w, Fraction(0))]
        for w in all_words
    ]

    # Row-reduced echelon form over Fraction
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

    for r in range(row, nw):
        assert all(aug[r][c2] == 0 for c2 in range(nc)), (
            f'Inconsistent Cartan system at row {r}')
        assert aug[r][-1] == 0, (
            f'Inconsistent rhs at row {r}: {aug[r][-1]}')

    for col, r in pivot_col_to_row.items():
        c = aug[r][-1]
        if c:
            coeffs[cartan_names[col]] = coeffs.get(cartan_names[col], Fraction(0)) + c

    return {k: v for k, v in coeffs.items() if v}


def _decompose_gamma(
    gp: dict[tuple, dict[str, Fraction]],
    gens: OrderedDict, n: int,
) -> list[tuple[str, str, Fraction]]:
    """
    Convert {word: {gb: coeff}} to a list of (Zname, gb, coeff) triples.

    Uses _decompose_with_K so that the empty-word () from CCR constants is
    resolved jointly with H_{n+1} and K in one Gaussian elimination step.
    Z = 'K' means the even central element K = 1.

    Returns sorted list of (Zname, gb, coeff).
    """
    all_gbs: set[str] = set()
    for gb_dict in gp.values():
        all_gbs.update(gb_dict.keys())

    results: list[tuple[str, str, Fraction]] = []
    for gb in sorted(all_gbs):
        gb_poly: dict[tuple, Fraction] = {}
        for word, gb_dict in gp.items():
            c = gb_dict.get(gb, Fraction(0))
            if c:
                gb_poly[word] = c

        if gb_poly:
            for Zname, coeff in _decompose_with_K(gb_poly, gens, n).items():
                if coeff:
                    results.append((Zname, gb, coeff))

    return results


# ── Schema 2 builder ──────────────────────────────────────────────────────────

def build_schema2(n: int) -> dict:
    gens = build_generators(n)          # OrderedDict: name → (poly, parity)
    gen_names = list(gens.keys())

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(root, 'data', f'C_{n}_structure.json')) as f:
        s1 = json.load(f)

    labels = gb_labels_all(n)
    cols = []
    for j in range(1, n + 1):
        cols += [f'b_{j}_p', f'b_{j}_m']

    gb_parameters = {
        'count': 4 * n,
        'labels': labels,
        'deformed_relation': '[b_j^s, a_1^σ] = -gb_{σ,j,s} · κ',
        'gb_matrix': {
            'rows': ['a_1_p', 'a_1_m'],
            'cols': cols,
            'shape': [2, 2 * n],
            'ordering': 'Option A (interleaved): cols = b_1^+, b_1^-, b_2^+, b_2^-, ...',
            'label_format': 'gb_{σ}_{j}_{s}  (σ∈{p,m}, j=1..n, s∈{p,m})'
        }
    }

    deformation_entries = []
    for Xname in gen_names:
        X_poly, pX = gens[Xname]
        for Yname in gen_names:
            Y_poly, pY = gens[Yname]

            gp = _gamma_poly(X_poly, Y_poly, pX, pY)
            if not gp:
                continue

            for Zname, gb, coeff in _decompose_gamma(gp, gens, n):
                deformation_entries.append({
                    'X': Xname,
                    'Y': Yname,
                    'Z': Zname,
                    'gb': gb,
                    'coeff': str(coeff),
                    'sign_rule': 'graded'
                })

    return {
        'schema_version': '5.0',
        'schema_layer': 2,
        'algebra': s1['algebra'],
        'basis': s1['basis'],
        'parity': s1['parity'],
        'central_elements': s1['central_elements'],
        'gb_parameters': gb_parameters,
        'inhomogeneous_deformation': deformation_entries,
        'metadata': {
            'generated_by': 'build_C_gamma.py',
            'generation_date': str(date.today()),
            'description': (
                'Schema 2: inhomogeneous deformation γ(X,Y) for C(n+1) = osp(2|2n). '
                'Each entry {X,Y,Z,gb,coeff} records γ(X,Y) ∋ coeff·gb·Z '
                'so that [X,Y]_γ = [X,Y]_0 + κ·γ(X,Y). '
                'Z="K" entries denote the even central element K=1 '
                '(arising from CCR constant terms when b_k^- b_k^+ = b_k^+ b_k^- + 1).'
            ),
            'references': [
                'Frappat, Sciarrino, Sorba (2000)',
            ]
        }
    }


# ── Consistency verification ──────────────────────────────────────────────────

def verify_consistency(schema2: dict) -> list[str]:
    """
    Verify:
    1. All gb labels in entries are declared in gb_parameters.labels.
    2. Parity: p(Z) ≡ p(X) + p(Y) + 1  (mod 2).
    3. Anti-symmetry: γ(X,Y) = −(−1)^{pX pY} γ(Y,X).
    Returns a list of failure descriptions.
    """
    failures: list[str] = []

    parity: dict[str, int] = {k: int(v) for k, v in schema2['parity'].items()}
    parity['K'] = 0                         # K is even
    valid_gbs = set(schema2['gb_parameters']['labels'])
    all_gens = set(schema2['basis']['even'] + schema2['basis']['odd']) | {'K'}

    # Accumulate γ table
    gamma: dict[tuple, Fraction] = {}
    for e in schema2['inhomogeneous_deformation']:
        key = (e['X'], e['Y'], e['Z'], e['gb'])
        gamma[key] = gamma.get(key, Fraction(0)) + Fraction(e['coeff'])

    # 1. Valid gb labels
    for e in schema2['inhomogeneous_deformation']:
        if e['gb'] not in valid_gbs:
            failures.append(f"Unknown gb label '{e['gb']}'")

    # 2. Parity of Z
    for e in schema2['inhomogeneous_deformation']:
        X, Y, Z = e['X'], e['Y'], e['Z']
        if Z not in all_gens:
            failures.append(f"Unknown generator Z='{Z}' in ({X},{Y})")
            continue
        pZ = parity.get(Z, 0)
        pX = parity.get(X, 0)
        pY = parity.get(Y, 0)
        expected = (pX + pY + 1) % 2
        if pZ != expected:
            failures.append(
                f'Parity: [{X},{Y}]→{Z}: p(Z)={pZ}, expected {expected}')

    # 3. Anti-symmetry over all (X,Y) pairs
    all_pairs = set((e['X'], e['Y']) for e in schema2['inhomogeneous_deformation'])
    checked: set[tuple] = set()
    for (X, Y) in all_pairs:
        if (Y, X) in checked:
            continue
        checked.add((X, Y))
        pX = parity.get(X, 0)
        pY = parity.get(Y, 0)
        sign = Fraction((-1) ** (pX * pY))

        # Collect all (Z, gb) that appear for (X,Y) or (Y,X)
        zg_XY = {(Z, gb): c for (X2,Y2,Z,gb), c in gamma.items() if X2==X and Y2==Y}
        zg_YX = {(Z, gb): c for (X2,Y2,Z,gb), c in gamma.items() if X2==Y and Y2==X}
        all_zg = set(zg_XY.keys()) | set(zg_YX.keys())

        for (Z, gb) in all_zg:
            c_XY = zg_XY.get((Z, gb), Fraction(0))
            c_YX = zg_YX.get((Z, gb), Fraction(0))
            residual = c_XY + sign * c_YX
            if residual:
                failures.append(
                    f'Anti-sym: γ({X},{Y},{Z},{gb})={c_XY}, '
                    f'γ({Y},{X},{Z},{gb})={c_YX}, residual={residual}')

    return failures


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root, 'data')
    os.makedirs(out_dir, exist_ok=True)

    print('C(n+1) Schema 2 — inhomogeneous deformation build')
    print('=' * 58)

    all_ok = True
    for n in [1, 2, 3]:
        print(f'\nn={n}  C({n+1}) = osp(2|{2*n})')
        schema2 = build_schema2(n)
        nd = len(schema2['inhomogeneous_deformation'])
        print(f'  Deformation entries : {nd}')
        print(f'  GB parameters       : {4*n}')

        failures = verify_consistency(schema2)
        if failures:
            all_ok = False
            print(f'  Consistency : FAIL ({len(failures)} issues)')
            for msg in failures[:5]:
                print(f'    {msg}')
        else:
            print(f'  Consistency : PASS  '
                  f'(parity, anti-symmetry, gb labels)')

        out_path = os.path.join(out_dir, f'C_{n}_gamma.json')
        with open(out_path, 'w') as f:
            json.dump(schema2, f, indent=2)
        print(f'  Written     : {out_path}')

    print('\n' + '=' * 58)
    if all_ok:
        print('ALL CHECKS PASSED')
    else:
        print('FAILURES DETECTED — see above')
        sys.exit(1)


if __name__ == '__main__':
    main()
