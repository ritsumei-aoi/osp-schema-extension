import json
import os
import sympy as sp
from collections import defaultdict
from fractions import Fraction

def analyze_triviality(n):
    # Load C_{n}_structure.json and C_{n}_gamma.json
    struct_path = f"data/C_{n}_structure.json"
    gamma_path = f"data/C_{n}_gamma.json"
    
    with open(struct_path) as f:
        s1 = json.load(f)
    with open(gamma_path) as f:
        s2 = json.load(f)
        
    basis = s1["basis"]["odd"] + s1["basis"]["even"]
    parity = s1["parity"]
    dim = len(basis)
    idx_to_name = {i: name for i, name in enumerate(basis)}
    name_to_idx = {name: i for i, name in enumerate(basis)}
    
    # Structure constants of g: [X, Y]
    c_0 = defaultdict(Fraction)
    for e in s1["structure_constants"]:
        c_0[(name_to_idx[e["X"]], name_to_idx[e["Y"]], name_to_idx[e["Z"]])] = Fraction(e["coeff"])
        
    # Gamma constants: gamma_{XY}^{Z, param}
    # param names
    gb_matrix = s2["inhomogeneous_deformation"]["gb_matrix"]
    param_names = [p for row in gb_matrix["parameter_names"] for p in row]
    param_to_idx = {p: i for i, p in enumerate(param_names)}
    num_params = len(param_names)
    
    gamma_table = defaultdict(dict) # (X, Y, Z): {param_idx: coeff}
    for e in s2["gamma_structure_constants"]:
        x = name_to_idx[e["X"]]
        y = name_to_idx[e["Y"]]
        z = name_to_idx[e["Z"]]
        p = param_to_idx[e["param"]]
        gamma_table[(x, y, z)][p] = Fraction(e["coeff"])
        
    # Unknowns for odd map f: phi_{ij} where parity[i] != parity[j]
    # f(Z_j) = sum_i phi_{ij} Z_i
    f_vars = []
    for j in range(dim):
        for i in range(dim):
            if parity[basis[i]] != parity[basis[j]]:
                f_vars.append((i, j))
    num_f_vars = len(f_vars)
    f_var_to_col = {v: c for c, v in enumerate(f_vars)}
    
    # We want to examine: (delta f)(Z_j, Z_k)^m
    # for all pairs j < k (by graded anti-symmetry, j < k or all pairs gives same)
    # Let's consider independent pairs (j, k)
    # Formula for (delta f)(Z_j, Z_k)^m:
    # (-1)^{p(Z_j)} [Z_j, f(Z_k)]^m - (-1)^{(p(Z_j)+1)p(Z_k)} [Z_k, f(Z_j)]^m - f([Z_j, Z_k])^m
    
    # Equations indexed by (j, k, m)
    eq_keys = []
    eq_rows_coboundary = [] # coefficients of phi_{ij}
    eq_rows_gamma = []      # coefficients of gb_param
    
    for j in range(dim):
        pX = parity[basis[j]]
        for k in range(j, dim): # j <= k
            pY = parity[basis[k]]
            for m in range(dim):
                # Target parity for delta f and gamma is (pX + pY + 1) % 2
                if parity[basis[m]] != (pX + pY + 1) % 2:
                    continue
                    
                row_f = [Fraction(0)] * num_f_vars
                row_g = [Fraction(0)] * num_params
                
                # Term 1: (-1)^{pX} sum_i phi_{ik} [Z_j, Z_i]^m
                sign1 = -1 if pX == 1 else 1
                for i in range(dim):
                    if (i, k) in f_var_to_col:
                        c_ji_m = c_0.get((j, i, m), 0)
                        if c_ji_m != 0:
                            row_f[f_var_to_col[(i, k)]] += sign1 * c_ji_m
                            
                # Term 2: - (-1)^{(pX+1)pY} sum_i phi_{ij} [Z_k, Z_i]^m
                sign2 = -1 if ((pX + 1) * pY) % 2 == 1 else 1
                for i in range(dim):
                    if (i, j) in f_var_to_col:
                        c_ki_m = c_0.get((k, i, m), 0)
                        if c_ki_m != 0:
                            row_f[f_var_to_col[(i, j)]] -= sign2 * c_ki_m
                            
                # Term 3: - sum_l c_{jk}^l phi_{ml}
                for l in range(dim):
                    if (m, l) in f_var_to_col:
                        c_jk_l = c_0.get((j, k, l), 0)
                        if c_jk_l != 0:
                            row_f[f_var_to_col[(m, l)]] -= c_jk_l
                            
                # Gamma part
                if (j, k, m) in gamma_table:
                    for p_idx, c_val in gamma_table[(j, k, m)].items():
                        row_g[p_idx] = c_val
                        
                # Only keep if either row_f or row_g is non-zero
                if any(x != 0 for x in row_f) or any(x != 0 for x in row_g):
                    eq_keys.append((j, k, m))
                    eq_rows_coboundary.append(row_f)
                    eq_rows_gamma.append(row_g)
                    
    print(f"\n==================== C({n+1}) = osp(2|{2*n}) ====================")
    print(f"dim(g) = {dim}, dim(Hom(g,g)_1) = {num_f_vars}, num_params = {num_params}")
    print(f"Total non-trivial 2-cochain equations: {len(eq_keys)}")
    
    # Convert to sympy matrices
    M_cob = sp.Matrix([[sp.Rational(x.numerator, x.denominator) for x in row] for row in eq_rows_coboundary])
    M_gam = sp.Matrix([[sp.Rational(x.numerator, x.denominator) for x in row] for row in eq_rows_gamma])
    
    rank_cob = M_cob.rank()
    print(f"Rank of Coboundary operator delta (dim of B^2_1): {rank_cob}")
    
    # Kernel of delta (odd derivations Der_1(g))
    dim_der = num_f_vars - rank_cob
    print(f"Dimension of odd 1-cocycles (odd derivations Der_1(g)): {dim_der}")
    
    # Augmented matrix [M_cob | M_gam]
    M_aug = sp.Matrix.hstack(M_cob, M_gam)
    rank_aug = M_aug.rank()
    print(f"Rank of augmented matrix [delta | gamma]: {rank_aug}")
    
    # If rank_aug == rank_cob, then ALL gamma are coboundaries!
    # If rank_aug == rank_cob + num_params, then NO non-zero gamma is a coboundary!
    diff = rank_aug - rank_cob
    print(f"Difference (rank_aug - rank_cob): {diff} (out of {num_params} deformation parameters)")
    
    if diff == num_params:
        print(f"RESULT FOR C({n+1}): The deformation gamma(gb) is a coboundary IF AND ONLY IF gb = 0!")
        print(f"That is, the deformation is NON-TRIVIAL for ANY non-zero gb!")
    elif diff == 0:
        print(f"RESULT FOR C({n+1}): The deformation gamma(gb) is TRIVIAL for ALL gb!")
    else:
        print(f"RESULT FOR C({n+1}): Trivial on a subspace of dimension {num_params - diff}!")
        # Find linear relations on gb for triviality
        # Compute nullspace of left nulls of M_cob applied to M_gam
        null_cob = M_cob.T.nullspace()
        # Each v in null_cob satisfies v^T * M_cob = 0
        # For solvability, v^T * M_gam * gb must = 0
        relations = []
        for v in null_cob:
            rel = (v.T * M_gam).tolist()[0]
            if any(x != 0 for x in rel):
                relations.append(rel)
        print(f"Number of independent conditions on gb: {len(sp.Matrix(relations).rref()[1])}")
        
    return rank_cob, rank_aug, diff

for n in [1, 2, 3]:
    analyze_triviality(n)
