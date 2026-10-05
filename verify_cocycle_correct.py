"""
Verify 2-cocycle with correct graded signs for odd kappa
"""
import sympy as sp
from verify_cn1 import get_algebra
from verify_brackets import compute_brackets

def verify_cocycle_correct(n):
    alg = get_algebra(n)
    dim_g = alg['dim_g']
    generators = alg['generators']
    p = [g['parity'] for g in generators]
    
    bracket_0, gamma_def = compute_brackets(alg)
    
    jacobi_linear_ok = True
    violating = []
    
    for i in range(dim_g):
        for j in range(dim_g):
            for k in range(dim_g):
                # Jacobi sum:
                # cyclic sum over (i, j, k) with sign (-1)^(p[i]*p[k]):
                # [X, [Y, Z]_L] = [X, [Y, Z]_0]_0 + kappa * ( (-1)^p[X] [X, gamma(Y, Z)]_0 + gamma(X, [Y, Z]_0) )
                
                # Term 1:
                g_jk = gamma_def[j][k]
                t1a = sp.zeros(dim_g, 1)
                for m in range(dim_g):
                    if g_jk[m] != 0:
                        t1a += g_jk[m] * bracket_0[i][m]
                t1a *= (-1)**p[i] # due to [X, kappa ...] = (-1)^p[X] kappa [X, ...]
                
                b_jk = bracket_0[j][k]
                t1b = sp.zeros(dim_g, 1)
                for m in range(dim_g):
                    if b_jk[m] != 0:
                        t1b += b_jk[m] * gamma_def[i][m]
                        
                cyc1 = (t1a + t1b) * ((-1)**(p[i] * p[k]))
                
                # Term 2:
                g_ki = gamma_def[k][i]
                t2a = sp.zeros(dim_g, 1)
                for m in range(dim_g):
                    if g_ki[m] != 0:
                        t2a += g_ki[m] * bracket_0[j][m]
                t2a *= (-1)**p[j]
                
                b_ki = bracket_0[k][i]
                t2b = sp.zeros(dim_g, 1)
                for m in range(dim_g):
                    if b_ki[m] != 0:
                        t2b += b_ki[m] * gamma_def[j][m]
                        
                cyc2 = (t2a + t2b) * ((-1)**(p[j] * p[i]))
                
                # Term 3:
                g_ij = gamma_def[i][j]
                t3a = sp.zeros(dim_g, 1)
                for m in range(dim_g):
                    if g_ij[m] != 0:
                        t3a += g_ij[m] * bracket_0[k][m]
                t3a *= (-1)**p[k]
                
                b_ij = bracket_0[i][j]
                t3b = sp.zeros(dim_g, 1)
                for m in range(dim_g):
                    if b_ij[m] != 0:
                        t3b += b_ij[m] * gamma_def[k][m]
                        
                cyc3 = (t3a + t3b) * ((-1)**(p[k] * p[j]))
                
                tot = cyc1 + cyc2 + cyc3
                if any(sp.simplify(val) != 0 for val in tot):
                    jacobi_linear_ok = False
                    violating.append((generators[i]['name'], generators[j]['name'], generators[k]['name']))
                    
    print(f"Corrected 2-cocycle check for n={n}: {'PASSED (gamma_gb is a true 2-cocycle!)' if jacobi_linear_ok else 'FAILED'}")
    if not jacobi_linear_ok:
        print(f"Violating count: {len(violating)}")

verify_cocycle_correct(1)
