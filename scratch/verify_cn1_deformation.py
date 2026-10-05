import numpy as np
import sympy as sp
import json
import os

def build_cn1_algebra(n):
    even_basis = []
    for k in range(1, n+1):
        for l in range(k, n+1):
            even_basis.append(('B_pp', k, l, ('b', k, '+'), ('b', l, '+')))
    for k in range(1, n+1):
        for l in range(k, n+1):
            even_basis.append(('B_mm', k, l, ('b', k, '-'), ('b', l, '-')))
    for k in range(1, n+1):
        for l in range(1, n+1):
            even_basis.append(('B_pm', k, l, ('b', k, '+'), ('b', l, '-')))
    even_basis.append(('F_0', 0, 0, ('a', '+'), ('a', '-')))
    
    odd_basis = []
    for sigma in ['+', '-']:
        for k in range(1, n+1):
            for s in ['+', '-']:
                odd_basis.append(('O', sigma, k, s, ('a', sigma), ('b', k, s)))

    basis = []
    for b in even_basis:
        basis.append({'name': f"{b[0]}_{b[1]}_{b[2]}" if b[1]!=0 else "F_0", 'parity': 0, 'ops': (b[3], b[4]), 'tag': b})
    for b in odd_basis:
        basis.append({'name': f"O_{b[1]}_{b[2]}_{b[3]}", 'parity': 1, 'ops': (b[4], b[5]), 'tag': b})

    dim = len(basis)
    dim_even = len(even_basis)
    dim_odd = len(odd_basis)

    def reduce_two_ops(op1, op2):
        t1, t2 = op1[0], op2[0]
        if t1 == 'a' and t2 == 'a':
            s1, s2 = op1[1], op2[1]
            if s1 == '+' and s2 == '-':
                idx = [i for i, b in enumerate(basis) if b['name'] == 'F_0'][0]
                return {idx: 1}
            elif s1 == '-' and s2 == '+':
                idx = [i for i, b in enumerate(basis) if b['name'] == 'F_0'][0]
                return {idx: -1}
            else:
                return {}
        if t1 == 'a' and t2 == 'b':
            name = f"O_{op1[1]}_{op2[1]}_{op2[2]}"
            idx = [i for i, b in enumerate(basis) if b['name'] == name][0]
            return {idx: 1}
        if t1 == 'b' and t2 == 'a':
            name = f"O_{op2[1]}_{op1[1]}_{op1[2]}"
            idx = [i for i, b in enumerate(basis) if b['name'] == name][0]
            return {idx: 1}
        if t1 == 'b' and t2 == 'b':
            k, s1 = op1[1], op1[2]
            l, s2 = op2[1], op2[2]
            if s1 == '+' and s2 == '+':
                k_min, l_max = min(k, l), max(k, l)
                name = f"B_pp_{k_min}_{l_max}"
                idx = [i for i, b in enumerate(basis) if b['name'] == name][0]
                return {idx: 1}
            elif s1 == '-' and s2 == '-':
                k_min, l_max = min(k, l), max(k, l)
                name = f"B_mm_{k_min}_{l_max}"
                idx = [i for i, b in enumerate(basis) if b['name'] == name][0]
                return {idx: 1}
            elif s1 == '+' and s2 == '-':
                name = f"B_pm_{k}_{l}"
                idx = [i for i, b in enumerate(basis) if b['name'] == name][0]
                return {idx: 1}
            elif s1 == '-' and s2 == '+':
                name = f"B_pm_{l}_{k}"
                idx = [i for i, b in enumerate(basis) if b['name'] == name][0]
                return {idx: 1}
        return {}

    def delta_single_op(op1, op2):
        t1, t2 = op1[0], op2[0]
        if t1 == 'a' and t2 == 'b':
            sigma = op1[1]
            j, s = op2[1], op2[2]
            return {f"gb_{sigma}_{j}_{s}": 1}
        elif t1 == 'b' and t2 == 'a':
            sigma = op2[1]
            j, s = op1[1], op1[2]
            return {f"gb_{sigma}_{j}_{s}": -1}
        return {}

    def comm_single_op(op1, op2):
        t1, t2 = op1[0], op2[0]
        if t1 == 'a' and t2 == 'a':
            s1, s2 = op1[1], op2[1]
            if (s1 == '+' and s2 == '-') or (s1 == '-' and s2 == '+'):
                return True, 1
            return True, 0
        if t1 == 'b' and t2 == 'b':
            k, s1 = op1[1], op1[2]
            l, s2 = op2[1], op2[2]
            if k == l and s1 == '-' and s2 == '+':
                return True, 1
            if k == l and s1 == '+' and s2 == '-':
                return True, -1
            return True, 0
        return True, 0

    def p_op(op):
        return 1 if op[0] == 'a' else 0

    def calc_bracket_0(X_idx, Y_idx):
        X = basis[X_idx]
        Y = basis[Y_idx]
        u, v = X['ops']
        w, z = Y['ops']
        res = {}
        
        is_sc, val = comm_single_op(v, w)
        if is_sc and val != 0:
            vec = reduce_two_ops(u, z)
            for idx, c in vec.items():
                res[idx] = res.get(idx, 0) + val * c
                
        is_sc, val = comm_single_op(v, z)
        if is_sc and val != 0:
            sign = (-1)**(p_op(v) * p_op(w))
            vec = reduce_two_ops(u, w)
            for idx, c in vec.items():
                res[idx] = res.get(idx, 0) + sign * val * c
                
        is_sc, val = comm_single_op(u, w)
        if is_sc and val != 0:
            sign = (-1)**(p_op(v) * p_op(w))
            vec = reduce_two_ops(v, z)
            for idx, c in vec.items():
                res[idx] = res.get(idx, 0) + sign * val * c
                
        is_sc, val = comm_single_op(u, z)
        if is_sc and val != 0:
            sign = (-1)**(p_op(v) * p_op(z) + p_op(u) * p_op(w))
            vec = reduce_two_ops(v, w)
            for idx, c in vec.items():
                res[idx] = res.get(idx, 0) + sign * val * c
                
        return res

    def calc_gamma_gb(X_idx, Y_idx):
        X = basis[X_idx]
        Y = basis[Y_idx]
        u, v = X['ops']
        w, z = Y['ops']
        res = {}
        
        d_vw = delta_single_op(v, w)
        if d_vw:
            vec_uz = reduce_two_ops(u, z)
            for p_name, p_val in d_vw.items():
                for c_idx, c_val in vec_uz.items():
                    key = (c_idx, p_name)
                    res[key] = res.get(key, 0) + p_val * c_val

        d_vz = delta_single_op(v, z)
        if d_vz:
            sign = (-1)**(p_op(v) * p_op(w))
            vec_uw = reduce_two_ops(u, w)
            for p_name, p_val in d_vz.items():
                for c_idx, c_val in vec_uw.items():
                    key = (c_idx, p_name)
                    res[key] = res.get(key, 0) + sign * p_val * c_val

        d_uw = delta_single_op(u, w)
        if d_uw:
            sign = (-1)**(p_op(v) * p_op(w))
            vec_vz = reduce_two_ops(v, z)
            for p_name, p_val in d_uw.items():
                for c_idx, c_val in vec_vz.items():
                    key = (c_idx, p_name)
                    res[key] = res.get(key, 0) + sign * p_val * c_val

        d_uz = delta_single_op(u, z)
        if d_uz:
            sign = (-1)**(p_op(v) * p_op(z) + p_op(u) * p_op(w))
            vec_vw = reduce_two_ops(v, w)
            for p_name, p_val in d_uz.items():
                for c_idx, c_val in vec_vw.items():
                    key = (c_idx, p_name)
                    res[key] = res.get(key, 0) + sign * p_val * c_val

        return res

    C_tensor = np.zeros((dim, dim, dim))
    for a in range(dim):
        for b in range(dim):
            br = calc_bracket_0(a, b)
            for c, val in br.items():
                C_tensor[a, b, c] = val

    gb_params = []
    for sigma in ['+', '-']:
        for k in range(1, n+1):
            for s in ['+', '-']:
                gb_params.append(f"gb_{sigma}_{k}_{s}")
    num_gb = len(gb_params)

    gamma_tensor = np.zeros((dim, dim, dim, num_gb))
    for a in range(dim):
        for b in range(dim):
            g_dict = calc_gamma_gb(a, b)
            for (c, p_name), val in g_dict.items():
                p_idx = gb_params.index(p_name)
                gamma_tensor[a, b, c, p_idx] = val

    return basis, C_tensor, gamma_tensor, gb_params

