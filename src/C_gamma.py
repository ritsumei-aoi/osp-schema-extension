"""Inhomogeneous deformation γ of C(n+1) (Schema 2), symbolic in gb (I05).

The deformed bracket is [X,Y]_γ = [X,Y]_0 + κ γ(X,Y), with the oscillator
relation [b_k^s, a_1^σ] = -gb_{σ,k,s} κ. Each κ-linear term carries exactly one
gb parameter, so γ(X,Y) = Σ_g gb_g · γ_g(X,Y), with γ_g(X,Y) ∈ g.

Usage:
    python src/C_gamma.py     # writes data/C_{n}_gamma.json for n = 1, 2, 3
"""

import json
from fractions import Fraction
from pathlib import Path

from C_algebra import (Decomposer, bracket, build_basis, gb_label, kappa_free,
                       kappa_part)

GENERATION_DATE = '2026-10-08'
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'


def gb_parameters(n):
    """All 4n gb parameters as (σ, k, s) tuples, in a fixed order."""
    out = []
    for sigma in (1, -1):
        for k in range(1, n + 1):
            for s in (1, -1):
                out.append((sigma, k, s))
    return out


K_ELEMENT = {'label': 'K', 'parity': 0, 'elem': {(None, ()): Fraction(1)}}


def gamma_table(n):
    """Return (basis, gamma, residuals).

    gamma[(i, j)] = {k: {g: Fraction}} for i <= j, where
    [E_i, E_j]_γ = [E_i, E_j]_0 + κ Σ_k Σ_g gb_g · coeff · E_k.
    The index k = len(basis) is the central element K (the scalar 1), which is
    not in g. Its κ-coefficients are the K-components of γ.
    residuals[(i, j)] = κ-part words outside the span of basis ∪ {K} (must be empty).
    """
    basis = build_basis(n)
    dec = Decomposer(basis + [K_ELEMENT])
    gamma, residuals = {}, {}
    for i, X in enumerate(basis):
        for j in range(i, len(basis)):
            Y = basis[j]
            full = bracket(X['elem'], Y['elem'], X['parity'], Y['parity'])
            per_g = {}
            for g, word_coeffs in kappa_part(full).items():
                c, res = dec.coords({(None, w): v for w, v in word_coeffs.items()})
                if res:
                    residuals.setdefault((i, j), {})[g] = res
                for k, v in enumerate(c):
                    if v != 0:
                        per_g.setdefault(k, {})[g] = v
            if per_g:
                gamma[(i, j)] = per_g
    return basis, gamma, residuals


def check_schema1_match(n, basis):
    """The κ-free part of the deformed bracket must equal Schema 1 in data/.

    Reads ``data/C_{n}_structure.json`` and compares every (i, j) with i <= j.
    Returns the number of mismatching pairs.
    """
    with open(DATA_DIR / f'C_{n}_structure.json', encoding='utf-8') as f:
        s1 = json.load(f)
    labels = [b['label'] for b in basis]
    index = {lab: i for i, lab in enumerate(labels)}
    stored = {}
    for e in s1['structure_constants']:
        key = (index[e['X']], index[e['Y']])
        stored.setdefault(key, {})[index[e['Z']]] = Fraction(e['coeff'])
    dec = Decomposer(basis)
    mismatches = 0
    for i, X in enumerate(basis):
        for j in range(i, len(basis)):
            full = bracket(X['elem'], basis[j]['elem'],
                           X['parity'], basis[j]['parity'])
            c, _ = dec.coords(kappa_free(full))
            got = {k: c[k] for k in range(len(c)) if c[k] != 0}
            if got != stored.get((i, j), {}):
                mismatches += 1
    return mismatches


