#!/usr/bin/env python3
"""
compute_coboundary.py

Compute the coboundary delta-f for a general odd linear map f: g -> g.

Mathematical definition (C_coboundary_definition.md):
  (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)]
                  - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
                  - f([X, Y])

Parameterization of f (odd map, parity reversal):
  f(Z_j) = sum_i  phi_{i,j}  Z_i,   where p(Z_i) != p(Z_j)

phi label: phi_{out_1idx}_{in_1idx}  (1-indexed positions in all_labels = even + odd)

Output: data/C_{n}_coboundary.json  (Schema 4) for n=1,2,3.
"""

import sys
import json
import datetime
from fractions import Fraction
from collections import defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Load and build bracket table from Schema 1
# ---------------------------------------------------------------------------

def load_json(path):
    with open(path) as f:
        return json.load(f)


def build_bracket_table(schema1):
    """
    Returns:
        all_labels: list[str]  (even + odd, PBW order from schema)
        parity:     dict label -> int
        label_idx:  dict label -> int
        sc_raw:     dict (i,j) -> dict {label: Fraction}  for i <= j
    """
    basis = schema1['basis']
    all_labels = basis['even'] + basis['odd']
    parity = {lbl: schema1['parity'][lbl] for lbl in all_labels}
    label_idx = {lbl: i for i, lbl in enumerate(all_labels)}

    sc_raw = defaultdict(lambda: defaultdict(Fraction))
    for entry in schema1['structure_constants']:
        X, Y, Z = entry['X'], entry['Y'], entry['Z']
        i, j = label_idx[X], label_idx[Y]
        sc_raw[(i, j)][Z] += Fraction(entry['coeff'])

    return all_labels, parity, label_idx, sc_raw


def bracket(iX, iY, all_labels, parity, sc_raw):
    """
    Return [Z_iX, Z_iY] as {label: Fraction} using graded antisymmetry.
    """
    if iX <= iY:
        return dict(sc_raw.get((iX, iY), {}))
    else:
        px = parity[all_labels[iY]]
        py = parity[all_labels[iX]]
        sign = Fraction(-(-1) ** (px * py))
        raw = sc_raw.get((iY, iX), {})
        return {lbl: sign * c for lbl, c in raw.items() if sign * c != 0}


# ---------------------------------------------------------------------------
# Coboundary computation
# ---------------------------------------------------------------------------

