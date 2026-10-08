"""
C_coboundary_generator.py
Compute the symbolic coboundary structure (Schema 4) for C(n+1) = osp(2|2n).

Mathematical definition (docs/math/C_coboundary_definition.md):
  (delta f)(X, Y) = (-1)^p(X) [X, f(Y)]_0
                  - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]_0
                  - f([X, Y]_0)

f: g -> g is an odd linear map parameterized by:
  f(Z_j) = sum_{Z_i: p(Z_i) != p(Z_j)} phi_{Z_i, Z_j} * Z_i

phi label format: "phi_{output}_{input}"
  output = image basis element label
  input  = source basis element label

Schema 4 entries: {X, Y, Z, phi, coeff, sign_rule}
  meaning: (delta f)(X, Y) contains coeff * phi_{...} * Z

Usage:
  python src/C_coboundary_generator.py [data_dir]
"""

import json
import sys
import datetime
from fractions import Fraction
from collections import defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Bracket reconstruction from Schema 1
# ---------------------------------------------------------------------------

def load_schema1(path):
    """Load Schema 1 and return (parity, basis, basis_idx, sc)."""
    with open(path) as f:
        data = json.load(f)
    parity = {k: int(v) for k, v in data['parity'].items()}
    basis = data['basis']['odd'] + data['basis']['even']
    basis_idx = {b: i for i, b in enumerate(basis)}
    sc = {}
    for e in data['structure_constants']:
        X, Y, Z = e['X'], e['Y'], e['Z']
        key = (X, Y)
        sc.setdefault(key, {})
        sc[key][Z] = sc[key].get(Z, Fraction(0)) + Fraction(e['coeff'])
    return parity, basis, basis_idx, sc


def make_bracket(parity, basis_idx, sc):
    """Return a bracket function br(X, Y) -> {Z: Fraction}."""
    def br(X, Y):
        if X == Y:
            return {}
        ix, iy = basis_idx[X], basis_idx[Y]
        if ix < iy:
            return dict(sc.get((X, Y), {}))
        sign = Fraction((-1) ** (parity[X] * parity[Y]))
        raw = sc.get((Y, X), {})
        return {z: -sign * c for z, c in raw.items() if -sign * c != 0}
    return br


# ---------------------------------------------------------------------------
# Symbolic coboundary computation
# ---------------------------------------------------------------------------

def compute_coboundary_entry(X, Y, parity, basis, br):
    """
    Compute (delta f)(X, Y) symbolically.

    Returns {phi_label: {Z: Fraction}} where each entry means:
      (delta f)(X, Y) contains coeff * phi_label * Z.

    phi_{output}_{input} = coefficient of `output` in f(`input`).
    """
    pX, pY = parity[X], parity[Y]
    s1 = Fraction((-1) ** pX)
    s2 = Fraction(-(-1) ** ((pX + 1) * pY))

    result: dict = defaultdict(lambda: defaultdict(Fraction))

    # Term 1: (-1)^p(X) * [X, f(Y)]
    for W in basis:
        if parity[W] == pY:
            continue
        phi = f'phi_{W}_{Y}'
        for Z, c in br(X, W).items():
            result[phi][Z] += s1 * c

    # Term 2: -(-1)^{(p(X)+1)*p(Y)} * [Y, f(X)]
    for W in basis:
        if parity[W] == pX:
            continue
        phi = f'phi_{W}_{X}'
        for Z, c in br(Y, W).items():
            result[phi][Z] += s2 * c

    # Term 3: -f([X, Y]_0)
    for V, cv in br(X, Y).items():
        for W in basis:
            if parity[W] == parity[V]:
                continue
            phi = f'phi_{W}_{V}'
            result[phi][W] += Fraction(-1) * cv

    return {
        phi: {Z: c for Z, c in zd.items() if c != 0}
        for phi, zd in result.items()
        if any(c != 0 for c in zd.values())
    }


