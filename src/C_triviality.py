"""
C_triviality.py: Triviality condition analysis for C(n+1) = osp(2|2n).

Determines the conditions on gb parameters under which the inhomogeneous
deformation γ = (δf) for some odd map f: g → g.

Key mathematical fact:
  (δf)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])

Since f maps g → g and all brackets stay within g (no K-component in Schema 1),
the coboundary (δf) can never have a K-component. But γ(X,Y)^K ≠ 0 for many
(X,Y), requiring those K-coefficients to vanish.

Algorithm:
  1. K-constraint check: γ(X,Y)^K = 0 for all (X,Y) — direct constraint on gb.
  2. Augmented linear system: solve M·φ = N·gb over Q for any remaining constraints.
     M[row, j] = coefficient of φ_j in (δf)(X,Y)^Z
     N[row, k] = coefficient of gb_k in γ(X,Y)^Z  (non-K entries)
  3. Row-reduce [M | N]; rows where M-block vanishes give further constraints on gb.
  4. Report complete set of triviality conditions.
"""

from __future__ import annotations
import json
import sys
import os
from fractions import Fraction
from collections import defaultdict

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


def _load_schema2_raw(n: int) -> list[dict]:
    with open(f'data/C_{n}_gamma.json') as f:
        return json.load(f)['gamma_cocycle']


def _load_schema4_raw(n: int) -> tuple[list[str], list[dict]]:
    with open(f'data/C_{n}_coboundary.json') as f:
        data = json.load(f)
    return data['f_map']['phi_labels'], data['coboundary']


# ──────────────────────────────────────────────────────────────────
# K-constraint analysis
# ──────────────────────────────────────────────────────────────────

def analyze_K_constraints(n: int) -> dict:
    """
    From γ entries with c='K': since (δf)^K = 0 always,
    triviality requires γ(X,Y)^K = 0 for all (X,Y).

    Returns {gb_label: {(a,b): coeff}} — for each gb, the K-equations it enters.
    If any gb appears with non-zero coefficient in an equation that involves ONLY
    that gb, then that gb must be zero.
    """
    entries = _load_schema2_raw(n)
    k_entries = [e for e in entries if e['c'] == 'K']

    # Build matrix: rows = (a,b) pairs with K-component, cols = gb labels
    # Row content: {gb_label: Fraction}
    k_system: dict[tuple, dict] = {}
    for e in k_entries:
        key = (e['a'], e['b'])
        if key not in k_system:
            k_system[key] = {}
        for gb, c in e['coeff_gb'].items():
            k_system[key][gb] = k_system[key].get(gb, Fraction(0)) + _parse(c)

    # Remove zero rows
    k_system = {k: v for k, v in k_system.items() if any(c != 0 for c in v.values())}

    # Collect all gb labels
    all_gb = sorted(set(gb for row in k_system.values() for gb in row))

    # Build matrix rows as lists
    gb_idx = {g: i for i, g in enumerate(all_gb)}
    rows = []
    row_keys = []
    for key, gb_dict in k_system.items():
        row = [Fraction(0)] * len(all_gb)
        for gb, c in gb_dict.items():
            row[gb_idx[gb]] = c
        rows.append(row)
        row_keys.append(key)

    # Row-reduce to find independent constraints
    rref_rows, pivot_cols, rank = _row_reduce_square(rows, len(all_gb))

    # The constraints are: each pivot row gives one independent equation
    # If rank == len(all_gb): all gb are independently constrained → all gb = 0
    independent_constraints = []
    for r in range(rank):
        constraint = {all_gb[j]: rref_rows[r][j]
                      for j in range(len(all_gb)) if rref_rows[r][j] != 0}
        independent_constraints.append(constraint)

    return {
        'n': n,
        'k_entry_count': len(k_entries),
        'k_equation_count': len(k_system),
        'gb_labels': all_gb,
        'gb_count': len(all_gb),
        'k_constraint_rank': rank,
        'k_constraints_independent': independent_constraints,
        'all_gb_forced_zero': (rank == len(all_gb)),
    }


