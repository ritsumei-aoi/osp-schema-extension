"""
Verify Lie superalgebra structure constants and Jacobi identity for C(n+1).
"""
import sympy as sp
from collections import defaultdict
from verification.cn1_algebra import create_algebra, get_generators, superbracket

def decompose_into_basis(term_dict, gens, n):
    """
    Given a dict of normal-ordered monomials -> coeff,
    express it as a linear combination of generators gens.
    """
    # Monomials:
    # Odd:
    # ('a+', ('b+', j)) -> F_p_j_p
    # ('a+', ('b-', j)) -> F_p_j_m
    # ('a-', ('b+', j)) -> F_m_j_p
    # ('a-', ('b-', j)) -> F_m_j_m
    
    # Even roots:
    # (('b+', k), ('b+', k)) -> 2 * E_2d_k
    # (('b-', k), ('b-', k)) -> 2 * E_-2d_k
    # (('b+', k), ('b+', l)) with k < l -> E_dp_d_k_l
    # (('b-', k), ('b-', l)) with k < l -> E_dm_d_k_l
    # (('b+', k), ('b-', l)) with k != l:
    #    if k < l: E_pm_d_k_l
    #    if k > l: E_mp_d_l_k
    
    # Diagonal monomials:
    # b_j+ b_j- for j=1..n
    # a+ a-
    # and constant term ()
    
    # We know:
    # H_{n+1} = - b_n+ b_n- - 1/2  => b_n+ b_n- = - H_{n+1} - 1/2
    # H_k = b_{k-1}+ b_{k-1}- - b_k+ b_k- => b_{k-1}+ b_{k-1}- = H_k + b_k+ b_k-
    # H_1 = a+ a- + b_1+ b_1- => a+ a- = H_1 - b_1+ b_1-
    
    # Let's express diagonal monomials in terms of H_1..H_{n+1} and constant 1:
    diag_expr = {} # maps monomial to dict of gen -> coeff, and 'const' -> coeff
    # b_n+ b_n-:
    diag_expr[(('b+', n), ('b-', n))] = {f"H_{n+1}": sp.Integer(-1), 'const': sp.Rational(-1, 2)}
    
    curr = {f"H_{n+1}": sp.Integer(-1), 'const': sp.Rational(-1, 2)}
    for k in range(n, 1, -1):
        # b_{k-1}+ b_{k-1}- = H_k + b_k+ b_k-
        new_curr = defaultdict(lambda: sp.Integer(0))
        for g, c in curr.items():
            new_curr[g] += c
        new_curr[f"H_{k}"] += sp.Integer(1)
        diag_expr[(('b+', k-1), ('b-', k-1))] = dict(new_curr)
        curr = new_curr
        
    # a+ a- = H_1 - b_1+ b_1-
    new_curr = defaultdict(lambda: sp.Integer(0))
    for g, c in curr.items():
        new_curr[g] -= c
    new_curr["H_1"] += sp.Integer(1)
    diag_expr[('a+', 'a-')] = dict(new_curr)
    
    gen_coeffs = defaultdict(lambda: sp.Integer(0))
    const_total = sp.Integer(0)
    
    for mono, coeff in term_dict.items():
        if coeff == 0:
            continue
        if mono == ():
            const_total += coeff
        elif mono in diag_expr:
            for g, c in diag_expr[mono].items():
                if g == 'const':
                    const_total += coeff * c
                else:
                    gen_coeffs[g] += coeff * c
        elif len(mono) == 2 and mono[0] == 'a+':
            # Odd
            s_b, j = mono[1]
            sign = 'p' if s_b == 'b+' else 'm'
            gen_coeffs[f"F_p_{j}_{sign}"] += coeff
        elif len(mono) == 2 and mono[0] == 'a-':
            s_b, j = mono[1]
            sign = 'p' if s_b == 'b+' else 'm'
            gen_coeffs[f"F_m_{j}_{sign}"] += coeff
        elif len(mono) == 2 and isinstance(mono[0], tuple) and isinstance(mono[1], tuple):
            (s1, j1), (s2, j2) = mono
            if s1 == 'b+' and s2 == 'b+':
                if j1 == j2:
                    gen_coeffs[f"E_2d_{j1}"] += coeff * 2
                else:
                    k, l = min(j1, j2), max(j1, j2)
                    gen_coeffs[f"E_dp_d_{k}_{l}"] += coeff
            elif s1 == 'b-' and s2 == 'b-':
                if j1 == j2:
                    gen_coeffs[f"E_-2d_{j1}"] += coeff * 2
                else:
                    k, l = min(j1, j2), max(j1, j2)
                    gen_coeffs[f"E_dm_d_{k}_{l}"] += coeff
            elif s1 == 'b+' and s2 == 'b-':
                k, l = j1, j2
                if k < l:
                    gen_coeffs[f"E_pm_d_{k}_{l}"] += coeff
                elif k > l:
                    gen_coeffs[f"E_mp_d_{l}_{k}"] += coeff
                else:
                    raise ValueError(f"Should have been handled by diag: {mono}")
            elif s1 == 'b-' and s2 == 'b+':
                k, l = j1, j2
                if k < l:
                    gen_coeffs[f"E_mp_d_{k}_{l}"] += coeff
                elif k > l:
                    gen_coeffs[f"E_pm_d_{l}_{k}"] += coeff
                else:
                    raise ValueError(f"Should have been handled by diag: {mono}")
            else:
                raise ValueError(f"Unexpected monomial: {mono}")
        else:
            raise ValueError(f"Unknown monomial structure: {mono}")
            
    clean_gen = {}
    for g, c in gen_coeffs.items():
        c_sim = sp.simplify(c)
        if c_sim != 0:
            clean_gen[g] = c_sim
    const_total = sp.simplify(const_total)
    return clean_gen, const_total

