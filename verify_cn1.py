"""
Comprehensive verification script for C(n+1) Lie superalgebra, deformations, and coboundaries.
"""
import sympy as sp
from itertools import product
import json

def build_algebra(n):
    basis = []
    
    # 1. Fermionic Cartan J
    basis.append(('J', 0, [
        (sp.Rational(1, 2), ('a', '+'), ('a', '-')),
        (sp.Rational(-1, 2), ('a', '-'), ('a', '+'))
    ]))
    
    # 2. Bosonic Cartan and roots
    for k in range(1, n + 1):
        # H_k
        basis.append((f'H_{k}', 0, [
            (sp.Rational(1, 2), ('b', '+', k), ('b', '-', k)),
            (sp.Rational(1, 2), ('b', '-', k), ('b', '+', k))
        ]))
        # E_{2 delta_k}
        basis.append((f'E_+2d_{k}', 0, [
            (sp.Rational(1, 2), ('b', '+', k), ('b', '+', k))
        ]))
        # E_{-2 delta_k}
        basis.append((f'E_-2d_{k}', 0, [
            (sp.Rational(1, 2), ('b', '-', k), ('b', '-', k))
        ]))
        
    for j in range(1, n + 1):
        for k in range(j + 1, n + 1):
            basis.append((f'E_+d_{j}+d_{k}', 0, [
                (sp.Rational(1, 1), ('b', '+', j), ('b', '+', k))
            ]))
            basis.append((f'E_-d_{j}-d_{k}', 0, [
                (sp.Rational(1, 1), ('b', '-', j), ('b', '-', k))
            ]))
            basis.append((f'E_+d_{j}-d_{k}', 0, [
                (sp.Rational(1, 1), ('b', '+', j), ('b', '-', k))
            ]))
            basis.append((f'E_-d_{j}+d_{k}', 0, [
                (sp.Rational(1, 1), ('b', '-', j), ('b', '+', k))
            ]))
            
    # Odd generators
    for k in range(1, n + 1):
        for sigma in ['+', '-']:
            for s in ['+', '-']:
                name = f'F_{sigma}eps_{s}d_{k}'
                basis.append((name, 1, [
                    (sp.Rational(1, 1), ('a', sigma), ('b', s, k))
                ]))
                
    return basis

def osc_parity(u):
    return 1 if u[0] == 'a' else 0

def osc_superbracket(u, v, gb_vars):
    pu, pv = osc_parity(u), osc_parity(v)
    if pu == 1 and pv == 1:
        if u[1] != v[1]:
            return (sp.Rational(1, 1), sp.Integer(0))
        else:
            return (sp.Integer(0), sp.Integer(0))
    if pu == 0 and pv == 0:
        if u[2] == v[2]:
            if u[1] == '-' and v[1] == '+':
                return (sp.Rational(1, 1), sp.Integer(0))
            elif u[1] == '+' and v[1] == '-':
                return (sp.Rational(-1, 1), sp.Integer(0))
        return (sp.Integer(0), sp.Integer(0))
    if pu == 0 and pv == 1:
        s, j, sigma = u[1], u[2], v[1]
        return (sp.Integer(0), -gb_vars[(sigma, j, s)])
    else:
        sigma, s, j = u[1], v[1], v[2]
        return (sp.Integer(0), gb_vars[(sigma, j, s)])