def compute_coboundary_entries(schema1):
    """
    Compute (delta f)(X, Y) for all upper-triangular pairs (idx_X <= idx_Y).

    Returns list of {X, Y, phi_label, Z, coeff} with nonzero coeff.

    phi_label = f'phi_{out_1idx}_{in_1idx}'  (1-based indices into all_labels)
    """
    all_labels, parity, label_idx, sc_raw = build_bracket_table(schema1)
    n_total = len(all_labels)

    entries = []

    for iX in range(n_total):
        lbl_X = all_labels[iX]
        pX = parity[lbl_X]

        for iY in range(iX, n_total):
            lbl_Y = all_labels[iY]
            pY = parity[lbl_Y]

            # Accumulate phi contributions: cob[phi_label][Z_label] += coeff
            cob = defaultdict(lambda: defaultdict(Fraction))

            s1 = Fraction((-1) ** pX)                   # (-1)^{p(X)}
            s2 = Fraction(-(-1) ** ((pX + 1) * pY))     # -(-1)^{(p(X)+1)p(Y)}

            # --- Term 1: s1 * [X, f(Y)] ---
            # f(Y) has components in opposite-parity basis: phi_{iI+1, iY+1}
            for iI in range(n_total):
                if parity[all_labels[iI]] == pY:
                    continue  # f is odd: only opposite-parity outputs
                phi_lbl = f'phi_{iI + 1}_{iY + 1}'
                br = bracket(iX, iI, all_labels, parity, sc_raw)
                for lbl_w, c in br.items():
                    val = s1 * c
                    if val != 0:
                        cob[phi_lbl][lbl_w] += val

            # --- Term 2: s2 * [Y, f(X)] ---
            # f(X) has components in opposite-parity basis: phi_{iJ+1, iX+1}
            for iJ in range(n_total):
                if parity[all_labels[iJ]] == pX:
                    continue
                phi_lbl = f'phi_{iJ + 1}_{iX + 1}'
                br = bracket(iY, iJ, all_labels, parity, sc_raw)
                for lbl_w, c in br.items():
                    val = s2 * c
                    if val != 0:
                        cob[phi_lbl][lbl_w] += val

            # --- Term 3: -f([X, Y]) ---
            # [X,Y] = sum_k c_k Z_k; f(Z_k) contributes phi_{iM+1, iK+1} at Z_iM
            br_XY = bracket(iX, iY, all_labels, parity, sc_raw)
            for lbl_k, c_k in br_XY.items():
                iK = label_idx[lbl_k]
                pK = parity[lbl_k]
                for iM in range(n_total):
                    if parity[all_labels[iM]] == pK:
                        continue
                    phi_lbl = f'phi_{iM + 1}_{iK + 1}'
                    cob[phi_lbl][all_labels[iM]] += -c_k

            # Collect nonzero entries
            for phi_lbl, z_dict in cob.items():
                for lbl_w, total_c in z_dict.items():
                    if total_c != 0:
                        entries.append({
                            'X': lbl_X,
                            'Y': lbl_Y,
                            'phi_label': phi_lbl,
                            'Z': lbl_w,
                            'coeff': str(total_c),
                        })

    return entries


# ---------------------------------------------------------------------------
# phi matrix builder
# ---------------------------------------------------------------------------

def build_phi_matrix(schema1):
    """
    Build the list of all phi parameters with metadata.
    phi_{out_1idx}_{in_1idx}: coefficient of Z_out in f(Z_in).
    Only defined when p(Z_out) != p(Z_in) (f is odd).
    """
    basis = schema1['basis']
    all_labels = basis['even'] + basis['odd']
    parity = {lbl: schema1['parity'][lbl] for lbl in all_labels}

    params = []
    for iIn, lbl_in in enumerate(all_labels):
        for iOut, lbl_out in enumerate(all_labels):
            if parity[lbl_out] == parity[lbl_in]:
                continue
            params.append({
                'label': f'phi_{iOut + 1}_{iIn + 1}',
                'output_idx': iOut + 1,
                'output_lbl': lbl_out,
                'output_parity': parity[lbl_out],
                'input_idx': iIn + 1,
                'input_lbl': lbl_in,
                'input_parity': parity[lbl_in],
                'description': f'coeff of {lbl_out} in f({lbl_in})',
            })
    return params


# ---------------------------------------------------------------------------
# Schema 4 builder
# ---------------------------------------------------------------------------

def build_schema4(n, schema1):
    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n

    phi_params = build_phi_matrix(schema1)
    coboundary = compute_coboundary_entries(schema1)

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
        'phi_matrix': {
            'description': (
                f'Parameters of the general odd linear map f for C({n + 1}). '
                f'phi_{{out_idx}}_{{in_idx}}: coeff of Z_{{out}} in f(Z_{{in}}), '
                f'p(Z_{{out}}) != p(Z_{{in}}). '
                f'Total: {len(phi_params)} = 2 x {even_dim} x {odd_dim}.'
            ),
            'count': len(phi_params),
            'parameters': phi_params,
        },
        'coboundary': coboundary,
        'metadata': {
            'generated_by': 'src/compute_coboundary.py',
            'generation_date': datetime.date.today().isoformat(),
            'n': n,
            'coboundary_formula': (
                '(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] '
                '- (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])'
            ),
            'source_schema1': f'C_{n}_structure.json',
            'stats': {
                'phi_params': len(phi_params),
                'coboundary_entries': len(coboundary),
            },
            'references': [
                'C_coboundary_definition.md',
                'docs/json_schema_specification.md',
            ],
        },
    }


