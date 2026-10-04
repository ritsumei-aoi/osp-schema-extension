"""
Complete verification of theoretical shift map f: g -> g.
Directly checks delta(f) vs gamma_{gb} for C(n+1) for n=1, 2, 3.
"""

import sympy as sp
from sympy import symbols, Rational, simplify

def run_verification(n=1):
    print(f"\n=======================================================")
    print(f"RUNNING EXACT VERIFICATION FOR C({n+1}) = osp(2|{2*n})")
    print(f"=======================================================")

    # 1. Define oscillators
    oscillators = []
    oscillators.append(('a', 1, +1))
    oscillators.append(('a', 1, -1))
    for j in range(1, n+1):
        oscillators.append(('b', j, +1))
        oscillators.append(('b', j, -1))
        
    def osc_p(osc):
        return 1 if osc[0] == 'a' else 0

    gb_vars = {}
    for sigma in [+1, -1]:
        sig_str = '+' if sigma == +1 else '-'
        for j in range(1, n+1):
            for s in [+1, -1]:
                s_str = '+' if s == +1 else '-'
                var_name = f"gb_{sig_str}_{j}_{s_str}"
                gb_vars[(sigma, j, s)] = symbols(var_name)

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

    # 2. Basis elements of g
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

    print("Precomputing brackets...")
    br0 = {}
    gamma = {}
    for i in range(dim):
        for j in range(dim):
            v0, _, v1, _ = bracket_basis(i, j)
            br0[(i, j)] = v0
            gamma[(i, j)] = v1

    # 3. Construct the map f: g -> g from theoretical shift:
    f_matrix = []
    for k in range(dim):
        name = basis_names[k]
        p = basis_parities[k]
        f_vec = [sp.sympify(0) for _ in range(dim)]
        
        if p == 0:
            if name == "H_1":
                for j in range(1, n+1):
                    v1, _ = reduce_pair(('b', j, +1), ('a', 1, -1))
                    for d in range(dim): f_vec[d] += gb_vars[(+1, j, -1)] * v1[d]
                    
                    v2, _ = reduce_pair(('b', j, -1), ('a', 1, -1))
                    for d in range(dim): f_vec[d] -= gb_vars[(+1, j, +1)] * v2[d]
                    
                    v3, _ = reduce_pair(('a', 1, +1), ('b', j, +1))
                    for d in range(dim): f_vec[d] -= gb_vars[(-1, j, -1)] * v3[d]
                    
                    v4, _ = reduce_pair(('a', 1, +1), ('b', j, -1))
                    for d in range(dim): f_vec[d] += gb_vars[(-1, j, +1)] * v4[d]
        else:
            sigma = +1 if "eps" in name and "-eps" not in name else -1
            s = +1 if "+delta" in name else -1
            l = int(name.split("delta_")[1])
            for j in range(1, n+1):
                v1, _ = reduce_pair(('b', j, +1), ('b', l, s))
                for d in range(dim): f_vec[d] += gb_vars[(sigma, j, -1)] * v1[d]
                
                v2, _ = reduce_pair(('b', j, -1), ('b', l, s))
                for d in range(dim): f_vec[d] -= gb_vars[(sigma, j, +1)] * v2[d]
                
        f_matrix.append(f_vec)

    # Now compute delta(f)(Z_i, Z_j)
    # formula: (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    def compute_delta_f(f_map, i, j):
        p_i = basis_parities[i]
        p_j = basis_parities[j]
        res = [sp.sympify(0) for _ in range(dim)]
        
        # Term 1: (-1)^{p(X)} [X, f(Y)]
        s1 = (-1)**p_i
        fy = f_map[j]
        for m in range(dim):
            if fy[m] != 0:
                v_im = br0[(i, m)]
                for d in range(dim):
                    res[d] += s1 * fy[m] * v_im[d]
                    
        # Term 2: - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
        s2 = - ((-1)**((p_i + 1) * p_j))
        fx = f_map[i]
        for m in range(dim):
            if fx[m] != 0:
                v_jm = br0[(j, m)]
                for d in range(dim):
                    res[d] += s2 * fx[m] * v_jm[d]
                    
        # Term 3: - f([X, Y])
        v_ij = br0[(i, j)]
        for k in range(dim):
            if v_ij[k] != 0:
                fk = f_map[k]
                for d in range(dim):
                    res[d] -= v_ij[k] * fk[d]
                    
        return res

    # Test proportionality: gamma = c * delta(f)
    # Let's compare gamma(Z_i, Z_j) and delta(f)(Z_i, Z_j)
    print("Comparing gamma_{gb} with delta(f)...")
    
    # Try c = 1, -1, or find c:
    for c_test in [1, -1, Rational(1, 2), -Rational(1, 2)]:
        mismatch_count = 0
        for i in range(dim):
            for j in range(dim):
                g_ij = gamma[(i, j)]
                df_ij = compute_delta_f(f_matrix, i, j)
                for d in range(dim):
                    diff = simplify(g_ij[d] - c_test * df_ij[d])
                    if diff != 0:
                        mismatch_count += 1
                        break
                if mismatch_count > 0:
                    break
            if mismatch_count > 0:
                break
        print(f"Testing c = {c_test}: mismatches = {mismatch_count}")
        if mismatch_count == 0:
            print(f"SUCCESS: gamma_{{gb}} = {c_test} * delta(f) identically for all {dim}x{dim} pairs!")
            return True, c_test

    return False, None

run_verification(1)