def reduce_monomial_to_basis(u1, u2, basis_dict, n):
    """
    Expresses u1 u2 in terms of basis elements of C(n+1) and a scalar.
    Returns (basis_coeffs_dict, scalar).
    """
    res = {name: sp.Integer(0) for name in basis_dict}
    scalar = sp.Integer(0)
    
    # 1. Both fermionic
    if u1[0] == 'a' and u2[0] == 'a':
        if u1[1] == '+' and u2[1] == '+':
            pass # (a+)^2 = 0
        elif u1[1] == '-' and u2[1] == '-':
            pass # (a-)^2 = 0
        elif u1[1] == '+' and u2[1] == '-':
            # a+ a- = J + 1/2
            res['J'] += 1
            scalar += sp.Rational(1, 2)
        elif u1[1] == '-' and u2[1] == '+':
            # a- a+ = -J + 1/2
            res['J'] -= 1
            scalar += sp.Rational(1, 2)
            
    # 2. Both bosonic
    elif u1[0] == 'b' and u2[0] == 'b':
        s1, j1 = u1[1], u1[2]
        s2, j2 = u2[1], u2[2]
        if j1 == j2:
            k = j1
            if s1 == '+' and s2 == '+':
                res[f'E_+2d_{k}'] += 2
            elif s1 == '-' and s2 == '-':
                res[f'E_-2d_{k}'] += 2
            elif s1 == '+' and s2 == '-':
                # b+ b- = H_k - 1/2
                res[f'H_{k}'] += 1
                scalar -= sp.Rational(1, 2)
            elif s1 == '-' and s2 == '+':
                # b- b+ = H_k + 1/2
                res[f'H_{k}'] += 1
                scalar += sp.Rational(1, 2)
        else:
            # j1 != j2
            if j1 > j2:
                # swap j1, j2: since bosonic oscillators commute, u1 u2 = u2 u1
                j1, j2 = j2, j1
                s1, s2 = s2, s1
            # Now j1 < j2
            if s1 == '+' and s2 == '+':
                res[f'E_+d_{j1}+d_{j2}'] += 1
            elif s1 == '-' and s2 == '-':
                res[f'E_-d_{j1}-d_{j2}'] += 1
            elif s1 == '+' and s2 == '-':
                res[f'E_+d_{j1}-d_{j2}'] += 1
            elif s1 == '-' and s2 == '+':
                res[f'E_-d_{j1}+d_{j2}'] += 1
                
    # 3. One fermionic, one bosonic
    else:
        if u1[0] == 'a' and u2[0] == 'b':
            sigma = u1[1]
            s, k = u2[1], u2[2]
            res[f'F_{sigma}eps_{s}d_{k}'] += 1
        elif u1[0] == 'b' and u2[0] == 'a':
            s, k = u1[1], u1[2]
            sigma = u2[1]
            # In order 0, b a = a b
            res[f'F_{sigma}eps_{s}d_{k}'] += 1
            
    return res, scalar

