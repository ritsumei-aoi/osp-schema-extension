#!/usr/bin/env python3
"""
Algebraic computation of triviality conditions for C(n+1) = osp(2|2n)
inhomogeneous deformations.

Uses exact symbolic oscillator algebra (no Fock space truncation).
"""

import numpy as np
from fractions import Fraction
from itertools import product as iterproduct
import json


# --- Oscillator algebra utilities ---

def osc_parity(label):
    return 1 if label.startswith('a') else 0


def osc_normal_order_key(label):
    if label == 'a+': return (0, 0, 0)
    if label == 'a-': return (0, 0, 1)
    j = int(label[1:-1])
    s = 0 if label[-1] == '+' else 1
    return (1, j, s)


def osc_supercommutator(X, Y):
    pX, pY = osc_parity(X), osc_parity(Y)
    if pX == 1 and pY == 1:
        if (X == 'a+' and Y == 'a-') or (X == 'a-' and Y == 'a+'):
            return Fraction(1)
        return Fraction(0)
    if pX == 0 and pY == 0:
        jX, sX = X[1:-1], X[-1]
        jY, sY = Y[1:-1], Y[-1]
        if jX != jY: return Fraction(0)
        if sX == '-' and sY == '+': return Fraction(1)
        if sX == '+' and sY == '-': return Fraction(-1)
        return Fraction(0)
    return Fraction(0)


def normalize_bilinear(X, Y):
    """Put X*Y in normal order. Returns (coeff, osc1, osc2, scalar)."""
    kX, kY = osc_normal_order_key(X), osc_normal_order_key(Y)
    if kX <= kY:
        return (Fraction(1), X, Y, Fraction(0))
    pX, pY = osc_parity(X), osc_parity(Y)
    if X == Y and pX == 1:
        return (Fraction(0), X, Y, Fraction(0))
    sign = Fraction((-1) ** (pX * pY))
    comm = osc_supercommutator(X, Y)
    return (sign, Y, X, comm)


# --- Generator definitions ---

def get_all_bilinears(n):
    """Get all possible bilinear labels in normal order."""
    oscs = ['a+', 'a-']
    for k in range(1, n + 1):
        oscs.extend([f'b{k}+', f'b{k}-'])
    bilinears = []
    for i, o1 in enumerate(oscs):
        for j, o2 in enumerate(oscs):
            if osc_normal_order_key(o1) <= osc_normal_order_key(o2):
                if osc_parity(o1) == 1 and o1 == o2:
                    continue  # fermionic squared = 0
                bilinears.append((o1, o2))
    return bilinears


def normalize_gen_decomp(raw_decomp):
    """Normalize all bilinears in a generator decomposition."""
    result = []
    for c, o1, o2 in raw_decomp:
        nc, no1, no2, sc = normalize_bilinear(o1, o2)
        if nc != Fraction(0):
            result.append((c * nc, no1, no2))
    # Combine duplicates
    combined = {}
    for c, o1, o2 in result:
        key = (o1, o2)
        combined[key] = combined.get(key, Fraction(0)) + c
    return [(c, o1, o2) for (o1, o2), c in combined.items() if c != Fraction(0)]


def get_generators(n):
    """Return list of (label, decomposition, parity)."""
    gens = []
    raw = []
    raw.append(('H_1', [(Fraction(1), 'a+', 'a-'), (Fraction(1), 'b1+', 'b1-')], 0))
    for k in range(2, n + 1):
        raw.append((f'H_{k}',
                     [(Fraction(1), f'b{k-1}+', f'b{k-1}-'),
                      (Fraction(-1), f'b{k}+', f'b{k}-')], 0))
    raw.append((f'H_{n+1}', [(Fraction(-1), f'b{n}+', f'b{n}-')], 0))
    for k in range(1, n + 1):
        raw.append((f'E_2d{k}', [(Fraction(1, 2), f'b{k}+', f'b{k}+')], 0))
    for k in range(1, n + 1):
        raw.append((f'E_-2d{k}', [(Fraction(1, 2), f'b{k}-', f'b{k}-')], 0))
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k != l:
                raw.append((f'E_d{k}-d{l}', [(Fraction(1), f'b{k}+', f'b{l}-')], 0))
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            raw.append((f'E_d{k}+d{l}', [(Fraction(1), f'b{k}+', f'b{l}+')], 0))
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            raw.append((f'E_-d{k}-d{l}', [(Fraction(1), f'b{k}-', f'b{l}-')], 0))
    for k in range(1, n + 1):
        raw.append((f'E_e+d{k}', [(Fraction(1), 'a+', f'b{k}+')], 1))
    for k in range(1, n + 1):
        raw.append((f'E_e-d{k}', [(Fraction(1), 'a+', f'b{k}-')], 1))
    for k in range(1, n + 1):
        raw.append((f'E_-e+d{k}', [(Fraction(1), 'a-', f'b{k}+')], 1))
    for k in range(1, n + 1):
        raw.append((f'E_-e-d{k}', [(Fraction(1), 'a-', f'b{k}-')], 1))

    for label, decomp, p in raw:
        gens.append((label, normalize_gen_decomp(decomp), p))
    return gens


