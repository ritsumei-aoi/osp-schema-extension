"""
Compute triviality conditions for inhomogeneous deformations of C(n+1) = osp(2|2n).

Uses a truncated Fock-space matrix representation with large enough cutoff.
"""

import numpy as np
from itertools import product as iterproduct
import json


def build_fock_space(n_bos, n_max):
    """Build oscillator matrices on truncated Fock space |n_f, n_b1, ..., n_b_nbos>."""
    dim_bos = n_max ** n_bos
    dim_total = 2 * dim_bos

    def state_index(n_f, n_b_tuple):
        bos_idx = 0
        for k in range(n_bos):
            bos_idx = bos_idx * n_max + n_b_tuple[k]
        return n_f * dim_bos + bos_idx

    def bos_tuple_from_idx(idx):
        t = []
        for k in range(n_bos - 1, -1, -1):
            t.append(idx % n_max)
            idx //= n_max
        return tuple(reversed(t))

    a_plus = np.zeros((dim_total, dim_total))
    a_minus = np.zeros((dim_total, dim_total))

    for n_f in [0, 1]:
        for bos_idx in range(dim_bos):
            n_b = bos_tuple_from_idx(bos_idx)
            src = state_index(n_f, n_b)
            if n_f == 0:
                tgt = state_index(1, n_b)
                a_plus[tgt, src] = 1.0
            if n_f == 1:
                tgt = state_index(0, n_b)
                a_minus[tgt, src] = 1.0

    b_plus = []
    b_minus = []
    for j in range(n_bos):
        bp = np.zeros((dim_total, dim_total))
        bm = np.zeros((dim_total, dim_total))
        for n_f in [0, 1]:
            for bos_idx in range(dim_bos):
                n_b = list(bos_tuple_from_idx(bos_idx))
                src = state_index(n_f, tuple(n_b))
                # b+ with sqrt normalization
                if n_b[j] + 1 < n_max:
                    n_b2 = list(n_b); n_b2[j] += 1
                    tgt = state_index(n_f, tuple(n_b2))
                    bp[tgt, src] = np.sqrt(n_b[j] + 1)
                # b- with sqrt normalization
                if n_b[j] > 0:
                    nj = n_b[j]
                    n_b2 = list(n_b); n_b2[j] -= 1
                    tgt = state_index(n_f, tuple(n_b2))
                    bm[tgt, src] = np.sqrt(nj)
        b_plus.append(bp)
        b_minus.append(bm)

    return {
        'a_plus': a_plus, 'a_minus': a_minus,
        'b_plus': b_plus, 'b_minus': b_minus,
        'dim': dim_total, 'identity': np.eye(dim_total)
    }


def super_bracket(A, pA, B, pB):
    sign = (-1) ** (pA * pB)
    return A @ B - sign * B @ A


def build_generators(ap, am, bp_list, bm_list, I, n):
    """Build generators of C(n+1). Returns list of (name, matrix, parity)."""
    generators = []

    # N_f (so(2) generator)
    N_f = ap @ am
    generators.append(('N_f', N_f, 0))

    # H_1 = a+a- + b_1+b_1-
    H1 = N_f + bp_list[0] @ bm_list[0]
    generators.append(('H_1', H1, 0))

    # H_k for k=2,...,n
    for k in range(1, n):
        Hk = bp_list[k-1] @ bm_list[k-1] - bp_list[k] @ bm_list[k]
        generators.append((f'H_{k+1}', Hk, 0))

    # H_{n+1} = -b_n+b_n- - 1/2
    Hn1 = -bp_list[n-1] @ bm_list[n-1] - 0.5 * I
    generators.append((f'H_{n+1}', Hn1, 0))

    # Even root generators
    for k in range(n):
        for l in range(k+1, n):
            generators.append((f'E_d{k+1}+d{l+1}', bp_list[k] @ bp_list[l], 0))
            generators.append((f'E_-d{k+1}-d{l+1}', bm_list[k] @ bm_list[l], 0))
            generators.append((f'E_d{k+1}-d{l+1}', bp_list[k] @ bm_list[l], 0))
            generators.append((f'E_-d{k+1}+d{l+1}', bp_list[l] @ bm_list[k], 0))
        generators.append((f'E_2d{k+1}', 0.5 * bp_list[k] @ bp_list[k], 0))
        generators.append((f'E_-2d{k+1}', 0.5 * bm_list[k] @ bm_list[k], 0))

    # Odd root generators
    for k in range(n):
        generators.append((f'E_e+d{k+1}', ap @ bp_list[k], 1))
        generators.append((f'E_e-d{k+1}', ap @ bm_list[k], 1))
        generators.append((f'E_-e+d{k+1}', am @ bp_list[k], 1))
        generators.append((f'E_-e-d{k+1}', am @ bm_list[k], 1))

    return generators