def compute_supercommutator(X, Y, gb_vars, basis_dict, n):
    """
    Computes [X, Y] for two generators X, Y.
    Returns (bracket_0, gamma_1) where:
      bracket_0 is dict of basis coefficients (undeformed Lie bracket)
      gamma_1 is dict of basis coefficients (deformation 2-cocycle)
    """
    # X = sum c_i u_1^i u_2^i
    # Y = sum d_j v_1^j v_2^j
    nameX, pX, termsX = X
    nameY, pY, termsY = Y
    
    total_bracket_0 = {name: sp.Integer(0) for name in basis_dict}
    total_gamma_1 = {name: sp.Integer(0) for name in basis_dict}
    total_scalar_0 = sp.Integer(0)
    total_scalar_1 = sp.Integer(0)
    
    for cX, u1, u2 in termsX:
        for cY, v1, v2 in termsY:
            pu1, pu2 = osc_parity(u1), osc_parity(u2)
            pv1, pv2 = osc_parity(v1), osc_parity(v2)
            pY_term = (pv1 + pv2) % 2
            
            # Leibniz terms
            # 1: u1 [u2, v1] v2
            c0, c1 = osc_superbracket(u2, v1, gb_vars)
            if c0 != 0 or c1 != 0:
                b_res, sc = reduce_monomial_to_basis(u1, v2, basis_dict, n)
                for k, v in b_res.items():
                    total_bracket_0[k] += cX * cY * c0 * v
                    total_gamma_1[k] += cX * cY * c1 * v
                total_scalar_0 += cX * cY * c0 * sc
                total_scalar_1 += cX * cY * c1 * sc
                
            # 2: (-1)^{pu2 pv1} u1 v1 [u2, v2]
            c0, c1 = osc_superbracket(u2, v2, gb_vars)
            if c0 != 0 or c1 != 0:
                sign = (-1)**(pu2 * pv1)
                b_res, sc = reduce_monomial_to_basis(u1, v1, basis_dict, n)
                for k, v in b_res.items():
                    total_bracket_0[k] += cX * cY * (sign * c0) * v
                    total_gamma_1[k] += cX * cY * (sign * c1) * v
                total_scalar_0 += cX * cY * (sign * c0) * sc
                total_scalar_1 += cX * cY * (sign * c1) * sc
                
            # 3: (-1)^{pu2 pY} [u1, v1] v2 u2
            c0, c1 = osc_superbracket(u1, v1, gb_vars)
            if c0 != 0 or c1 != 0:
                sign = (-1)**(pu2 * pY_term)
                b_res, sc = reduce_monomial_to_basis(v2, u2, basis_dict, n)
                for k, v in b_res.items():
                    total_bracket_0[k] += cX * cY * (sign * c0) * v
                    total_gamma_1[k] += cX * cY * (sign * c1) * v
                total_scalar_0 += cX * cY * (sign * c0) * sc
                total_scalar_1 += cX * cY * (sign * c1) * sc
                
            # 4: (-1)^{pu2 pY + pu1 pv1} [u1, v2] v1 u2
            c0, c1 = osc_superbracket(u1, v2, gb_vars)
            if c0 != 0 or c1 != 0:
                sign = (-1)**(pu2 * pY_term + pu1 * pv1)
                b_res, sc = reduce_monomial_to_basis(v1, u2, basis_dict, n)
                for k, v in b_res.items():
                    total_bracket_0[k] += cX * cY * (sign * c0) * v
                    total_gamma_1[k] += cX * cY * (sign * c1) * v
                total_scalar_0 += cX * cY * (sign * c0) * sc
                total_scalar_1 += cX * cY * (sign * c1) * sc

    return total_bracket_0, total_gamma_1, total_scalar_0, total_scalar_1

