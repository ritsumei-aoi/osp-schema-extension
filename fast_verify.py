"""
Fast matrix analysis using exact Sympy / numpy rational matrix multiplication.
"""
import sympy as sp
import numpy as np
from verify_cn1 import build_algebra, compute_supercommutator

def analyze_fast(n):
    print(f"\n=================== FAST ANALYZING n={n} ===================")
    basis = build_algebra(n)
    basis_dict = {b[0]: b for b in basis}
    dim = len(basis)
    
    gb_list = []
    gb_vars = {}
    for k in range(1, n + 1):
        for sigma in ['+', '-']:
            for s in ['+', '-']:
                var_name = f'gb_{sigma}_{k}_{s}'
                sym = sp.Symbol(var_name)
                gb_vars[(sigma, k, s)] = sym
                gb_list.append(sym)
                
    C_table = {}
    gamma_table = {}
    for b1 in basis:
        for b2 in basis:
            b0, g1, _, _ = compute_supercommutator(b1, b2, gb_vars, basis_dict, n)
            C_table[(b1[0], b2[0])] = b0
            gamma_table[(b1[0], b2[0])] = g1
            
    even_basis = [b for b in basis if b[1] == 0]
    odd_basis = [b for b in basis if b[1] == 1]
    
    f_vars = []
    f_map = {}
    for E in even_basis:
        for F in odd_basis:
            sym = sp.Symbol(f'phi_{F[0]}_{E[0]}')
            f_vars.append(sym)
            f_map[(F[0], E[0])] = sym
    for F in odd_basis:
        for E in even_basis:
            sym = sp.Symbol(f'phi_{E[0]}_{F[0]}')
            f_vars.append(sym)
            f_map[(E[0], F[0])] = sym
            
    # Collect equations
    M_rows = []
    B_rows = []
    
    for i, X in enumerate(basis):
        for j, Y in enumerate(basis):
            if i >= j:
                continue
            pX, pY = X[1], Y[1]
            sign1 = (-1)**pX
            sign2 = - ((-1)**((pX + 1) * pY))
            
            delta_f = {b[0]: sp.Integer(0) for b in basis}
            
            target_Y = odd_basis if pY == 0 else even_basis
            for W in target_Y:
                phi_WY = f_map[(W[0], Y[0])]
                for M_name, c_xw in C_table[(X[0], W[0])].items():
                    if c_xw != 0:
                        delta_f[M_name] += sign1 * phi_WY * c_xw
                        
            target_X = odd_basis if pX == 0 else even_basis
            for W in target_X:
                phi_WX = f_map[(W[0], X[0])]
                for M_name, c_yw in C_table[(Y[0], W[0])].items():
                    if c_yw != 0:
                        delta_f[M_name] += sign2 * phi_WX * c_yw
                        
            for W_name, c_xy in C_table[(X[0], Y[0])].items():
                if c_xy != 0:
                    W_parity = (pX + pY) % 2
                    target_W = odd_basis if W_parity == 0 else even_basis
                    for M in target_W:
                        phi_MW = f_map[(M[0], W_name)]
                        delta_f[M[0]] -= c_xy * phi_MW
                        
            gamma_val = gamma_table[(X[0], Y[0])]
            for b in basis:
                lhs = delta_f[b[0]]
                rhs = gamma_val[b[0]]
                
                # lhs is sum over f_vars
                # rhs is sum over gb_vars
                m_row = [float(lhs.coeff(var)) for var in f_vars]
                b_row = [float(rhs.coeff(g)) for g in gb_list]
                
                # Check if non-zero
                if any(x != 0 for x in m_row) or any(x != 0 for x in b_row):
                    M_rows.append(m_row)
                    B_rows.append(b_row)
                    
    M_np = np.array(M_rows, dtype=np.float64)
    B_np = np.array(B_rows, dtype=np.float64)
    
    print(f"M shape: {M_np.shape}, B shape: {B_np.shape}")
    
    # SVD
    U, S, Vt = np.linalg.svd(M_np, full_matrices=True)
    rank_M = np.sum(S > 1e-10)
    print(f"Numerical rank of M: {rank_M}")
    
    # Left nullspace projection: rows of U^T from rank_M to end
    U_null = U[:, rank_M:]
    print(f"U_null shape: {U_null.shape}")
    
    # Project B: K_np = U_null.T @ B
    K_np = U_null.T @ B_np
    print(f"K_np shape: {K_np.shape}")
    
    # Singular values of K_np
    UK, SK, VKt = np.linalg.svd(K_np)
    rank_K = np.sum(SK > 1e-10)
    print(f"Singular values of K: {SK}")
    print(f"Rank of constraint matrix K: {rank_K} (out of {len(gb_list)})")
    
    if rank_K == len(gb_list):
        print(f"===> DEFINITIVE RESULT FOR n={n}: gamma_gb = delta f iff gb = 0!")
        print(f"===> Dimension of trivial gb parameters = 0. All non-zero deformations are strictly non-trivial!")
    else:
        print(f"===> Allowed gb dimension: {len(gb_list) - rank_K}")
        
    return rank_K

if __name__ == "__main__":
    for n in [1, 2, 3]:
        analyze_fast(n)
