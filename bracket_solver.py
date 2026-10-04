import sympy as sp
from algebra_helper import build_algebra
from reduction import get_osc_parity, deformed_bracket_osc, reduce_pair_to_basis

def compute_bracket(X, Y, n, basis, basis_map, gb_dict):
    # X and Y are elements of basis: (name, parity, [ (coeff, osc1, osc2), ... ])
    pX = X[1]
    pY = Y[1]
    dim = len(basis)
    
    vec_0 = [sp.Rational(0)] * dim
    vec_gamma = [sp.Rational(0)] * dim
    
    for (cA, u1, u2) in X[2]:
        pu1 = get_osc_parity(u1)
        pu2 = get_osc_parity(u2)
        for (cB, v1, v2) in Y[2]:
            pv1 = get_osc_parity(v1)
            pv2 = get_osc_parity(v2)
            
            # Term 1: u1 [u2, v1] v2
            c0, ck = deformed_bracket_osc(u2, v1, gb_dict)
            if c0 != 0:
                r = reduce_pair_to_basis(u1, v2, n, basis_map)
                for i in range(dim):
                    vec_0[i] += cA * cB * c0 * r[i]
            if ck != 0:
                s = (-1)**pu1
                r = reduce_pair_to_basis(u1, v2, n, basis_map)
                for i in range(dim):
                    vec_gamma[i] += cA * cB * ck * s * r[i]
                    
            # Term 2: (-1)^{p(u2) p(v1)} u1 v1 [u2, v2]
            c0, ck = deformed_bracket_osc(u2, v2, gb_dict)
            s_base = (-1)**(pu2 * pv1)
            if c0 != 0:
                r = reduce_pair_to_basis(u1, v1, n, basis_map)
                for i in range(dim):
                    vec_0[i] += cA * cB * s_base * c0 * r[i]
            if ck != 0:
                s = s_base * ((-1)**(pu1 + pv1))
                r = reduce_pair_to_basis(u1, v1, n, basis_map)
                for i in range(dim):
                    vec_gamma[i] += cA * cB * ck * s * r[i]
                    
            # Term 3: (-1)^{p(u2) p(Y)} [u1, v1] v2 u2
            c0, ck = deformed_bracket_osc(u1, v1, gb_dict)
            s_base = (-1)**(pu2 * pY)
            if c0 != 0:
                r = reduce_pair_to_basis(v2, u2, n, basis_map)
                for i in range(dim):
                    vec_0[i] += cA * cB * s_base * c0 * r[i]
            if ck != 0:
                s = s_base
                r = reduce_pair_to_basis(v2, u2, n, basis_map)
                for i in range(dim):
                    vec_gamma[i] += cA * cB * ck * s * r[i]
                    
            # Term 4: (-1)^{p(u2) p(Y) + p(u1) p(v1)} v1 [u1, v2] u2
            c0, ck = deformed_bracket_osc(u1, v2, gb_dict)
            s_base = (-1)**(pu2 * pY + pu1 * pv1)
            if c0 != 0:
                r = reduce_pair_to_basis(v1, u2, n, basis_map)
                for i in range(dim):
                    vec_0[i] += cA * cB * s_base * c0 * r[i]
            if ck != 0:
                s = s_base * ((-1)**pv1)
                r = reduce_pair_to_basis(v1, u2, n, basis_map)
                for i in range(dim):
                    vec_gamma[i] += cA * cB * ck * s * r[i]
                    
    return vec_0, vec_gamma

print("compute_bracket defined.")
