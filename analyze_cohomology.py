"""
Detailed cohomology and deformation analysis for n = 1, 2, 3
"""
import sympy as sp
from verify_cn1 import get_algebra
from verify_brackets import compute_brackets
from solve_triviality import compute_delta_f
import json

def check_2cocycle(alg, bracket_0, gamma_def):
    """
    Check the 2-cocycle condition for gamma in Lie superalgebra cohomology:
    d gamma (X, Y, Z) = 0
    where for odd 2-cochain gamma:
    d gamma(X, Y, Z) = 
      (-1)^(p(X)p(Z)) [X, gamma(Y, Z)] + (-1)^(p(X)p(Z) + p(X)) gamma(X, [Y, Z])
      + (-1)^(p(Y)p(X)) [Y, gamma(Z, X)] + (-1)^(p(Y)p(X) + p(Y)) gamma(Y, [Z, X])
      + (-1)^(p(Z)p(Y)) [Z, gamma(X, Y)] + (-1)^(p(Z)p(Y) + p(Z)) gamma(Z, [X, Y]) = 0
    Or alternatively, deformed Jacobi identity at linear order in kappa:
    Jacobi([X, Y]_gamma, Z) + cyclic = 0
    """
    dim_g = alg['dim_g']
    generators = alg['generators']
    p = [g['parity'] for g in generators]
    
    # Let's check the deformed Jacobi identity at linear order in kappa:
    # J(X, Y, Z) = (-1)^(p(X)p(Z)) [X, [Y, Z]_gamma]_gamma + cyclic = 0
    # Linear order in kappa gives:
    # (-1)^(p(X)p(Z)) ( [X, gamma(Y, Z)]_0 + gamma(X, [Y, Z]_0) ) + cyclic = 0
    
    jacobi_linear_ok = True
    violating_triplets = []
    
    for i in range(dim_g):
        for j in range(dim_g):
            for k in range(dim_g):
                # We need [X, [Y, Z]_gamma] at order kappa:
                # [X, [Y, Z]_0 + kappa gamma(Y, Z)]
                # = [X, [Y, Z]_0]_0 + kappa ( [X, gamma(Y,Z)]_0 + gamma(X, [Y,Z]_0) )
                
                # Term 1: [X, gamma(Y, Z)]_0
                g_jk = gamma_def[j][k]
                term1a = sp.zeros(dim_g, 1)
                for m in range(dim_g):
                    if g_jk[m] != 0:
                        term1a += g_jk[m] * bracket_0[i][m]
                        
                # Term 1b: gamma(X, [Y, Z]_0)
                b_jk = bracket_0[j][k]
                term1b = sp.zeros(dim_g, 1)
                for m in range(dim_g):
                    if b_jk[m] != 0:
                        term1b += b_jk[m] * gamma_def[i][m]
                        
                cyc1 = (term1a + term1b) * ((-1)**(p[i] * p[k]))
                
                # Term 2: [Y, gamma(Z, X)]_0 + gamma(Y, [Z, X]_0)
                g_ki = gamma_def[k][i]
                term2a = sp.zeros(dim_g, 1)
                for m in range(dim_g):
                    if g_ki[m] != 0:
                        term2a += g_ki[m] * bracket_0[j][m]
                b_ki = bracket_0[k][i]
                term2b = sp.zeros(dim_g, 1)
                for m in range(dim_g):
                    if b_ki[m] != 0:
                        term2b += b_ki[m] * gamma_def[j][m]
                cyc2 = (term2a + term2b) * ((-1)**(p[j] * p[i]))
                
                # Term 3: [Z, gamma(X, Y)]_0 + gamma(Z, [X, Y]_0)
                g_ij = gamma_def[i][j]
                term3a = sp.zeros(dim_g, 1)
                for m in range(dim_g):
                    if g_ij[m] != 0:
                        term3a += g_ij[m] * bracket_0[k][m]
                b_ij = bracket_0[i][j]
                term3b = sp.zeros(dim_g, 1)
                for m in range(dim_g):
                    if b_ij[m] != 0:
                        term3b += b_ij[m] * gamma_def[k][m]
                cyc3 = (term3a + term3b) * ((-1)**(p[k] * p[j]))
                
                tot = cyc1 + cyc2 + cyc3
                if any(sp.simplify(val) != 0 for val in tot):
                    jacobi_linear_ok = False
                    violating_triplets.append((generators[i]['name'], generators[j]['name'], generators[k]['name']))
                    
    print(f"2-cocycle condition for gamma_gb: {'PASSED' if jacobi_linear_ok else 'FAILED'}")
    if not jacobi_linear_ok:
        print(f"Violating triplets count: {len(violating_triplets)}")
    return jacobi_linear_ok

