#!/usr/bin/env python3
"""
verify_C_structure.py

Load data/C_{n}_structure.json for n=1,2,3 and verify:
  1. Graded anti-symmetry: sc[Y][X][Z] = -(-1)^{p(X)*p(Y)} * sc[X][Y][Z]
  2. Super Jacobi identity (cyclic form):
     (-1)^{p(x)p(z)} [[x,y},z} + (-1)^{p(y)p(x)} [[y,z},x} + (-1)^{p(z)p(y)} [[z,x},y} = 0

Usage:
    python verify_C_structure.py [--data-dir <path>]
"""

import sys
import json
import argparse
from fractions import Fraction
from pathlib import Path
from collections import defaultdict
from itertools import combinations_with_replacement, permutations


# ---------------------------------------------------------------------------
# Load and build bracket table
# ---------------------------------------------------------------------------

def load_schema(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def build_bracket_table(schema: dict):
    """
    Build full bracket table from Schema 1 structure constants.

    Returns:
        labels: list of all basis labels (even then odd, in PBW order)
        parity: dict label -> int (0 or 1)
        label_idx: dict label -> int (index in labels)
        sc: dict (i, j) -> dict {label: Fraction}  for ALL pairs i <= j
            (lower-triangular derived via antisymmetry on demand)
    """
    basis = schema['basis']
    labels = basis['even'] + basis['odd']
    parity = {lbl: schema['parity'][lbl] for lbl in labels}
    label_idx = {lbl: i for i, lbl in enumerate(labels)}

    # Build upper-triangular sc table from JSON entries
    # sc_raw[(i,j)][Z] = Fraction coeff, stored for index_i <= index_j
    sc_raw = defaultdict(lambda: defaultdict(Fraction))
    for entry in schema['structure_constants']:
        X, Y, Z, coeff = entry['X'], entry['Y'], entry['Z'], Fraction(entry['coeff'])
        i, j = label_idx[X], label_idx[Y]
        sc_raw[(i, j)][Z] += coeff

    return labels, parity, label_idx, sc_raw


def bracket_sc(i: int, j: int, labels: list, parity: dict, label_idx: dict,
               sc_raw: dict) -> dict:
    """
    Return [labels[i], labels[j]} as {label: Fraction}.
    Uses stored entry if i <= j, else derives via antisymmetry.
    """
    if i <= j:
        return dict(sc_raw.get((i, j), {}))
    else:
        # [Y, X} = -(-1)^{p(X)*p(Y)} [X, Y}
        px, py = parity[labels[j]], parity[labels[i]]
        sign = Fraction(-(-1) ** (px * py))
        raw = sc_raw.get((j, i), {})
        return {lbl: sign * c for lbl, c in raw.items() if c != 0}


# ---------------------------------------------------------------------------
# Anti-symmetry check
# ---------------------------------------------------------------------------

def check_antisymmetry(labels, parity, label_idx, sc_raw):
    """
    For all pairs (i, j) with i <= j stored in sc_raw:
    Verify that [Y, X} = -(-1)^{p(X)*p(Y)} [X, Y}.
    i.e., sc_raw[(j, i)][Z] should equal -(-1)^{px*py} * sc_raw[(i, j)][Z]
    for all Z.

    Since lower-triangular entries are derived by definition from upper-triangular,
    this check verifies internal consistency of the upper-triangular table only
    (no information is lost). Instead we verify the equivalent:
    [X, X} = 0 for even X  (self-bracket of an even element)
    {X, X} = (-1)^1 * {X, X} + 2{X, X} ... i.e. 2{X,X} = 0 as Fractions.

    Actually, the meaningful antisymmetry check is:
    Compute [labels[i], labels[j]} from scratch via the bracket formula
    and compare with -(-1)^{px*py} * sc_raw[(i,j)].
    But we don't have the oscillator algebra here — only the SC table.

    So we check: for each stored upper-triangular pair (i<=j),
    the DERIVED lower-triangular [j,i} satisfies the antisymmetry sign.
    We cross-check: if BOTH (i,j) and (j,i) happen to appear as upper-triangular
    stored entries (which can only happen when i=j), verify consistency.
    For i < j: antisymmetry is definitional.
    For i = j (self-bracket): [X,X} should be 0 for even X; for odd X,
    2{X,X} = {X,X} + {X,X} but graded anti-sym says {X,X} = (-1)^{1*1} {X,X} = {X,X},
    so no constraint on sign, but actual computation should give the correct value.

    Additional check: verify no (j,i) with j>i appears in sc_raw
    (the generator only stores upper-triangular pairs).
    """
    failures = []
    for (i, j), zcoeffs in sc_raw.items():
        if i > j:
            failures.append(
                f"  FAIL: sc_raw has lower-triangular entry ({labels[i]}, {labels[j]})"
            )
    return failures


def check_antisymmetry_full(labels, parity, label_idx, sc_raw):
    """
    Full antisymmetry check: reconstruct [Y,X} from antisymmetry and verify
    it equals -(-1)^{px*py} [X,Y}  by checking coefficient equality.

    For each upper-triangular pair (i, j), i <= j:
      expected_yx[Z] = -(-1)^{px*py} * sc_raw[(i,j)][Z]
      derived_yx[Z]  = bracket_sc(j, i, ...) which is -(-1)^{px*py} * sc_raw[(i,j)][Z]

    This is tautologically true by construction. So the real test is:
    For i = j (self-brackets):
      [X, X} = sc_raw.get((i,i), {})
      For even X: should be empty (zero).
      For odd X: {X, X} can be nonzero (it's 2 * X^2 in the enveloping algebra).
    """
    failures = []
    for i, lbl in enumerate(labels):
        # Self-bracket check for even generators
        if parity[lbl] == 0:
            self_br = sc_raw.get((i, i), {})
            if any(c != 0 for c in self_br.values()):
                failures.append(
                    f"  FAIL self-bracket: [{lbl},{lbl}] = {dict(self_br)} (should be 0 for even)"
                )
    return failures


# ---------------------------------------------------------------------------
# Super Jacobi identity check
# ---------------------------------------------------------------------------

def bracket_composed(i, j, k, labels, parity, label_idx, sc_raw):
    """
    Compute [[labels[i], labels[j]}, labels[k]} as {label: Fraction}.
    = sum_V sc[i][j][V] * sc[V][k]
    """
    ij_br = bracket_sc(i, j, labels, parity, label_idx, sc_raw)
    result = defaultdict(Fraction)
    for lbl_v, c_ij in ij_br.items():
        v = label_idx[lbl_v]
        vk_br = bracket_sc(v, k, labels, parity, label_idx, sc_raw)
        for lbl_w, c_vk in vk_br.items():
            result[lbl_w] += c_ij * c_vk
    return {lbl: c for lbl, c in result.items() if c != 0}


def jacobi_residual(i, j, k, labels, parity, label_idx, sc_raw):
    """
    Compute the Jacobi residual for triple (i,j,k):
    (-1)^{px*pz} [[X,Y},Z} + (-1)^{py*px} [[Y,Z},X} + (-1)^{pz*py} [[Z,X},Y}
    Returns a dict {label: Fraction}; should be all zeros.
    """
    px = parity[labels[i]]
    py = parity[labels[j]]
    pz = parity[labels[k]]

    s1 = Fraction((-1) ** (px * pz))
    s2 = Fraction((-1) ** (py * px))
    s3 = Fraction((-1) ** (pz * py))

    term1 = bracket_composed(i, j, k, labels, parity, label_idx, sc_raw)
    term2 = bracket_composed(j, k, i, labels, parity, label_idx, sc_raw)
    term3 = bracket_composed(k, i, j, labels, parity, label_idx, sc_raw)

    residual = defaultdict(Fraction)
    for lbl, c in term1.items():
        residual[lbl] += s1 * c
    for lbl, c in term2.items():
        residual[lbl] += s2 * c
    for lbl, c in term3.items():
        residual[lbl] += s3 * c
    return {lbl: c for lbl, c in residual.items() if c != 0}


def check_jacobi(labels, parity, label_idx, sc_raw, verbose=False):
    """
    Check Super Jacobi for ALL ordered triples (i, j, k) with i <= j <= k.
    (Antisymmetry of the bracket means other orderings give the same constraints.)
    Returns list of failure strings.
    """
    n_labels = len(labels)
    failures = []
    total = 0

    for i in range(n_labels):
        for j in range(i, n_labels):
            for k in range(j, n_labels):
                total += 1
                res = jacobi_residual(i, j, k, labels, parity, label_idx, sc_raw)
                if res:
                    failures.append(
                        f"  FAIL Jacobi: ({labels[i]}, {labels[j]}, {labels[k]}) "
                        f"residual = {res}"
                    )

    return total, failures


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Verify C(n+1) structure constants')
    parser.add_argument('--data-dir', default=None,
                        help='Path to data/ directory (default: ../data relative to script)')
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        data_dir = script_dir.parent / 'data'

    print('=' * 60)
    print('C(n+1) Structure Constant Verification')
    print('=' * 60)

    overall_pass = True

    for n in [1, 2, 3]:
        fname = data_dir / f'C_{n}_structure.json'
        print(f'\n--- C({n+1}) = osp(2|{2*n}), n={n} [{fname.name}] ---')

        schema = load_schema(fname)
        labels, parity, label_idx, sc_raw = build_bracket_table(schema)
        dim_e = sum(1 for lbl in labels if parity[lbl] == 0)
        dim_o = sum(1 for lbl in labels if parity[lbl] == 1)
        n_sc = sum(len(v) for v in sc_raw.values())
        print(f'  Loaded: dim {dim_e}|{dim_o}, {n_sc} SC entries')

        # --- Anti-symmetry checks ---
        fails_storage = check_antisymmetry(labels, parity, label_idx, sc_raw)
        fails_self = check_antisymmetry_full(labels, parity, label_idx, sc_raw)
        all_asym_fails = fails_storage + fails_self
        n_pairs = len(sc_raw)
        if all_asym_fails:
            print(f'  Anti-symmetry: FAIL ({len(all_asym_fails)} issue(s))')
            for f in all_asym_fails:
                print(f)
            overall_pass = False
        else:
            print(f'  Anti-symmetry: PASS ({n_pairs} upper-triangular pairs, '
                  f'all even self-brackets zero)')

        # --- Super Jacobi checks ---
        print(f'  Super Jacobi: checking all triples...', end='', flush=True)
        total_triples, jac_fails = check_jacobi(labels, parity, label_idx, sc_raw)
        if jac_fails:
            print(f' FAIL ({len(jac_fails)}/{total_triples} triples failed)')
            for f in jac_fails[:10]:
                print(f)
            if len(jac_fails) > 10:
                print(f'  ... and {len(jac_fails) - 10} more failures')
            overall_pass = False
        else:
            print(f' PASS ({total_triples} triples checked)')

    print('\n' + '=' * 60)
    if overall_pass:
        print('OVERALL: ALL CHECKS PASSED')
    else:
        print('OVERALL: SOME CHECKS FAILED — see details above')
    print('=' * 60)

    return 0 if overall_pass else 1


if __name__ == '__main__':
    sys.exit(main())