# ──────────────────────────────────────────────────────────────────
# Full linear system: M·φ = N·gb (non-K part)
# ──────────────────────────────────────────────────────────────────

def analyze_full_system(n: int) -> dict:
    """
    Build and analyze the full linear system for triviality.

    For non-K entries: γ(X,Y)^Z must equal (δf)(X,Y)^Z.
    Setting up M·φ = N·gb (M from Schema 4, N from Schema 2 non-K),
    find the conditions on gb for consistency.
    """
    # Load Schema 2 non-K entries
    gamma_entries = _load_schema2_raw(n)
    gamma_nk: dict[tuple, dict] = {}  # (a,b,c) → {gb: Fraction}
    for e in gamma_entries:
        if e['c'] == 'K':
            continue
        key = (e['a'], e['b'], e['c'])
        if key not in gamma_nk:
            gamma_nk[key] = {}
        for gb, cs in e['coeff_gb'].items():
            gamma_nk[key][gb] = gamma_nk[key].get(gb, Fraction(0)) + _parse(cs)

    # Load Schema 4 coboundary entries
    phi_labels, cb_entries = _load_schema4_raw(n)
    cb: dict[tuple, dict] = {}
    for e in cb_entries:
        key = (e['X'], e['Y'], e['Z'])
        cb[key] = {lbl: _parse(c) for lbl, c in e['coeff_phi'].items()}

    # Union of row keys
    all_rows = sorted(set(gamma_nk.keys()) | set(cb.keys()))

    # Index maps
    phi_idx = {l: i for i, l in enumerate(phi_labels)}
    all_gb = sorted(set(gb for row in gamma_nk.values() for gb in row))
    gb_idx = {g: i for i, g in enumerate(all_gb)}
    nphi = len(phi_labels)
    ngb = len(all_gb)
    nrows = len(all_rows)

    # Build M (phi columns) and N (gb columns) matrices
    M = [[Fraction(0)] * nphi for _ in range(nrows)]
    N = [[Fraction(0)] * ngb for _ in range(nrows)]

    for i, key in enumerate(all_rows):
        for lbl, c in cb.get(key, {}).items():
            j = phi_idx.get(lbl)
            if j is not None:
                M[i][j] = c
        for gb, c in gamma_nk.get(key, {}).items():
            j = gb_idx.get(gb)
            if j is not None:
                N[i][j] = c

    # Row-reduce [M | N] using only M-columns as pivot candidates
    # Rows where M-block vanishes give constraints on gb
    aug = [M[i] + N[i] for i in range(nrows)]
    rank, additional_constraints = _find_consistency_constraints(aug, nphi, ngb, all_gb)

    return {
        'n': n,
        'nrows': nrows,
        'nphi': nphi,
        'ngb': ngb,
        'M_rank': rank,
        'additional_constraints_count': len(additional_constraints),
        'additional_constraints': additional_constraints,
        'all_gb': all_gb,
    }


# ──────────────────────────────────────────────────────────────────
# Rational linear algebra
# ──────────────────────────────────────────────────────────────────

