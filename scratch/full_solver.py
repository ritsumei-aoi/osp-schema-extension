import json
import numpy as np
import sympy as sp
from sympy import symbols, Matrix, zeros, simplify, solve, Symbol, eye

def comm_b(b1, b2):
    # b1 = (j1, s1), b2 = (j2, s2)
    # [b1, b2] = Omega(s1, s2) if j1 == j2 else 0
    # s in {1: '+', -1: '-'}
    # [b-, b+] = 1 => [b-, b+] = 1, [b+, b-] = -1
    j1, s1 = b1
    j2, s2 = b2
    if j1 != j2:
        return 0
    if s1 == -1 and s2 == 1:
        return 1
    elif s1 == 1 and s2 == -1:
        return -1
    return 0

def solve_cn1(n):
    print(f"\n==================================================")
    print(f"  FULL SOLVER FOR C({n+1}) (n = {n})")
    print(f"==================================================")

    # Bosons: (j, s) where j in 1..n, s in {1 (+), -1 (-)}
    bosons = []
    for j in range(1, n + 1):
        bosons.append((j, 1))
        bosons.append((j, -1))
        
    num_bosons = len(bosons)

    # Even basis:
    # Index 0: J0
    # Index 1..: B_{(j1,s1),(j2,s2)} for (j1,s1) <= (j2,s2)
    # B_{b1, b2} = 1/2 (b1 b2 + b2 b1)
    even_basis = ['J0']
    boson_pairs = []
    for i in range(num_bosons):
        for k in range(i, num_bosons):
            b1, b2 = bosons[i], bosons[k]
            boson_pairs.append((b1, b2))
            even_basis.append((b1, b2))
            
    dim_even = len(even_basis)

    # Odd basis:
    # F_{(sigma, j, s)} = a1^sigma b_j^s where sigma in {1 (+), -1 (-)}
    odd_basis = []
    for sigma in [1, -1]:
        for j in range(1, n + 1):
            for s in [1, -1]:
                odd_basis.append((sigma, j, s))
                
    dim_odd = len(odd_basis)
    dim_total = dim_even + dim_odd

    # gb parameters:
    gb_syms = {}
    gb_list = []
    for sigma_val, sigma_str in [(1, '+'), (-1, '-')]:
        for j in range(1, n + 1):
            for s_val, s_str in [(1, '+'), (-1, '-')]:
                sym = Symbol(f"gb_{sigma_str}_{j}_{s_str}")
                gb_syms[(sigma_val, j, s_val)] = sym
                gb_list.append(sym)

    num_gb = len(gb_list)
    print(f"dim_even = {dim_even}, dim_odd = {dim_odd}, dim_total = {dim_total}")
    print(f"gb parameters ({len(gb_list)}): {gb_list}")

    # Helper to express b_A b_B in basis of even_basis
    # b_A b_B = 1/2 (b_A b_B + b_B b_A) + 1/2 [b_A, b_B] = B_{min, max} + 1/2 comm_b(b_A, b_B)
    # Note: 1/2 comm_b is a scalar constant.
    def b_prod_to_even(bA, bB):
        # returns dict of {basis_index: coeff}
        res = {}
        # Find B_{min, max}
        iA = bosons.index(bA)
        iB = bosons.index(bB)
        if iA <= iB:
            pair = (bA, bB)
        else:
            pair = (bB, bA)
        idx = even_basis.index(pair)
        res[idx] = 1
        return res

    # 1. Compute undeformed brackets [X, Y]_0
    # Even-Even:
    # [J0, J0] = 0
    # [J0, B] = 0
    # [B_{b1,b2}, B_{b3,b4}] = 1/2 [b1 b2 + b2 b1, b3 b4]
    # Using [b1 b2, b3 b4] = b1 [b2, b3] b4 + b1 b3 [b2, b4] + [b1, b3] b4 b2 + b3 [b1, b4] b2
    def bracket_even_even(idx1, idx2):
        res = zeros(dim_even, 1)
        if idx1 == 0 or idx2 == 0:
            return res
        b1, b2 = even_basis[idx1]
        b3, b4 = even_basis[idx2]
        
        # [b1 b2, b3 b4] + [b2 b1, b3 b4] = 2 [b1 b2, b3 b4]
        # So [B_{b1,b2}, B_{b3,b4}] = 1/2 [b1 b2, b3 b4] + 1/2 [b1 b2, b4 b3]
        # Let's compute [bA bB, bC bD]:
        def comm_quad(bA, bB, bC, bD):
            # returns dict of even_basis index -> coeff
            d = {}
            # term 1: comm_b(bB, bC) * bA bD
            c1 = comm_b(bB, bC)
            if c1 != 0:
                for idx, val in b_prod_to_even(bA, bD).items():
                    d[idx] = d.get(idx, 0) + c1 * val
            # term 2: comm_b(bB, bD) * bA bC
            c2 = comm_b(bB, bD)
            if c2 != 0:
                for idx, val in b_prod_to_even(bA, bC).items():
                    d[idx] = d.get(idx, 0) + c2 * val
            # term 3: comm_b(bA, bC) * bB bD
            c3 = comm_b(bA, bC)
            if c3 != 0:
                for idx, val in b_prod_to_even(bB, bD).items():
                    d[idx] = d.get(idx, 0) + c3 * val
            # term 4: comm_b(bA, bD) * bB bC
            c4 = comm_b(bA, bD)
            if c4 != 0:
                for idx, val in b_prod_to_even(bB, bC).items():
                    d[idx] = d.get(idx, 0) + c4 * val
            return d

        # B12 = 1/2(b1 b2 + b2 b1), B34 = 1/2(b3 b4 + b4 b3)
        # [B12, B34] = 1/4 (comm(b1,b2,b3,b4) + comm(b1,b2,b4,b3) + comm(b2,b1,b3,b4) + comm(b2,b1,b4,b3))
        d_tot = {}
        for (A, B) in [(b1, b2), (b2, b1)]:
            for (C, D) in [(b3, b4), (b4, b3)]:
                q = comm_quad(A, B, C, D)
                for idx, val in q.items():
                    d_tot[idx] = d_tot.get(idx, 0) + val / 4
        for idx, val in d_tot.items():
            res[idx, 0] = val
        return res

    # Even-Odd:
    # [J0, F_{\sigma, j, s}] = \sigma F_{\sigma, j, s}
    # [B_{b1,b2}, F_{\sigma, j2, s2}] = 1/2 [b1 b2 + b2 b1, b_{j2}^{s2}] a1^\sigma
    # = 1/2 (b1 [b2, b_{j2}^{s2}] + [b1, b_{j2}^{s2}] b2 + b2 [b1, b_{j2}^{s2}] + [b2, b_{j2}^{s2}] b1) a1^\sigma
    # = (comm_b(b2, b_{j2}^{s2}) b1 + comm_b(b1, b_{j2}^{s2}) b2) a1^\sigma
    def bracket_even_odd(idx_even, idx_odd):
        res = zeros(dim_odd, 1)
        sigma, j2, s2 = odd_basis[idx_odd]
        b_target = (j2, s2)
        if idx_even == 0:
            # J0
            res[idx_odd, 0] = sigma
            return res
        b1, b2 = even_basis[idx_even]
        c2 = comm_b(b2, b_target)
        c1 = comm_b(b1, b_target)
        if c2 != 0:
            # c2 * a1^\sigma b1 = c2 * F_{\sigma, b1}
            idx_f1 = odd_basis.index((sigma, b1[0], b1[1]))
            res[idx_f1, 0] += c2
        if c1 != 0:
            # c1 * a1^\sigma b2 = c1 * F_{\sigma, b2}
            idx_f2 = odd_basis.index((sigma, b2[0], b2[1]))
            res[idx_f2, 0] += c1
        return res

    # Odd-Odd:
    # {F_{\sigma1, j1, s1}, F_{\sigma2, j2, s2}} = \delta_{\sigma1, -\sigma2} b_{j1}^{s1} b_{j2}^{s2}
    def bracket_odd_odd(idx_odd1, idx_odd2):
        res = zeros(dim_even, 1)
        sigma1, j1, s1 = odd_basis[idx_odd1]
        sigma2, j2, s2 = odd_basis[idx_odd2]
        if sigma1 == -sigma2:
            b1 = (j1, s1)
            b2 = (j2, s2)
            for idx, val in b_prod_to_even(b1, b2).items():
                res[idx, 0] += val
        return res

    # 2. Deformed 2-cocycle \gamma_{gb}
    # \gamma(even, even) = 0
    # \gamma(J0, F_{\sigma, j, s}) = \sigma gb_{\sigma, j, s} J0 (up to scalar)
    # \gamma(B_{b1,b2}, F_{\sigma, j2, s2}) = - gb_{\sigma, b1} b2 b_{j2}^{s2} - gb_{\sigma, b2} b1 b_{j2}^{s2}
    # \gamma(F_{\sigma1, b1}, F_{\sigma2, b2}) = - gb_{\sigma2, b1} F_{\sigma1, b2} - gb_{\sigma1, b2} F_{\sigma2, b1}
    def gamma_even_odd(idx_even, idx_odd):
        res = zeros(dim_even, 1)
        sigma, j2, s2 = odd_basis[idx_odd]
        if idx_even == 0:
            # J0
            gb_val = gb_syms[(sigma, j2, s2)]
            res[0, 0] = sigma * gb_val
            return res
        b1, b2 = even_basis[idx_even]
        gb1 = gb_syms[(sigma, b1[0], b1[1])]
        gb2 = gb_syms[(sigma, b2[0], b2[1])]
        b_target = (j2, s2)
        # - gb1 * b2 b_target - gb2 * b1 b_target
        for idx, val in b_prod_to_even(b2, b_target).items():
            res[idx, 0] -= gb1 * val
        for idx, val in b_prod_to_even(b1, b_target).items():
            res[idx, 0] -= gb2 * val
        return res

    def gamma_odd_odd(idx_odd1, idx_odd2):
        res = zeros(dim_odd, 1)
        sigma1, j1, s1 = odd_basis[idx_odd1]
        sigma2, j2, s2 = odd_basis[idx_odd2]
        b1 = (j1, s1)
        b2 = (j2, s2)
        gb_sig2_b1 = gb_syms[(sigma2, j1, s1)]
        gb_sig1_b2 = gb_syms[(sigma1, j2, s2)]
        
        # - gb_{\sigma2, b1} F_{\sigma1, b2} - gb_{\sigma1, b2} F_{\sigma2, b1}
        idx_f_sig1_b2 = odd_basis.index((sigma1, b2[0], b2[1]))
        idx_f_sig2_b1 = odd_basis.index((sigma2, b1[0], b1[1]))
        
        res[idx_f_sig1_b2, 0] -= gb_sig2_b1
        res[idx_f_sig2_b1, 0] -= gb_sig1_b2
        return res

    # Now let's set up the map f: g -> g.
    # f_0: g_0 -> g_1 (dim_odd x dim_even variables)
    # f_1: g_1 -> g_0 (dim_even x dim_odd variables)
    # Total map f variables: 2 * dim_even * dim_odd
    
    # f_0 matrix variables: phi_{odd, even}
    # f_1 matrix variables: psi_{even, odd}
    
    f0_vars = {}
    f1_vars = {}
    f_var_list = []
    for i_odd in range(dim_odd):
        for i_even in range(dim_even):
            sym = Symbol(f"phi_{i_odd}_{i_even}")
            f0_vars[(i_odd, i_even)] = sym
            f_var_list.append(sym)
            
    for i_even in range(dim_even):
        for i_odd in range(dim_odd):
            sym = Symbol(f"psi_{i_even}_{i_odd}")
            f1_vars[(i_even, i_odd)] = sym
            f_var_list.append(sym)

    num_f_vars = len(f_var_list)
    print(f"Number of f map variables: {num_f_vars}")

    # Now let's build the coboundary system: \delta f(X, Y) = \gamma(X, Y)
    # Pairs of (X, Y):
    # Category 1: Even-Even (X in g_0, Y in g_0)
    # (\delta f)(X, Y) = [X, f(Y)] - [Y, f(X)] - f([X, Y])  (in g_1)
    # \gamma(X, Y) = 0
    # Equation: (\delta f)(X_e1, X_e2) = 0
    
    # Category 2: Even-Odd (X in g_0, Y in g_1)
    # (\delta f)(X, Y) = [X, f(Y)] + [Y, f(X)] - f([X, Y])  (in g_0)
    # Equation: (\delta f)(X_e, Y_o) = \gamma(X_e, Y_o)
    
    # Category 3: Odd-Odd (X in g_1, Y in g_1)
    # (\delta f)(X, Y) = - [X, f(Y)] - [Y, f(X)] - f([X, Y])  (in g_1)
    # Equation: (\delta f)(X_o1, X_o2) = \gamma(X_o1, X_o2)

    eqs = []
    
    # Category 1: Even-Even
    for i1 in range(dim_even):
        for i2 in range(i1 + 1, dim_even):
            # f(X_i2) is in g_1: vector of f0_vars[(k_odd, i2)]
            # [X_i1, f(X_i2)]_0:
            term1 = zeros(dim_odd, 1)
            for k_odd in range(dim_odd):
                coef = f0_vars[(k_odd, i2)]
                term1 += coef * bracket_even_odd(i1, k_odd)
                
            # [X_i2, f(X_i1)]_0:
            term2 = zeros(dim_odd, 1)
            for k_odd in range(dim_odd):
                coef = f0_vars[(k_odd, i1)]
                term2 += coef * bracket_even_odd(i2, k_odd)
                
            # f([X_i1, X_i2]_0):
            br_ee = bracket_even_even(i1, i2)
            term3 = zeros(dim_odd, 1)
            for k_even in range(dim_even):
                c_ee = br_ee[k_even, 0]
                if c_ee != 0:
                    for k_odd in range(dim_odd):
                        term3[k_odd, 0] += c_ee * f0_vars[(k_odd, k_even)]
                        
            delta_f = term1 - term2 - term3
            for k_odd in range(dim_odd):
                eqs.append(delta_f[k_odd, 0]) # should equal 0

    # Category 2: Even-Odd
    for i_even in range(dim_even):
        for i_odd in range(dim_odd):
            # [X_even, f(Y_odd)]_0: f(Y_odd) is in g_0 with components psi_{k_even, i_odd}
            # [X_even, X_{k_even}]_0
            term1 = zeros(dim_even, 1)
            for k_even in range(dim_even):
                coef = f1_vars[(k_even, i_odd)]
                if i_even <= k_even:
                    term1 += coef * bracket_even_even(i_even, k_even)
                else:
                    term1 -= coef * bracket_even_even(k_even, i_even)
                    
            # [Y_odd, f(X_even)]_0: f(X_even) is in g_1 with components phi_{k_odd, i_even}
            # {Y_odd, Y_{k_odd}}_0
            term2 = zeros(dim_even, 1)
            for k_odd in range(dim_odd):
                coef = f0_vars[(k_odd, i_even)]
                term2 += coef * bracket_odd_odd(i_odd, k_odd)
                
            # f([X_even, Y_odd]_0): bracket is in g_1 with components br_eo[k_odd]
            br_eo = bracket_even_odd(i_even, i_odd)
            term3 = zeros(dim_even, 1)
            for k_odd in range(dim_odd):
                c_eo = br_eo[k_odd, 0]
                if c_eo != 0:
                    for k_even in range(dim_even):
                        term3[k_even, 0] += c_eo * f1_vars[(k_even, k_odd)]
                        
            delta_f = term1 + term2 - term3
            g_eo = gamma_even_odd(i_even, i_odd)
            for k_even in range(dim_even):
                eqs.append(delta_f[k_even, 0] - g_eo[k_even, 0])

    # Category 3: Odd-Odd (skew-symmetric: i1 <= i2)
    for i1 in range(dim_odd):
        for i2 in range(i1, dim_odd):
            # - [Y_i1, f(Y_i2)]_0: f(Y_i2) is in g_0 with components psi_{k_even, i2}
            # [Y_i1, X_{k_even}]_0 = - [X_{k_even}, Y_i1]_0
            term1 = zeros(dim_odd, 1)
            for k_even in range(dim_even):
                coef = f1_vars[(k_even, i2)]
                term1 -= coef * bracket_even_odd(k_even, i1)
                
            # - [Y_i2, f(Y_i1)]_0:
            term2 = zeros(dim_odd, 1)
            for k_even in range(dim_even):
                coef = f1_vars[(k_even, i1)]
                term2 -= coef * bracket_even_odd(k_even, i2)
                
            # f([Y_i1, Y_i2]_0): bracket is in g_0 with components br_oo[k_even]
            br_oo = bracket_odd_odd(i1, i2)
            term3 = zeros(dim_odd, 1)
            for k_even in range(dim_even):
                c_oo = br_oo[k_even, 0]
                if c_oo != 0:
                    for k_odd in range(dim_odd):
                        term3[k_odd, 0] += c_oo * f0_vars[(k_odd, k_even)]
                        
            delta_f = term1 + term2 - term3
            g_oo = gamma_odd_odd(i1, i2)
            for k_odd in range(dim_odd):
                eqs.append(delta_f[k_odd, 0] - g_oo[k_odd, 0])

    print(f"Total scalar equations in linear system: {len(eqs)}")

    # We can write the linear system as: M * f_vec = RHS(gb)
    # where M is a matrix of size (num_eqs x num_f_vars) with constant numeric entries,
    # and RHS(gb) is a vector of size num_eqs linear in gb_list.
    
    # Let's build M and RHS_matrix (num_eqs x num_gb):
    M = zeros(len(eqs), num_f_vars)
    RHS = zeros(len(eqs), num_gb)
    
    for row_idx, eq in enumerate(eqs):
        # eq is of the form: sum_j M_{row, j} f_j - sum_k RHS_{row, k} gb_k = 0
        # or eq = L(f) - R(gb)
        # So L(f) = coefficient of f_j, R(gb) = - (constant term w.r.t f)
        lin_coeff = sp.linear_eq_to_matrix([eq], f_var_list)
        for col_f, f_sym in enumerate(f_var_list):
            M[row_idx, col_f] = lin_coeff[0][0, col_f]
            
        # The remainder w.r.t f_vars is - R(gb):
        rem = eq - sum(M[row_idx, col_f] * f_var_list[col_f] for col_f in range(num_f_vars))
        # rem is equal to - R(gb), so R(gb) = - rem
        for col_gb, gb_sym in enumerate(gb_list):
            RHS[row_idx, col_gb] = - rem.coeff(gb_sym)

    print("Building numeric numpy matrices for fast SVD / rank analysis...")
    M_np = np.array(M.tolist(), dtype=np.float64)
    RHS_np = np.array(RHS.tolist(), dtype=np.float64)
    
    rank_M = np.linalg.matrix_rank(M_np)
    print(f"Rank of M matrix: {rank_M} / {num_f_vars} (nullity = {num_f_vars - rank_M})")
    
    # Triviality condition: RHS(gb) must be in the column space (image) of M!
    # Equivalently, Projector onto Kernel(M^T) * RHS(gb) = 0!
    # Let's compute basis for Kernel(M^T):
    # M^T * v = 0
    U, S, Vh = np.linalg.svd(M_np)
    # U has columns corresponding to singular values.
    # Columns of U corresponding to singular values near 0 form a basis for Ker(M^T)!
    tol = 1e-10
    null_indices = np.where(S < tol)[0]
    # Also include the columns of U beyond len(S) if M_np has more rows than cols
    num_rows, num_cols = M_np.shape
    extra_null = list(range(len(S), num_rows))
    
    ker_MT_cols = []
    for idx in range(len(S), num_rows):
        ker_MT_cols.append(U[:, idx])
    for idx in null_indices:
        ker_MT_cols.append(U[:, idx])
        
    print(f"Dimension of Ker(M^T) (number of linear constraints on RHS): {len(ker_MT_cols)}")
    
    # Compute constraints on gb:
    gb_constraints = []
    for v in ker_MT_cols:
        # v^T * RHS_np * gb_vec == 0
        c_vec = v @ RHS_np
        # clean up small floating values:
        c_vec_clean = [0.0 if abs(x) < 1e-10 else float(x) for x in c_vec]
        if any(abs(x) > 1e-10 for x in c_vec_clean):
            expr = sum(c_vec_clean[k] * gb_list[k] for k in range(num_gb))
            gb_constraints.append(expr)

    print(f"\nNumber of non-trivial constraints on gb: {len(gb_constraints)}")
    
    # Let's simplify constraints using SymPy matrix rank / rref on constraint matrix!
    if len(gb_constraints) > 0:
        C_mat = zeros(len(gb_constraints), num_gb)
        for r, expr in enumerate(gb_constraints):
            for c, sym in enumerate(gb_list):
                C_mat[r, c] = sp.sympify(expr).coeff(sym)
        
        rref_C, pivots = C_mat.rref()
        print(f"Rank of gb constraint matrix: {len(pivots)} / {num_gb}")
        print("Independent gb constraint equations (RREF):")
        for p_idx, r in enumerate(range(len(pivots))):
            row_expr = sum(rref_C[r, c] * gb_list[c] for c in range(num_gb))
            print(f"  Constraint {r+1}: {row_expr} = 0")
    else:
        print("NO CONSTRAINTS! All gb configurations are trivial!")

    result_data = {
        "n": n,
        "algebra": f"C({n+1}) = osp(2|{2*n})",
        "dim_even": dim_even,
        "dim_odd": dim_odd,
        "dim_total": dim_total,
        "num_gb": num_gb,
        "gb_parameters": [str(g) for g in gb_list],
        "num_f_vars": num_f_vars,
        "num_eqs": len(eqs),
        "rank_M": int(rank_M),
        "num_constraints": len(pivots) if len(gb_constraints) > 0 else 0,
        "constraints_rref": [str(sum(rref_C[r, c] * gb_list[c] for c in range(num_gb))) for r in range(len(pivots))] if len(gb_constraints) > 0 else [],
        "trivial_for_all_gb": (len(gb_constraints) == 0 or len(pivots) == 0)
    }

    return result_data

if __name__ == '__main__':
    all_results = {}
    for n in [1, 2, 3]:
        res = solve_cn1(n)
        all_results[f"C({n+1})"] = res
        
    with open("scratch/verification_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("\nSaved verification_results.json successfully!")
