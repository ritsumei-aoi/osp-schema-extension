import sympy as sp
from algebra_helper import build_algebra
from bracket_solver import compute_bracket

def inspect_f_map(n=1):
    basis = build_algebra(n)
    dim = len(basis)
    basis_map = {b[0]: i for i, b in enumerate(basis)}
    
    gb_keys = []
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                gb_keys.append((sigma, j, s))
                
    # We want to find f for each gb_key
    # Let's parameterize f as f_ij where f(Z_j) = sum_i phi_{ij} Z_i
    f_map_indices = []
    for j in range(dim):
        pj = basis[j][1]
        for i in range(dim):
            pi = basis[i][1]
            if pi != pj:
                f_map_indices.append((i, j))
                
    f_idx_lookup = {pair: idx for idx, pair in enumerate(f_map_indices)}
    num_f_vars = len(f_map_indices)
    
    # Compute structure constants C
    gb_zero = {k: sp.Rational(0) for k in gb_keys}
    C = [[[sp.Rational(0) for _ in range(dim)] for _ in range(dim)] for _ in range(dim)]
    for i in range(dim):
        for j in range(dim):
            v0, _ = compute_bracket(basis[i], basis[j], n, basis, basis_map, gb_zero)
            for k in range(dim):
                C[i][j][k] = v0[k]
                
    pair_list = []
    for i in range(dim):
        for j in range(dim):
            if i < j or (i == j and basis[i][1] == 1):
                pair_list.append((i, j))
                
    # For each gb parameter, solve \delta f = \gamma
    for gb_key in gb_keys:
        gb_dict = dict(gb_zero)
        gb_dict[gb_key] = sp.Rational(1)
        
        # RHS: gamma(basis[i], basis[j])_l
        A_rows = []
        b_vec = []
        
        for (i, j) in pair_list:
            pX = basis[i][1]
            pY = basis[j][1]
            _, vg = compute_bracket(basis[i], basis[j], n, basis, basis_map, gb_dict)
            
            for l in range(dim):
                row = [sp.Rational(0)] * num_f_vars
                # 1. (-1)^{pX} sum_k phi_{(k, j)} C^l_{ik}
                sign1 = (-1)**pX
                for k in range(dim):
                    if (k, j) in f_idx_lookup and C[i][k][l] != 0:
                        row[f_idx_lookup[(k, j)]] += sign1 * C[i][k][l]
                        
                # 2. - (-1)^{(pX+1)pY} sum_k phi_{(k, i)} C^l_{jk}
                sign2 = - ((-1)**((pX + 1) * pY))
                for k in range(dim):
                    if (k, i) in f_idx_lookup and C[j][k][l] != 0:
                        row[f_idx_lookup[(k, i)]] += sign2 * C[j][k][l]
                        
                # 3. - sum_k C^k_{ij} phi_{(l, k)}
                for k in range(dim):
                    if (l, k) in f_idx_lookup and C[i][j][k] != 0:
                        row[f_idx_lookup[(l, k)]] -= C[i][j][k]
                        
                A_rows.append(row)
                b_vec.append(vg[l])
                
        A_mat = sp.Matrix(A_rows)
        b_mat = sp.Matrix(b_vec)
        sol = A_mat.gauss_jordan_solve(b_mat)
        f_sol = sol[0]
        
        print(f"\n--- Solution f for parameter gb_{gb_key} ---")
        for idx, (out_idx, in_idx) in enumerate(f_map_indices):
            val = f_sol[idx]
            if val != 0:
                print(f"  f({basis[in_idx][0]}) = {val} * {basis[out_idx][0]}")

if __name__ == '__main__':
    inspect_f_map(1)