def _row_reduce_square(rows: list, ncols: int) -> tuple:
    """
    Row-reduce a matrix (list of lists of Fraction) to RREF.
    Returns (rref_rows, pivot_cols, rank).
    """
    mat = [list(row) for row in rows]
    nrows = len(mat)
    pivot_cols = []
    r = 0
    for col in range(ncols):
        # Find pivot
        pivot = None
        for row in range(r, nrows):
            if mat[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        mat[r], mat[pivot] = mat[pivot], mat[r]
        scale = mat[r][col]
        mat[r] = [x / scale for x in mat[r]]
        for row in range(nrows):
            if row != r and mat[row][col] != 0:
                f = mat[row][col]
                mat[row] = [mat[row][k] - f * mat[r][k] for k in range(ncols)]
        pivot_cols.append(col)
        r += 1
    return mat, pivot_cols, r


def _find_consistency_constraints(aug: list, nphi: int, ngb: int, gb_labels: list) -> tuple:
    """
    Row-reduce [M | N] using only the first nphi columns as pivot candidates.
    Returns (M_rank, constraints) where each constraint is a dict {gb_label: coeff}
    representing a linear equation that must hold for consistency.
    """
    mat = [list(row) for row in aug]
    nrows = len(mat)
    total_cols = nphi + ngb
    rank = 0

    for col in range(nphi):  # pivot only in M-columns
        pivot = None
        for r in range(rank, nrows):
            if mat[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            continue
        mat[rank], mat[pivot] = mat[pivot], mat[rank]
        scale = mat[rank][col]
        mat[rank] = [x / scale for x in mat[rank]]
        for r in range(nrows):
            if r != rank and mat[r][col] != 0:
                f = mat[r][col]
                mat[r] = [mat[r][k] - f * mat[rank][k] for k in range(total_cols)]
        rank += 1

    # Rows beyond rank: M-block is all-zero, N-block must also be zero
    constraints = []
    seen = set()
    for r in range(rank, nrows):
        n_part = tuple(mat[r][nphi:])
        if all(c == 0 for c in n_part):
            continue
        if n_part in seen:
            continue
        seen.add(n_part)
        constraint = {gb_labels[j]: mat[r][nphi + j]
                      for j in range(ngb) if mat[r][nphi + j] != 0}
        if constraint:
            constraints.append(constraint)

    return rank, constraints


# ──────────────────────────────────────────────────────────────────
# Main report
# ──────────────────────────────────────────────────────────────────

def run_triviality_analysis(n: int) -> dict:
    """Run full triviality analysis for C(n+1)."""
    k_result = analyze_K_constraints(n)
    full_result = analyze_full_system(n)
    return {'K': k_result, 'full': full_result}


def print_report(n: int, res: dict) -> None:
    k = res['K']
    f = res['full']
    print(f"\n{'='*60}")
    print(f"C({n+1}) = osp(2|{2*n}):  n = {n}")
    print(f"{'='*60}")
    print(f"  gb parameters: {k['gb_count']}  ({', '.join(k['gb_labels'])})")
    print()
    print(f"  [K-constraint analysis]")
    print(f"  K-entries in gamma:  {k['k_entry_count']}")
    print(f"  Distinct (a,b) pairs with gamma^K != 0:  {k['k_equation_count']}")
    print(f"  Rank of K-constraint system:  {k['k_constraint_rank']} / {k['gb_count']}")
    print(f"  All gb forced to zero by K-constraints:  {k['all_gb_forced_zero']}")
    if not k['all_gb_forced_zero']:
        print("  Independent K-constraints:")
        for c in k['k_constraints_independent']:
            terms = " + ".join(f"({v}){gb}" for gb, v in c.items())
            print(f"    {terms} = 0")
    print()
    print(f"  [Full linear system (non-K entries)]")
    print(f"  Total rows (X,Y,Z) triples:  {f['nrows']}")
    print(f"  phi parameters:  {f['nphi']}")
    print(f"  gb parameters:  {f['ngb']}")
    print(f"  Rank of M (coboundary):  {f['M_rank']}")
    print(f"  Additional gb constraints from non-K part:  {f['additional_constraints_count']}")
    if f['additional_constraints']:
        print("  Additional constraints:")
        for c in f['additional_constraints'][:5]:
            terms = " + ".join(f"({v}){gb}" for gb, v in c.items())
            print(f"    {terms} = 0")
        if len(f['additional_constraints']) > 5:
            print(f"    ... ({len(f['additional_constraints'])-5} more)")


if __name__ == '__main__':
    for n in [1, 2, 3]:
        res = run_triviality_analysis(n)
        print_report(n, res)
    print()
