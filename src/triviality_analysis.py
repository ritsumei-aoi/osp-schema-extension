#!/usr/bin/env python3
"""
triviality_analysis.py
Determine whether the inhomogeneous deformation of C(n+1) = osp(2|2n) is trivial.

Triviality condition: γ(X,Y) = (δf)(X,Y) for some odd linear map f: g → g.
We solve the linear system over Q to check consistency.

The general odd map f is parameterized by φ_{(i,j)} for every parity-violating
pair (basis_i, basis_j), giving a large linear system whose solvability decides
the question.

Additionally we compare γ|_{gb=1} with the specific δf_0 (index-paired, φ=1)
from Schema 4 to quantify agreement / discrepancy.
"""
from __future__ import annotations
import json, os
from collections import defaultdict
from fractions import Fraction

# ── helpers ──────────────────────────────────────────────────────────────────

def load(path):
    with open(path) as f:
        return json.load(f)

def pf(s):
    if '/' in s:
        n, d = s.split('/'); return Fraction(int(n), int(d))
    return Fraction(int(s))

def fstr(f):
    return str(f.numerator) if f.denominator == 1 else f'{f.numerator}/{f.denominator}'

# ── extract gamma from Layer 3 (strip kappa·) ────────────────────────────────

def extract_gamma(schema3: dict) -> dict[tuple, Fraction]:
    """Returns {(X,Y,Z): coeff} for kappa entries, with Z having kappa· stripped."""
    result = {}
    for e in schema3['evaluated_brackets']:
        if e['type'] != 'kappa':
            continue
        Z_raw = e['Z']
        if Z_raw == 'kappa':
            Z = 'K'  # κ·K = κ, K = identity
        elif Z_raw.startswith('kappa·'):
            Z = Z_raw[6:]
        else:
            continue
        key = (e['X'], e['Y'], Z)
        result[key] = result.get(key, Fraction(0)) + pf(e['coeff'])
    return {k: v for k, v in result.items() if v}

# ── extract delta_f from Layer 4 ─────────────────────────────────────────────

def extract_delta_f(schema4: dict) -> dict[tuple, Fraction]:
    result = {}
    for e in schema4['coboundary']:
        key = (e['X'], e['Y'], e['Z'])
        result[key] = result.get(key, Fraction(0)) + pf(e['coeff'])
    return {k: v for k, v in result.items() if v}

# ── direct comparison γ vs δf_0 ──────────────────────────────────────────────

def compare_gamma_df(gamma: dict, df: dict, basis_all: list) -> dict:
    """
    Check if γ = c·δf_0 for a single scalar c (proportionality).
    Returns {status, scalar, discrepancies}.
    """
    all_keys = set(gamma) | set(df)
    if not all_keys:
        return {'status': 'both_zero', 'scalar': None, 'discrepancies': []}

    # Find candidate c from the first overlapping key
    c = None
    for k in sorted(all_keys):
        g = gamma.get(k, Fraction(0))
        d = df.get(k, Fraction(0))
        if g == 0 and d == 0:
            continue
        if g != 0 and d != 0:
            c = g / d
            break
        # one is zero, other isn't: proportionality fails immediately
        return {
            'status': 'not_proportional',
            'scalar': None,
            'discrepancies': [{'key': k, 'gamma': fstr(g), 'delta_f': fstr(d)}]
        }

    if c is None:
        return {'status': 'both_zero', 'scalar': None, 'discrepancies': []}

    # Verify c works for all keys
    discrep = []
    for k in sorted(all_keys):
        g = gamma.get(k, Fraction(0))
        d = df.get(k, Fraction(0))
        if g != c * d:
            discrep.append({'key': k, 'gamma': fstr(g), 'c_times_df': fstr(c * d),
                            'delta_f': fstr(d)})

    return {
        'status': 'proportional' if not discrep else 'not_proportional',
        'scalar': fstr(c),
        'discrepancies': discrep,
    }

# ── general triviality check via linear system ────────────────────────────────

