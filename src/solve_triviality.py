import json
import sympy as sp
import numpy as np
from collections import defaultdict

def analyze_triviality(n):
    with open(f"data/C_{n}_gamma.json", "r") as f:
        schema2 = json.load(f)
    with open(f"data/C_{n}_coboundary.json", "r") as f:
        schema4 = json.load(f)
        
    gb_params = schema2['gb_matrix']['parameters']
    phi_params = schema4['f_map_parameters']
    
    # parse gamma
    gamma_eqs = defaultdict(int)
    for entry in schema2['inhomogeneous_deformation']:
        key = (entry['X'], entry['Y'], entry['Z'])
        gamma_eqs[key] = sp.sympify(entry['gamma_coeff'])
        
    # parse coboundary
    coboundary_eqs = defaultdict(int)
    for entry in schema4['coboundary_deformation']:
        key = (entry['X'], entry['Y'], entry['Z'])
        coboundary_eqs[key] = sp.sympify(entry['coboundary_coeff'])
        
    all_keys = set(gamma_eqs.keys()) | set(coboundary_eqs.keys())
    
    print(f"\n--- Analyzing C({n+1}) ---")
    print(f"Number of equations: {len(all_keys)}")
    print(f"Number of phi variables: {len(phi_params)}")
    print(f"Number of gb parameters: {len(gb_params)}")
    
    # We want to find constraints on gb such that coboundary_eqs = gamma_eqs
    # M * phi = G * gb
    
    M_rows = []
    G_rows = []
    
    phi_syms = [sp.Symbol(p) for p in phi_params]
    gb_syms = [sp.Symbol(p) for p in gb_params]
    
    for key in all_keys:
        cb_expr = coboundary_eqs[key]
        gm_expr = gamma_eqs[key]
        
        # Extract coefficients for M
        m_row = []
        if isinstance(cb_expr, sp.Expr):
            cb_expr = sp.expand(cb_expr)
            for p in phi_syms:
                m_row.append(float(cb_expr.coeff(p)))
        else:
            m_row = [0.0] * len(phi_syms)
        M_rows.append(m_row)
        
        # Extract coefficients for G
        g_row = []
        if isinstance(gm_expr, sp.Expr):
            gm_expr = sp.expand(gm_expr)
            for p in gb_syms:
                g_row.append(float(gm_expr.coeff(p)))
        else:
            g_row = [0.0] * len(gb_syms)
        G_rows.append(g_row)
        
    M_float = np.array(M_rows, dtype=float)
    G_float = np.array(G_rows, dtype=float)
    
    rank_M = np.linalg.matrix_rank(M_float)
    
    # Check intersection of ColumnSpace(M) and ColumnSpace(G)
    # We want M * phi - G * gb = 0 to have non-zero gb solutions.
    # Matrix A = [M, G]
    A = np.hstack((M_float, G_float))
    rank_A = np.linalg.matrix_rank(A)
    rank_G = np.linalg.matrix_rank(G_float)
    
    print(f"Rank of M: {rank_M}")
    print(f"Rank of G: {rank_G}")
    print(f"Rank of [M, G]: {rank_A}")
    
    U, S, Vh = np.linalg.svd(M_float.T)
    null_space = Vh[rank_M:]
    L = null_space.T
    if L.size > 0:
        # Find the vector with minimum non-zero entries
        # Or just pick the first vector in L and find large entries
        v = L[:, 0]
        # Clean up v by thresholding
        v[np.abs(v) < 1e-9] = 0
        
        # Scale to make it nice
        idx = np.nonzero(v)[0]
        if len(idx) > 0:
            scale = v[idx[0]]
            v = v / scale
            v = np.round(v, 4)
            
            print("\nExample constraint equation (sum of c_i * Eq_i = 0):")
            keys = list(all_keys)
            for i in idx:
                print(f"  {v[i]:.2f} * {keys[i]}")
            
            # The right hand side is v^T * G_float * gb
            rhs = np.dot(v, G_float)
            rhs = np.round(rhs, 4)
            rhs_expr = sum(rhs[j] * gb_syms[j] for j in range(len(gb_syms)) if abs(rhs[j]) > 1e-9)
            print(f"This must equal: {rhs_expr} == 0")

if __name__ == "__main__":
    for n in [1, 2, 3]:
        analyze_triviality(n)