def select_independent(generators, tol=1e-8):
    """Select a maximal linearly independent subset of generators."""
    mats = [g[1] for g in generators]
    n = len(mats)
    dim = mats[0].shape[0]

    # Also include identity for augmented decomposition
    vecs = np.column_stack([m.flatten() for m in mats])

    selected = []
    current_rank = 0
    for idx in range(n):
        test = vecs[:, selected + [idx]] if selected else vecs[:, [idx]]
        r = np.linalg.matrix_rank(test, tol=tol)
        if r > current_rank:
            selected.append(idx)
            current_rank = r

    return [generators[i] for i in selected], selected


def decompose_in_basis(mat, basis_mats, identity, tol=1e-8):
    """Decompose mat = sum c_k basis_mats[k] + scalar * identity. Return coefficients (exclude scalar)."""
    n_basis = len(basis_mats)
    dim = mat.shape[0]

    # Build augmented matrix [basis | identity]
    cols = [m.flatten() for m in basis_mats] + [identity.flatten()]
    A = np.column_stack(cols)
    b = mat.flatten()

    coeffs, _, _, _ = np.linalg.lstsq(A, b, rcond=None)

    # Verify
    reconstructed = A @ coeffs
    err = np.max(np.abs(reconstructed - b))

    return coeffs[:n_basis], coeffs[n_basis], err


def compute_structure_constants(generators, I, tol=1e-8):
    """Compute structure constants [Z_i, Z_j] = sum_k c^k_{ij} Z_k (mod scalar)."""
    n_gen = len(generators)
    names = [g[0] for g in generators]
    mats = [g[1] for g in generators]
    parities = [g[2] for g in generators]

    sc = {}
    for i in range(n_gen):
        for j in range(i, n_gen):
            bracket = super_bracket(mats[i], parities[i], mats[j], parities[j])
            coeffs, scalar, err = decompose_in_basis(bracket, mats, I, tol)

            if err > 0.01:
                print(f"  WARNING: decomposition error {err:.2e} for [{names[i]}, {names[j]}]")

            d = {}
            for k in range(n_gen):
                c = round(coeffs[k] * 2) / 2  # round to nearest half-integer
                if abs(c) > tol:
                    d[k] = c

            sc[(i, j)] = d
            # Super-antisymmetry: [Y, X] = -(-1)^{pX*pY} [X, Y]
            sign = -((-1) ** (parities[i] * parities[j]))
            sc[(j, i)] = {k: sign * v for k, v in d.items()}

    return sc


def compute_gamma_numerical(ops, generators, n, tol=1e-6):
    """
    Compute gamma_gb via finite-difference perturbation.

    For gb_{sigma,j,s}, the deformation is [b_j^s, a^sigma] = -gb * kappa.
    We realize this by replacing b_j^s -> b_j^s + eps * a^{-sigma}.
    Then [b_j^s + eps*a^{-sigma}, a^sigma] = eps * {a^{-sigma}, a^sigma} = eps * I.

    The sign convention: the deformed relation is [b,a] = -gb*kappa,
    so our perturbation gives gb -> -eps (the extra factor is handled by sign).
    """
    ap, am = ops['a_plus'], ops['a_minus']
    bp, bm = ops['b_plus'], ops['b_minus']
    I = ops['identity']

    n_gen = len(generators)
    names = [g[0] for g in generators]
    mats = [g[1] for g in generators]
    parities = [g[2] for g in generators]

    gb_params = []
    for sigma in ['+', '-']:
        for j in range(1, n+1):
            for s in ['+', '-']:
                gb_params.append(f'gb_{sigma},{j},{s}')

    eps = 1e-5
    gamma_components = {}

    for gb_name in gb_params:
        parts = gb_name.split('_')[1]
        sigma_str, j_str, s_str = parts.split(',')
        j_idx = int(j_str) - 1

        a_neg_sigma = am if sigma_str == '+' else ap

        bp_def = [m.copy() for m in bp]
        bm_def = [m.copy() for m in bm]
        if s_str == '+':
            bp_def[j_idx] = bp[j_idx] + eps * a_neg_sigma
        else:
            bm_def[j_idx] = bm[j_idx] + eps * a_neg_sigma

        gens_def = build_generators(ap, am, bp_def, bm_def, I, n)

        gamma_comp = {}
        for i in range(n_gen):
            for j2 in range(n_gen):
                bracket_def = super_bracket(gens_def[i][1], parities[i], gens_def[j2][1], parities[j2])
                bracket_orig = super_bracket(mats[i], parities[i], mats[j2], parities[j2])
                correction = (bracket_def - bracket_orig) / eps

                coeffs, scalar, err = decompose_in_basis(correction, mats, I, tol=0.01)

                nonzero = {}
                for k in range(n_gen):
                    c = round(coeffs[k] * 2) / 2
                    if abs(c) > tol:
                        nonzero[k] = c

                if nonzero:
                    gamma_comp[(i, j2)] = nonzero

        gamma_components[gb_name] = gamma_comp

    return gamma_components, gb_params