def solve_triviality(schema1: dict, schema3: dict) -> dict:
    """
    Set up the linear system  Σ_{(i,j)} φ_{ij} · (∂δf/∂φ_{ij})(X,Y,Z) = γ(X,Y,Z)
    and check consistency using Gaussian elimination over Q.

    The general odd f is f(Z_j) = Σ_{p(Z_i)≠p(Z_j)} φ_{ij} Z_i.
    Then (δf)(X,Y) = (-1)^{pX}[X,f(Y)] - (-1)^{(pX+1)pY}[Y,f(X)] - f([X,Y]).

    Since this is linear in the φ_{ij}, we compute the "basis coboundaries":
      δe_{ij}  where e_{ij} is the elementary map Z_j → Z_i (all other → 0).
    Then δf = Σ_{ij} φ_{ij} · δe_{ij}.
    """
    parity = {k: int(v) for k, v in schema1['parity'].items()}
    basis_even = schema1['basis']['even']
    basis_odd  = schema1['basis']['odd']
    basis_all  = basis_even + basis_odd

    # Schema 1 bracket
    sc: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(Fraction)))
    for e in schema1['structure_constants']:
        sc[e['X']][e['Y']][e['Z']] += pf(e['coeff'])
    def bracket(X, Y):
        return {Z: c for Z, c in sc[X][Y].items() if c}

    # γ target (from Layer 3)
    gamma = extract_gamma(schema3)

    # Free variables: φ_{ij} for parity-violating pairs
    free_vars = []
    for j, Zj in enumerate(basis_all):
        for i, Zi in enumerate(basis_all):
            if (parity[Zi] + parity[Zj]) % 2 == 1:
                free_vars.append((Zi, Zj))  # f(Zj) += φ · Zi

    # For each free variable φ_{ij}, compute the contribution to (δf)(X,Y,Z)
    # using the elementary map e_{ij}: Zj → Zi (1 unit), all others → 0.

    def delta_e(src_gen, img_gen):
        """(δe_{src→img})(X,Y) as {(X,Y,Z): coeff}."""
        pSrc = parity[src_gen]  # parity of the domain element
        pImg = parity[img_gen]
        result = {}
        def add(X, Y, poly, scale):
            for Z, c in poly.items():
                key = (X, Y, Z)
                v = result.get(key, Fraction(0)) + scale * c
                if v: result[key] = v
                else: result.pop(key, None)

        for X in basis_all:
            pX = parity[X]
            for Y in basis_all:
                pY = parity[Y]
                sXfY = Fraction((-1) ** pX)
                sYfX = Fraction((-1) ** ((pX + 1) * pY))

                # term1: (-1)^pX [X, f(Y)]; f(Y) = img_gen if Y==src_gen
                if Y == src_gen:
                    add(X, Y, bracket(X, img_gen), sXfY)
                # term2: -(-1)^{(pX+1)pY} [Y, f(X)]; f(X) = img_gen if X==src_gen
                if X == src_gen:
                    add(X, Y, bracket(Y, img_gen), -sYfX)
                # term3: -f([X,Y]); -img_gen·coeff if src_gen in [X,Y]
                XY = bracket(X, Y)
                for Z, c in XY.items():
                    if Z == src_gen:
                        key = (X, Y, img_gen)
                        v = result.get(key, Fraction(0)) - c
                        if v: result[key] = v
                        else: result.pop(key, None)
        return result

    # Precompute δe for all free variables
    print(f'    Building {len(free_vars)} basis coboundaries...', flush=True)
    de_list = []
    for (img_gen, src_gen) in free_vars:
        de_list.append(delta_e(src_gen, img_gen))

    # All constraint keys: union of gamma keys and all δe keys
    all_keys = set(gamma.keys())
    for de in de_list:
        all_keys.update(de.keys())
    all_keys = sorted(all_keys)

    n_rows = len(all_keys)
    n_cols = len(free_vars)

    # Build augmented matrix [A | b] where A[r,c] = de_list[c][all_keys[r]],
    # b[r] = gamma[all_keys[r]]
    key_idx = {k: r for r, k in enumerate(all_keys)}
    aug = [[Fraction(0)] * (n_cols + 1) for _ in range(n_rows)]
    for r, k in enumerate(all_keys):
        aug[r][-1] = gamma.get(k, Fraction(0))
    for c, de in enumerate(de_list):
        for k, v in de.items():
            aug[key_idx[k]][c] = v

    print(f'    Linear system: {n_rows} equations, {n_cols} unknowns', flush=True)

    # Gaussian elimination
    pivot_rows = []
    row = 0
    for col in range(n_cols):
        pr = next((r for r in range(row, n_rows) if aug[r][col] != 0), None)
        if pr is None:
            continue
        aug[pr], aug[row] = aug[row], aug[pr]
        pv = aug[row][col]
        aug[row] = [x / pv for x in aug[row]]
        for r in range(n_rows):
            if r != row and aug[r][col] != 0:
                f_val = aug[r][col]
                aug[r] = [aug[r][c2] - f_val * aug[row][c2]
                          for c2 in range(n_cols + 1)]
        pivot_rows.append((col, row))
        row += 1

    # Check consistency: zero rows must have zero rhs
    inconsistencies = []
    for r in range(row, n_rows):
        if aug[r][-1] != 0:
            inconsistencies.append({
                'key': all_keys[r],
                'rhs': fstr(aug[r][-1]),
                'gamma': fstr(gamma.get(all_keys[r], Fraction(0))),
            })

    is_trivial = len(inconsistencies) == 0
    rank_A = len(pivot_rows)
    n_free = n_cols - rank_A  # degrees of freedom in the solution

    # If trivial, extract one particular solution
    solution = {}
    if is_trivial:
        for col, r in pivot_rows:
            val = aug[r][-1]
            if val:
                src_gen = free_vars[col][1]
                img_gen = free_vars[col][0]
                solution[f'phi[{img_gen} <- {src_gen}]'] = fstr(val)

    return {
        'is_trivial': is_trivial,
        'n_equations': n_rows,
        'n_unknowns': n_cols,
        'rank': rank_A,
        'degrees_of_freedom': n_free,
        'inconsistencies': inconsistencies[:10],  # at most 10
        'n_inconsistencies': len(inconsistencies),
        'solution_nonzero': solution if is_trivial else {},
    }