def build_design_matrix(n, gens):
    """Build design matrix: rows = bilinears, columns = generators.
    D[bilinear_idx, gen_idx] = coefficient of that bilinear in that generator.
    """
    bilinears = get_all_bilinears(n)
    bil_map = {b: i for i, b in enumerate(bilinears)}
    num_bil = len(bilinears)
    num_gen = len(gens)

    D = np.zeros((num_bil, num_gen))
    for g_idx, (label, decomp, p) in enumerate(gens):
        for c, o1, o2 in decomp:
            b_idx = bil_map[(o1, o2)]
            D[b_idx, g_idx] = float(c)

    return D, bilinears, bil_map


def decompose_in_basis(bilinear_vec, D, tol=1e-10):
    """Express a bilinear vector as a linear combination of generators.
    Returns (gen_coeffs_array, scalar_residual).
    """
    coeffs, residuals, rank, sv = np.linalg.lstsq(D, bilinear_vec, rcond=None)
    reconstructed = D @ coeffs
    residual = np.max(np.abs(reconstructed - bilinear_vec))
    coeffs[np.abs(coeffs) < tol] = 0
    return coeffs, residual


# --- Bracket computation ---

def bracket_of_bilinears(c1, A, B, c2, C, D):
    """Compute [c1*AB, c2*CD] using Leibniz expansion.
    Returns list of (coeff, osc1, osc2) in normal order, plus scalar.
    """
    pA, pB, pC, pD = osc_parity(A), osc_parity(B), osc_parity(C), osc_parity(D)
    coeff = c1 * c2
    terms = []
    total_scalar = Fraction(0)

    for (contraction_fn, result_pair, sign_exp) in [
        ((B, C), (A, D), 0),
        ((B, D), (A, C), pB * pC),
        ((A, C), (D, B), pB * (pC + pD)),
        ((A, D), (C, B), pB * (pC + pD) + pA * pC),
    ]:
        comm = osc_supercommutator(*contraction_fn)
        if comm != Fraction(0):
            sign = Fraction((-1) ** sign_exp)
            X, Y = result_pair
            nc, o1, o2, sc = normalize_bilinear(X, Y)
            if nc != Fraction(0):
                terms.append((coeff * sign * comm * nc, o1, o2))
            total_scalar += coeff * sign * comm * sc

    return terms, total_scalar


def deformed_supercommutator(X, Y, b_label, a_label):
    """Kappa-coefficient of the deformed [X, Y]."""
    if X == b_label and Y == a_label:
        return Fraction(-1)
    if X == a_label and Y == b_label:
        return Fraction(1)
    return Fraction(0)


def gamma_bilinear(c1, A, B, c2, C, D, b_label, a_label):
    """Kappa-correction to [c1*AB, c2*CD] from [b,a]=-kappa."""
    pA, pB, pC, pD = osc_parity(A), osc_parity(B), osc_parity(C), osc_parity(D)
    coeff = c1 * c2
    terms = []
    total_scalar = Fraction(0)

    for (contraction_pair, result_pair, sign_exp) in [
        ((B, C), (A, D), 0),
        ((B, D), (A, C), pB * pC),
        ((A, C), (D, B), pB * (pC + pD)),
        ((A, D), (C, B), pB * (pC + pD) + pA * pC),
    ]:
        comm = deformed_supercommutator(*contraction_pair, b_label, a_label)
        if comm != Fraction(0):
            sign = Fraction((-1) ** sign_exp)
            X, Y = result_pair
            nc, o1, o2, sc = normalize_bilinear(X, Y)
            if nc != Fraction(0):
                terms.append((coeff * sign * comm * nc, o1, o2))
            total_scalar += coeff * sign * comm * sc

    return terms, total_scalar


