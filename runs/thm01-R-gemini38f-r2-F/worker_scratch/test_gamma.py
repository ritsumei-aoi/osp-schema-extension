import sys
sys.path.append('.')
sys.path.append('<home>/notebook/git/thm01-R-agy-home/worker-thm01-R-gemini38f-r2-F/.gemini/antigravity-cli/brain/3090f976-3b8f-4950-840e-bdc00768cc80/scratch')
from test_poly import Poly, Monomial
from src.C_generators import build_c_generators, decompose_in_basis

from fractions import Fraction
from collections import defaultdict
import sympy as sp


# Let's test for n=1: C(2) = osp(2|2)
# Deformation parameters:
# gb_{a1_p, b1_p}, gb_{a1_p, b1_m}, gb_{a1_m, b1_p}, gb_{a1_m, b1_m}
# Convention from C_inhomogeneous_definition.md:
# [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
# [a_1^sigma, b_j^s] = + gb_{sigma, j, s} * kappa

# Let's define the single-oscillator deformed commutator omega(xi, eta):
# returns a dict of {param_name: Fraction}
def get_omega(xi_name, eta_name, n, sign_choice=1):
    # sign_choice: +1 for [b, a] = - gb * kappa (Eq. 22)
    #              -1 for [b, a] = + gb * kappa
    res = {}
    # Check if one is boson and one is fermion
    is_xi_b = xi_name.startswith("b_")
    is_eta_b = eta_name.startswith("b_")
    is_xi_a = xi_name.startswith("a_")
    is_eta_a = eta_name.startswith("a_")
    
    if is_xi_b and is_eta_a:
        # [b_j^s, a_1^sigma]
        sigma = "p" if "p" in eta_name else "m"
        parts = xi_name.split("_")
        j = parts[1]
        s = parts[2]
        param = f"gb_a1{sigma}_b{j}{s}"
        res[param] = Fraction(-1 * sign_choice)
    elif is_xi_a and is_eta_b:
        # [a_1^sigma, b_j^s] = - [b_j^s, a_1^sigma] = + gb * kappa
        sigma = "p" if "p" in xi_name else "m"
        parts = eta_name.split("_")
        j = parts[1]
        s = parts[2]
        param = f"gb_a1{sigma}_b{j}{s}"
        res[param] = Fraction(1 * sign_choice)
    return res

def compute_gamma_term(xi1, xi2, eta1, eta2, n, sign_choice=1):
    # Evaluates the first-order deformation of [\xi1 \xi2, \eta1 \eta2}
    # Returns dict of {param: Poly}
    # Formula:
    # term 1: \omega(\xi2, \eta1) * \xi1 * \eta2
    # term 2: (-1)^{p(\xi2) p(\eta1)} * \omega(\xi2, \eta2) * \xi1 * \eta1
    # term 3: (-1)^{p(\xi2) p(Y)} * \omega(\xi1, \eta1) * \eta2 * \xi2
    # term 4: (-1)^{p(\xi2) p(Y) + p(\xi1) p(\eta1)} * \omega(\xi1, \eta2) * \eta1 * \xi2
    
    p_xi1 = 1 if xi1.startswith("a_") else 0
    p_xi2 = 1 if xi2.startswith("a_") else 0
    p_eta1 = 1 if eta1.startswith("a_") else 0
    p_eta2 = 1 if eta2.startswith("a_") else 0
    p_Y = (p_eta1 + p_eta2) % 2
    
    P_xi1 = Poly.from_osc(xi1, n)
    P_xi2 = Poly.from_osc(xi2, n)
    P_eta1 = Poly.from_osc(eta1, n)
    P_eta2 = Poly.from_osc(eta2, n)
    
    res = defaultdict(lambda: Poly(n=n))
    
    # 1. omega(xi2, eta1)
    w1 = get_omega(xi2, eta1, n, sign_choice)
    if w1:
        prod1 = P_xi1 * P_eta2
        for param, coeff in w1.items():
            res[param] = res[param] + prod1 * coeff
            
    # 2. omega(xi2, eta2)
    w2 = get_omega(xi2, eta2, n, sign_choice)
    if w2:
        s2 = -1 if (p_xi2 * p_eta1) % 2 == 1 else 1
        prod2 = P_xi1 * P_eta1
        for param, coeff in w2.items():
            res[param] = res[param] + prod2 * (coeff * s2)
            
    # 3. omega(xi1, eta1)
    w3 = get_omega(xi1, eta1, n, sign_choice)
    if w3:
        s3 = -1 if (p_xi2 * p_Y) % 2 == 1 else 1
        prod3 = P_eta2 * P_xi2
        for param, coeff in w3.items():
            res[param] = res[param] + prod3 * (coeff * s3)
            
    # 4. omega(xi1, eta2)
    w4 = get_omega(xi1, eta2, n, sign_choice)
    if w4:
        s4 = -1 if (p_xi2 * p_Y + p_xi1 * p_eta1) % 2 == 1 else 1
        prod4 = P_eta1 * P_xi2
        for param, coeff in w4.items():
            res[param] = res[param] + prod4 * (coeff * s4)
            
    return res

def compute_gamma_XY(X_name, Y_name, data, n, sign_choice=1):
    # Returns dict of {param: dict of {Z: coeff}}
    gen_data = data["generators"]
    # Deconstruct X and Y into standard form monomials (words)
    # Note: we need the quadratic words of X and Y
    # In C_generators, generators are Poly objects.
    X_poly = gen_data[X_name]
    Y_poly = gen_data[Y_name]
    
    total_res = defaultdict(lambda: Poly(n=n))
    
    for m_X, c_X in X_poly.terms.items():
        words_X = m_X.to_words()
        if len(words_X) < 2:
            continue
        xi1, xi2 = words_X[0], words_X[1]
        for m_Y, c_Y in Y_poly.terms.items():
            words_Y = m_Y.to_words()
            if len(words_Y) < 2:
                continue
            eta1, eta2 = words_Y[0], words_Y[1]
            term_dict = compute_gamma_term(xi1, xi2, eta1, eta2, n, sign_choice)
            for param, poly in term_dict.items():
                total_res[param] = total_res[param] + poly * (c_X * c_Y)
                
    # Now decompose total_res[param] in the basis!
    full_basis = data["odd_basis"] + data["even_basis"]
    decomp_by_param = {}
    for param, poly in total_res.items():
        if poly.terms:
            decomp = decompose_in_basis(poly, full_basis, gen_data)
            if decomp is None:
                print(f"FAILED to decompose gamma({X_name}, {Y_name}) for {param}: {poly.terms}")
            else:
                decomp_by_param[param] = decomp
    return decomp_by_param

data = build_c_generators(1)
print("Testing gamma for C(2)...")
count = 0
failures = 0
full_basis = data["odd_basis"] + data["even_basis"]
for X in full_basis:
    for Y in full_basis:
        res = compute_gamma_XY(X, Y, data, 1)
        if res:
            count += 1
print(f"Non-zero gamma pairs for C(2): {count}")