def analyze_triviality(n):
    basis, C_tensor, gamma_tensor, gb_params = build_cn1_algebra(n)
    dim = len(basis)
    dim_even = sum(1 for b in basis if b['parity'] == 0)
    dim_odd = sum(1 for b in basis if b['parity'] == 1)
    even_indices = [i for i, b in enumerate(basis) if b['parity'] == 0]
    odd_indices = [i for i, b in enumerate(basis) if b['parity'] == 1]
    
    # Map f indices: phi_{r, s} where r is target, s is source.
    # f maps even -> odd, and odd -> even.
    # We index phi as a vector.
    phi_map = {}
    phi_list = []
    # even -> odd
    for s in even_indices:
        for r in odd_indices:
            phi_map[(r, s)] = len(phi_list)
            phi_list.append((r, s))
    # odd -> even
    for s in odd_indices:
        for r in even_indices:
            phi_map[(r, s)] = len(phi_list)
            phi_list.append((r, s))
            
    num_phi = len(phi_list) # 2 * dim_even * dim_odd
    print(f"n={n}: Number of f parameters = {num_phi}, Number of gb parameters = {len(gb_params)}")
    
    # We construct the linear system delta_f = gamma_gb
    # Equations are indexed by independent pairs (a, b) with a < b (or super-skew symmetric independent pairs) and target component c.
    # Super-skew symmetry: gamma(b, a) = - (-1)^{p(a)p(b)} gamma(a, b).
    # So we only need pairs a <= b.
    eq_rows_phi = []
    eq_rows_gb = []
    
    for a in range(dim):
        for b in range(a, dim): # a <= b
            p_a = basis[a]['parity']
            p_b = basis[b]['parity']
            
            # Determine parity of output c for (delta f)(Z_a, Z_b):
            # p((delta f)(Z_a, Z_b)) = p(a) + p(b) + 1 mod 2.
            target_parity = (p_a + p_b + 1) % 2
            target_c_list = [c for c in range(dim) if basis[c]['parity'] == target_parity]
            
            for c in target_c_list:
                row_phi = np.zeros(num_phi)
                
                # Formula for (delta f)(Z_a, Z_b):
                # (-1)^{p(a)} [Z_a, f(Z_b)] - (-1)^{(p(a)+1)p(b)} [Z_b, f(Z_a)] - f([Z_a, Z_b])
                
                # 1. (-1)^{p(a)} [Z_a, f(Z_b)]
                # f(Z_b) = sum_k phi_{k, b} Z_k (where p(k) = 1 - p(b))
                k_b_parity = 1 - p_b
                for k in range(dim):
                    if basis[k]['parity'] == k_b_parity:
                        if (k, b) in phi_map:
                            phi_idx = phi_map[(k, b)]
                            coeff = ((-1)**p_a) * C_tensor[a, k, c]
                            row_phi[phi_idx] += coeff
                            
                # 2. - (-1)^{(p(a)+1)p(b)} [Z_b, f(Z_a)]
                # f(Z_a) = sum_k phi_{k, a} Z_k (where p(k) = 1 - p(a))
                k_a_parity = 1 - p_a
                sign_2 = - ((-1)**((p_a + 1) * p_b))
                for k in range(dim):
                    if basis[k]['parity'] == k_a_parity:
                        if (k, a) in phi_map:
                            phi_idx = phi_map[(k, a)]
                            coeff = sign_2 * C_tensor[b, k, c]
                            row_phi[phi_idx] += coeff
                            
                # 3. - f([Z_a, Z_b])
                # [Z_a, Z_b] = sum_m C_{a,b}^m Z_m (where p(m) = p(a) + p(b) mod 2)
                # f(Z_m) = sum_c phi_{c, m} Z_c
                for m in range(dim):
                    if C_tensor[a, b, m] != 0:
                        if (c, m) in phi_map:
                            phi_idx = phi_map[(c, m)]
                            row_phi[phi_idx] -= C_tensor[a, b, m]
                            
                row_gb = gamma_tensor[a, b, c, :]
                
                # Store equation: row_phi @ phi = row_gb @ gb
                if np.any(row_phi != 0) or np.any(row_gb != 0):
                    eq_rows_phi.append(row_phi)
                    eq_rows_gb.append(row_gb)
                    
    M_phi = np.array(eq_rows_phi) # shape (num_eqs, num_phi)
    M_gb = np.array(eq_rows_gb)   # shape (num_eqs, num_gb)
    
    print(f"Total non-trivial equations for n={n}: {M_phi.shape[0]}")
    
    # We want to check if for ANY non-zero gb, M_gb @ gb is in the column space of M_phi.
    # That is, M_phi @ phi = M_gb @ gb.
    # Using SVD/nullspace of M_phi:
    # Let P_perp be the projection matrix onto the orthogonal complement of col(M_phi).
    # Then M_phi @ phi = M_gb @ gb has a solution phi iff P_perp @ M_gb @ gb = 0.
    
    U, S, Vt = np.linalg.svd(M_phi, full_matrices=True)
    rank_phi = np.sum(S > 1e-10)
    print(f"Rank of M_phi for n={n}: {rank_phi} out of {num_phi} variables and {M_phi.shape[0]} equations")
    
    # The left nullspace of M_phi is U[:, rank_phi:].T
    left_null_phi = U[:, rank_phi:].T
    
    # Obstruction matrix for gb:
    Obs_gb = left_null_phi @ M_gb # shape (num_eqs - rank_phi, num_gb)
    
    # Rank of obstruction matrix
    rank_obs = np.linalg.matrix_rank(Obs_gb, tol=1e-10)
    print(f"Obstruction matrix shape for gb: {Obs_gb.shape}, Rank: {rank_obs}")
    
    # Nullspace of Obs_gb gives the allowable gb parameters!
    U_obs, S_obs, Vt_obs = np.linalg.svd(Obs_gb, full_matrices=True)
    rank_obs_svd = np.sum(S_obs > 1e-10)
    
    gb_nullspace_dim = len(gb_params) - rank_obs_svd
    print(f"Dimension of allowable gb parameters for triviality: {gb_nullspace_dim} out of {len(gb_params)}")

    if gb_nullspace_dim > 0:
        null_gb_basis = Vt_obs[rank_obs_svd:, :]
        print("Allowable gb vectors (nullspace basis of obstruction):")
        for vec in null_gb_basis:
            vec_clean = [round(x, 6) for x in vec]
            print(" ", dict(zip(gb_params, vec_clean)))
    else:
        print("RESULT: ONLY gb = 0 gives a trivial deformation! Any non-zero gb is NON-TRIVIAL!")

    return {
        'n': n,
        'dim_total': dim,
        'dim_even': dim_even,
        'dim_odd': dim_odd,
        'num_gb': len(gb_params),
        'num_phi': num_phi,
        'rank_M_phi': int(rank_phi),
        'rank_obs': int(rank_obs_svd),
        'gb_nullspace_dim': int(gb_nullspace_dim)
    }

if __name__ == '__main__':
    results = []
    for n in [1, 2, 3]:
        print(f"\n=================== ANALYZING n = {n} ===================")
        res = analyze_triviality(n)
        results.append(res)
    print("\nSUMMARY RESULTS:", json.dumps(results, indent=2))