def compute_bracket_vec(gen_i, gen_j, bil_map, num_bil):
    """Compute [Z_i, Z_j] as a bilinear vector + scalar."""
    _, decomp_i, _ = gen_i
    _, decomp_j, _ = gen_j
    vec = np.zeros(num_bil)
    total_scalar = Fraction(0)

    for c1, A, B in decomp_i:
        for c2, C, D in decomp_j:
            terms, sc = bracket_of_bilinears(c1, A, B, c2, C, D)
            total_scalar += sc
            for c, o1, o2 in terms:
                if (o1, o2) in bil_map:
                    vec[bil_map[(o1, o2)]] += float(c)

    return vec, float(total_scalar)


def compute_gamma_vec(gen_i, gen_j, b_label, a_label, bil_map, num_bil):
    """Compute gamma(Z_i, Z_j) as a bilinear vector + scalar."""
    _, decomp_i, _ = gen_i
    _, decomp_j, _ = gen_j
    vec = np.zeros(num_bil)
    total_scalar = Fraction(0)

    for c1, A, B in decomp_i:
        for c2, C, D in decomp_j:
            terms, sc = gamma_bilinear(c1, A, B, c2, C, D, b_label, a_label)
            total_scalar += sc
            for c, o1, o2 in terms:
                if (o1, o2) in bil_map:
                    vec[bil_map[(o1, o2)]] += float(c)

    return vec, float(total_scalar)


# --- Main analysis ---

def run_analysis(n):
    print(f"\n{'='*60}")
    print(f"  C({n+1}) = osp(2|{2*n})")
    print(f"{'='*60}")

    gens = get_generators(n)
    num = len(gens)
    expected = 2 * n * n + 5 * n + 1
    print(f"  Dimension: {num} (expected {expected})")
    assert num == expected

    D, bilinears, bil_map = build_design_matrix(n, gens)
    num_bil = len(bilinears)
    print(f"  Bilinear space dimension: {num_bil}")
    print(f"  Design matrix rank: {np.linalg.matrix_rank(D)}")

    # Compute structure constants
    print("  Computing structure constants...")
    struct = np.zeros((num, num, num))
    scalar_bracket = np.zeros((num, num))

    for i in range(num):
        for j in range(num):
            bvec, sc = compute_bracket_vec(gens[i], gens[j], bil_map, num_bil)
            scalar_bracket[i, j] = sc
            if np.max(np.abs(bvec)) > 1e-15:
                coeffs, res = decompose_in_basis(bvec, D)
                if res > 1e-8:
                    print(f"  WARNING: [{gens[i][0]},{gens[j][0]}] residual={res:.2e}")
                struct[i, j, :] = coeffs

    struct[np.abs(struct) < 1e-10] = 0

    # Verify antisymmetry
    parities = [g[2] for g in gens]
    errors = 0
    for i in range(num):
        for j in range(i + 1, num):
            sign = (-1) ** (parities[i] * parities[j])
            for k in range(num):
                diff = struct[i, j, k] + sign * struct[j, i, k]
                if abs(diff) > 1e-8:
                    errors += 1
    print(f"  Antisymmetry violations: {errors}")

    # Print non-trivial brackets
    print("  Non-trivial brackets (i <= j):")
    bracket_count = 0
    for i in range(num):
        for j in range(i, num):
            nonzero = [(k, struct[i, j, k]) for k in range(num) if abs(struct[i, j, k]) > 1e-10]
            if nonzero:
                terms = " + ".join(f"{Fraction(v).limit_denominator(100)}*{gens[k][0]}" for k, v in nonzero)
                sc = scalar_bracket[i, j]
                sc_str = f" + {Fraction(sc).limit_denominator(100)}" if abs(sc) > 1e-10 else ""
                print(f"    [{gens[i][0]}, {gens[j][0]}] = {terms}{sc_str}")
                bracket_count += 1
    print(f"  Total: {bracket_count}")

    # Compute gamma
    print("\n  Computing gamma...")
    gb_params = []
    for j in range(1, n + 1):
        for sigma in ['+', '-']:
            for s in ['+', '-']:
                gb_params.append((sigma, j, s))
    num_params = len(gb_params)

    gamma = np.zeros((num_params, num, num, num))
    gamma_scalar = np.zeros((num_params, num, num))

    for p_idx, (sigma, j, s) in enumerate(gb_params):
        b_label = f'b{j}{"+" if s == "+" else "-"}'
        a_label = f'a{"+" if sigma == "+" else "-"}'

        for i in range(num):
            for jj in range(num):
                gvec, gsc = compute_gamma_vec(gens[i], gens[jj], b_label, a_label, bil_map, num_bil)
                gamma_scalar[p_idx, i, jj] = gsc
                if np.max(np.abs(gvec)) > 1e-15:
                    coeffs, res = decompose_in_basis(gvec, D)
                    if res > 1e-8:
                        print(f"  WARNING: gamma residual for gb_{gb_params[p_idx]}, "
                              f"({gens[i][0]},{gens[jj][0]}): {res:.2e}")
                    gamma[p_idx, i, jj, :] = coeffs

    gamma[np.abs(gamma) < 1e-10] = 0

    # Print gamma
    for p_idx in range(num_params):
        print(f"\n  gamma for gb_{gb_params[p_idx]}:")
        for i in range(num):
            for jj in range(i, num):
                nonzero = [(k, gamma[p_idx, i, jj, k]) for k in range(num) if abs(gamma[p_idx, i, jj, k]) > 1e-10]
                if nonzero:
                    terms = " + ".join(f"{Fraction(v).limit_denominator(100)}*{gens[k][0]}" for k, v in nonzero)
                    sc = gamma_scalar[p_idx, i, jj]
                    sc_str = f" + sc({Fraction(sc).limit_denominator(100)})" if abs(sc) > 1e-10 else ""
                    print(f"    gamma({gens[i][0]}, {gens[jj][0]}) = {terms}{sc_str}")

    # Solve triviality
    print("\n  Solving triviality system...")
    result = solve_triviality(n, gens, struct, gamma, gamma_scalar, gb_params)

    print(f"\n  === RESULTS for C({n+1}) ===")
    print(f"  ALL trivial: {result['all_trivial']}")
    print(f"  rank(delta) = {result['rank_A']}, rank(delta|gamma) = {result['rank_combined']}")
    print(f"  #phi = {result['num_phi']}, #equations = {result['num_eq']}")

    for param, info in result['individual'].items():
        status = "TRIVIAL" if info['is_trivial'] else "NON-TRIVIAL"
        print(f"    {param}: {status} (residual={info['residual']:.2e})")

    if result['constraints']:
        print(f"  Constraints for triviality ({len(result['constraints'])}):")
        for terms in result['constraints']:
            expr = " + ".join(f"{v:.6f}*gb_{p}" for v, p in terms)
            print(f"    {expr} = 0")

    return result, gens, struct, gamma, gamma_scalar, gb_params