# ---------------------------------------------------------------------------
# Consistency verification
# ---------------------------------------------------------------------------

def verify_schema4(schema4, schema1):
    """
    Verify Schema 4 consistency:
      1. phi_params count = 2 * dim_even * dim_odd
      2. All phi labels in coboundary entries appear in phi_matrix
      3. Parity of Z must equal p_X XOR p_Y XOR 1 for each entry
      4. All X, Y, Z labels are valid basis elements
    """
    failures = []
    basis = schema1['basis']
    all_labels = basis['even'] + basis['odd']
    parity_map = {lbl: schema1['parity'][lbl] for lbl in all_labels}
    label_set = set(all_labels)

    n = schema4['algebra']['n']
    dim_e = 2 * n * n + n + 1
    dim_o = 4 * n
    expected_phi = 2 * dim_e * dim_o
    actual_phi = schema4['phi_matrix']['count']
    if actual_phi != expected_phi:
        failures.append(f'phi_params count: {actual_phi} != {expected_phi}')

    known_phi = {p['label'] for p in schema4['phi_matrix']['parameters']}

    for entry in schema4['coboundary']:
        X, Y, phi_lbl, Z_lbl = entry['X'], entry['Y'], entry['phi_label'], entry['Z']

        for lbl in (X, Y, Z_lbl):
            if lbl not in label_set:
                failures.append(f'Unknown label: {lbl} in entry ({X},{Y})')

        if phi_lbl not in known_phi:
            failures.append(f'Unknown phi_label: {phi_lbl} in entry ({X},{Y})')

        if X in parity_map and Y in parity_map and Z_lbl in parity_map:
            pX, pY = parity_map[X], parity_map[Y]
            expected_pZ = pX ^ pY ^ 1
            actual_pZ = parity_map[Z_lbl]
            if actual_pZ != expected_pZ:
                failures.append(
                    f'Parity mismatch: ({X},{Y}) -> {Z_lbl}; '
                    f'expected p(Z)={expected_pZ}, got {actual_pZ}'
                )

    return failures


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    dry_run = '--dry-run' in sys.argv

    if '--data-dir' in sys.argv:
        idx = sys.argv.index('--data-dir')
        data_dir = Path(sys.argv[idx + 1])
    else:
        data_dir = Path(__file__).parent.parent / 'data'
    if not dry_run:
        data_dir.mkdir(exist_ok=True)

    overall_pass = True

    for n in [1, 2, 3]:
        print(f'\n--- C({n + 1}) = osp(2|{2 * n}), n={n} ---', flush=True)

        schema1 = load_json(data_dir / f'C_{n}_structure.json')

        print(f'  Building Schema 4...', flush=True)
        schema4 = build_schema4(n, schema1)
        stats = schema4['metadata']['stats']
        print(f'  phi params: {stats["phi_params"]}')
        print(f'  coboundary entries: {stats["coboundary_entries"]}')

        failures = verify_schema4(schema4, schema1)
        if failures:
            print(f'  Consistency: FAIL ({len(failures)} issue(s))')
            for msg in failures[:5]:
                print(f'    {msg}')
            overall_pass = False
        else:
            print(f'  Consistency: PASS')

        out_name = f'C_{n}_coboundary.json'
        if dry_run:
            print(f'  [dry-run] would write data/{out_name}')
        else:
            out = data_dir / out_name
            with open(out, 'w') as f:
                json.dump(schema4, f, indent=2)
            print(f'  written: {out}')

    print(f'\n{"OVERALL: ALL CHECKS PASSED" if overall_pass else "OVERALL: SOME CHECKS FAILED"}')
    return 0 if overall_pass else 1


if __name__ == '__main__':
    sys.exit(main())
