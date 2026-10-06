"""
C_coboundary.py: Schema 4 (Coboundary Structure) for C(n+1) = osp(2|2n).

Computes the symbolic coboundary (delta f)(X,Y) of a general odd linear map
f: g -> g, parametrized by phi_{image,domain} coefficients:

  f(Z_j) = sum_i  phi_{Z_i, Z_j} * Z_i   (p(Z_i) != p(Z_j))

Coboundary formula (from C_coboundary_definition.md):
  (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)]
                 - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)]
                 - f([X, Y])

Output: data/C_{n}_coboundary.json  (Schema 4, layer 4).
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
# Load Schema 1
# ──────────────────────────────────────────────────────────────────

def _parse(s: str) -> Fraction:
    if '/' in s:
        a, b = s.split('/')
        return Fraction(int(a), int(b))
    return Fraction(int(s))


def _coeff_str(c: Fraction) -> str:
    return str(c.numerator) if c.denominator == 1 else f'{c.numerator}/{c.denominator}'


def _load_schema1(n: int) -> tuple[dict, dict]:
    """Return (parity, fwd) where fwd = {(X,Y): {Z: Fraction}} (forward direction only)."""
    with open(f'data/C_{n}_structure.json') as f:
        schema = json.load(f)
    parity = {k: int(v) for k, v in schema['parity'].items()}
    fwd: dict = defaultdict(lambda: defaultdict(Fraction))
    for entry in schema['structure_constants']:
        X, Y, Z = entry['X'], entry['Y'], entry['Z']
        fwd[(X, Y)][Z] += _parse(entry['coeff'])
    return parity, {k: dict(v) for k, v in fwd.items()}


def _build_full_bt(parity: dict, fwd: dict) -> dict:
    """Build full bracket table (both directions) from forward-only Schema 1 data."""
    bt: dict = {}
    for (X, Y), terms in fwd.items():
        bt[(X, Y)] = dict(terms)
        if X != Y:
            sign = Fraction((-1) ** (parity[X] * parity[Y]))
            bt[(Y, X)] = {Z: -sign * c for Z, c in terms.items()}
    return bt


# ──────────────────────────────────────────────────────────────────
# Symbolic coboundary computation
# ──────────────────────────────────────────────────────────────────

def _phi_label(image: str, domain: str) -> str:
    """phi_{image}_{domain} = coefficient of Z_image in f(Z_domain)."""
    return f'phi_{image}_{domain}'


def compute_coboundary_symbolic(n: int) -> dict:
    """
    Compute (delta f)(X,Y)^Z symbolically for all triples.

    Returns:
      {(X, Y, Z): {phi_label: Fraction}}  — non-zero entries only.
    """
    parity, fwd = _load_schema1(n)
    bt = _build_full_bt(parity, fwd)

    odd_basis, even_basis = basis_list(n)
    all_basis = even_basis + odd_basis

    # Pre-group basis by parity for fast lookup
    parity_group: dict[int, list] = {0: even_basis, 1: odd_basis}

    result: dict = {}

    for X in all_basis:
        pX = parity[X]
        sign1 = Fraction((-1) ** pX)               # for Term 1

        for Y in all_basis:
            pY = parity[Y]
            sign2 = Fraction(-(-1) ** ((pX + 1) * pY))  # for Term 2

            # coeff_Z[Z][phi_label] accumulates the linear form
            coeff_Z: dict = defaultdict(lambda: defaultdict(Fraction))

            # ── Term 1: (-1)^{pX} [X, f(Y)] ──────────────────────────
            # f(Y) = sum_{image: p(image)!=pY} phi_{image,Y} * Z_image
            # Contribution: sign1 * sum_{image} phi_{image,Y} * bt[(X,image)]^Z
            for image in parity_group[1 - pY]:  # p(image) != pY
                lbl = _phi_label(image, Y)
                for Z, c in bt.get((X, image), {}).items():
                    coeff_Z[Z][lbl] += sign1 * c

            # ── Term 2: -(-1)^{(pX+1)pY} [Y, f(X)] ──────────────────
            # f(X) = sum_{image: p(image)!=pX} phi_{image,X} * Z_image
            # Contribution: sign2 * sum_{image} phi_{image,X} * bt[(Y,image)]^Z
            for image in parity_group[1 - pX]:  # p(image) != pX
                lbl = _phi_label(image, X)
                for Z, c in bt.get((Y, image), {}).items():
                    coeff_Z[Z][lbl] += sign2 * c

            # ── Term 3: -f([X, Y]) ────────────────────────────────────
            # [X,Y] = sum_k c_k Z_k;  f(Z_k) = sum_{Z: p(Z)!=p(Zk)} phi_{Z,Zk} Z
            # Contribution to (δf)^Z: -c_k * phi_{Z,Zk}  for each k with p(Z)!=p(Zk)
            for Zk, ck in bt.get((X, Y), {}).items():
                pZk = parity[Zk]
                for Z in parity_group[1 - pZk]:  # p(Z) != pZk
                    lbl = _phi_label(Z, Zk)
                    coeff_Z[Z][lbl] -= ck

            # Collect non-zero entries
            for Z, phi_dict in coeff_Z.items():
                nonzero = {lbl: c for lbl, c in phi_dict.items() if c != 0}
                if nonzero:
                    result[(X, Y, Z)] = nonzero

    return result


# ──────────────────────────────────────────────────────────────────
# Schema 4 JSON builder
# ──────────────────────────────────────────────────────────────────

def generate_schema4(n: int) -> dict:
    """Build Schema 4 JSON for C(n+1)."""
    parity, _ = _load_schema1(n)
    odd_basis, even_basis = basis_list(n)
    all_basis = even_basis + odd_basis

    # Enumerate all valid phi parameters (ordered: even→odd then odd→even)
    phi_labels: list[str] = []
    for domain in all_basis:
        for image in all_basis:
            if parity[image] != parity[domain]:
                phi_labels.append(_phi_label(image, domain))

    # Compute symbolic coboundary
    cb = compute_coboundary_symbolic(n)

    # Build JSON entries — sorted for deterministic output
    idx = {g: i for i, g in enumerate(all_basis)}

    entries = []
    for (X, Y, Z) in sorted(cb.keys(),
                             key=lambda t: (idx[t[0]], idx[t[1]], idx[t[2]])):
        phi_dict = cb[(X, Y, Z)]
        entries.append({
            'X': X,
            'Y': Y,
            'Z': Z,
            'coeff_phi': {lbl: _coeff_str(c) for lbl, c in phi_dict.items()},
        })

    return {
        'schema_version': '5.0',
        'schema_layer': 4,
        'algebra': {
            'family': 'C',
            'n': n,
            'cartan_type': f'C({n + 1})',
            'alternative_notation': {'osp': f'osp(2|{2 * n})'},
            'schema1_file': f'C_{n}_structure.json',
        },
        'f_map': {
            'description': (
                'Odd linear map f: g -> g; '
                'f(Z_domain) = sum_image phi_{image}_{domain} * Z_image, '
                'where p(Z_image) != p(Z_domain)'
            ),
            'parity_rule': 'f(even) -> odd subspace;  f(odd) -> even subspace',
            'phi_labels': phi_labels,
            'phi_count': len(phi_labels),
        },
        'coboundary': entries,
        'metadata': {
            'generated_by': 'src/C_coboundary.py',
            'generation_date': str(date.today()),
            'formula': (
                '(delta_f)(X,Y) = (-1)^{p(X)}[X,f(Y)] '
                '- (-1)^{(p(X)+1)*p(Y)}[Y,f(X)] - f([X,Y])'
            ),
            'notes': (
                'Symbolic output: each (X,Y,Z) entry gives the rational linear form '
                'in phi parameters whose value equals (delta_f)(X,Y)^Z. '
                'Only non-zero entries stored. '
                'phi_{image}_{domain}: coefficient of Z_image in f(Z_domain).'
            ),
            'references': [
                'docs/math/C_coboundary_definition.md',
                'docs/math/B0n_schema_v5.md',
                'Issue I07-1',
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
        schema = generate_schema4(n)
        out_path = out_dir / f'C_{n}_coboundary.json'
        with open(out_path, 'w') as f:
            json.dump(schema, f, indent=2)
        phi_count = schema['f_map']['phi_count']
        cb_count = len(schema['coboundary'])
        print(f'C({n + 1}): {phi_count} phi params, {cb_count} coboundary entries → {out_path}')


if __name__ == '__main__':
    main()