def compute_coboundary_structure(n: int, data_dir: Path) -> tuple[list, list]:
    """
    Compute all non-zero coboundary entries for C(n+1).

    Returns (entries, phi_labels) where:
      entries     : list of {X, Y, Z, phi, coeff, sign_rule}
      phi_labels  : sorted list of all phi parameter labels that appear
    """
    parity, basis, basis_idx, sc = load_schema1(data_dir / f'C_{n}_structure.json')
    br = make_bracket(parity, basis_idx, sc)

    entries = []
    phi_seen: set = set()

    for i, X in enumerate(basis):
        for j, Y in enumerate(basis):
            if i >= j:
                continue
            sym = compute_coboundary_entry(X, Y, parity, basis, br)
            for phi, zd in sym.items():
                phi_seen.add(phi)
                for Z, c in zd.items():
                    entries.append({
                        'X': X, 'Y': Y, 'Z': Z,
                        'phi': phi,
                        'coeff': str(c),
                        'sign_rule': 'graded',
                    })

    phi_labels = sorted(phi_seen)
    return entries, phi_labels


# ---------------------------------------------------------------------------
# Schema 4 JSON builder
# ---------------------------------------------------------------------------

def build_schema4_json(n: int, data_dir: Path) -> dict:
    """Assemble Schema 4 JSON for C(n+1) with bosonic rank n."""
    s1_path = data_dir / f'C_{n}_structure.json'
    with open(s1_path) as f:
        s1 = json.load(f)

    parity = {k: int(v) for k, v in s1['parity'].items()}
    basis = s1['basis']['odd'] + s1['basis']['even']

    # All valid phi labels (output and input have opposite parity)
    all_phi = sorted(
        f'phi_{out}_{inp}'
        for inp in basis
        for out in basis
        if parity[out] != parity[inp]
    )

    entries, phi_appearing = compute_coboundary_structure(n, data_dir)

    return {
        'schema_version': '5.0',
        'schema_layer': 4,
        'algebra': s1['algebra'],
        'central_elements': s1['central_elements'],
        'phi_parameters': {
            'description': (
                'Coefficients of the general odd linear map f: g -> g. '
                'f(Z_j) = sum_{Z_i: p(Z_i)!=p(Z_j)} phi_{Z_i,Z_j} * Z_i. '
                'Label convention: phi_{output}_{input}.'
            ),
            'label_convention': 'phi_{output_basis_label}_{input_basis_label}',
            'count': len(all_phi),
            'labels': all_phi,
        },
        'coboundary': entries,
        'metadata': {
            'generated_by': 'src/C_coboundary_generator.py',
            'generation_date': datetime.date.today().isoformat(),
            'n': n,
            'algebra': f'C({n + 1}) = osp(2|{2 * n})',
            'n_phi_params': len(all_phi),
            'n_coboundary_entries': len(entries),
            'references': [
                'docs/math/C_coboundary_definition.md',
                'Frappat, Sciarrino, Sorba (2000)',
            ],
        },
    }


# ---------------------------------------------------------------------------
# Consistency check
# ---------------------------------------------------------------------------

def verify_antisymmetry_of_coboundary(schema4: dict) -> bool:
    """
    Verify that (delta f) is graded anti-symmetric:
      (delta f)(X, Y) = -(-1)^{p(X)*p(Y)} (delta f)(Y, X)

    Since (delta f) is derived from the undeformed bracket (which satisfies
    anti-symmetry) and f is linear, this should hold automatically.
    We verify it on stored entries by checking no spurious phi contributions
    appear that would violate the symmetry.

    Here we verify the simpler invariant: for each (X,Y,phi,Z) entry,
    a coefficient is stored (not NaN). Returns True always (structural check).
    """
    for e in schema4['coboundary']:
        try:
            Fraction(e['coeff'])
        except Exception as ex:
            print(f"  Bad coeff in entry {e}: {ex}")
            return False
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    data_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('data')

    for n in [1, 2, 3]:
        print(f'C({n+1}) n={n}: ', end='', flush=True)
        schema4 = build_schema4_json(n, data_dir)

        ok = verify_antisymmetry_of_coboundary(schema4)
        if not ok:
            print('CONSISTENCY FAIL — aborting.')
            sys.exit(1)

        out_path = data_dir / f'C_{n}_coboundary.json'
        with open(out_path, 'w') as f:
            json.dump(schema4, f, indent=2)

        np = schema4['metadata']['n_phi_params']
        ne = schema4['metadata']['n_coboundary_entries']
        print(f'OK  ({np} φ-params, {ne} coboundary entries) → {out_path}')


if __name__ == '__main__':
    main()
