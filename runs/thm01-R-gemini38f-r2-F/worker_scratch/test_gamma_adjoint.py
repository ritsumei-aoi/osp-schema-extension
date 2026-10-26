import sys
sys.path.append('.')
from src.C_generators import build_c_generators, Poly
from fractions import Fraction
import sympy as sp
from collections import defaultdict

# Deformation relation:
# [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
# [a_1^sigma, b_j^s] = + gb_{sigma, j, s} * kappa
# All other [v, w] undeformed:
# [a_1^-, a_1^+] = 1, [a_1^+, a_1^-] = 1
# [b_j^-, b_k^+] = delta_{jk}, [b_j^+, b_k^-] = - delta_{jk}

def get_bracket_A(v1, v2, n, sign_choice=1):
    # returns (c_K, dict of {gb_param: c_kappa})
    # [v1, v2] in A
    # v1, v2 are strings: a_1_p, a_1_m, b_k_p, b_k_m
    c_K = Fraction(0)
    c_kappa = {}
    
    # Parities
    p1 = 1 if v1.startswith("a_") else 0
    p2 = 1 if v2.startswith("a_") else 0
    
    if p1 == 1 and p2 == 1:
        # {a_1^-, a_1^+} = 1
        if (v1 == "a_1_m" and v2 == "a_1_p") or (v1 == "a_1_p" and v2 == "a_1_m"):
            c_K = Fraction(1)
    elif p1 == 0 and p2 == 0:
        # [b_j^-, b_k^+] = delta_jk
        parts1 = v1.split("_")
        parts2 = v2.split("_")
        j, s1 = int(parts1[1]), parts1[2]
        k, s2 = int(parts2[1]), parts2[2]
        if j == k and s1 != s2:
            if s1 == "m" and s2 == "p":
                c_K = Fraction(1)
            elif s1 == "p" and s2 == "m":
                c_K = Fraction(-1)
    else:
        # Mixed: [b_j^s, a_1^sigma] = - gb * kappa
        if p1 == 0 and p2 == 1:
            # v1 is boson, v2 is fermion
            sigma = "p" if "p" in v2 else "m"
            parts = v1.split("_")
            j, s = parts[1], parts[2]
            param = f"gb_a1{sigma}_b{j}{s}"
            c_kappa[param] = Fraction(-1 * sign_choice)
        else:
            # v1 is fermion, v2 is boson
            # [a_1^sigma, b_j^s] = - [b_j^s, a_1^sigma] = + gb * kappa
            sigma = "p" if "p" in v1 else "m"
            parts = v2.split("_")
            j, s = parts[1], parts[2]
            param = f"gb_a1{sigma}_b{j}{s}"
            c_kappa[param] = Fraction(1 * sign_choice)
            
    return c_K, c_kappa

# Action of quadratic generator X on v in A:
# X = sum c_i xi_1 xi_2
# [X, v] = xi_1 [xi_2, v] + (-1)^{p(xi_2) p(v)} [xi_1, v] xi_2
# In A, [xi, v] = c_K(xi, v) K + c_kappa(xi, v) kappa.
# Since K=1:
# [xi, v] = c_K(xi, v) + c_kappa(xi, v) kappa.
# So:
# [X, v] = xi_1 (c_K(xi_2, v) + c_kappa(xi_2, v) kappa) 
#        + (-1)^{p(xi_2) p(v)} (c_K(xi_1, v) + c_kappa(xi_1, v) kappa) xi_2
# = [X, v]_0 + kappa * [X, v]_1
# where [X, v]_0 = c_K(xi_2, v) xi_1 + (-1)^{p(xi_2) p(v)} c_K(xi_1, v) xi_2 (element of V!)
# and [X, v]_1 = c_kappa(xi_2, v) xi_1 + (-1)^{p(xi_2) p(v)} c_kappa(xi_1, v) xi_2 (also an element of V!)

def act_on_v(X_name, v, data, n, sign_choice=1):
    # Returns (v0_dict, v1_dict_by_param)
    # v0_dict: {target_v: Fraction}
    # v1_dict_by_param: {param: {target_v: Fraction}}
    gen = data["generators"][X_name]
    v0_dict = defaultdict(Fraction)
    v1_dict = defaultdict(lambda: defaultdict(Fraction))
    
    p_v = 1 if v.startswith("a_") else 0
    
    for m, c in gen.terms.items():
        words = m.to_words()
        if len(words) == 2:
            xi1, xi2 = words[0], words[1]
            p_xi1 = 1 if xi1.startswith("a_") else 0
            p_xi2 = 1 if xi2.startswith("a_") else 0
            
            # [xi2, v]
            cK_2, ckap_2 = get_bracket_A(xi2, v, n, sign_choice)
            # [xi1, v]
            cK_1, ckap_1 = get_bracket_A(xi1, v, n, sign_choice)
            
            # term from [xi2, v] * xi1
            if cK_2 != 0:
                v0_dict[xi1] += c * cK_2
            for param, ck in ckap_2.items():
                v1_dict[param][xi1] += c * ck
                
            # term from [xi1, v] * xi2
            sign_cross = -1 if (p_xi2 * p_v) % 2 == 1 else 1
            if cK_1 != 0:
                v0_dict[xi2] += c * cK_1 * sign_cross
            for param, ck in ckap_1.items():
                v1_dict[param][xi2] += c * ck * sign_cross
                
    return dict(v0_dict), {param: dict(v1_dict[param]) for param in v1_dict}