def solve_triviality(n, gens, struct, gamma, gamma_scalar, gb_params):
    num = len(gens)
    num_params = len(gb_params)
    parities = [g[2] for g in gens]

    # f: odd linear map, phi[j][m] nonzero when p(m) != p(j)
    phi_indices = []
    for j in range(num):
        for m in range(num):
            if parities[m] != parities[j]:
                phi_indices.append((j, m))
    num_phi = len(phi_indices)
    phi_map = {(j, m): idx for idx, (j, m) in enumerate(phi_indices)}

    # Build delta_f equations: for each (i, j, k):
    # (delta f)_{ij}^k = (-1)^{pi} sum_m C[i,m,k]*phi[j,m]
    #                  - (-1)^{(pi+1)*pj} sum_m C[j,m,k]*phi[i,m]
    #                  - sum_l C[i,j,l]*phi[l,k]
    rows = []
    rhs_vecs = [[] for _ in range(num_params)]

    for i in range(num):
        for j in range(i, num):
            pi, pj = parities[i], parities[j]
            for k in range(num):
                row = np.zeros(num_phi)

                for m in range(num):
                    if (j, m) in phi_map and abs(struct[i, m, k]) > 1e-15:
                        row[phi_map[(j, m)]] += ((-1) ** pi) * struct[i, m, k]

                for m in range(num):
                    if (i, m) in phi_map and abs(struct[j, m, k]) > 1e-15:
                        row[phi_map[(i, m)]] -= ((-1) ** ((pi + 1) * pj)) * struct[j, m, k]

                for l in range(num):
                    if (l, k) in phi_map and abs(struct[i, j, l]) > 1e-15:
                        row[phi_map[(l, k)]] -= struct[i, j, l]

                # Check if this equation is nontrivial
                has_lhs = np.any(np.abs(row) > 1e-15)
                has_rhs = any(abs(gamma[p, i, j, k]) > 1e-15 for p in range(num_params))

                if has_lhs or has_rhs:
                    rows.append(row)
                    for p in range(num_params):
                        rhs_vecs[p].append(gamma[p, i, j, k])

    A = np.array(rows)
    num_eq = A.shape[0]
    print(f"  System: {num_eq} equations, {num_phi} unknowns")

    rank_A = np.linalg.matrix_rank(A, tol=1e-8)

    # Check individual parameters
    results_indiv = {}
    for p in range(num_params):
        b = np.array(rhs_vecs[p])
        phi_sol, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
        res = np.max(np.abs(A @ phi_sol - b))
        label = f"gb_{gb_params[p]}"
        results_indiv[label] = {'is_trivial': res < 1e-6, 'residual': float(res)}

    # Check all simultaneously
    gamma_cols = np.array([rhs_vecs[p] for p in range(num_params)]).T
    combined = np.hstack([A, gamma_cols])
    rank_combined = np.linalg.matrix_rank(combined, tol=1e-8)
    all_trivial = (rank_combined == rank_A)

    # Find constraints
    constraint_terms = []
    if not all_trivial:
        U, S, Vt = np.linalg.svd(A, full_matrices=True)
        null_AT = U[:, rank_A:]
        proj = null_AT.T @ gamma_cols
        proj[np.abs(proj) < 1e-8] = 0
        nz = np.any(np.abs(proj) > 1e-8, axis=1)
        if np.any(nz):
            C_mat = proj[nz]
            Uc, Sc, Vtc = np.linalg.svd(C_mat)
            rc = np.sum(Sc > 1e-8)
            indep = Vtc[:rc]
            indep[np.abs(indep) < 1e-8] = 0
            for row in indep:
                terms = [(float(row[p]), gb_params[p]) for p in range(num_params) if abs(row[p]) > 1e-8]
                if terms:
                    constraint_terms.append(terms)

    return {
        'all_trivial': all_trivial,
        'rank_A': int(rank_A),
        'rank_combined': int(rank_combined),
        'num_phi': num_phi,
        'num_eq': num_eq,
        'individual': results_indiv,
        'constraints': constraint_terms,
    }


