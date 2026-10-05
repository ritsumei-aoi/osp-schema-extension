"""
Full verification and solving script for C(n+1) triviality analysis
"""
import sympy as sp
from itertools import product
from verify_cn1 import get_algebra
from verify_brackets import build_representation_map, compute_brackets

def test_algebra_consistency(n):
    print(f"\n=================== Testing n = {n} ===================")
    alg = get_algebra(n)
    dim_g = alg['dim_g']
    generators = alg['generators']
    p = [g['parity'] for g in generators]
    
    bracket_0, gamma_def = compute_brackets(alg)
    
    # 1. Check graded skew-symmetry of bracket_0
    # [Y, X] = - (-1)^(p(X)p(Y)) [X, Y]
    skew_0_ok = True
    for i in range(dim_g):
        for j in range(dim_g):
            expected = - ((-1)**(p[i]*p[j])) * bracket_0[i][j]
            diff = bracket_0[j][i] - expected
            if any(val != 0 for val in diff):
                print(f"Skew-symmetry failed for bracket_0 between {generators[i]['name']} and {generators[j]['name']}")
                skew_0_ok = False
                break
        if not skew_0_ok:
            break
    print(f"bracket_0 graded skew-symmetry: {'PASSED' if skew_0_ok else 'FAILED'}")
    
    # 2. Check graded Jacobi identity of bracket_0:
    # (-1)^(p(X)p(Z)) [X, [Y, Z]] + (-1)^(p(Y)p(X)) [Y, [Z, X]] + (-1)^(p(Z)p(Y)) [Z, [X, Y]] = 0
    jacobi_0_ok = True
    for i in range(dim_g):
        for j in range(dim_g):
            for k in range(dim_g):
                # [Y, Z]
                b_jk = bracket_0[j][k]
                # [X, [Y, Z]] = sum_m b_jk[m] bracket_0[i][m]
                term1 = sp.zeros(dim_g, 1)
                for m in range(dim_g):
                    if b_jk[m] != 0:
                        term1 += b_jk[m] * bracket_0[i][m]
                term1 *= (-1)**(p[i]*p[k])
                
                # [Z, X]
                b_ki = bracket_0[k][i]
                term2 = sp.zeros(dim_g, 1)
                for m in range(dim_g):
                    if b_ki[m] != 0:
                        term2 += b_ki[m] * bracket_0[j][m]
                term2 *= (-1)**(p[j]*p[i])
                
                # [X, Y]
                b_ij = bracket_0[i][j]
                term3 = sp.zeros(dim_g, 1)
                for m in range(dim_g):
                    if b_ij[m] != 0:
                        term3 += b_ij[m] * bracket_0[k][m]
                term3 *= (-1)**(p[k]*p[j])
                
                total = term1 + term2 + term3
                if any(val != 0 for val in total):
                    print(f"Jacobi failed for ({generators[i]['name']}, {generators[j]['name']}, {generators[k]['name']})")
                    jacobi_0_ok = False
                    break
            if not jacobi_0_ok:
                break
        if not jacobi_0_ok:
            break
    print(f"bracket_0 graded Jacobi identity: {'PASSED' if jacobi_0_ok else 'FAILED'}")
    
    # 3. Check gamma_def skew-symmetry
    # In deformed bracket [X, Y] = [X, Y]_0 + kappa * gamma(X, Y),
    # since p(kappa) = 1, [Y, X]_gamma = - (-1)^(p(X)p(Y)) [X, Y]_gamma.
    # [Y, X]_0 + kappa gamma(Y, X) = - (-1)^(p(X)p(Y)) ([X, Y]_0 + kappa gamma(X, Y))
    # But notice kappa * gamma(X, Y) vs gamma: kappa is central,
    # so gamma(Y, X) = - (-1)^(p(X)p(Y)) gamma(X, Y) or with sign?
    # Let's check what gamma_def gives directly from commutator:
    print("\nChecking gamma_def properties...")
    skew_gamma_ok = True
    for i in range(dim_g):
        for j in range(dim_g):
            expected = - ((-1)**(p[i]*p[j])) * gamma_def[i][j]
            diff = gamma_def[j][i] - expected
            if any(sp.simplify(val) != 0 for val in diff):
                print(f"Skew-symmetry failed for gamma_def between {generators[i]['name']} and {generators[j]['name']}: diff = {diff}")
                skew_gamma_ok = False
                break
        if not skew_gamma_ok:
            break
    print(f"gamma_def graded skew-symmetry: {'PASSED' if skew_gamma_ok else 'FAILED'}")
    
    return alg, bracket_0, gamma_def

test_algebra_consistency(1)