def compute_coboundary_matrix(n_gen, parities, structure_constants):
    """
    Build coboundary matrix A where A @ phi = gamma_vector.

    (delta f)(Z_i, Z_j) = (-1)^{p_i} [Z_i, f(Z_j)] - (-1)^{(p_i+1)*p_j} [Z_j, f(Z_i)] - f([Z_i,Z_j])

    f is odd: phi_{a,b} nonzero only when p(Z_a) != p(Z_b).
    """
    phi_indices = [(a, b) for a in range(n_gen) for b in range(n_gen) if parities[a] != parities[b]]
    n_phi = len(phi_indices)

    eq_indices = [(i, j, k) for i in range(n_gen) for j in range(i+1, n_gen) for k in range(n_gen)]
    n_eq = len(eq_indices)

    def get_sc(i, j, k):
        return structure_constants.get((i, j), {}).get(k, 0.0)

    A = np.zeros((n_eq, n_phi))

    for eq_row, (i, j, k) in enumerate(eq_indices):
        pi, pj = parities[i], parities[j]
        for phi_col, (a, b) in enumerate(phi_indices):
            val = 0.0
            # Term 1: (-1)^{pi} * c^k_{i,a} * delta(b,j)
            if b == j:
                val += ((-1)**pi) * get_sc(i, a, k)
            # Term 2: -(-1)^{(pi+1)*pj} * c^k_{j,a} * delta(b,i)
            if b == i:
                val -= ((-1)**((pi+1)*pj)) * get_sc(j, a, k)
            # Term 3: -c^b_{i,j} * delta(a,k)
            if a == k:
                val -= get_sc(i, j, b)
            A[eq_row, phi_col] = val

    return A, phi_indices, eq_indices


def solve_triviality(gamma_components, gb_params, A_cob, phi_indices, eq_indices,
                     n_gen, parities, names, tol=1e-4):
    """Determine which gb configurations are trivial (gamma = delta f)."""
    n_eq = len(eq_indices)
    n_phi = len(phi_indices)
    n_gb = len(gb_params)

    B = np.zeros((n_eq, n_gb))
    for gb_idx, gb_name in enumerate(gb_params):
        gc = gamma_components[gb_name]
        for eq_row, (i, j, k) in enumerate(eq_indices):
            if (i, j) in gc:
                B[eq_row, gb_idx] = gc[(i, j)].get(k, 0.0)

    # gamma = B @ gb, coboundary = A @ phi
    # Need B @ gb in Image(A)
    U, S, Vt = np.linalg.svd(A_cob, full_matrices=True)
    rank_A = np.sum(S > tol)
    P_A = U[:, :rank_A] @ U[:, :rank_A].T

    constraint = (np.eye(n_eq) - P_A) @ B

    U2, S2, Vt2 = np.linalg.svd(constraint, full_matrices=True)
    n_constraints = np.sum(np.abs(S2) > tol)

    print(f"\n  gb parameters: {n_gb}")
    print(f"  Coboundary rank: {rank_A} / {n_eq} eqs, {n_phi} phi-params")
    print(f"  Constraints on gb: {n_constraints}")
    print(f"  Trivial deformation space dim: {n_gb - n_constraints}")

    if n_constraints == n_gb:
        conclusion = "ONLY gb=0 is trivial"
    elif n_constraints == 0:
        conclusion = "ALL deformations are trivial"
    else:
        conclusion = f"{n_gb - n_constraints}-dim family of trivial deformations"
    print(f"  => {conclusion}")

    # Show constraint details
    if 0 < n_constraints < n_gb:
        print(f"\n  Trivial subspace basis vectors:")
        trivial_space = Vt2[n_constraints:, :]
        for row_idx in range(trivial_space.shape[0]):
            v = trivial_space[row_idx]
            terms = [f"{v[i]:+.3f}*{gb_params[i]}" for i in range(n_gb) if abs(v[i]) > tol]
            print(f"    v{row_idx}: {' '.join(terms)}")

    return {
        'n_gb': n_gb, 'rank_A': int(rank_A),
        'n_constraints': int(n_constraints),
        'dim_trivial': int(n_gb - n_constraints),
        'conclusion': conclusion,
        'gb_params': gb_params,
        'B_matrix': B.tolist(),
    }