# ── main ─────────────────────────────────────────────────────────────────────

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root, 'data')

    print('Triviality Analysis: C(n+1) inhomogeneous deformation')
    print('=' * 72)

    for n in [1, 2, 3]:
        print(f'\nn={n}  C({n+1}) = osp(2|{2*n})')
        print('-' * 50)

        s1 = load(os.path.join(data_dir, f'C_{n}_structure.json'))
        s3 = load(os.path.join(data_dir, f'C_{n}_evaluated.json'))
        s4 = load(os.path.join(data_dir, f'C_{n}_coboundary.json'))

        gamma  = extract_gamma(s3)
        delta_f = extract_delta_f(s4)
        basis_all = s1['basis']['even'] + s1['basis']['odd']

        # ── Part A: proportionality check with δf_0 ──────────────────────
        cmp = compare_gamma_df(gamma, delta_f, basis_all)
        print(f'  Proportionality to δf_0 (index-paired, φ=1):')
        print(f'    Status   : {cmp["status"]}')
        if cmp['scalar']:
            print(f'    Scalar c : γ = {cmp["scalar"]} · δf_0')
        if cmp['discrepancies']:
            nd = len(cmp['discrepancies'])
            print(f'    Discrepancies: {nd}')
            for disc in cmp['discrepancies'][:4]:
                X, Y, Z = disc['key']
                print(f'      ({X},{Y},{Z}): γ={disc["gamma"]},  c·δf={disc.get("c_times_df","?")}')
            if nd > 4:
                print(f'      ... {nd} total')

        # ── Part B: general triviality (full linear system) ───────────────
        print(f'  General triviality (solve δf = γ over Q):')
        res = solve_triviality(s1, s3)
        print(f'    Equations  : {res["n_equations"]}')
        print(f'    Unknowns   : {res["n_unknowns"]}')
        print(f'    Rank(A)    : {res["rank"]}')
        print(f'    Free params: {res["degrees_of_freedom"]}')
        verdict = 'TRIVIAL' if res['is_trivial'] else 'NON-TRIVIAL'
        print(f'    Verdict    : {verdict}')
        if res['is_trivial']:
            nz = res['solution_nonzero']
            print(f'    Solution (non-zero φ): {len(nz)} entries')
            for k, v in sorted(nz.items())[:6]:
                print(f'      {k} = {v}')
            if len(nz) > 6:
                print(f'      ... {len(nz)} total')
        else:
            print(f'    Inconsistent equations: {res["n_inconsistencies"]}')
            for inc in res['inconsistencies'][:4]:
                X, Y, Z = inc['key']
                print(f'      ({X},{Y},{Z}): rhs={inc["rhs"]}  (γ={inc["gamma"]})')

    print('\n' + '=' * 72)

if __name__ == '__main__':
    main()
