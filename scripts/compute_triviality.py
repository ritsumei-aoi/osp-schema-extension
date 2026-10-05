"""
Compute triviality conditions for C(n+1) = osp(2|2n) inhomogeneous deformations.

For each n=1,2,3:
1. Construct generators of C(n+1) as bilinear oscillator expressions
2. Compute structure constants [e_i, e_j] = sum c_{ij}^k e_k
3. Compute the deformation cocycle gamma_gb in the generator basis
4. Compute the coboundary operator delta_f
5. Determine when gamma_gb = delta_f (triviality conditions)
"""

import numpy as np
from fractions import Fraction
import json
import sys

def compute_triviality(n, verbose=False):
    num_osc = 2 + 2 * n  # a+, a-, b_1+, b_1-, ..., b_n+, b_n-

    def parity(i):
        return 1 if i < 2 else 0

    def bracket1(i, j):
        """Undeformed single-oscillator super-bracket [c_i, c_j]. Returns scalar."""
        if i == 0 and j == 1:
            return 1  # {a+, a-} = 1
        if i == 1 and j == 0:
            return 1  # {a-, a+} = 1
        if i >= 2 and j >= 2:
            ki, si = divmod(i - 2, 2)
            kj, sj = divmod(j - 2, 2)
            if ki == kj:
                if si == 1 and sj == 0:
                    return 1   # [b_k-, b_k+] = 1
                if si == 0 and sj == 1:
                    return -1  # [b_k+, b_k-] = -1
        return 0

    def deformation_info(i, j):
        """If [c_i, c_j] has deformation, return (gb_index, sign). Else None.
        Convention: [b_k^s, a^sigma] = -gb_{sigma,k,s} * kappa
        so [a^sigma, b_k^s] = +gb_{sigma,k,s} * kappa
        gb_index = sigma * 2n + k * 2 + s
        where sigma in {0,1}, k in {0,...,n-1}, s in {0,1}
        """
        if i >= 2 and j < 2:  # [b, a]
            k, s = divmod(i - 2, 2)
            sigma = j
            gb_idx = sigma * (2 * n) + k * 2 + s
            return (gb_idx, -1)
        if i < 2 and j >= 2:  # [a, b]
            sigma = i
            k, s = divmod(j - 2, 2)
            gb_idx = sigma * (2 * n) + k * 2 + s
            return (gb_idx, +1)
        return None

    # Build generator list
    # Each generator = list of (coeff, osc1, osc2)
    generators = []
    gen_names = []
    gen_parity = []
    gen_scalar = []  # scalar part of generator (e.g., -1/2 for H_{n+1})

    # H_1 = a+a- + b_1+b_1-
    generators.append([(1.0, 0, 1), (1.0, 2, 3)])
    gen_names.append('H_1')
    gen_parity.append(0)
    gen_scalar.append(0.0)

    # H_k = b_{k-1}+b_{k-1}- - b_k+b_k- for k=2,...,n
    for k in range(2, n + 1):
        generators.append([(1.0, 2 * (k - 1), 2 * (k - 1) + 1), (-1.0, 2 * k, 2 * k + 1)])
        gen_names.append(f'H_{k}')
        gen_parity.append(0)
        gen_scalar.append(0.0)

    # H_{n+1} = -b_n+b_n- - 1/2
    generators.append([(-1.0, 2 * n, 2 * n + 1)])
    gen_names.append(f'H_{n + 1}')
    gen_parity.append(0)
    gen_scalar.append(-0.5)

    # E_{delta_k - delta_l} = b_k+ b_l- for k != l
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k != l:
                generators.append([(1.0, 2 * k, 2 * l + 1)])
                gen_names.append(f'E_{{d{k}-d{l}}}')
                gen_parity.append(0)
                gen_scalar.append(0.0)

    # E_{delta_k + delta_l} = b_k+ b_l+ for k < l
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            generators.append([(1.0, 2 * k, 2 * l)])
            gen_names.append(f'E_{{d{k}+d{l}}}')
            gen_parity.append(0)
            gen_scalar.append(0.0)

    # E_{-delta_k - delta_l} = b_k- b_l- for k < l
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            generators.append([(1.0, 2 * k + 1, 2 * l + 1)])
            gen_names.append(f'E_{{-d{k}-d{l}}}')
            gen_parity.append(0)
            gen_scalar.append(0.0)

    # E_{2delta_k} = (b_k+)^2 / 2
    for k in range(1, n + 1):
        generators.append([(0.5, 2 * k, 2 * k)])
        gen_names.append(f'E_{{2d{k}}}')
        gen_parity.append(0)
        gen_scalar.append(0.0)

    # E_{-2delta_k} = (b_k-)^2 / 2
    for k in range(1, n + 1):
        generators.append([(0.5, 2 * k + 1, 2 * k + 1)])
        gen_names.append(f'E_{{-2d{k}}}')
        gen_parity.append(0)
        gen_scalar.append(0.0)

    # Odd generators
    # E_{eps+delta_k} = a+ b_k+
    for k in range(1, n + 1):
        generators.append([(1.0, 0, 2 * k)])
        gen_names.append(f'E_{{e+d{k}}}')
        gen_parity.append(1)
        gen_scalar.append(0.0)

    # E_{eps-delta_k} = a+ b_k-
    for k in range(1, n + 1):
        generators.append([(1.0, 0, 2 * k + 1)])
        gen_names.append(f'E_{{e-d{k}}}')
        gen_parity.append(1)
        gen_scalar.append(0.0)

    # E_{-eps+delta_k} = a- b_k+
    for k in range(1, n + 1):
        generators.append([(1.0, 1, 2 * k)])
        gen_names.append(f'E_{{-e+d{k}}}')
        gen_parity.append(1)
        gen_scalar.append(0.0)

    # E_{-eps-delta_k} = a- b_k-
    for k in range(1, n + 1):
        generators.append([(1.0, 1, 2 * k + 1)])
        gen_names.append(f'E_{{-e-d{k}}}')
        gen_parity.append(1)
        gen_scalar.append(0.0)

    dim_g = len(generators)
    expected_dim = 2 * n ** 2 + 5 * n + 1
    assert dim_g == expected_dim, f"dim={dim_g}, expected={expected_dim}"

    if verbose:
        print(f"\n=== C({n+1}) = osp(2|{2*n}), dim = {dim_g} ===")
        print(f"Even: {sum(1 for p in gen_parity if p == 0)}, Odd: {sum(1 for p in gen_parity if p == 1)}")
        for i, (name, par) in enumerate(zip(gen_names, gen_parity)):
            print(f"  e_{i} = {name} (p={par})")

    # Build monomial basis: pairs (i, j) with i <= j, excluding (0,0) and (1,1)
    monomial_list = []
    monomial_index = {}
    for i in range(num_osc):
        for j in range(i, num_osc):
            if i == j and parity(i) == 1:
                continue  # fermionic squared = 0
            monomial_list.append((i, j))
            monomial_index[(i, j)] = len(monomial_list) - 1

    num_mono = len(monomial_list)
    assert num_mono == dim_g, f"monomials={num_mono}, dim_g={dim_g}"

    # Express each generator in monomial basis + scalar
    # gen_mono[alpha, m] = coefficient of monomial m in generator alpha
    gen_mono = np.zeros((dim_g, num_mono))
    for alpha in range(dim_g):
        for coeff, i, j in generators[alpha]:
            if i > j:
                # Normal order: need to swap
                sign = (-1) ** (parity(i) * parity(j))
                scalar_add = bracket1(j, i)  # hmm, this needs careful handling
                # c_i c_j = (-1)^{p_i p_j} c_j c_i + [c_i, c_j]
                # but [c_i, c_j] is a scalar here
                # So c_i c_j = sign * c_j c_i + bracket1(i, j)
                # Wait: for super bracket, c_i c_j - (-1)^{p_i p_j} c_j c_i = [c_i, c_j]
                # So c_i c_j = (-1)^{p_i p_j} c_j c_i + [c_i, c_j]
                if j < i:
                    idx = monomial_index.get((j, i))
                    if idx is not None:
                        gen_mono[alpha, idx] += coeff * sign
                    gen_scalar[alpha] += coeff * bracket1(i, j)
            elif i == j:
                idx = monomial_index.get((i, j))
                if idx is not None:
                    gen_mono[alpha, idx] += coeff
            else:
                idx = monomial_index.get((i, j))
                if idx is not None:
                    gen_mono[alpha, idx] += coeff

    # Invert: monomial -> generator decomposition
    # gen_mono is dim_g x num_mono, and num_mono = dim_g
    # We need gen_mono_inv such that monomial = gen_mono_inv @ generator + scalar part
    gen_mono_inv = np.linalg.inv(gen_mono)

    # Verify inversion
    identity_check = gen_mono @ gen_mono_inv
    assert np.allclose(identity_check, np.eye(dim_g)), "Inversion failed"

    # Function to express a monomial c_i c_j (possibly not normal ordered) in generator basis
    def monomial_to_gen(i, j):
        """Express c_i c_j as linear combination of generators + scalar.
        Returns (gen_coeffs, scalar) where gen_coeffs is array of length dim_g.
        """
        gen_coeffs = np.zeros(dim_g)
        scalar = 0.0

        if i == j and parity(i) == 1:
            return gen_coeffs, 0.0  # fermionic squared = 0

        if i <= j:
            idx = monomial_index.get((i, j))
            if idx is not None:
                gen_coeffs = gen_mono_inv[idx, :].copy()
        else:
            # c_i c_j = (-1)^{p_i p_j} c_j c_i + [c_i, c_j]_scalar
            sign = (-1) ** (parity(i) * parity(j))
            scalar = bracket1(i, j)
            if i == j:
                idx = monomial_index.get((i, j))
            else:
                idx = monomial_index.get((j, i))
            if idx is not None:
                gen_coeffs = sign * gen_mono_inv[idx, :].copy()

        return gen_coeffs, scalar

    # Compute structure constants: [e_i, e_j] = sum_k c_{ij}^k e_k + scalar
    # Using undeformed brackets
    struct_const = np.zeros((dim_g, dim_g, dim_g))
    struct_scalar = np.zeros((dim_g, dim_g))

    for i_gen in range(dim_g):
        for j_gen in range(dim_g):
            # [e_i, e_j] = sum over term pairs
            total_gen = np.zeros(dim_g)
            total_scalar = 0.0

            for coeff_i, Ai, Bi in generators[i_gen]:
                for coeff_j, Cj, Dj in generators[j_gen]:
                    # [c_A c_B, c_C c_D] using Leibniz
                    pA, pB, pC, pD = parity(Ai), parity(Bi), parity(Cj), parity(Dj)

                    # 4 terms from Leibniz expansion
                    terms = []

                    # T1: c_A [c_B, c_C] c_D, sign = 1
                    bc = bracket1(Bi, Cj)
                    if bc != 0:
                        g, s = monomial_to_gen(Ai, Dj)
                        terms.append((bc, g, s))

                    # T2: (-1)^{pB pC} c_A c_C [c_B, c_D]
                    bd = bracket1(Bi, Dj)
                    if bd != 0:
                        sign2 = (-1) ** (pB * pC)
                        g, s = monomial_to_gen(Ai, Cj)
                        terms.append((bd * sign2, g, s))

                    # T3: (-1)^{pB(pC+pD)} [c_A, c_C] c_D c_B
                    ac = bracket1(Ai, Cj)
                    if ac != 0:
                        sign3 = (-1) ** (pB * (pC + pD))
                        g, s = monomial_to_gen(Dj, Bi)
                        terms.append((ac * sign3, g, s))

                    # T4: (-1)^{pB(pC+pD)+pA pC} c_C [c_A, c_D] c_B
                    ad = bracket1(Ai, Dj)
                    if ad != 0:
                        sign4 = (-1) ** (pB * (pC + pD) + pA * pC)
                        g, s = monomial_to_gen(Cj, Bi)
                        terms.append((ad * sign4, g, s))

                    for val, g, s in terms:
                        total_gen += coeff_i * coeff_j * val * g
                        total_scalar += coeff_i * coeff_j * val * s

            struct_const[i_gen, j_gen, :] = total_gen
            struct_scalar[i_gen, j_gen] = total_scalar

    # Verify super-antisymmetry: [e_i, e_j] = -(-1)^{pi pj} [e_j, e_i]
    for i_gen in range(dim_g):
        for j_gen in range(dim_g):
            pi, pj = gen_parity[i_gen], gen_parity[j_gen]
            sign = -(-1) ** (pi * pj)
            diff = struct_const[i_gen, j_gen] - sign * struct_const[j_gen, i_gen]
            if not np.allclose(diff, 0, atol=1e-10):
                print(f"WARNING: super-antisymmetry violated for ({gen_names[i_gen]}, {gen_names[j_gen]})")
                print(f"  [e_i, e_j] = {struct_const[i_gen, j_gen]}")
                print(f"  sign * [e_j, e_i] = {sign * struct_const[j_gen, i_gen]}")

    if verbose:
        print("\nStructure constants (non-zero):")
        for i_gen in range(dim_g):
            for j_gen in range(i_gen, dim_g):
                c = struct_const[i_gen, j_gen]
                nonzero = np.nonzero(np.abs(c) > 1e-10)[0]
                if len(nonzero) > 0:
                    terms = " + ".join(f"{c[k]:.4g}*{gen_names[k]}" for k in nonzero)
                    print(f"  [{gen_names[i_gen]}, {gen_names[j_gen]}] = {terms}")

    # Compute deformation cocycle gamma_gb
    # gamma_gb(e_i, e_j) = sum over gb parameters of gb_p * gamma_p(e_i, e_j)
    # gamma_p is the coefficient matrix for each gb parameter
    num_gb = 4 * n
    gamma_gb = np.zeros((dim_g, dim_g, dim_g, num_gb))
    gamma_scalar = np.zeros((dim_g, dim_g, num_gb))

    for i_gen in range(dim_g):
        for j_gen in range(dim_g):
            for coeff_i, Ai, Bi in generators[i_gen]:
                for coeff_j, Cj, Dj in generators[j_gen]:
                    pA, pB, pC, pD = parity(Ai), parity(Bi), parity(Cj), parity(Dj)

                    # Check each of the 4 sub-brackets for deformation
                    # T1: c_A [c_B, c_C]_def c_D
                    # kappa-coefficient sign: (-1)^{pA}
                    info = deformation_info(Bi, Cj)
                    if info is not None:
                        gb_idx, def_sign = info
                        kappa_sign = (-1) ** pA
                        g, s = monomial_to_gen(Ai, Dj)
                        gamma_gb[i_gen, j_gen, :, gb_idx] += coeff_i * coeff_j * def_sign * kappa_sign * g
                        gamma_scalar[i_gen, j_gen, gb_idx] += coeff_i * coeff_j * def_sign * kappa_sign * s

                    # T2: (-1)^{pB pC} c_A c_C [c_B, c_D]_def
                    # kappa-coefficient sign: (-1)^{pA + pC}
                    info = deformation_info(Bi, Dj)
                    if info is not None:
                        gb_idx, def_sign = info
                        total_sign = (-1) ** (pB * pC) * def_sign * (-1) ** (pA + pC)
                        g, s = monomial_to_gen(Ai, Cj)
                        gamma_gb[i_gen, j_gen, :, gb_idx] += coeff_i * coeff_j * total_sign * g
                        gamma_scalar[i_gen, j_gen, gb_idx] += coeff_i * coeff_j * total_sign * s

                    # T3: (-1)^{pB(pC+pD)} [c_A, c_C]_def c_D c_B
                    # kappa already on left, sign: 1
                    info = deformation_info(Ai, Cj)
                    if info is not None:
                        gb_idx, def_sign = info
                        total_sign = (-1) ** (pB * (pC + pD)) * def_sign
                        g, s = monomial_to_gen(Dj, Bi)
                        gamma_gb[i_gen, j_gen, :, gb_idx] += coeff_i * coeff_j * total_sign * g
                        gamma_scalar[i_gen, j_gen, gb_idx] += coeff_i * coeff_j * total_sign * s

                    # T4: (-1)^{pB(pC+pD)+pA pC} c_C [c_A, c_D]_def c_B
                    # kappa sign: (-1)^{pC}
                    info = deformation_info(Ai, Dj)
                    if info is not None:
                        gb_idx, def_sign = info
                        total_sign = (-1) ** (pB * (pC + pD) + pA * pC + pC) * def_sign
                        g, s = monomial_to_gen(Cj, Bi)
                        gamma_gb[i_gen, j_gen, :, gb_idx] += coeff_i * coeff_j * total_sign * g
                        gamma_scalar[i_gen, j_gen, gb_idx] += coeff_i * coeff_j * total_sign * s

    if verbose:
        print("\nDeformation cocycle gamma_gb (non-zero entries):")
        for i_gen in range(dim_g):
            for j_gen in range(dim_g):
                for p in range(num_gb):
                    c = gamma_gb[i_gen, j_gen, :, p]
                    nonzero = np.nonzero(np.abs(c) > 1e-10)[0]
                    if len(nonzero) > 0:
                        terms = " + ".join(f"{c[k]:.4g}*{gen_names[k]}" for k in nonzero)
                        print(f"  gamma_gb({gen_names[i_gen]}, {gen_names[j_gen]})[gb_{p}] = {terms}")

    # Build the coboundary matrix
    # (delta f)(e_i, e_j) = (-1)^{pi} sum_k phi^k_j [e_i, e_k]
    #                     - (-1)^{(pi+1)pj} sum_k phi^k_i [e_j, e_k]
    #                     - sum_l c_{ij}^l sum_k phi^k_l e_k
    #
    # f is odd: phi^k_l != 0 only if p(e_k) = p(e_l) + 1 mod 2
    #
    # Equation indexing:
    # For each (i, j, m) where m is the generator index of the output,
    # we have: gamma_gb(e_i, e_j)[m] = (delta f)(e_i, e_j)[m]

    # Free parameters of f: phi^k_l where p(e_k) != p(e_l)
    f_params = []
    f_param_index = {}
    for l in range(dim_g):
        for k in range(dim_g):
            if gen_parity[k] != gen_parity[l]:
                f_param_index[(k, l)] = len(f_params)
                f_params.append((k, l))
    num_f = len(f_params)

    # Build equations: for each independent pair (i, j) and output index m
    # gamma_gb(e_i, e_j)[m] = sum over phi of A_{ijm,phi} * phi

    # Independent pairs: i <= j for even-even / odd-odd, all (i,j) for mixed
    # Actually, using super-antisymmetry, we only need i < j for same parity,
    # and all (i, j) for i even, j odd. But for simplicity, let's use all (i, j) with i <= j
    # (with appropriate handling of the antisymmetry).

    # Actually let's just use all pairs (i, j) with i < j, plus (i, i) for odd generators
    # (since [e_i, e_i] = {e_i, e_i} for odd e_i, which can be non-zero).

    equations = []  # list of (i, j, m) for the equation gamma_gb[i,j,m] = delta_f[i,j,m]
    for i_gen in range(dim_g):
        for j_gen in range(i_gen, dim_g):
            if i_gen == j_gen and gen_parity[i_gen] == 0:
                continue  # [even, even] = 0 trivially
            for m in range(dim_g):
                equations.append((i_gen, j_gen, m))

    num_eq = len(equations)

    # Build matrix A (coboundary) and vector b (gamma_gb)
    # For each equation (i, j, m): sum_phi A[eq, phi] * phi = sum_p B[eq, p] * gb_p
    A_mat = np.zeros((num_eq, num_f))
    B_mat = np.zeros((num_eq, num_gb))

    for eq_idx, (i_gen, j_gen, m) in enumerate(equations):
        pi, pj = gen_parity[i_gen], gen_parity[j_gen]

        # Coboundary terms:
        # Term 1: (-1)^{pi} sum_k phi^k_j c_{ik}^m
        for k in range(dim_g):
            if (k, j_gen) in f_param_index:
                phi_idx = f_param_index[(k, j_gen)]
                A_mat[eq_idx, phi_idx] += (-1) ** pi * struct_const[i_gen, k, m]

        # Term 2: -(-1)^{(pi+1)pj} sum_k phi^k_i c_{jk}^m
        for k in range(dim_g):
            if (k, i_gen) in f_param_index:
                phi_idx = f_param_index[(k, i_gen)]
                A_mat[eq_idx, phi_idx] -= (-1) ** ((pi + 1) * pj) * struct_const[j_gen, k, m]

        # Term 3: -sum_l c_{ij}^l phi^m_l
        for l in range(dim_g):
            if (m, l) in f_param_index:
                phi_idx = f_param_index[(m, l)]
                A_mat[eq_idx, phi_idx] -= struct_const[i_gen, j_gen, l]

        # Gamma_gb terms:
        for p in range(num_gb):
            B_mat[eq_idx, p] = gamma_gb[i_gen, j_gen, m, p]

    # The triviality condition is: B_mat @ gb = A_mat @ phi
    # i.e., B_mat @ gb in Image(A_mat) for all gb
    # i.e., Image(B_mat) subset Image(A_mat)

    rank_A = np.linalg.matrix_rank(A_mat, tol=1e-8)
    rank_B = np.linalg.matrix_rank(B_mat, tol=1e-8)
    AB = np.hstack([A_mat, B_mat])
    rank_AB = np.linalg.matrix_rank(AB, tol=1e-8)

    print(f"\n--- Results for C({n+1}) = osp(2|{2*n}) ---")
    print(f"dim(g) = {dim_g}")
    print(f"Number of gb parameters = {num_gb}")
    print(f"Number of f parameters (odd map) = {num_f}")
    print(f"Number of equations = {num_eq}")
    print(f"rank(A) = {rank_A} (coboundary image dimension)")
    print(f"rank(B) = {rank_B} (gamma_gb image dimension)")
    print(f"rank([A|B]) = {rank_AB}")

    if rank_AB == rank_A:
        print(f"=> Image(B) ⊆ Image(A): ALL gb deformations are trivial (coboundaries)")
        print(f"=> H²(g, g_ad) restricted to gamma_gb = 0")
        trivial = True
    else:
        obstruction_dim = rank_AB - rank_A
        print(f"=> Image(B) ⊄ Image(A): obstruction dimension = {obstruction_dim}")
        print(f"=> Some gb deformations are NON-trivial")
        trivial = False

        # Find the conditions on gb for triviality
        # We need B @ gb in Image(A)
        # Let P be the projector onto the orthogonal complement of Image(A)
        U, S, Vt = np.linalg.svd(A_mat, full_matrices=True)
        null_rows = U[:, rank_A:]  # rows orthogonal to Image(A)
        # Condition: null_rows^T @ B @ gb = 0
        constraint_matrix = null_rows.T @ B_mat
        # Clean up small entries
        constraint_matrix[np.abs(constraint_matrix) < 1e-10] = 0
        constraint_rank = np.linalg.matrix_rank(constraint_matrix, tol=1e-8)
        print(f"\nTriviality constraint matrix rank = {constraint_rank}")
        print(f"Constraint matrix ({constraint_matrix.shape[0]} x {constraint_matrix.shape[1]}):")
        # Find the essential constraints (row reduce)
        # Use SVD of constraint_matrix to find the essential rows
        if constraint_rank > 0:
            Uc, Sc, Vtc = np.linalg.svd(constraint_matrix)
            essential = Vtc[:constraint_rank]
            print("Essential constraints on gb (rows of V^T):")
            for row_idx in range(constraint_rank):
                row = essential[row_idx]
                row[np.abs(row) < 1e-10] = 0
                nonzero = np.nonzero(np.abs(row) > 1e-10)[0]
                if len(nonzero) > 0:
                    terms = " + ".join(f"{row[p]:.6g}*gb_{p}" for p in nonzero)
                    print(f"  Constraint {row_idx}: {terms} = 0")

    # Also verify Jacobi identity for structure constants
    jacobi_violations = 0
    for i_gen in range(dim_g):
        for j_gen in range(dim_g):
            for k_gen in range(dim_g):
                pi, pj, pk = gen_parity[i_gen], gen_parity[j_gen], gen_parity[k_gen]
                # Super Jacobi: (-1)^{pi pk} [e_i, [e_j, e_k]] + cyclic = 0
                term1 = (-1) ** (pi * pk) * struct_const[i_gen] @ struct_const[j_gen, k_gen]
                term2 = (-1) ** (pj * pi) * struct_const[j_gen] @ struct_const[k_gen, i_gen]
                term3 = (-1) ** (pk * pj) * struct_const[k_gen] @ struct_const[i_gen, j_gen]
                jacobi = term1 + term2 + term3
                if np.max(np.abs(jacobi)) > 1e-8:
                    jacobi_violations += 1

    print(f"\nJacobi identity violations: {jacobi_violations}")

    # Generate verification data
    verification_data = {
        "n": n,
        "algebra": f"C({n+1}) = osp(2|{2*n})",
        "dim_g": dim_g,
        "dim_even": sum(1 for p in gen_parity if p == 0),
        "dim_odd": sum(1 for p in gen_parity if p == 1),
        "num_gb_params": num_gb,
        "num_f_params": num_f,
        "num_equations": num_eq,
        "rank_coboundary": int(rank_A),
        "rank_gamma": int(rank_B),
        "rank_combined": int(rank_AB),
        "all_trivial": trivial,
        "jacobi_violations": jacobi_violations,
        "generator_names": gen_names,
        "generator_parities": gen_parity,
    }

    if not trivial:
        verification_data["obstruction_dim"] = int(rank_AB - rank_A)

    # Export structure constants as nested dict
    sc_dict = {}
    for i_gen in range(dim_g):
        for j_gen in range(dim_g):
            c = struct_const[i_gen, j_gen]
            nonzero = np.nonzero(np.abs(c) > 1e-10)[0]
            if len(nonzero) > 0:
                key = f"[{gen_names[i_gen]},{gen_names[j_gen]}]"
                sc_dict[key] = {gen_names[int(k)]: round(float(c[k]), 10) for k in nonzero}
    verification_data["structure_constants_sample"] = dict(list(sc_dict.items())[:30])

    # Export gamma_gb sample
    gamma_dict = {}
    for i_gen in range(dim_g):
        for j_gen in range(i_gen, dim_g):
            for p in range(num_gb):
                c = gamma_gb[i_gen, j_gen, :, p]
                nonzero = np.nonzero(np.abs(c) > 1e-10)[0]
                if len(nonzero) > 0:
                    key = f"gamma({gen_names[i_gen]},{gen_names[j_gen]})[gb_{p}]"
                    gamma_dict[key] = {gen_names[int(k)]: round(float(c[k]), 10) for k in nonzero}
    verification_data["gamma_gb_sample"] = dict(list(gamma_dict.items())[:30])

    return verification_data


if __name__ == "__main__":
    all_results = {}
    for n in [1, 2, 3]:
        result = compute_triviality(n, verbose=(n == 1))
        all_results[f"C({n+1})"] = result

    # Save verification data
    output_path = "data/verification_artifacts.json"
    import os
    os.makedirs("data", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nVerification data saved to {output_path}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY OF TRIVIALITY ANALYSIS")
    print("=" * 60)
    for key, result in all_results.items():
        status = "ALL TRIVIAL" if result["all_trivial"] else f"NON-TRIVIAL (obstruction dim = {result.get('obstruction_dim', '?')})"
        print(f"{key}: {status} (Jacobi check: {'PASS' if result['jacobi_violations'] == 0 else 'FAIL'})")
