import sympy as sp
from itertools import product
import json
from algebra_helper import build_algebra
from bracket_solver import compute_bracket

def analyze_triviality(n):
    print(f"\n=======================================================")
    print(f"       ANALYZING TRIVIALITY FOR C({n+1}) = osp(2|{2*n})")
    print(f"=======================================================")
    
    basis = build_algebra(n)
    dim = len(basis)
    basis_map = {b[0]: i for i, b in enumerate(basis)}
    
    even_indices = [i for i, b in enumerate(basis) if b[1] == 0]
    odd_indices = [i for i, b in enumerate(basis) if b[1] == 1]
    
    dim_even = len(even_indices)
    dim_odd = len(odd_indices)
    
    print(f"dim = {dim} (even: {dim_even}, odd: {dim_odd})")
    
    # 1. Compute standard structure constants C^k_{ij}
    gb_zero = {}
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                gb_zero[(sigma, j, s)] = sp.Rational(0)
                
    C = [[[sp.Rational(0) for _ in range(dim)] for _ in range(dim)] for _ in range(dim)]
    for i in range(dim):
        for j in range(dim):
            v0, _ = compute_bracket(basis[i], basis[j], n, basis, basis_map, gb_zero)
            for k in range(dim):
                C[i][j][k] = v0[k]
                
    # 2. Deformation parameters gb:
    # There are 4*n parameters
    gb_keys = []
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                gb_keys.append((sigma, j, s))
                
    num_gb = len(gb_keys)
    print(f"Number of gb parameters: {num_gb}")
    
    # For each gb parameter, compute the 2-cocycle gamma^{(sigma, j, s)}(X_i, X_j)
    # gamma_tensor[p_idx][i][j][k] is coefficient of basis[k] in gamma^{(p_idx)}(basis[i], basis[j])
    gamma_tensor = []
    for p_idx, (sigma, j_gb, s_gb) in enumerate(gb_keys):
        gb_dict = dict(gb_zero)
        gb_dict[(sigma, j_gb, s_gb)] = sp.Rational(1)
        
        g_mat = [[[sp.Rational(0) for _ in range(dim)] for _ in range(dim)] for _ in range(dim)]
        for i in range(dim):
            for j in range(dim):
                _, vg = compute_bracket(basis[i], basis[j], n, basis, basis_map, gb_dict)
                for k in range(dim):
                    g_mat[i][j][k] = vg[k]
        gamma_tensor.append(g_mat)
        
    # Check 2-cocycle property for each gamma^{(p)}
    # The 2-cocycle condition in Lie superalgebra cohomology:
    # d\gamma(X, Y, Z) = 0
    # Let's verify this!
    
    # 3. Parameterize odd linear map f: g -> g
    # f maps g_0 -> g_1 (dim_even * dim_odd parameters)
    # f maps g_1 -> g_0 (dim_odd * dim_even parameters)
    # Total parameters in f: 2 * dim_even * dim_odd
    # Let phi be variables for f:
    # f(basis[j]) = sum_i phi[i, j] basis[i]
    # where if p(basis[j]) == 0, basis[i] has p=1
    # if p(basis[j]) == 1, basis[i] has p=0.
    
    f_vars = []
    f_map_indices = [] # list of (out_idx, in_idx)
    for j in range(dim):
        pj = basis[j][1]
        for i in range(dim):
            pi = basis[i][1]
            if pi != pj: # parity reversing
                f_map_indices.append((i, j))
                
    num_f_vars = len(f_map_indices)
    print(f"Number of odd map f parameters: {num_f_vars}")
    
    # Let's express (\delta f)(basis[i], basis[j]) in terms of f_vars:
    # (\delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    # Let X = basis[i], Y = basis[j].
    # f(Y) = sum_{k: (k, j) in f_indices} phi_{(k, j)} basis[k]
    # [X, f(Y)] = sum_k phi_{(k, j)} [basis[i], basis[k]] = sum_{k, l} phi_{(k, j)} C^l_{ik} basis[l]
    # f(X) = sum_{k: (k, i) in f_indices} phi_{(k, i)} basis[k]
    # [Y, f(X)] = sum_k phi_{(k, i)} [basis[j], basis[k]] = sum_{k, l} phi_{(k, i)} C^l_{jk} basis[l]
    # [X, Y] = sum_k C^k_{ij} basis[k]
    # f([X, Y]) = sum_k C^k_{ij} f(basis[k]) = sum_{k, l: (l, k) in f_indices} C^k_{ij} phi_{(l, k)} basis[l]
    
    # So (\delta f)(basis[i], basis[j])_l = 
    # (-1)^{pX} sum_k phi_{(k, j)} C^l_{ik}
    # - (-1)^{(pX+1)pY} sum_k phi_{(k, i)} C^l_{jk}
    # - sum_k C^k_{ij} phi_{(l, k)}
    
    # We want to see if for ANY gb (or any non-zero gb), there exists f such that:
    # \delta f = \gamma_{gb} (or c * \gamma_{gb})
    
    # Let's set up the linear system:
    # Independent pairs (i, j) for skew-supersymmetric 2-cochains:
    # For (i, j), (\delta f)(j, i) = -(-1)^{pX pY} (\delta f)(i, j).
    # We only need pairs i <= j (except when pX=pY=1 and i=j, [X, X] is not trivially 0!).
    # In general, let's collect all pairs (i, j) with 0 <= i <= j < dim (or all pairs and remove duplicates).
    
    equations = [] # list of dict: {f_var_idx: coeff, ... , 'gb_idx': coeff}
    # For each pair (i, j) and each component l:
    # \delta f(basis[i], basis[j])_l - sum_{p} gb_p * gamma_tensor[p][i][j][l] = 0
    
    pair_list = []
    for i in range(dim):
        for j in range(dim):
            if i < j:
                pair_list.append((i, j))
            elif i == j and basis[i][1] == 1:
                # odd generator with itself: [X, X] = 2 X^2 can be non-zero
                pair_list.append((i, j))
                
    print(f"Number of independent generator pairs (i, j): {len(pair_list)}")
    
    # Build matrix M: columns correspond to [phi_0, phi_1, ..., phi_{num_f-1}, gb_0, ..., gb_{num_gb-1}]
    # Row for each (i, j, l) where at least one entry is non-zero.
    rows = []
    f_idx_lookup = {pair: idx for idx, pair in enumerate(f_map_indices)}
    
    for (i, j) in pair_list:
        pX = basis[i][1]
        pY = basis[j][1]
        
        for l in range(dim):
            row = [sp.Rational(0)] * (num_f_vars + num_gb)
            is_nonzero = False
            
            # 1. (-1)^{pX} sum_k phi_{(k, j)} C^l_{ik}
            sign1 = (-1)**pX
            for k in range(dim):
                if (k, j) in f_idx_lookup and C[i][k][l] != 0:
                    var_idx = f_idx_lookup[(k, j)]
                    coeff = sign1 * C[i][k][l]
                    row[var_idx] += coeff
                    is_nonzero = True
                    
            # 2. - (-1)^{(pX+1)pY} sum_k phi_{(k, i)} C^l_{jk}
            sign2 = - ((-1)**((pX + 1) * pY))
            for k in range(dim):
                if (k, i) in f_idx_lookup and C[j][k][l] != 0:
                    var_idx = f_idx_lookup[(k, i)]
                    coeff = sign2 * C[j][k][l]
                    row[var_idx] += coeff
                    is_nonzero = True
                    
            # 3. - sum_k C^k_{ij} phi_{(l, k)}
            for k in range(dim):
                if (l, k) in f_idx_lookup and C[i][j][k] != 0:
                    var_idx = f_idx_lookup[(l, k)]
                    coeff = - C[i][j][k]
                    row[var_idx] += coeff
                    is_nonzero = True
                    
            # 4. - sum_p gb_p * gamma_tensor[p][i][j][l]
            for p_idx in range(num_gb):
                g_val = gamma_tensor[p_idx][i][j][l]
                if g_val != 0:
                    row[num_f_vars + p_idx] -= g_val
                    is_nonzero = True
                    
            if is_nonzero:
                rows.append(row)
                
    print(f"Total non-zero equation rows: {len(rows)}")
    
    # Solve linear system using Sympy Matrix
    M = sp.Matrix(rows)
    print(f"Matrix shape: {M.shape}")
    
    # We want to find the nullspace of M:
    # Any solution (phi, gb) in nullspace has \delta f = \gamma_{gb}.
    # Specifically, what is the projection of the nullspace onto the gb variables?
    # If the projection is {0}, then \delta f = \gamma_{gb} IMPLIES gb = 0!
    # That would mean NO non-zero gb deformation is a coboundary!
    
    rref_M, pivots = M.rref()
    print(f"Rank of matrix: {len(pivots)}")
    
    # Let's find nullspace
    nullspace = M.nullspace()
    print(f"Nullspace dimension: {len(nullspace)}")
    
    # Check the gb components of the nullspace vectors:
    gb_nullspace_vectors = []
    for v in nullspace:
        gb_part = [v[num_f_vars + p] for p in range(num_gb)]
        if any(x != 0 for x in gb_part):
            gb_nullspace_vectors.append((v, gb_part))
            
    print(f"Number of nullspace vectors with non-zero gb components: {len(gb_nullspace_vectors)}")
    
    if len(gb_nullspace_vectors) == 0:
        print(f"===> CONCLUSION for C({n+1}): gamma_gb is a coboundary IF AND ONLY IF gb = 0.")
        print(f"===> That is, ALL non-trivial gb deformations are NON-TRIVIAL (non-coboundary)!")
    else:
        print(f"===> Found non-zero gb deformations that are coboundaries!")
        for v, gb_part in gb_nullspace_vectors:
            print("gb_part:", gb_part)
            
    # Also check if each gamma^{(p)} individually is in the image of \delta:
    # That is, for each p, solve \delta f = gamma^{(p)}
    # Matrix of delta f alone:
    M_delta = sp.Matrix([row[:num_f_vars] for row in rows])
    rank_delta = len(M_delta.rref()[1])
    print(f"Rank of coboundary operator delta alone: {rank_delta} (out of {num_f_vars} f parameters)")
    print(f"Dimension of 1-cocycles (ker delta on f): {num_f_vars - rank_delta}")
    
    return {
        'n': n,
        'algebra': f'C({n+1})',
        'dim': dim,
        'dim_even': dim_even,
        'dim_odd': dim_odd,
        'num_gb': num_gb,
        'num_f_vars': num_f_vars,
        'rank_delta': rank_delta,
        'ker_delta': num_f_vars - rank_delta,
        'gb_in_coboundary_dim': len(gb_nullspace_vectors)
    }

if __name__ == '__main__':
    results = {}
    for n in [1, 2, 3]:
        res = analyze_triviality(n)
        results[f"C({n+1})"] = res
    with open('triviality_results.json', 'w') as out:
        json.dump(results, out, indent=2)
    print("\nSaved results to triviality_results.json")