# Now for [X, Y]:
# [X, Y] act on v:
# [X, [Y, v]] - (-1)^{pX pY} [Y, [X, v]]
# Let's compute the coefficient of kappa in this double action:
# It comes from:
# 1. [X, [Y, v]_1] + [X, [Y, v]_0]_1
# - (-1)^{pX pY} ( [Y, [X, v]_1] + [Y, [X, v]_0]_1 )

def compute_gamma_action_on_V(X_name, Y_name, data, n, v_names, sign_choice=1):
    # Returns dict of {param: matrix (dim_V x dim_V)}
    dim_V = len(v_names)
    v_to_idx = {v: i for i, v in enumerate(v_names)}
    
    pX = data["parities"][X_name]
    pY = data["parities"][Y_name]
    sign_XY = -1 if (pX * pY) % 2 == 1 else 1
    
    # We will accumulate the matrix for each param
    param_matrices = defaultdict(lambda: sp.zeros(dim_V, dim_V))
    
    for col, v in enumerate(v_names):
        # 1. [Y, v]
        Y_v0, Y_v1 = act_on_v(Y_name, v, data, n, sign_choice)
        # 2. [X, v]
        X_v0, X_v1 = act_on_v(X_name, v, data, n, sign_choice)
        
        # All params that appear
        all_params = set(Y_v1.keys()) | set(X_v1.keys())
        
        # Term 1: [X, [Y, v]]_kappa
        # Part 1a: [X, [Y, v]_1]
        for param, target_dict in Y_v1.items():
            for w, cw in target_dict.items():
                w_v0, _ = act_on_v(X_name, w, data, n, sign_choice)
                for u, cu in w_v0.items():
                    param_matrices[param][v_to_idx[u], col] += sp.Rational(cw * cu)
                    
        # Part 1b: [X, [Y, v]_0]_1
        for w, cw in Y_v0.items():
            _, w_v1 = act_on_v(X_name, w, data, n, sign_choice)
            for param, target_dict in w_v1.items():
                for u, cu in target_dict.items():
                    param_matrices[param][v_to_idx[u], col] += sp.Rational(cw * cu)
                    
        # Term 2: - sign_XY * [Y, [X, v]]_kappa
        # Part 2a: [Y, [X, v]_1]
        for param, target_dict in X_v1.items():
            for w, cw in target_dict.items():
                w_v0, _ = act_on_v(Y_name, w, data, n, sign_choice)
                for u, cu in w_v0.items():
                    param_matrices[param][v_to_idx[u], col] -= sign_XY * sp.Rational(cw * cu)
                    
        # Part 2b: [Y, [X, v]_0]_1
        for w, cw in X_v0.items():
            _, w_v1 = act_on_v(Y_name, w, data, n, sign_choice)
            for param, target_dict in w_v1.items():
                for u, cu in target_dict.items():
                    param_matrices[param][v_to_idx[u], col] -= sign_XY * sp.Rational(cw * cu)
                    
    return param_matrices

# Let's test this on C(2) (n=1)!
data = build_c_generators(1)
v_names = ["a_1_p", "a_1_m", "b_1_p", "b_1_m"]
dim_V = 4
full_basis = data["odd_basis"] + data["even_basis"]

# Build basis matrix of ad(Z) on V:
ad_basis_vecs = []
for name in full_basis:
    poly_Z = data["generators"][name]
    p_Z = data["parities"][name]
    mat = sp.zeros(dim_V, dim_V)
    for col, v in enumerate(v_names):
        z_v0, _ = act_on_v(name, v, data, 1)
        for u, cu in z_v0.items():
            mat[v_names.index(u), col] = sp.Rational(cu)
    ad_basis_vecs.append(sp.Matrix(mat).reshape(dim_V * dim_V, 1))
Ad_Matrix = sp.Matrix.hstack(*ad_basis_vecs)

print("Testing all generator pairs for C(2)...")
all_closed = True
non_zero_gammas = 0
for X in full_basis:
    for Y in full_basis:
        param_mats = compute_gamma_action_on_V(X, Y, data, 1, v_names)
        for param, mat in param_mats.items():
            vec = sp.Matrix(mat).reshape(dim_V * dim_V, 1)
            try:
                sol, params = Ad_Matrix.gauss_jordan_solve(vec)
                residual = Ad_Matrix * sol - vec
                if any(r != 0 for r in residual):
                    print(f"FAILED (residual != 0) for ({X}, {Y}), param={param}")
                    all_closed = False
                    break
                else:
                    if any(val != 0 for val in sol):
                        non_zero_gammas += 1
            except Exception as e:
                print(f"FAILED ({e}) for ({X}, {Y}), param={param}")
                print(f"Matrix of action on V:\n{mat}")
                all_closed = False
                break

        if not all_closed:
            break

print(f"All gamma brackets closed in basis: {all_closed}")
print(f"Total non-zero gamma components: {non_zero_gammas}")