def build_artifacts(n, result, gens, struct, gamma, gamma_scalar, gb_params):
    num = len(gens)
    labels = [g[0] for g in gens]
    pars = [g[2] for g in gens]

    s_dict = {}
    for i in range(num):
        for j in range(num):
            for k in range(num):
                v = struct[i, j, k]
                if abs(v) > 1e-10:
                    s_dict[f"[{labels[i]},{labels[j]}]->{labels[k]}"] = str(Fraction(v).limit_denominator(100))

    g_dict = {}
    for p in range(len(gb_params)):
        for i in range(num):
            for j in range(num):
                for k in range(num):
                    v = gamma[p, i, j, k]
                    if abs(v) > 1e-10:
                        key = f"gb_{gb_params[p]}:gamma({labels[i]},{labels[j]})->{labels[k]}"
                        g_dict[key] = str(Fraction(v).limit_denominator(100))

    gs_dict = {}
    for p in range(len(gb_params)):
        for i in range(num):
            for j in range(num):
                v = gamma_scalar[p, i, j]
                if abs(v) > 1e-10:
                    key = f"gb_{gb_params[p]}:scalar({labels[i]},{labels[j]})"
                    gs_dict[key] = str(Fraction(v).limit_denominator(100))

    return {
        'algebra': f'C({n+1}) = osp(2|{2*n})',
        'n': n,
        'dimension': num,
        'even_dim': sum(1 for p in pars if p == 0),
        'odd_dim': sum(1 for p in pars if p == 1),
        'generators': labels,
        'parities': pars,
        'gb_params': [str(p) for p in gb_params],
        'triviality': {
            'all_trivial': result['all_trivial'],
            'rank_delta': result['rank_A'],
            'rank_delta_plus_gamma': result['rank_combined'],
            'individual': result['individual'],
            'constraints': [
                {str(p): float(v) for v, p in terms}
                for terms in result.get('constraints', [])
            ],
        },
        'structure_constants': s_dict,
        'gamma_cocycle': g_dict,
        'gamma_scalar_parts': gs_dict,
    }


if __name__ == '__main__':
    all_artifacts = {}
    for n_val in [1, 2, 3]:
        result, gens, struct, gamma, gamma_scalar, gb_params = run_analysis(n_val)
        artifact = build_artifacts(n_val, result, gens, struct, gamma, gamma_scalar, gb_params)
        all_artifacts[f'C({n_val+1})'] = artifact

    path = '/Users/aoi/notebook/git/thm01-R-batch/thm01-R-opus46-b07-C/verification_artifacts.json'
    with open(path, 'w') as f:
        json.dump(all_artifacts, f, indent=2, default=str)
    print(f"\nArtifacts saved to {path}")
