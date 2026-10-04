"""
Solve triviality condition gamma_gb = delta f for C(n+1).
"""

import sympy as sp
from sympy import symbols, Matrix, zeros, Rational, simplify, solve, Eq

from scripts.test_jacobi import solve_Cn1

def analyze_triviality(n=1):
    print(f"\n=======================================================")
    print(f"ANALYZING TRIVIALITY FOR C({n+1}) = osp(2|{2*n})")
    print(f"=======================================================")

    # Oscillators
    oscillators = []
    oscillators.append(('a', 1, +1))
    oscillators.append(('a', 1, -1))
    for j in range(1, n+1):
        oscillators.append(('b', j, +1))
        oscillators.append(('b', j, -1))
        
    def osc_p(osc):
        return 1 if osc[0] == 'a' else 0

    gb_vars = {}
    gb_list = []
    for sigma in [+1, -1]:
        sig_str = '+' if sigma == +1 else '-'
        for j in range(1, n+1):
            for s in [+1, -1]:
                s_str = '+' if s == +1 else '-'
                var_name = f"gb_{sig_str}_{j}_{s_str}"
                sym = symbols(var_name)
                gb_vars[(sigma, j, s)] = sym
                gb_list.append(sym)

    def comm_0(u, v):
        if u[0] == 'a' and v[0] == 'a':
            if (u[2] == -1 and v[2] == +1) or (u[2] == +1 and v[2] == -1):
                return Rational(1)
            return Rational(0)
        elif u[0] == 'b' and v[0] == 'b':
            if u[1] == v[1]:
                if u[2] == -1 and v[2] == +1:
                    return Rational(1)
                elif u[2] == +1 and v[2] == -1:
                    return Rational(-1)
            return Rational(0)
        return Rational(0)
            
    def comm_1(u, v):
        if u[0] == 'b' and v[0] == 'a':
            return -gb_vars[(v[2], u[1], u[2])]
        elif u[0] == 'a' and v[0] == 'b':
            return gb_vars[(u[2], v[1], v[2])]
        return Rational(0)

    # Basis elements of g
    basis = []
    basis_names = []
    basis_parities = []
    
    basis.append([(Rational(1), ('a', 1, +1), ('a', 1, -1)),
                  (Rational(1), ('b', 1, +1), ('b', 1, -1))])
    basis_names.append("H_1")
    basis_parities.append(0)
    
    for k in range(2, n+1):
        basis.append([(Rational(1), ('b', k-1, +1), ('b', k-1, -1)),
                      (Rational(-1), ('b', k, +1), ('b', k, -1))])
        basis_names.append(f"H_{k}")
        basis_parities.append(0)
        
    basis.append([(Rational(-1), ('b', n, +1), ('b', n, -1))])
    basis_names.append(f"H_{n+1}")
    basis_parities.append(0)
    
    for k in range(1, n+1):
        basis.append([(Rational(1, 2), ('b', k, +1), ('b', k, +1))])
        basis_names.append(f"E_2delta_{k}")
        basis_parities.append(0)
        
    for k in range(1, n+1):
        basis.append([(Rational(1, 2), ('b', k, -1), ('b', k, -1))])
        basis_names.append(f"E_-2delta_{k}")
        basis_parities.append(0)
        
    for k in range(1, n+1):
        for l in range(1, n+1):
            if k != l:
                basis.append([(Rational(1), ('b', k, +1), ('b', l, -1))])
                basis_names.append(f"E_delta_{k}-delta_{l}")
                basis_parities.append(0)
                
    for k in range(1, n+1):
        for l in range(k+1, n+1):
            basis.append([(Rational(1), ('b', k, +1), ('b', l, +1))])
            basis_names.append(f"E_delta_{k}+delta_{l}")
            basis_parities.append(0)
            
    for k in range(1, n+1):
        for l in range(k+1, n+1):
            basis.append([(Rational(1), ('b', k, -1), ('b', l, -1))])
            basis_names.append(f"E_-delta_{k}-delta_{l}")
            basis_parities.append(0)

    dim_even = len(basis)
    
    for l in range(1, n+1):
        basis.append([(Rational(1), ('a', 1, +1), ('b', l, +1))])
        basis_names.append(f"E_eps+delta_{l}")
        basis_parities.append(1)
        
    for l in range(1, n+1):
        basis.append([(Rational(1), ('a', 1, +1), ('b', l, -1))])
        basis_names.append(f"E_eps-delta_{l}")
        basis_parities.append(1)
        
    for l in range(1, n+1):
        basis.append([(Rational(1), ('a', 1, -1), ('b', l, +1))])
        basis_names.append(f"E_-eps+delta_{l}")
        basis_parities.append(1)
        
    for l in range(1, n+1):
        basis.append([(Rational(1), ('a', 1, -1), ('b', l, -1))])
        basis_names.append(f"E_-eps-delta_{l}")
        basis_parities.append(1)
        
    dim = len(basis)

    def reduce_pair(u, v):
        vec = [Rational(0)] * dim
        scalar = Rational(0)
        
        if u[0] == 'a' and v[0] == 'a':
            if u[2] == +1 and v[2] == -1:
                vec[0] += Rational(1)
                for k in range(2, n+1):
                    vec[k-1] -= Rational(1)
                vec[n] += Rational(1)
            elif u[2] == -1 and v[2] == +1:
                vec[0] -= Rational(1)
                for k in range(2, n+1):
                    vec[k-1] += Rational(1)
                vec[n] -= Rational(1)
                scalar += Rational(1)
                
        elif u[0] == 'b' and v[0] == 'b':
            k, s_k = u[1], u[2]
            l, s_l = v[1], v[2]
            if s_k == +1 and s_l == +1:
                if k == l:
                    idx = basis_names.index(f"E_2delta_{k}")
                    vec[idx] += Rational(2)
                elif k < l:
                    idx = basis_names.index(f"E_delta_{k}+delta_{l}")
                    vec[idx] += Rational(1)
                else:
                    idx = basis_names.index(f"E_delta_{l}+delta_{k}")
                    vec[idx] += Rational(1)
            elif s_k == -1 and s_l == -1:
                if k == l:
                    idx = basis_names.index(f"E_-2delta_{k}")
                    vec[idx] += Rational(2)
                elif k < l:
                    idx = basis_names.index(f"E_-delta_{k}-delta_{l}")
                    vec[idx] += Rational(1)
                else:
                    idx = basis_names.index(f"E_-delta_{l}-delta_{k}")
                    vec[idx] += Rational(1)
            elif s_k == +1 and s_l == -1:
                if k != l:
                    idx = basis_names.index(f"E_delta_{k}-delta_{l}")
                    vec[idx] += Rational(1)
                else:
                    for m in range(k+1, n+1):
                        vec[m-1] += Rational(1)
                    vec[n] -= Rational(1)
            elif s_k == -1 and s_l == +1:
                if k != l:
                    idx = basis_names.index(f"E_delta_{l}-delta_{k}")
                    vec[idx] += Rational(1)
                else:
                    for m in range(k+1, n+1):
                        vec[m-1] += Rational(1)
                    vec[n] -= Rational(1)
                    scalar += Rational(1)
                    
        elif u[0] == 'a' and v[0] == 'b':
            sig = u[2]
            l, s = v[1], v[2]
            sig_s = "eps" if sig == +1 else "-eps"
            s_s = f"+delta_{l}" if s == +1 else f"-delta_{l}"
            name = f"E_{sig_s}{s_s}"
            idx = basis_names.index(name)
            vec[idx] += Rational(1)
        elif u[0] == 'b' and v[0] == 'a':
            sig = v[2]
            l, s = u[1], u[2]
            sig_s = "eps" if sig == +1 else "-eps"
            s_s = f"+delta_{l}" if s == +1 else f"-delta_{l}"
            name = f"E_{sig_s}{s_s}"
            idx = basis_names.index(name)
            vec[idx] += Rational(1)
            
        return vec, scalar

    def bracket_monomial(u1, u2, w1, w2):
        p1, p2 = osc_p(u1), osc_p(u2)
        q1, q2 = osc_p(w1), osc_p(w2)
        
        vec0 = [Rational(0)] * dim
        scalar0 = Rational(0)
        
        c0_21 = comm_0(u2, w1)
        if c0_21 != 0:
            v, s = reduce_pair(u1, w2)
            for idx in range(dim): vec0[idx] += c0_21 * v[idx]
            scalar0 += c0_21 * s
            
        c0_22 = comm_0(u2, w2)
        if c0_22 != 0:
            sign = (-1)**(p2 * q1)
            v, s = reduce_pair(u1, w1)
            for idx in range(dim): vec0[idx] += sign * c0_22 * v[idx]
            scalar0 += sign * c0_22 * s
            
        c0_11 = comm_0(u1, w1)
        if c0_11 != 0:
            sign = (-1)**(p2 * (q1 + q2))
            v, s = reduce_pair(w2, u2)
            for idx in range(dim): vec0[idx] += sign * c0_11 * v[idx]
            scalar0 += sign * c0_11 * s
            
        c0_12 = comm_0(u1, w2)
        if c0_12 != 0:
            sign = (-1)**(p2 * (q1 + q2) + p1 * q1)
            v, s = reduce_pair(w1, u2)
            for idx in range(dim): vec0[idx] += sign * c0_12 * v[idx]
            scalar0 += sign * c0_12 * s
            
        vec1 = [sp.sympify(0) for _ in range(dim)]
        scalar1 = sp.sympify(0)
        
        c1_21 = comm_1(u2, w1)
        if c1_21 != 0:
            sign = (-1)**p1
            v, s = reduce_pair(u1, w2)
            for idx in range(dim): vec1[idx] += sign * c1_21 * v[idx]
            scalar1 += sign * c1_21 * s
            
        c1_22 = comm_1(u2, w2)
        if c1_22 != 0:
            sign = (-1)**(p2 * q1 + p1 + q1)
            v, s = reduce_pair(u1, w1)
            for idx in range(dim): vec1[idx] += sign * c1_22 * v[idx]
            scalar1 += sign * c1_22 * s
            
        c1_11 = comm_1(u1, w1)
        if c1_11 != 0:
            sign = (-1)**(p2 * (q1 + q2))
            v, s = reduce_pair(w2, u2)
            for idx in range(dim): vec1[idx] += sign * c1_11 * v[idx]
            scalar1 += sign * c1_11 * s
            
        c1_12 = comm_1(u1, w2)
        if c1_12 != 0:
            sign = (-1)**(p2 * (q1 + q2) + p1 * q1 + q1)
            v, s = reduce_pair(w1, u2)
            for idx in range(dim): vec1[idx] += sign * c1_12 * v[idx]
            scalar1 += sign * c1_12 * s
            
        return vec0, scalar0, vec1, scalar1

    def bracket_basis(i, j):
        b_i = basis[i]
        b_j = basis[j]
        out_v0 = [Rational(0)] * dim
        out_s0 = Rational(0)
        out_v1 = [sp.sympify(0) for _ in range(dim)]
        out_s1 = sp.sympify(0)
        
        for c_i, u1, u2 in b_i:
            for c_j, w1, w2 in b_j:
                t_v0, t_s0, t_v1, t_s1 = bracket_monomial(u1, u2, w1, w2)
                coeff = c_i * c_j
                for idx in range(dim):
                    out_v0[idx] += coeff * t_v0[idx]
                    out_v1[idx] += coeff * t_v1[idx]
                out_s0 += coeff * t_s0
                out_s1 += coeff * t_s1
        return out_v0, out_s0, out_v1, out_s1

    # Precompute all undeformed brackets [Z_i, Z_j]_0 and deformed gamma_{ij}
    print("Precomputing all brackets...")
    br0 = {}
    gamma = {}
    gamma_scalar = {}
    for i in range(dim):
        for j in range(dim):
            v0, s0, v1, s1 = bracket_basis(i, j)
            br0[(i, j)] = v0
            gamma[(i, j)] = v1
            gamma_scalar[(i, j)] = s1

    # Check parity of gamma
    print("Checking parity of gamma(X, Y)...")
    parity_ok = True
    for i in range(dim):
        p_i = basis_parities[i]
        for j in range(dim):
            p_j = basis_parities[j]
            expected_p = (p_i + p_j + 1) % 2
            v1 = gamma[(i, j)]
            for d in range(dim):
                if v1[d] != 0 and basis_parities[d] != expected_p:
                    print(f"Parity mismatch at ({basis_names[i]}, {basis_names[j]}) -> {basis_names[d]}")
                    parity_ok = False
    print(f"Gamma parity consistency: {parity_ok}")

    # Now define the linear map f: g -> g
    # f is an odd linear map:
    # f(Z_j) = sum_i phi_{i, j} Z_i
    # phi_{i, j} is non-zero only when p(Z_i) != p(Z_j)
    phi_vars = {}
    for j in range(dim):
        p_j = basis_parities[j]
        for i in range(dim):
            p_i = basis_parities[i]
            if p_i != p_j:
                phi_vars[(i, j)] = symbols(f"phi_{i}_{j}")

    print(f"Number of parameters in f: {len(phi_vars)}")

    # Formula for delta f:
    # (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    # For basis elements Z_i, Z_j:
    # f(Z_j) = sum_m phi_{m, j} Z_m
    # [Z_i, f(Z_j)] = sum_m phi_{m, j} [Z_i, Z_m]_0
    # [Z_j, f(Z_i)] = sum_m phi_{m, i} [Z_j, Z_m]_0
    # f([Z_i, Z_j]_0) = f(sum_k br0[(i, j)][k] Z_k) = sum_k br0[(i, j)][k] sum_m phi_{m, k} Z_m

    def delta_f(i, j):
        p_i = basis_parities[i]
        p_j = basis_parities[j]
        res = [sp.sympify(0) for _ in range(dim)]
        
        # Term 1: (-1)^{p(X)} [X, f(Y)]
        s1 = (-1)**p_i
        for m in range(dim):
            if (m, j) in phi_vars:
                phi = phi_vars[(m, j)]
                v_im = br0[(i, m)]
                for d in range(dim):
                    if v_im[d] != 0:
                        res[d] += s1 * phi * v_im[d]
                        
        # Term 2: - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
        s2 = - ((-1)**((p_i + 1) * p_j))
        for m in range(dim):
            if (m, i) in phi_vars:
                phi = phi_vars[(m, i)]
                v_jm = br0[(j, m)]
                for d in range(dim):
                    if v_jm[d] != 0:
                        res[d] += s2 * phi * v_jm[d]
                        
        # Term 3: - f([X, Y])
        v_ij = br0[(i, j)]
        for k in range(dim):
            if v_ij[k] != 0:
                c_k = v_ij[k]
                for m in range(dim):
                    if (m, k) in phi_vars:
                        res[m] -= c_k * phi_vars[(m, k)]
                        
        return res

    # Now set up the equations: gamma(Z_i, Z_j) == delta_f(Z_i, Z_j)
    # Collect all linear equations in gb_list and phi_vars
    print("Setting up linear equations gamma_{gb} = delta f...")
    eqs = []
    for i in range(dim):
        for j in range(dim):
            g_vec = gamma[(i, j)]
            d_vec = delta_f(i, j)
            for d in range(dim):
                diff = simplify(g_vec[d] - d_vec[d])
                if diff != 0:
                    eqs.append(diff)

    print(f"Total equations: {len(eqs)}")

    # We want to solve for phi in terms of gb:
    # Does there exist phi for EVERY gb?
    # Or does gamma = delta f impose conditions on gb?
    # Let's solve the linear system for phi_vars!
    phi_list = list(phi_vars.values())
    print("Solving linear system for phi parameters in terms of gb...")
    sol = sp.solve(eqs, phi_list, dict=True)
    print(f"Solution: {sol}")
    
    # Also check if gb must satisfy any constraints!
    # To find constraints on gb, solve for ALL variables (phi_list + gb_list):
    # or eliminate phi_list:
    sol_all = sp.solve(eqs, phi_list + gb_list, dict=True)
    print(f"Solution over all variables (phi and gb): {sol_all}")
    
    # Let's inspect the remaining constraints on gb:
    # We can form the linear system M * phi = rhs(gb)
    # and find the rank of M vs augmented matrix [M | rhs]
    A_mat, b_vec = sp.linear_eq_to_matrix(eqs, phi_list)
    print(f"Matrix A shape: {A_mat.shape}")
    print(f"Rank of A: {A_mat.rank()}")
    
    # Check if there are constraints on gb:
    # If rhs is not in the column space of A, what are the conditions on gb?
    # To find conditions on gb:
    # Find left nullspace of A (vectors v such that v^T A = 0)
    null_left = A_mat.T.nullspace()
    print(f"Left nullspace dimension (number of obstruction equations): {len(null_left)}")
    
    gb_obstructions = []
    for v in null_left:
        ob = simplify(sum(v[i] * b_vec[i] for i in range(len(v))))
        if ob != 0:
            gb_obstructions.append(ob)
            
    print(f"Number of non-trivial obstruction equations on gb: {len(gb_obstructions)}")
    for ob in gb_obstructions[:10]:
        print("  Obstruction:", ob, "= 0")

    return sol, gb_obstructions

analyze_triviality(1)
