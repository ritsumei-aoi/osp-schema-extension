"""
Verify undeformed bracket, skew-supersymmetry, and super Jacobi identity for C(n+1).
"""

import sympy as sp
from sympy import symbols, Matrix, zeros, Rational, simplify

def solve_Cn1(n=1):
    print(f"\n==================== RUNNING FOR n = {n} ====================")
    oscillators = []
    oscillators.append(('a', 1, +1))
    oscillators.append(('a', 1, -1))
    for j in range(1, n+1):
        oscillators.append(('b', j, +1))
        oscillators.append(('b', j, -1))
        
    def osc_p(osc):
        return 1 if osc[0] == 'a' else 0
        
    def osc_name(osc):
        sign = '+' if osc[2] == +1 else '-'
        return f"{osc[0]}_{osc[1]}^{sign}"

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

    # Basis elements of g
    basis = []
    basis_names = []
    basis_parities = []
    
    # H_1 = a1+ a1- + b1+ b1-
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
    print(f"Basis size: {dim} ({dim_even} even, {dim - dim_even} odd)")

    # Mapping from a pair of oscillators (u, v) to a vector in g (plus scalar)
    def reduce_pair(u, v):
        vec = [Rational(0)] * dim
        scalar = Rational(0)
        
        # u, v both fermions
        if u[0] == 'a' and v[0] == 'a':
            if u[2] == +1 and v[2] == +1:
                pass
            elif u[2] == -1 and v[2] == -1:
                pass
            elif u[2] == +1 and v[2] == -1:
                # a1+ a1- = H_1 - sum_{k=2}^n H_k + H_{n+1}
                vec[0] += Rational(1) # H_1
                for k in range(2, n+1):
                    vec[k-1] -= Rational(1) # H_k
                vec[n] += Rational(1) # H_{n+1}
            elif u[2] == -1 and v[2] == +1:
                # a1- a1+ = 1 - a1+ a1-
                vec[0] -= Rational(1)
                for k in range(2, n+1):
                    vec[k-1] += Rational(1)
                vec[n] -= Rational(1)
                scalar += Rational(1)
                
        # u, v both bosons
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
                else: # k > l
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
                    # b_k+ b_k- = sum_{m=k+1}^n H_m - H_{n+1}
                    for m in range(k+1, n+1):
                        vec[m-1] += Rational(1)
                    vec[n] -= Rational(1)
            elif s_k == -1 and s_l == +1:
                if k != l:
                    idx = basis_names.index(f"E_delta_{l}-delta_{k}")
                    vec[idx] += Rational(1)
                else:
                    # b_k- b_k+ = b_k+ b_k- + 1
                    for m in range(k+1, n+1):
                        vec[m-1] += Rational(1)
                    vec[n] -= Rational(1)
                    scalar += Rational(1)
                    
        # one fermion, one boson
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

    # Bracket of two monomials [u1 u2, w1 w2]
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

    # Bracket of two basis elements
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

    print("Checking undeformed bracket skew-supersymmetry...")
    skew_ok = True
    for i in range(dim):
        p_i = basis_parities[i]
        for j in range(dim):
            p_j = basis_parities[j]
            v0_ij, s0_ij, _, _ = bracket_basis(i, j)
            v0_ji, s0_ji, _, _ = bracket_basis(j, i)
            expected_factor = - ((-1)**(p_i * p_j))
            for idx in range(dim):
                if v0_ij[idx] != expected_factor * v0_ji[idx]:
                    print(f"Skew fail at ({basis_names[i]}, {basis_names[j]}) index {basis_names[idx]}: {v0_ij[idx]} vs {expected_factor * v0_ji[idx]}")
                    skew_ok = False
                    break
            if s0_ij != expected_factor * s0_ji:
                print(f"Scalar skew fail at ({basis_names[i]}, {basis_names[j]}): {s0_ij} vs {expected_factor * s0_ji}")
                skew_ok = False
                break
    print(f"Skew-supersymmetry verified: {skew_ok}")

    print("Checking Jacobi identity on all triples...")
    jacobi_ok = True
    for i in range(dim):
        p_i = basis_parities[i]
        for j in range(i, dim):
            p_j = basis_parities[j]
            for k in range(j, dim):
                p_k = basis_parities[k]
                
                def br_vec(idx, vec):
                    res = [Rational(0)] * dim
                    for m in range(dim):
                        if vec[m] != 0:
                            v, _, _, _ = bracket_basis(idx, m)
                            for d in range(dim):
                                res[d] += vec[m] * v[d]
                    return res
                    
                v_jk, _, _, _ = bracket_basis(j, k)
                t1 = br_vec(i, v_jk)
                s1 = (-1)**(p_i * p_k)
                
                v_ki, _, _, _ = bracket_basis(k, i)
                t2 = br_vec(j, v_ki)
                s2 = (-1)**(p_j * p_i)
                
                v_ij, _, _, _ = bracket_basis(i, j)
                t3 = br_vec(k, v_ij)
                s3 = (-1)**(p_k * p_j)
                
                for d in range(dim):
                    val = s1 * t1[d] + s2 * t2[d] + s3 * t3[d]
                    if val != 0:
                        print(f"Jacobi failed for ({basis_names[i]}, {basis_names[j]}, {basis_names[k]}) at {basis_names[d]}: {val}")
                        jacobi_ok = False
                        break
                if not jacobi_ok: break
            if not jacobi_ok: break
        if not jacobi_ok: break
    print(f"Super Jacobi identity verified: {jacobi_ok}")

solve_Cn1(1)
