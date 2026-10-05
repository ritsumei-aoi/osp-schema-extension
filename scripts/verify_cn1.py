import numpy as np
import sympy as sp

def analyze_triviality(n):
    print(f"\n==========================================")
    print(f"TRIVIALITY ANALYSIS FOR C({n}+1) = osp(2|{2*n})")
    print(f"==========================================")

    bosonic_labels = []
    for k in range(1, n + 1):
        bosonic_labels.append((k, '+'))
        bosonic_labels.append((k, '-'))
    
    num_b = 2 * n
    
    even_basis = ['J']
    sp_basis = []
    for A in range(num_b):
        for B in range(A, num_b):
            sp_basis.append((A, B))
            even_basis.append(f"B_{A}_{B}")
            
    odd_basis = []
    for sigma in ['+', '-']:
        for A in range(num_b):
            odd_basis.append(f"F_{sigma}_{A}")

    dim_even = len(even_basis)
    dim_odd = len(odd_basis)
    total_dim = dim_even + dim_odd

    basis = even_basis + odd_basis
    parity = np.array([0]*dim_even + [1]*dim_odd)
    basis_to_idx = {name: i for i, name in enumerate(basis)}

    def ccr_b(A, B):
        k1, s1 = bosonic_labels[A]
        k2, s2 = bosonic_labels[B]
        if k1 == k2 and s1 != s2:
            if s1 == '-' and s2 == '+':
                return 1
            elif s1 == '+' and s2 == '-':
                return -1
        return 0

    # 1. Structure constants matrix C
    C = np.zeros((total_dim, total_dim, total_dim), dtype=float)

    # Even-Even: [B_{A,B}, B_{C,D}]
    for idx1, (A, B) in enumerate(sp_basis, start=1):
        for idx2, (C_idx, D) in enumerate(sp_basis, start=1):
            factor1 = 0.5 if A == B else 1.0
            factor2 = 0.5 if C_idx == D else 1.0

            terms = [
                (ccr_b(B, C_idx), A, D),
                (ccr_b(B, D), A, C_idx),
                (ccr_b(A, C_idx), B, D),
                (ccr_b(A, D), B, C_idx)
            ]
            for coeff, X, Y in terms:
                if coeff != 0:
                    val = coeff * factor1 * factor2
                    min_XY, max_XY = min(X, Y), max(X, Y)
                    target_idx = basis_to_idx[f"B_{min_XY}_{max_XY}"]
                    mult = 2.0 if X == Y else 1.0
                    C[idx1, idx2, target_idx] += val * mult

    # Even-Odd: [J, F] and [B, F]
    for A in range(num_b):
        f_plus_idx = basis_to_idx[f"F_+_{A}"]
        f_minus_idx = basis_to_idx[f"F_-_{A}"]
        j_idx = basis_to_idx['J']
        C[j_idx, f_plus_idx, f_plus_idx] = 1.0
        C[f_plus_idx, j_idx, f_plus_idx] = -1.0
        
        C[j_idx, f_minus_idx, f_minus_idx] = -1.0
        C[f_minus_idx, j_idx, f_minus_idx] = 1.0

    for b_idx, (A, B) in enumerate(sp_basis, start=1):
        factor = 0.5 if A == B else 1.0
        for sigma in ['+', '-']:
            for C_idx in range(num_b):
                f_idx = basis_to_idx[f"F_{sigma}_{C_idx}"]
                term1_coeff = factor * ccr_b(A, C_idx)
                term2_coeff = factor * ccr_b(B, C_idx)
                
                if term1_coeff != 0:
                    target_f = basis_to_idx[f"F_{sigma}_{B}"]
                    C[b_idx, f_idx, target_f] += term1_coeff
                    C[f_idx, b_idx, target_f] -= term1_coeff
                if term2_coeff != 0:
                    target_f = basis_to_idx[f"F_{sigma}_{A}"]
                    C[b_idx, f_idx, target_f] += term2_coeff
                    C[f_idx, b_idx, target_f] -= term2_coeff

    # Odd-Odd: [F_{+, A}, F_{-, B}]
    j_idx = basis_to_idx['J']
    for A in range(num_b):
        for B in range(num_b):
            f_pA = basis_to_idx[f"F_+_{A}"]
            f_mB = basis_to_idx[f"F_-_{B}"]
            
            min_AB, max_AB = min(A, B), max(A, B)
            target_b = basis_to_idx[f"B_{min_AB}_{max_AB}"]
            mult = 2.0 if A == B else 1.0
            
            C[f_pA, f_mB, target_b] += 1.0 * mult
            C[f_mB, f_pA, target_b] += 1.0 * mult

            ccr_BA = ccr_b(B, A)
            if ccr_BA != 0:
                C[f_pA, f_mB, j_idx] += -1.0 * ccr_BA
                C[f_mB, f_pA, j_idx] += -1.0 * ccr_BA

    # 2. Build parameter map for f: g -> g (odd map)
    # f maps g_0 -> g_1 (dim_even x dim_odd parameters)
    # f maps g_1 -> g_0 (dim_odd x dim_even parameters)
    # Total f parameters = 2 * dim_even * dim_odd

    # Map parameter index to (src_idx, target_idx)
    f_params = []
    for src in range(dim_even): # g_0
        for tgt in range(dim_even, total_dim): # g_1
            f_params.append((src, tgt))

    for src in range(dim_even, total_dim): # g_1
        for tgt in range(dim_even): # g_0
            f_params.append((src, tgt))

    num_f_params = len(f_params)
    print(f"Number of odd map f parameters: {num_f_params}")

    # We evaluate delta f for each pair (i, j) with i <= j
    # Coboundary formula:
    # (delta f)(Z_i, Z_j) = (-1)^{p(i)} [Z_i, f(Z_j)] - (-1)^{(p(i)+1)p(j)} [Z_j, f(Z_i)] - f([Z_i, Z_j])

    # We store the linear operator Delta mapping f_params -> 2-cocycle components (i, j, k)
    # For symmetry/skew-symmetry:
    # Note: \gamma(Z_i, Z_j) has symmetry: \gamma(Z_j, Z_i) = - (-1)^{p(i)p(j)} \gamma(Z_i, Z_j)
    # So we only need pairs (i, j) with i <= j.

    pairs = []
    for i in range(total_dim):
        for j in range(i, total_dim):
            pairs.append((i, j))

    num_pairs = len(pairs)
    num_equations = num_pairs * total_dim
    print(f"Number of independent generator pairs (i <= j): {num_pairs}")
    print(f"Total equations per deformation: {num_equations}")

    Delta = np.zeros((num_equations, num_f_params), dtype=float)

    def get_eq_idx(pair_idx, k):
        return pair_idx * total_dim + k

    for p_idx, (i, j) in enumerate(pairs):
        pi, pj = parity[i], parity[j]
        sign1 = (-1.0)**pi
        sign2 = - (-1.0)**((pi + 1) * pj)
        
        # [Z_i, Z_j] = sum_m C_{i, j}^m Z_m
        comm_ij = C[i, j, :]

        for param_idx, (src, tgt) in enumerate(f_params):
            # Term 1: (-1)^{pi} [Z_i, f(Z_j)]
            # f(Z_j) has term phi_{tgt, src} Z_{tgt} if src == j
            if src == j:
                # [Z_i, Z_{tgt}] = sum_k C_{i, tgt}^k Z_k
                for k in range(total_dim):
                    Delta[get_eq_idx(p_idx, k), param_idx] += sign1 * C[i, tgt, k]

            # Term 2: - (-1)^{(pi+1)pj} [Z_j, f(Z_i)]
            # f(Z_i) has term phi_{tgt, src} Z_{tgt} if src == i
            if src == i:
                # [Z_j, Z_{tgt}] = sum_k C_{j, tgt}^k Z_k
                for k in range(total_dim):
                    Delta[get_eq_idx(p_idx, k), param_idx] += sign2 * C[j, tgt, k]

            # Term 3: - f([Z_i, Z_j])
            # [Z_i, Z_j] = sum_m C_{i, j}^m Z_m
            # f(Z_m) has term phi_{tgt, src} Z_{tgt} if src == m
            coeff_m = comm_ij[src]
            if coeff_m != 0:
                Delta[get_eq_idx(p_idx, tgt), param_idx] -= coeff_m

    # Compute rank of Delta
    rank_Delta = np.linalg.matrix_rank(Delta)
    print(f"Rank of Coboundary Operator Delta matrix: {rank_Delta} / {num_f_params}")

    # 3. Build gamma_gb tensor for symbolic gb parameters
    # gb parameters: gb_{sigma, A} for sigma in ['+', '-'], A in 0 ... num_b-1
    gb_names = []
    for sigma in ['+', '-']:
        for A in range(num_b):
            gb_names.append(f"gb_{sigma}_{A}")

    num_gb = len(gb_names)
    print(f"Number of gb deformation parameters: {num_gb}")

    Gamma_gb = np.zeros((num_equations, num_gb), dtype=float)

    gb_to_idx = {name: i for i, name in enumerate(gb_names)}

    for p_idx, (i, j) in enumerate(pairs):
        name_i, name_j = basis[i], basis[j]
        pi, pj = parity[i], parity[j]

        # Case 1: Even-Even (i in g_0, j in g_0)
        if pi == 0 and pj == 0:
            if name_i == 'J' and name_j.startswith('B_'):
                # gamma_gb(J, B_{A,B})
                _, A_str, B_str = name_j.split('_')
                A, B = int(A_str), int(B_str)
                # gamma(J, b_A b_B) = gb_{-,A} F_{+,B} + gb_{-,B} F_{+,A} + gb_{+,A} F_{-,B} + gb_{+,B} F_{-,A}
                # (with factor 0.5 if A == B)
                terms = [
                    ('gb_-_' + str(A), f"F_+_{B}"),
                    ('gb_-_' + str(B), f"F_+_{A}"),
                    ('gb_+_' + str(A), f"F_-_{B}"),
                    ('gb_+_' + str(B), f"F_-_{A}")
                ]
                factor = 0.5 if A == B else 1.0
                for gb_name, target_f in terms:
                    gb_k = gb_to_idx[gb_name]
                    target_k = basis_to_idx[target_f]
                    Gamma_gb[get_eq_idx(p_idx, target_k), gb_k] += factor * 1.0

        # Case 2: Even-Odd (i in g_0, j in g_1)
        elif pi == 0 and pj == 1:
            if name_i == 'J' and name_j.startswith('F_'):
                # gamma_gb(J, F_{tau, C}) = tau * gb_{tau, C} J
                _, tau, C_str = name_j.split('_')
                C_idx = int(C_str)
                gb_name = f"gb_{tau}_{C_idx}"
                gb_k = gb_to_idx[gb_name]
                j_k = basis_to_idx['J']
                sign = 1.0 if tau == '+' else -1.0
                Gamma_gb[get_eq_idx(p_idx, j_k), gb_k] += sign

            elif name_i.startswith('B_') and name_j.startswith('F_'):
                # gamma_gb(B_{A,B}, F_{sigma, C}) = - (gb_{sigma, B} b_A b_C + gb_{sigma, A} b_B b_C)
                _, A_str, B_str = name_i.split('_')
                A, B = int(A_str), int(B_str)
                _, sigma, C_str = name_j.split('_')
                C_idx = int(C_str)
                factor = 0.5 if A == B else 1.0

                terms = [
                    (f"gb_{sigma}_{B}", A, C_idx),
                    (f"gb_{sigma}_{A}", B, C_idx)
                ]
                for gb_name, X, Y in terms:
                    gb_k = gb_to_idx[gb_name]
                    min_XY, max_XY = min(X, Y), max(X, Y)
                    target_b = basis_to_idx[f"B_{min_XY}_{max_XY}"]
                    mult = 2.0 if X == Y else 1.0
                    Gamma_gb[get_eq_idx(p_idx, target_b), gb_k] -= factor * mult * 1.0

        # Case 3: Odd-Odd (i in g_1, j in g_1)
        elif pi == 1 and pj == 1:
            if name_i.startswith('F_') and name_j.startswith('F_'):
                # gamma_gb(F_{sigma, A}, F_{tau, B}) = - (gb_{tau, A} F_{sigma, B} + gb_{sigma, B} F_{tau, A})
                _, sigma, A_str = name_i.split('_')
                A = int(A_str)
                _, tau, B_str = name_j.split('_')
                B = int(B_str)

                terms = [
                    (f"gb_{tau}_{A}", f"F_{sigma}_{B}"),
                    (f"gb_{sigma}_{B}", f"F_{tau}_{A}")
                ]
                for gb_name, target_f in terms:
                    gb_k = gb_to_idx[gb_name]
                    target_k = basis_to_idx[target_f]
                    Gamma_gb[get_eq_idx(p_idx, target_k), gb_k] -= 1.0

    # 4. Check compatibility: For which vectors in colspace(Gamma_gb) do they lie in colspace(Delta)?
    # That is, we solve Delta @ phi = Gamma_gb @ gb
    # Projects Gamma_gb onto orth space of Null(Delta^T)
    
    # SVD or QR of Delta:
    U, S, Vt = np.linalg.svd(Delta, full_matrices=True)
    r = np.sum(S > 1e-10)
    # The left singular vectors U[:, r:] span the kernel of Delta^T
    # If Gamma_gb is in colspace(Delta), then U[:, r:].T @ Gamma_gb must be 0!
    
    U_kernel = U[:, r:].T
    projection_error_matrix = U_kernel @ Gamma_gb
    max_proj_err = np.max(np.abs(projection_error_matrix))
    print(f"Max Projection Error of Gamma_gb onto Null(Delta^T): {max_proj_err:.6e}")
    
    rank_combined = np.linalg.matrix_rank(np.hstack([Delta, Gamma_gb]))
    print(f"Rank of Delta: {r}")
    print(f"Rank of [Delta | Gamma_gb]: {rank_combined}")

    if rank_combined == r:
        print(f"==> RESULT: EVERY gb deformation IS TRIVIAL for C({n}+1)!")
    else:
        # Find which linear combinations of gb parameters are non-trivial!
        print(f"==> RESULT: NON-TRIVIAL DEFORMATIONS EXIST!")
        # SVD of projection_error_matrix to find non-trivial gb subspace
        U_p, S_p, Vt_p = np.linalg.svd(projection_error_matrix)
        nontrivial_dim = np.sum(S_p > 1e-10)
        trivial_dim = num_gb - nontrivial_dim
        print(f"Dimension of trivial gb space: {trivial_dim} / {num_gb}")
        print(f"Dimension of non-trivial gb space: {nontrivial_dim} / {num_gb}")

        # Let's inspect the singular vectors of Vt_p (the non-trivial gb constraints)
        print("Non-trivial singular values:", S_p[S_p > 1e-10])

    return

if __name__ == "__main__":
    for n in [1, 2, 3]:
        analyze_triviality(n)
