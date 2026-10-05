"""
Linear algebra analysis of gamma = delta f.
"""
import sympy as sp
from verify_cn1 import build_algebra, compute_supercommutator

def analyze_system(n):
    print(f"\n=================== ANALYZING n={n} ===================")
    basis = build_algebra(n)
    basis_dict = {b[0]: b for b in basis}
    dim = len(basis)
    
    gb_vars = {}
    gb_list = []
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
    
    # f_vars:
    # phi_F_E for F in odd, E in even: f(E) = sum phi_F_E F
    # phi_E_F for E in even, F in odd: f(F) = sum phi_E_F E
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
            
    # Build linear system: for each pair (X, Y) with i < j, and each basis element Z:
    # (delta f)(X, Y)_Z = gamma(X, Y)_Z
    # LHS is linear in f_vars, RHS is linear in gb_vars.
    eqs = []
    
    for i, X in enumerate(basis):
        for j, Y in enumerate(basis):
            if i >= j:
                continue
            pX, pY = X[1], Y[1]
            sign1 = (-1)**pX
            sign2 = - ((-1)**((pX + 1) * pY))
            
            delta_f = {b[0]: sp.Integer(0) for b in basis}
            
            # Term 1: (-1)^{pX} [X, f(Y)]
            target_Y = odd_basis if pY == 0 else even_basis
            for W in target_Y:
                phi_WY = f_map[(W[0], Y[0])]
                for M_name, c_xw in C_table[(X[0], W[0])].items():
                    if c_xw != 0:
                        delta_f[M_name] += sign1 * phi_WY * c_xw
                        
            # Term 2: - (-1)^{(pX+1)pY} [Y, f(X)]
            target_X = odd_basis if pX == 0 else even_basis
            for W in target_X:
                phi_WX = f_map[(W[0], X[0])]
                for M_name, c_yw in C_table[(Y[0], W[0])].items():
                    if c_yw != 0:
                        delta_f[M_name] += sign2 * phi_WX * c_yw
                        
            # Term 3: - f([X, Y])
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
                eq = lhs - rhs
                if eq != 0:
                    eqs.append((eq, lhs, rhs, X[0], Y[0], b[0]))
                    
    print(f"Total non-trivial equation entries: {len(eqs)}")
    
    # Form matrix M where M * f = b(gb)
    # Each row is an equation: lhs - rhs = 0 => lhs = rhs
    rows = []
    rhs_rows = []
    for eq, lhs, rhs, x_name, y_name, z_name in eqs:
        row = [lhs.coeff(var) for var in f_vars]
        rows.append(row)
        rhs_rows.append(rhs)
        
    M = sp.Matrix(rows)
    b = sp.Matrix(rhs_rows)
    
    print(f"Matrix M shape: {M.shape}")
    print(f"Number of f variables: {len(f_vars)}")
    print(f"Number of gb variables: {len(gb_list)}")
    
    # Compute rank of M
    rank_M = M.rank()
    print(f"Rank of M: {rank_M}")
    
    # Check consistency: M * f = b(gb)
    # The augmented matrix [M | b] rank must equal rank_M for consistency.
    # Alternatively, use nullspace of M.T to find constraints on b(gb).
    # If v in nullspace(M.T), then v^T M = 0 => v^T b(gb) = 0 is a constraint on gb!
    null_MT = M.T.nullspace()
    print(f"Dimension of left nullspace of M (constraints on rhs): {len(null_MT)}")
    
    constraints = []
    for v in null_MT:
        # v is column vector of length len(eqs)
        constraint = sum(v[k] * rhs_rows[k] for k in range(len(rhs_rows)))
        constraint = sp.simplify(constraint)
        if constraint != 0:
            constraints.append(constraint)
            
    print(f"Number of non-zero constraints on gb: {len(constraints)}")
    
    # Unique linear constraints on gb:
    # Let's put constraints into a matrix K * gb = 0
    gb_eq_rows = []
    for c in constraints:
        row = [c.coeff(g) for g in gb_list]
        gb_eq_rows.append(row)
        
    if gb_eq_rows:
        K = sp.Matrix(gb_eq_rows)
        print(f"Constraint matrix K shape: {K.shape}, rank: {K.rank()}")
        # Check nullspace of K (allowed gb parameters for triviality)
        null_K = K.nullspace()
        print(f"Dimension of allowed gb subspace (trivial deformations): {len(null_K)}")
        if len(null_K) == 0:
            print("===> RESULT: gamma_gb = delta f iff gb = 0!")
            print("===> Therefore, NO non-trivial inhomogeneous deformation is a coboundary!")
            print("===> The inhomogeneous deformation is NON-TRIVIAL for all non-zero gb!")
        else:
            print(f"===> Allowed gb vectors: {null_K}")
    else:
        print("===> No constraints on gb! All deformations are coboundaries!")

if __name__ == "__main__":
    for n in [1, 2, 3]:
        analyze_system(n)