def check_deformed_jacobi(n, basis):
    """Super-Jacobi of the full deformed bracket (κ-free and κ-linear parts).

    Uses the engine's κ-aware product. Returns the number of failing triples.
    """
    parity = [b['parity'] for b in basis]
    elems = [b['elem'] for b in basis]
    failing = 0
    N = len(basis)
    # Brackets of basis elements, cached. Their total parity is p(i)+p(j);
    # κ carries parity 1, so the total parity of a κ-term is the same.
    cache = {}

    def br(i, j):
        if (i, j) not in cache:
            cache[(i, j)] = bracket(elems[i], elems[j], parity[i], parity[j])
        return cache[(i, j)]

    for x in range(N):
        for y in range(N):
            for z in range(N):
                pxy = (parity[x] + parity[y]) % 2
                pyz = (parity[y] + parity[z]) % 2
                pxz = (parity[x] + parity[z]) % 2
                # [X,[Y,Z]]
                lhs = bracket(elems[x], br(y, z), parity[x], pyz)
                # [[X,Y],Z]
                rhs1 = bracket(br(x, y), elems[z], pxy, parity[z])
                # (-1)^{pX pY} [Y,[X,Z]]
                t = bracket(elems[y], br(x, z), parity[y], pxz)
                s = -1 if (parity[x] * parity[y]) % 2 else 1
                diff = dict(lhs)
                for k, v in rhs1.items():
                    diff[k] = diff.get(k, 0) - v
                for k, v in t.items():
                    diff[k] = diff.get(k, 0) - s * v
                if any(v != 0 for v in diff.values()):
                    failing += 1
    return failing


def build_schema2(n, gamma, basis):
    labels = [b['label'] for b in basis]
    gb_params = []
    for g in gb_parameters(n):
        sigma, k, s = g
        gb_params.append({
            'label': gb_label(g),
            'sigma': '+' if sigma > 0 else '-',
            'k': k,
            's': '+' if s > 0 else '-',
            'parity': 1,
        })
    entries = []
    for (i, j) in sorted(gamma):
        for k, per_g in sorted(gamma[(i, j)].items()):
            terms = [{'gb': gb_label(g), 'coeff': str(v)}
                     for g, v in sorted(per_g.items())]
            z_label = labels[k] if k < len(labels) else 'K'
            entries.append({'X': labels[i], 'Y': labels[j],
                            'Z': z_label, 'terms': terms})
    columns = []
    for k in range(1, n + 1):
        columns += [f'b_{k}_p', f'b_{k}_m']
    return {
        'schema_version': '5.0',
        'layer': 'Schema 2: inhomogeneous deformation (gamma)',
        'algebra': {'family': 'C', 'm': 1, 'n': n,
                    'cartan_type': f'C({n + 1})'},
        'gb_matrix': {
            'shape': [2, 2 * n],
            'rows': {'+': 'a_1_p', '-': 'a_1_m'},
            'columns': columns,
            'parameters': gb_params,
            'description': 'gb_{σ,k,s} with σ the fermion sign and (k,s) the boson label',
        },
        'deformation_relation': {
            'boson_fermion': '[b_k^s, a_1^σ] = -gb_{σ,k,s} κ',
            'bracket': '[X,Y]_γ = [X,Y]_0 + κ γ(X,Y)',
            'parity': 'γ(X,Y) has parity p(X)+p(Y)+1; κ odd',
        },
        'gamma': entries,
        'metadata': {
            'generated_by': 'src/C_gamma.py',
            'generation_date': GENERATION_DATE,
            'references': [
                'docs/math/C_inhomogeneous_definition.md',
                'Bakalov and Sullivan (2017)',
            ],
        },
    }


def main():
    DATA_DIR.mkdir(exist_ok=True)
    for n in (1, 2, 3):
        basis, gamma, residuals = gamma_table(n)
        schema = build_schema2(n, gamma, basis)
        path = DATA_DIR / f'C_{n}_gamma.json'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
            f.write('\n')
        k_entries = sum(1 for e in schema['gamma'] if e['Z'] == 'K')
        print(f'n={n}: wrote {path.name}: {len(schema["gamma"])} gamma entries '
              f'({k_entries} with Z=K), {len(residuals)} residual pairs')
        print(f'  Schema 1 (JSON) mismatches: {check_schema1_match(n, basis)}')
        print(f'  deformed super-Jacobi failing triples: {check_deformed_jacobi(n, basis)}')


if __name__ == '__main__':
    main()