def analyze_cn1(n, n_max=10):
    """Full analysis for C(n+1) = osp(2|2n)."""
    print(f"\n{'='*60}")
    print(f"C({n+1}) = osp(2|{2*n}), n={n}")
    print(f"{'='*60}")

    exp_even = 2*n*n + n + 1
    exp_odd = 4*n
    exp_total = exp_even + exp_odd
    print(f"  Expected: even={exp_even}, odd={exp_odd}, total={exp_total}")

    ops = build_fock_space(n, n_max)
    print(f"  Fock dim: {ops['dim']} (n_max={n_max})")

    ap, am = ops['a_plus'], ops['a_minus']
    bp, bm = ops['b_plus'], ops['b_minus']
    I = ops['identity']

    generators = build_generators(ap, am, bp, bm, I, n)
    generators, selected = select_independent(generators)
    n_gen = len(generators)
    n_even = sum(1 for g in generators if g[2] == 0)
    n_odd = sum(1 for g in generators if g[2] == 1)
    print(f"  Independent generators: {n_gen} ({n_even} even, {n_odd} odd)")
    names = [g[0] for g in generators]
    parities = [g[2] for g in generators]
    mats = [g[1] for g in generators]
    print(f"  Names: {names}")

    if n_gen != exp_total:
        print(f"  WARNING: expected {exp_total}, got {n_gen}")

    print("\n  Computing structure constants...")
    sc = compute_structure_constants(generators, I)

    # Print nonzero structure constants
    print("  Nonzero brackets:")
    for i in range(n_gen):
        for j in range(i+1, n_gen):
            if sc[(i,j)]:
                terms = [f"{v:+g}*{names[k]}" for k, v in sorted(sc[(i,j)].items())]
                print(f"    [{names[i]}, {names[j]}] = {' '.join(terms)}")

    # Verify Jacobi (spot check)
    import random; random.seed(42)
    max_jac_err = 0
    for _ in range(min(200, n_gen**3)):
        i, j, k = random.choices(range(n_gen), k=3)
        pi, pj, pk = parities[i], parities[j], parities[k]
        b_ij = super_bracket(mats[i], pi, mats[j], pj)
        t1 = super_bracket(b_ij, (pi+pj)%2, mats[k], pk) * ((-1)**(pi*pk))
        b_jk = super_bracket(mats[j], pj, mats[k], pk)
        t2 = super_bracket(b_jk, (pj+pk)%2, mats[i], pi) * ((-1)**(pj*pi))
        b_ki = super_bracket(mats[k], pk, mats[i], pi)
        t3 = super_bracket(b_ki, (pk+pi)%2, mats[j], pj) * ((-1)**(pk*pj))
        err = np.max(np.abs(t1 + t2 + t3))
        max_jac_err = max(max_jac_err, err)
    print(f"\n  Jacobi max error: {max_jac_err:.2e}")

    print("\n  Computing gamma_gb...")
    gamma_components, gb_params = compute_gamma_numerical(ops, generators, n)

    for gb_name, gc in gamma_components.items():
        n_nz = sum(len(v) for v in gc.values())
        print(f"    {gb_name}: {n_nz} nonzero components")

    print("\n  Computing coboundary matrix...")
    A_cob, phi_indices, eq_indices = compute_coboundary_matrix(n_gen, parities, sc)
    print(f"  Shape: {A_cob.shape}, phi params: {len(phi_indices)}")

    print("\n  Solving triviality...")
    result = solve_triviality(gamma_components, gb_params, A_cob, phi_indices, eq_indices,
                              n_gen, parities, names)

    return result, generators, sc, gamma_components, gb_params


def main():
    all_results = {}

    for n in [1, 2, 3]:
        n_max = 8 if n <= 2 else 6
        result, gens, sc, gamma, gb_params = analyze_cn1(n, n_max)
        all_results[f'C({n+1})'] = result

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for key, r in all_results.items():
        print(f"\n{key}: {r['conclusion']}")
        print(f"  gb params: {r['n_gb']}, constraints: {r['n_constraints']}, "
              f"trivial dim: {r['dim_trivial']}")

    output = {
        'metadata': {
            'algebra': 'C(n+1) = osp(2|2n)',
            'problem': 'triviality of inhomogeneous gb-deformations',
            'method': 'Fock-space matrix representation + finite-difference gamma + coboundary analysis',
        },
        'results': {
            key: {
                'n_gb_params': r['n_gb'],
                'gb_param_names': r['gb_params'],
                'coboundary_rank': r['rank_A'],
                'n_constraints': r['n_constraints'],
                'dim_trivial': r['dim_trivial'],
                'conclusion': r['conclusion'],
            }
            for key, r in all_results.items()
        }
    }

    with open('verification/triviality_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    print("\nSaved to verification/triviality_results.json")

    return all_results


if __name__ == '__main__':
    main()
