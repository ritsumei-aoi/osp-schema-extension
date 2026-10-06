"""
C_evaluated.py: Schema 3 (Evaluated Structure) generator for C(n+1) = osp(2|2n).

Reads Schema 1 (structure constants) and Schema 2 (gamma cocycle), substitutes
concrete gb values, and emits the evaluated deformed bracket:

  [X, Y]_gamma = [X, Y]_0  +  kappa * gamma(X, Y)|_{gb=values}

Output: data/C_{n}_evaluated_{profile}.json (Schema 3, layer 3).
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
from C_generators import basis_list


# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────

def _parse(s: str) -> Fraction:
    if '/' in s:
        a, b = s.split('/')
        return Fraction(int(a), int(b))
    return Fraction(int(s))


def _coeff_str(c: Fraction) -> str:
    return str(c.numerator) if c.denominator == 1 else f'{c.numerator}/{c.denominator}'


# ──────────────────────────────────────────────────────────────────
# Load Schema 1
# ──────────────────────────────────────────────────────────────────

def _load_schema1(n: int) -> tuple[dict, dict]:
    """
    Returns:
      parity: {gen_label: int}
      fwd: {(X, Y): {Z: Fraction}}  — forward (canonical) direction only
    """
    with open(f'data/C_{n}_structure.json') as f:
        schema = json.load(f)
    parity = {k: int(v) for k, v in schema['parity'].items()}
    fwd: dict = defaultdict(lambda: defaultdict(Fraction))
    for entry in schema['structure_constants']:
        X, Y, Z = entry['X'], entry['Y'], entry['Z']
        fwd[(X, Y)][Z] += _parse(entry['coeff'])
    return parity, {k: dict(v) for k, v in fwd.items()}


# ──────────────────────────────────────────────────────────────────
# Load Schema 2
# ──────────────────────────────────────────────────────────────────

def _load_schema2(n: int) -> dict:
    """
    Returns:
      gamma: {(a, b): {c: {gb_label: Fraction}}}
    """
    with open(f'data/C_{n}_gamma.json') as f:
        schema = json.load(f)
    gamma: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(Fraction)))
    for entry in schema['gamma_cocycle']:
        a, b, c = entry['a'], entry['b'], entry['c']
        for gb, cstr in entry['coeff_gb'].items():
            gamma[(a, b)][c][gb] += _parse(cstr)
    return {
        k: {c: dict(gc) for c, gc in cv.items()}
        for k, cv in gamma.items()
    }


# ──────────────────────────────────────────────────────────────────
# Evaluate gamma at specific gb values
# ──────────────────────────────────────────────────────────────────

def _eval_gamma(gamma_ab: dict, gb_values: dict) -> dict:
    """
    Substitute gb_values into gamma(a, b).
    gamma_ab: {c: {gb_label: Fraction}}
    Returns: {c: Fraction}  (non-zero only)
    """
    result: dict = {}
    for c, gb_coeffs in gamma_ab.items():
        val = sum(gb_coeffs.get(gb, Fraction(0)) * gb_values.get(gb, Fraction(0))
                  for gb in gb_coeffs)
        if val != 0:
            result[c] = val
    return result


# ──────────────────────────────────────────────────────────────────
# gb profile builders
# ──────────────────────────────────────────────────────────────────

def _gb_all_plus(n: int) -> dict:
    return {f'gb_{s}_{j}_{t}': Fraction(1)
            for s in ['p', 'm'] for j in range(1, n + 1) for t in ['p', 'm']}


def _gb_diagonal(n: int) -> dict:
    """gb_{sigma,j,s} = 1 if sigma==s else 0."""
    return {f'gb_{s}_{j}_{t}': Fraction(1) if s == t else Fraction(0)
            for s in ['p', 'm'] for j in range(1, n + 1) for t in ['p', 'm']}


def _gb_anti_diagonal(n: int) -> dict:
    """gb_{sigma,j,s} = 1 if sigma!=s else 0."""
    return {f'gb_{s}_{j}_{t}': Fraction(1) if s != t else Fraction(0)
            for s in ['p', 'm'] for j in range(1, n + 1) for t in ['p', 'm']}


PROFILES = {
    'all_plus': (_gb_all_plus, 'All 4n gb parameters set to +1'),
    'diagonal': (_gb_diagonal, 'gb_{sigma,j,s}=1 if sigma==s, else 0 (creation-creation and annihilation-annihilation)'),
    'anti_diagonal': (_gb_anti_diagonal, 'gb_{sigma,j,s}=1 if sigma!=s, else 0 (creation-annihilation and annihilation-creation)'),
}


# ──────────────────────────────────────────────────────────────────
# Schema 3 builder
# ──────────────────────────────────────────────────────────────────

def generate_schema3(n: int, profile_name: str) -> dict:
    """Build Schema 3 JSON for C(n+1) with given gb profile."""
    gb_builder, description = PROFILES[profile_name]
    gb_values = gb_builder(n)

    parity, fwd = _load_schema1(n)
    gamma_table = _load_schema2(n)

    odd_basis, even_basis = basis_list(n)
    all_basis = even_basis + odd_basis
    idx = {g: i for i, g in enumerate(all_basis)}

    # Collect canonical (X, Y) pairs: idx[X] <= idx[Y]
    canonical: set = set()
    for (X, Y) in fwd:
        canonical.add((X, Y))  # Schema 1 already uses canonical ordering
    for (a, b) in gamma_table:
        if a in idx and b in idx and idx[a] <= idx[b]:
            canonical.add((a, b))

    entries = []
    for X, Y in sorted(canonical, key=lambda p: (idx[p[0]], idx[p[1]])):
        g_dict = fwd.get((X, Y), {})
        gamma_ab = gamma_table.get((X, Y), {})
        kappa_dict = _eval_gamma(gamma_ab, gb_values) if gamma_ab else {}

        if not g_dict and not kappa_dict:
            continue

        entry: dict = {'X': X, 'Y': Y}
        entry['g_part'] = [{'Z': Z, 'coeff': _coeff_str(c)}
                           for Z, c in g_dict.items()]
        if kappa_dict:
            entry['kappa_part'] = [{'Z': Z, 'coeff': _coeff_str(c)}
                                   for Z, c in kappa_dict.items()]

        entries.append(entry)

    # Non-zero gb values for profile record
    gb_nonzero = {gb: _coeff_str(v) for gb, v in gb_values.items() if v != 0}

    return {
        'schema_version': '5.0',
        'schema_layer': 3,
        'algebra': {
            'family': 'C',
            'n': n,
            'cartan_type': f'C({n + 1})',
            'alternative_notation': {'osp': f'osp(2|{2 * n})'},
            'schema1_file': f'C_{n}_structure.json',
            'schema2_file': f'C_{n}_gamma.json',
        },
        'gb_profile': {
            'label': profile_name,
            'description': description,
            'values': gb_nonzero,
        },
        'deformed_brackets': entries,
        'metadata': {
            'generated_by': 'src/C_evaluated.py',
            'generation_date': str(date.today()),
            'notes': (
                'Stores one canonical (X,Y) direction per pair (same convention as Schema 1). '
                'g_part = [X,Y]_0 (rational, from Schema 1). '
                'kappa_part = gamma(X,Y)|_{gb=values} (rational, from Schema 2). '
                'K = even central element. '
                'Omit kappa_part key when gamma(X,Y)=0 for the chosen profile.'
            ),
            'references': [
                'docs/math/C_inhomogeneous_definition.md',
                'docs/math/B0n_schema_v5.md',
                'Issue I06-1',
            ],
        },
    }


# ──────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────

def main() -> None:
    out_dir = Path('data')
    out_dir.mkdir(exist_ok=True)
    for n in [1, 2, 3]:
        for profile_name in PROFILES:
            schema = generate_schema3(n, profile_name)
            out_path = out_dir / f'C_{n}_evaluated_{profile_name}.json'
            with open(out_path, 'w') as f:
                json.dump(schema, f, indent=2)
            n_deformed = len(schema['deformed_brackets'])
            n_kappa = sum(1 for e in schema['deformed_brackets'] if 'kappa_part' in e)
            print(f'C({n + 1}) [{profile_name}]: {n_deformed} bracket entries, '
                  f'{n_kappa} with kappa_part → {out_path}')


if __name__ == '__main__':
    main()