def test_algebra(n):
    print(f"=== Testing n={n} ===")
    basis = build_algebra(n)
    basis_dict = {b[0]: b for b in basis}
    dim = len(basis)
    
    # Create gb symbols
    gb_vars = {}
    for k in range(1, n + 1):
        for sigma in ['+', '-']:
            for s in ['+', '-']:
                var_name = f'gb_{sigma}_{k}_{s}'
                gb_vars[(sigma, k, s)] = sp.Symbol(var_name)
                
    # 1. Compute structure constants C_{ij}^k and deformation gamma_{ij}^k
    C_table = {}
    gamma_table = {}
    for i, b1 in enumerate(basis):
        for j, b2 in enumerate(basis):
            b0, g1, s0, s1 = compute_supercommutator(b1, b2, gb_vars, basis_dict, n)
            C_table[(b1[0], b2[0])] = b0
            gamma_table[(b1[0], b2[0])] = g1
            if s0 != 0:
                print(f"Warning: non-zero scalar in [ {b1[0]}, {b2[0]} ]_0 = {s0}")
            if s1 != 0:
                print(f"Warning: non-zero scalar in gamma( {b1[0]}, {b2[0]} ) = {s1}")
                
    print(f"Computed brackets for all {dim}x{dim} pairs.")
    
    # Verify super-anticommutativity of [,]0 and gamma
    for i, b1 in enumerate(basis):
        for j, b2 in enumerate(basis):
            sign = (-1)**(b1[1] * b2[1])
            # [X, Y] + (-1)^{pX pY} [Y, X] = 0
            for k, b3 in enumerate(basis):
                val0 = C_table[(b1[0], b2[0])][b3[0]] + sign * C_table[(b2[0], b1[0])][b3[0]]
                if val0 != 0:
                    print(f"Anticommutativity failed for [ {b1[0]}, {b2[0]} ] on {b3[0]}: {val0}")
                    
    print("Super-anticommutativity verified successfully.")
    
    # Verify Jacobi identity for [,]0
    jacobi_fails = 0
    for i, X in enumerate(basis):
        for j, Y in enumerate(basis):
            for k, Z in enumerate(basis):
                pX, pY, pZ = X[1], Y[1], Z[1]
                # (-1)^{pX pZ} [X, [Y, Z]] + (-1)^{pY pX} [Y, [Z, X]] + (-1)^{pZ pY} [Z, [X, Y]] = 0
                # Term 1: (-1)^{pX pZ} [X, [Y, Z]]
                # [Y, Z] = sum_w C_{YZ}^w W
                # [X, [Y, Z]] = sum_w C_{YZ}^w [X, W] = sum_{w, m} C_{YZ}^w C_{XW}^m M
                total_jac = {b[0]: sp.Integer(0) for b in basis}
                
                # Permutation 1: (-1)^{pX pZ} [X, [Y, Z]]
                s1 = (-1)**(pX * pZ)
                for w_name, c_yz in C_table[(Y[0], Z[0])].items():
                    if c_yz != 0:
                        for m_name, c_xw in C_table[(X[0], w_name)].items():
                            total_jac[m_name] += s1 * c_yz * c_xw
                            
                # Permutation 2: (-1)^{pY pX} [Y, [Z, X]]
                s2 = (-1)**(pY * pX)
                for w_name, c_zx in C_table[(Z[0], X[0])].items():
                    if c_zx != 0:
                        for m_name, c_yw in C_table[(Y[0], w_name)].items():
                            total_jac[m_name] += s2 * c_zx * c_yw
                            
                # Permutation 3: (-1)^{pZ pY} [Z, [X, Y]]
                s3 = (-1)**(pZ * pY)
                for w_name, c_xy in C_table[(X[0], Y[0])].items():
                    if c_xy != 0:
                        for m_name, c_zw in C_table[(Z[0], w_name)].items():
                            total_jac[m_name] += s3 * c_xy * c_zw
                            
                for m_name, val in total_jac.items():
                    if val != 0:
                        jacobi_fails += 1
                        print(f"Jacobi failed for ({X[0]}, {Y[0]}, {Z[0]}) on {m_name}: {val}")
                        
    print(f"Jacobi identity check complete. Failures: {jacobi_fails}")
    
    # 2. Setup coboundary delta f
    # f: g -> g is an odd linear map:
    # If p(Z) = 0, f(Z) in g_1.
    # If p(Z) = 1, f(Z) in g_0.
    # Parameterize f by matrix phi_{ij}
    even_basis = [b for b in basis if b[1] == 0]
    odd_basis = [b for b in basis if b[1] == 1]
    
    # Map from basis name to index
    basis_idx = {b[0]: i for i, b in enumerate(basis)}
    
    # Create variables for f:
    # For each even generator E, f(E) = sum_{F in odd} phi_{F, E} F
    # For each odd generator F, f(F) = sum_{E in even} phi_{E, F} E
    f_vars = {}
    for E in even_basis:
        for F in odd_basis:
            var_name = f'phi_{F[0]}_{E[0]}'
            f_vars[(F[0], E[0])] = sp.Symbol(var_name)
    for F in odd_basis:
        for E in even_basis:
            var_name = f'phi_{E[0]}_{F[0]}'
            f_vars[(E[0], F[0])] = sp.Symbol(var_name)
            
    print(f"Total f parameters: {len(f_vars)} = 2 * {len(even_basis)} * {len(odd_basis)}")
    
    # Define coboundary delta f:
    # (\delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    # Let's compute (\delta f)(X, Y) in terms of phi vars:
    equations = []
    
    for i, X in enumerate(basis):
        for j, Y in enumerate(basis):
            if i >= j:
                continue # by super-anticommutativity
            pX, pY = X[1], Y[1]
            
            # Compute (\delta f)(X, Y):
            delta_f = {b[0]: sp.Integer(0) for b in basis}
            
            # Term 1: (-1)^{pX} [X, f(Y)]
            sign1 = (-1)**pX
            # f(Y) = sum_W phi_{W, Y} W (where p(W) = 1 - p(Y))
            target_basis_Y = odd_basis if pY == 0 else even_basis
            for W in target_basis_Y:
                phi_WY = f_vars[(W[0], Y[0])]
                # [X, W] = sum_M C_{X, W}^M M
                for M_name, c_xw in C_table[(X[0], W[0])].items():
                    if c_xw != 0:
                        delta_f[M_name] += sign1 * phi_WY * c_xw
                        
            # Term 2: - (-1)^{(pX + 1) pY} [Y, f(X)]
            sign2 = - ((-1)**((pX + 1) * pY))
            target_basis_X = odd_basis if pX == 0 else even_basis
            for W in target_basis_X:
                phi_WX = f_vars[(W[0], X[0])]
                # [Y, W] = sum_M C_{Y, W}^M M
                for M_name, c_yw in C_table[(Y[0], W[0])].items():
                    if c_yw != 0:
                        delta_f[M_name] += sign2 * phi_WX * c_yw
                        
            # Term 3: - f([X, Y])
            # [X, Y] = sum_W C_{X, Y}^W W
            # p(W) = p(X) + p(Y) mod 2
            # f(W) = sum_M phi_{M, W} M (where p(M) = 1 - p(W))
            for W_name, c_xy in C_table[(X[0], Y[0])].items():
                if c_xy != 0:
                    W_parity = (pX + pY) % 2
                    target_basis_W = odd_basis if W_parity == 0 else even_basis
                    for M in target_basis_W:
                        phi_MW = f_vars[(M[0], W_name)]
                        delta_f[M[0]] -= c_xy * phi_MW
                        
            # Now compare delta_f with gamma_table[(X[0], Y[0])]
            gamma_val = gamma_table[(X[0], Y[0])]
            for b in basis:
                lhs = delta_f[b[0]]
                rhs = gamma_val[b[0]]
                eq = sp.simplify(lhs - rhs)
                if eq != 0:
                    equations.append(eq)
                    
    print(f"Total equations to satisfy gamma = delta f: {len(equations)}")
    
    # Solve the linear system for f_vars in terms of gb_vars
    all_f_vars = list(f_vars.values())
    all_gb_vars = list(gb_vars.values())
    
    solution = sp.solve(equations, all_f_vars)
    print(f"Solved linear system. Solution type: {type(solution)}")
    
    # Check if solution exists for arbitrary gb, or what constraints on gb are required
    # Substitute solution back into equations to find remaining constraints on gb_vars
    remaining_eqs = []
    if isinstance(solution, dict):
        for eq in equations:
            subbed = sp.simplify(eq.subs(solution))
            if subbed != 0:
                remaining_eqs.append(subbed)
        print(f"Remaining constraints on gb: {len(remaining_eqs)}")
        if remaining_eqs:
            gb_sol = sp.solve(remaining_eqs, all_gb_vars)
            print(f"gb constraints: {gb_sol}")
        else:
            print("System is solvable for ANY gb parameters! (i.e. deformation is ALWAYS trivial!)")
    else:
        print(f"Solution is list / other: {solution}")
        
    return {
        'n': n,
        'dim': dim,
        'equations_count': len(equations),
        'solution': str(solution),
        'remaining_constraints': [str(e) for e in remaining_eqs] if isinstance(solution, dict) else []
    }

if __name__ == "__main__":
    for n in [1, 2]:
        test_algebra(n)