def analyze_triviality_complete(n):
    print(f"\n=======================================================")
    print(f"       ANALYZING C({n+1}) = osp(2|{2*n})")
    print(f"=======================================================")
    alg = get_algebra(n)
    dim_g = alg['dim_g']
    generators = alg['generators']
    p = [g['parity'] for g in generators]
    
    print(f"Algebra dim: {dim_g} (Even: {sum(1 for x in p if x==0)}, Odd: {sum(1 for x in p if x==1)})")
    
    bracket_0, gamma_def = compute_brackets(alg)
    check_2cocycle(alg, bracket_0, gamma_def)
    
    # Number of pairs (i, j) with i <= j
    pairs = [(i, j) for i in range(dim_g) for j in range(i, dim_g)]
    # Target space of 2-cochains: dim = len(pairs) * dim_g
    
    # 1. Map odd linear maps f to delta f (coboundaries)
    # Basis of odd maps f: E_{a, b} where p[a] != p[b]
    odd_map_basis = []
    for j in range(dim_g):
        for i in range(dim_g):
            if p[i] != p[j]:
                odd_map_basis.append((i, j))
                
    dim_f_space = len(odd_map_basis)
    print(f"Dimension of odd linear maps Hom(g, g)_odd: {dim_f_space}")
    
    # We construct the matrix representing delta: Hom(g, g)_odd -> C^2(g, g)_odd
    # For each basis map E_{a, b} (f(Z_b) = Z_a, f(Z_k) = 0 for k != b):
    # Compute delta(E_{a, b})
    
    # Vector of cochain: indexed by ((i, j), k)
    cochain_dim = len(pairs) * dim_g
    
    delta_matrix_cols = []
    for col_idx, (a, b) in enumerate(odd_map_basis):
        # Construct phi matrix with 1 at (a, b) and 0 elsewhere
        phi = sp.zeros(dim_g, dim_g)
        phi[a, b] = 1
        d_f = compute_delta_f(alg, phi, bracket_0)
        
        # Flatten d_f into vector
        col_vec = []
        for i, j in pairs:
            for k in range(dim_g):
                col_vec.append(d_f[i][j][k])
        delta_matrix_cols.append(col_vec)
        
    # Coboundary matrix M_delta: shape (cochain_dim, dim_f_space)
    # Columns are delta(E_{a,b})
    M_delta = sp.Matrix(delta_matrix_cols).T
    print(f"Coboundary matrix shape: {M_delta.shape}")
    
    # Rank of coboundary operator
    # Note: rank(M_delta) = dim B^2(g, g)_odd
    # Also dim Z^1(g, g)_odd (odd derivations) = dim_f_space - rank(M_delta)
    r = M_delta.rank()
    print(f"dim B^2(g, g)_odd (rank of coboundary operator): {r}")
    print(f"dim Der(g, g)_odd (1-cocycles / odd derivations): {dim_f_space - r}")
    
    # Now, express gamma_def as linear combination of gb parameters
    gb_list = list(alg['gb_symbols'].values())
    print(f"Number of gb parameters: {len(gb_list)}")
    
    # For each gb parameter, compute gamma vector
    gamma_cols = []
    for sym in gb_list:
        sub_dict = {s: (1 if s == sym else 0) for s in gb_list}
        col_vec = []
        for i, j in pairs:
            for k in range(dim_g):
                val = gamma_def[i][j][k].subs(sub_dict)
                col_vec.append(val)
        gamma_cols.append(col_vec)
        
    M_gamma = sp.Matrix(gamma_cols).T
    print(f"Gamma matrix shape: {M_gamma.shape}")
    r_gamma = M_gamma.rank()
    print(f"Rank of gamma deformation space: {r_gamma}")
    
    # Check if any non-zero linear combination of gamma_cols lies in Col(M_delta)
    # Augmented matrix: [M_delta | M_gamma]
    M_aug = M_delta.row_join(M_gamma)
    r_aug = M_aug.rank()
    print(f"Rank of [M_delta | M_gamma]: {r_aug}")
    
    # By linear algebra:
    # dim(Col(M_delta) intersect Col(M_gamma)) = rank(M_delta) + rank(M_gamma) - rank([M_delta | M_gamma])
    dim_intersection = r + r_gamma - r_aug
    print(f"dim( B^2(g, g)_odd INTERSECT Im(gamma_gb) ) = {dim_intersection}")
    
    if dim_intersection == 0:
        print(">>> CONCLUSION: The intersection is {0}. NO NON-ZERO gb DEFORMATION IS A COBOUNDARY! <<<")
        print(">>> Therefore, gamma_gb is TRIVIAL IF AND ONLY IF gb = 0. <<<")
    else:
        print(f">>> Non-trivial intersection found of dimension {dim_intersection}! <<<")
        # Find the nullspace of augmented matrix to get the relations
        null = M_aug.nullspace()
        print(f"Nullspace vectors count: {len(null)}")
        for v in null:
            gb_part = v[dim_f_space:]
            if any(val != 0 for val in gb_part):
                print("gb coefficients for trivial deformation:", list(zip(gb_list, gb_part)))
                
    return {
        'n': n,
        'dim_g': dim_g,
        'dim_f_space': dim_f_space,
        'rank_B2': r,
        'dim_Der': dim_f_space - r,
        'num_gb': len(gb_list),
        'rank_gamma': r_gamma,
        'rank_aug': r_aug,
        'dim_intersection': dim_intersection
    }

res1 = analyze_triviality_complete(1)
res2 = analyze_triviality_complete(2)
