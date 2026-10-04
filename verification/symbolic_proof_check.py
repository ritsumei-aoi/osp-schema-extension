"""
Symbolic verification of the Whitehead-Cartan obstruction proof for general n.
"""
import sympy as sp

def verify_symbolic_proof():
    # Variables for gb parameters of index k
    gb_plus_plus = sp.Symbol('gb_+_k_+')
    gb_plus_minus = sp.Symbol('gb_+_k_-')
    gb_minus_plus = sp.Symbol('gb_-_k_+')
    gb_minus_minus = sp.Symbol('gb_-_k_-')
    
    # Coefficients of w = f(H_0)
    c_plus_plus = sp.Symbol('c_+_k_+')
    c_plus_minus = sp.Symbol('c_+_k_-')
    c_minus_plus = sp.Symbol('c_-_k_+')
    c_minus_minus = sp.Symbol('c_-_k_-')
    
    # Matching equations:
    # From [w, E_+2d_k] = gamma(H_0, E_+2d_k):
    # - c_+_k_- = gb_-_k_+
    # - c_-_k_- = gb_+_k_+
    eq1 = - c_plus_minus - gb_minus_plus
    eq2 = - c_minus_minus - gb_plus_plus
    
    # From [w, E_-2d_k] = gamma(H_0, E_-2d_k):
    # c_+_k_+ = gb_-_k_-
    # c_-_k_+ = gb_+_k_-
    eq3 = c_plus_plus - gb_minus_minus
    eq4 = c_minus_plus - gb_plus_minus
    
    # From [w, h_k] = gamma(H_0, h_k):
    # [w, h_k] components are:
    # E_+e+d_k component: - c_+_k_+
    # E_+e-d_k component: + c_+_k_-
    # E_-e+d_k component: - c_-_k_+
    # E_-e-d_k component: + c_-_k_-
    # gamma(H_0, h_k) components are:
    # E_+e+d_k component: gb_-_k_-
    # E_+e-d_k component: gb_-_k_+
    # E_-e+d_k component: gb_+_k_-
    # E_-e-d_k component: gb_+_k_+
    eq5 = - c_plus_plus - gb_minus_minus
    eq6 = c_plus_minus - gb_minus_plus
    eq7 = - c_minus_plus - gb_plus_minus
    eq8 = c_minus_minus - gb_plus_plus
    
    all_eqs = [eq1, eq2, eq3, eq4, eq5, eq6, eq7, eq8]
    sol = sp.solve(all_eqs, [c_plus_plus, c_plus_minus, c_minus_plus, c_minus_minus,
                             gb_plus_plus, gb_plus_minus, gb_minus_plus, gb_minus_minus])
    print("Solution to Whitehead-Cartan matching equations:", sol)
    assert all(v == 0 for v in sol.values()), "All gb parameters must be identically zero!"
    print("Proof analytically verified!")

if __name__ == '__main__':
    verify_symbolic_proof()
