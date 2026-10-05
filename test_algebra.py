#!/usr/bin/env python3
"""
Test Jacobi identity and triviality condition for C(n+1) = osp(2|2n).
"""

import sympy as sp
from algebra_engine import get_basis, compute_supercommutator_bracket

def test_algebra(n):
    print(f"================ Testing n = {n} ================")
    basis = get_basis(n)
    basis_names = [b[0] for b in basis]
    dim = len(basis)
    print(f"Basis size: {dim}")
    
    # Define gb variables
    gb_vars = {}
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                gb_vars[(sigma, j, s)] = sp.Symbol(f"gb_{sigma}_{j}_{s}")
                
    # 1. Test skew-supersymmetry
    print("Testing skew-supersymmetry...")
    for i in range(dim):
        for j in range(i, dim):
            g1, g2 = basis[i], basis[j]
            p1, p2 = g1[1], g2[1]
            sign = (-1)**(p1 * p2)
            
            b0_ij, g_ij = compute_supercommutator_bracket(g1, g2, basis_names, gb_vars)
            b0_ji, g_ji = compute_supercommutator_bracket(g2, g1, basis_names, gb_vars)
            
            # Check undeformed
            for k in basis_names:
                v_ij = b0_ij.get(k, sp.Integer(0))
                v_ji = b0_ji.get(k, sp.Integer(0))
                if sp.simplify(v_ji + sign * v_ij) != 0:
                    print(f"Skew-supersymmetry failed for undeformed [{g1[0]}, {g2[0]}]: {v_ji} != {-sign * v_ij}")
                    return False
                    
            # Check gamma
            for k in basis_names:
                v_ij = g_ij.get(k, sp.Integer(0))
                v_ji = g_ji.get(k, sp.Integer(0))
                if sp.simplify(v_ji + sign * v_ij) != 0:
                    print(f"Skew-supersymmetry failed for gamma({g1[0]}, {g2[0]}): {v_ji} != {-sign * v_ij}")
                    return False
    print("Skew-supersymmetry PASSED!")
    
    # 2. Test Super-Jacobi identity for undeformed bracket
    print("Testing Super-Jacobi identity for undeformed bracket...")
    jacobi_passed = True
    # Helper to compute bracket of linear combinations
    def bracket_linear(dict1, g2_elem):
        res = {k: sp.Integer(0) for k in basis_names}
        for name, coeff in dict1.items():
            if coeff == 0:
                continue
            idx = basis_names.index(name)
            b0 = compute_supercommutator_bracket(basis[idx], g2_elem, basis_names)
            for k, v in b0.items():
                res[k] += coeff * v
        return {k: v for k, v in res.items() if v != 0}

    for i in range(dim):
        for j in range(i, dim):
            for k in range(j, dim):
                X, Y, Z = basis[i], basis[j], basis[k]
                px, py, pz = X[1], Y[1], Z[1]
                
                # Term 1: (-1)^{px pz} [X, [Y, Z]]
                b_yz = compute_supercommutator_bracket(Y, Z, basis_names)
                # [X, b_yz] = - (-1)^{px (py+pz)} [b_yz, X]
                b_x_yz = bracket_linear(b_yz, X)
                s1 = (-1)**(px * pz) * (-1)**(1 + px * (py + pz)) # because bracket_linear computes [b_yz, X]
                
                # Term 2: (-1)^{py px} [Y, [Z, X]]
                b_zx = compute_supercommutator_bracket(Z, X, basis_names)
                b_y_zx = bracket_linear(b_zx, Y)
                s2 = (-1)**(py * px) * (-1)**(1 + py * (pz + px))
                
                # Term 3: (-1)^{pz py} [Z, [X, Y]]
                b_xy = compute_supercommutator_bracket(X, Y, basis_names)
                b_z_xy = bracket_linear(b_xy, Z)
                s3 = (-1)**(pz * py) * (-1)**(1 + pz * (px + py))
                
                total = {name: sp.Integer(0) for name in basis_names}
                for name, coeff in b_x_yz.items():
                    total[name] += s1 * coeff
                for name, coeff in b_y_zx.items():
                    total[name] += s2 * coeff
                for name, coeff in b_z_xy.items():
                    total[name] += s3 * coeff
                    
                for name, coeff in total.items():
                    if sp.simplify(coeff) != 0:
                        print(f"Jacobi failed for ({X[0]}, {Y[0]}, {Z[0]}): {name} -> {coeff}")
                        jacobi_passed = False
                        break
                if not jacobi_passed:
                    break
            if not jacobi_passed:
                break
        if not jacobi_passed:
            break
            
    if jacobi_passed:
        print("Super-Jacobi identity PASSED!")
    else:
        print("Super-Jacobi identity FAILED!")
        
    return True

test_algebra(1)
test_algebra(2)