def test_algebra_structure(n=1):
    print(f"\n==========================================")
    print(f"Testing Lie superalgebra structure for n={n}")
    print(f"==========================================")
    gb, reduce_word = create_algebra(n)
    gens, parities = get_generators(n)
    gen_names = list(gens.keys())
    dim = len(gen_names)
    print(f"Dimension: {dim} (Even: {sum(1 for p in parities.values() if p==0)}, Odd: {sum(1 for p in parities.values() if p==1)})")
    
    # Compute all brackets
    # c0: structure constants [X_i, X_j]_0 = sum_k c_{ij}^k X_k
    # gamma: [X_i, X_j]_1 = sum_k gamma_{ij}^k X_k
    c0 = defaultdict(lambda: defaultdict(lambda: sp.Integer(0)))
    gamma = defaultdict(lambda: defaultdict(lambda: sp.Integer(0)))
    
    for i, g1 in enumerate(gen_names):
        for j, g2 in enumerate(gen_names):
            br = superbracket(g1, g2, gens, parities, reduce_word)
            
            # Separate c0 terms and ck terms
            t0 = {k: v[0] for k, v in br.items() if v[0] != 0}
            tk = {k: v[1] for k, v in br.items() if v[1] != 0}
            
            dec0, const0 = decompose_into_basis(t0, gens, n)
            deck, constk = decompose_into_basis(tk, gens, n)
            
            if const0 != 0:
                print(f"WARNING: Nonzero constant in undeformed bracket [{g1}, {g2}]: {const0}")
            if constk != 0:
                print(f"WARNING: Nonzero constant in gamma [{g1}, {g2}]: {constk}")
                
            for k_gen, val in dec0.items():
                c0[(g1, g2)][k_gen] = val
            for k_gen, val in deck.items():
                gamma[(g1, g2)][k_gen] = val
                
    # Verify graded skew-symmetry of c0
    skew_ok = True
    for g1 in gen_names:
        for g2 in gen_names:
            p1, p2 = parities[g1], parities[g2]
            sign = -1 if (p1 == 1 and p2 == 1) else 1
            for g3 in gen_names:
                v12 = c0[(g1, g2)][g3]
                v21 = c0[(g2, g1)][g3]
                if sp.simplify(v12 + sign * v21) != 0:
                    print(f"Skew-symmetry failed for [{g1}, {g2}]: {v12} vs {v21}")
                    skew_ok = False
    print("Graded skew-symmetry of undeformed bracket:", "PASSED" if skew_ok else "FAILED")
    
    # Verify graded Jacobi identity of c0
    jacobi_ok = True
    count_tested = 0
    for i, g1 in enumerate(gen_names):
        p1 = parities[g1]
        for j in range(i, dim):
            g2 = gen_names[j]
            p2 = parities[g2]
            for k in range(j, dim):
                g3 = gen_names[k]
                p3 = parities[g3]
                
                # J(X, Y, Z) = (-1)^{p1 p3} [X, [Y, Z]] + (-1)^{p2 p1} [Y, [Z, X]] + (-1)^{p3 p2} [Z, [X, Y]]
                # In terms of basis:
                # [Y, Z] = sum_m c_{YZ}^m X_m
                # [X, [Y, Z]] = sum_m c_{YZ}^m [X, X_m] = sum_{m, r} c_{YZ}^m c_{X m}^r X_r
                res_r = defaultdict(lambda: sp.Integer(0))
                
                # term 1: (-1)^{p1 p3} [X, [Y, Z]]
                s1 = (-1)**(p1 * p3)
                for m, c_yz_m in c0[(g2, g3)].items():
                    for r, c_xm_r in c0[(g1, m)].items():
                        res_r[r] += s1 * c_yz_m * c_xm_r
                        
                # term 2: (-1)^{p2 p1} [Y, [Z, X]]
                s2 = (-1)**(p2 * p1)
                for m, c_zx_m in c0[(g3, g1)].items():
                    for r, c_ym_r in c0[(g2, m)].items():
                        res_r[r] += s2 * c_zx_m * c_ym_r
                        
                # term 3: (-1)^{p3 p2} [Z, [X, Y]]
                s3 = (-1)**(p3 * p2)
                for m, c_xy_m in c0[(g1, g2)].items():
                    for r, c_zm_r in c0[(g3, m)].items():
                        res_r[r] += s3 * c_xy_m * c_zm_r
                        
                for r, val in res_r.items():
                    if sp.simplify(val) != 0:
                        print(f"Jacobi failed for ({g1}, {g2}, {g3}) at component {r}: {val}")
                        jacobi_ok = False
                        break
                count_tested += 1
                if not jacobi_ok:
                    break
            if not jacobi_ok:
                break
        if not jacobi_ok:
            break
    print(f"Graded Jacobi identity of undeformed bracket ({count_tested} triples):", "PASSED" if jacobi_ok else "FAILED")
    
    return gen_names, parities, c0, gamma, gb

if __name__ == '__main__':
    test_algebra_structure(1)
