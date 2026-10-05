import sympy as sp
import numpy as np

def symbolic_analysis_n1():
    print("==========================================")
    print("EXACT SYMBOLIC PROOF FOR C(1+1) = osp(2|2)")
    print("==========================================")

    gb_p0 = sp.Symbol('gb_+_0')
    gb_p1 = sp.Symbol('gb_+_1')
    gb_m0 = sp.Symbol('gb_-_0')
    gb_m1 = sp.Symbol('gb_-_1')
    
    gb_vec = sp.Matrix([gb_p0, gb_p1, gb_m0, gb_m1])

    n = 1
    bosonic_labels = [(1, '+'), (1, '-')]
    num_b = 2
    even_basis = ['J', 'B_0_0', 'B_0_1', 'B_1_1']
    odd_basis = ['F_+_0', 'F_+_1', 'F_-_0', 'F_-_1']
    basis = even_basis + odd_basis
    parity = [0]*4 + [1]*4
    total_dim = 8
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

    C_tensor = np.zeros((total_dim, total_dim, total_dim), dtype=object)

    sp_basis = [(0,0), (0,1), (1,1)]
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
                    C_tensor[idx1, idx2, target_idx] += val * mult

    for A in range(num_b):
        f_plus_idx = basis_to_idx[f"F_+_{A}"]
        f_minus_idx = basis_to_idx[f"F_-_{A}"]
        j_idx = basis_to_idx['J']
        C_tensor[j_idx, f_plus_idx, f_plus_idx] = 1.0
        C_tensor[f_plus_idx, j_idx, f_plus_idx] = -1.0
        
        C_tensor[j_idx, f_minus_idx, f_minus_idx] = -1.0
        C_tensor[f_minus_idx, j_idx, f_minus_idx] = 1.0

    for b_idx, (A, B) in enumerate(sp_basis, start=1):
        factor = 0.5 if A == B else 1.0
        for sigma in ['+', '-']:
            for C_idx in range(num_b):
                f_idx = basis_to_idx[f"F_{sigma}_{C_idx}"]
                term1_coeff = factor * ccr_b(A, C_idx)
                term2_coeff = factor * ccr_b(B, C_idx)
                
                if term1_coeff != 0:
                    target_f = basis_to_idx[f"F_{sigma}_{B}"]
                    C_tensor[b_idx, f_idx, target_f] += term1_coeff
                    C_tensor[f_idx, b_idx, target_f] -= term1_coeff
                if term2_coeff != 0:
                    target_f = basis_to_idx[f"F_{sigma}_{A}"]
                    C_tensor[b_idx, f_idx, target_f] += term2_coeff
                    C_tensor[f_idx, b_idx, target_f] -= term2_coeff

    j_idx = basis_to_idx['J']
    for A in range(num_b):
        for B in range(num_b):
            f_pA = basis_to_idx[f"F_+_{A}"]
            f_mB = basis_to_idx[f"F_-_{B}"]
            
            min_AB, max_AB = min(A, B), max(A, B)
            target_b = basis_to_idx[f"B_{min_AB}_{max_AB}"]
            mult = 2.0 if A == B else 1.0
            
            C_tensor[f_pA, f_mB, target_b] += 1.0 * mult
            C_tensor[f_mB, f_pA, target_b] += 1.0 * mult

            ccr_BA = ccr_b(B, A)
            if ccr_BA != 0:
                C_tensor[f_pA, f_mB, j_idx] += -1.0 * ccr_BA
                C_tensor[f_mB, f_pA, j_idx] += -1.0 * ccr_BA

    pairs = []
    for i in range(total_dim):
        for j in range(i, total_dim):
            pairs.append((i, j))

    num_pairs = len(pairs)
    num_eqs = num_pairs * total_dim
    
    f_params = []
    for src in range(4):
        for tgt in range(4, 8):
            f_params.append((src, tgt))
    for src in range(4, 8):
        for tgt in range(4):
            f_params.append((src, tgt))

    num_f = len(f_params)

    Delta = sp.zeros(num_eqs, num_f)
    Gamma_gb = sp.zeros(num_eqs, 4)

    def get_eq_idx(pair_idx, k):
        return pair_idx * total_dim + k

    for p_idx, (i, j) in enumerate(pairs):
        pi, pj = parity[i], parity[j]
        sign1 = (-1.0)**pi
        sign2 = - (-1.0)**((pi + 1) * pj)
        comm_ij = C_tensor[i, j, :]

        for param_idx, (src, tgt) in enumerate(f_params):
            if src == j:
                for k in range(total_dim):
                    Delta[get_eq_idx(p_idx, k), param_idx] += sign1 * C_tensor[i, tgt, k]
            if src == i:
                for k in range(total_dim):
                    Delta[get_eq_idx(p_idx, k), param_idx] += sign2 * C_tensor[j, tgt, k]
            coeff_m = comm_ij[src]
            if coeff_m != 0:
                Delta[get_eq_idx(p_idx, tgt), param_idx] -= coeff_m

    gb_names = ['gb_+_0', 'gb_+_1', 'gb_-_0', 'gb_-_1']
    gb_to_idx = {name: i for i, name in enumerate(gb_names)}

    for p_idx, (i, j) in enumerate(pairs):
        name_i, name_j = basis[i], basis[j]
        pi, pj = parity[i], parity[j]

        if pi == 0 and pj == 0:
            if name_i == 'J' and name_j.startswith('B_'):
                _, A_str, B_str = name_j.split('_')
                A, B = int(A_str), int(B_str)
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

        elif pi == 0 and pj == 1:
            if name_i == 'J' and name_j.startswith('F_'):
                _, tau, C_str = name_j.split('_')
                C_idx = int(C_str)
                gb_name = f"gb_{tau}_{C_idx}"
                gb_k = gb_to_idx[gb_name]
                j_k = basis_to_idx['J']
                sign = 1.0 if tau == '+' else -1.0
                Gamma_gb[get_eq_idx(p_idx, j_k), gb_k] += sign

            elif name_i.startswith('B_') and name_j.startswith('F_'):
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

        elif pi == 1 and pj == 1:
            if name_i.startswith('F_') and name_j.startswith('F_'):
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

    print("Computing left nullspace of Delta in SymPy...")
    left_null = Delta.T.nullspace()
    print(f"Dimension of left nullspace of Delta: {len(left_null)}")

    print("Checking projection of Gamma_gb @ gb_vec onto left nullspace:")
    rhs = Gamma_gb * gb_vec
    
    obstructions = []
    for idx, vec in enumerate(left_null):
        proj = (vec.T * rhs)[0]
        proj_simp = sp.simplify(proj)
        if proj_simp != 0:
            obstructions.append(proj_simp)

    print(f"Number of non-zero obstruction equations: {len(obstructions)}")
    for i, obs in enumerate(obstructions):
        print(f"  Obstruction {i+1}: {obs} = 0")

    # Solve the obstruction system for gb_vec
    if len(obstructions) > 0:
        system_mat = sp.Matrix([[obs.coeff(gb_p0), obs.coeff(gb_p1), obs.coeff(gb_m0), obs.coeff(gb_m1)] for obs in obstructions])
        print("Obstruction matrix rank:", system_mat.rank())
        sol = sp.solve(obstructions, (gb_p0, gb_p1, gb_m0, gb_m1))
        print(f"Exact symbolic solution for gb parameters: {sol}")

if __name__ == "__main__":
    symbolic_analysis_n1()
