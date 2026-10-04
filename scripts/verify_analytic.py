"""
Test the universal formula for f and verify delta(f) == gamma for n=1, 2, 3.
"""
import sympy as sp
from general_algebra import setup_algebra

def test_analytic_formula(n):
    alg = setup_algebra(n)
    parities = alg['parities']
    c0 = alg['c0']
    gb_list = alg['gb_list']
    generators = alg['generators']
    gen_list = alg['gen_list']
    even_gens = alg['even_gens']
    odd_gens = alg['odd_gens']
    normal_order = alg['normal_order']
    
    # Precompute undeformed brackets [X, Y]_0
    def superbracket_monomial(u1, u2, w1, w2, c1_dict):
        pu1, pu2 = parities[u1], parities[u2]
        pw1, pw2 = parities[w1], parities[w2]
        pY = pw1 + pw2
        c0_u2_w1 = c0[(u2, w1)]
        c0_u2_w2 = c0[(u2, w2)]
        c0_u1_w1 = c0[(u1, w1)]
        c0_u1_w2 = c0[(u1, w2)]
        c1_u2_w1 = c1_dict.get((u2, w1), sp.Rational(0))
        c1_u2_w2 = c1_dict.get((u2, w2), sp.Rational(0))
        c1_u1_w1 = c1_dict.get((u1, w1), sp.Rational(0))
        c1_u1_w2 = c1_dict.get((u1, w2), sp.Rational(0))
        
        res0, res1 = {}, {}
        def add0(p, v): res0[p] = res0.get(p, sp.Rational(0)) + v
        def add1(p, v): res1[p] = res1.get(p, sp.Rational(0)) + v
        
        if c0_u2_w1 != 0: add0((u1, w2), c0_u2_w1)
        if c1_u2_w1 != 0: add1((u1, w2), c1_u2_w1 * (-1)**pu1)
        sign2 = (-1)**(pu2 * pw1)
        if c0_u2_w2 != 0: add0((u1, w1), sign2 * c0_u2_w2)
        if c1_u2_w2 != 0: add1((u1, w1), sign2 * c1_u2_w2 * (-1)**(pu1 + pw1))
        sign3 = (-1)**(pu2 * pY)
        if c0_u1_w1 != 0: add0((w2, u2), sign3 * c0_u1_w1)
        if c1_u1_w1 != 0: add1((w2, u2), sign3 * c1_u1_w1)
        sign4 = (-1)**(pu2 * pY + pu1 * pw1)
        if c0_u1_w2 != 0: add0((w1, u2), sign4 * c0_u1_w2)
        if c1_u1_w2 != 0: add1((w1, u2), sign4 * c1_u1_w2 * (-1)**pw1)
        return res0, res1

    br_0 = {}
    for g1 in gen_list:
        for g2 in gen_list:
            t1, _, _ = generators[g1]
            t2, _, _ = generators[g2]
            tot0 = {}
            for u1, u2, co1 in t1:
                for w1, w2, co2 in t2:
                    r0, _ = superbracket_monomial(u1, u2, w1, w2, {})
                    for p, v in r0.items():
                        tot0[p] = tot0.get(p, sp.Rational(0)) + co1 * co2 * v
            dec0, _ = normal_order(tot0)
            br_0[(g1, g2)] = dec0

    def compute_bracket_linear(d1, d2):
        res = {g: sp.Rational(0) for g in gen_list}
        for g1, c1 in d1.items():
            if c1 == 0: continue
            for g2, c2 in d2.items():
                if c2 == 0: continue
                for out_g, out_c in br_0[(g1, g2)].items():
                    if out_c != 0:
                        res[out_g] += c1 * c2 * out_c
        return res

    # Universal formula for f:
    # Given param = (sigma_0, k_0, s_0)
    # sigma_0 in {'p', 'm'}, k_0 in 1..n, s_0 in {'p', 'm'}
    def get_analytic_f(sigma_0, k_0, s_0):
        # returns dict mapping g -> dict of {target_g: coeff}
        f_map = {g: {} for g in gen_list}
        sgn_sigma = 1 if sigma_0 == 'p' else -1
        opp_sigma = 'm' if sigma_0 == 'p' else 'p'
        
        # 1. On odd generators:
        # f(F_{sigma_0, s_0, k_0}) = sgn_sigma * J
        f_map[f'F_{sigma_0}{s_0}_{k_0}']['J'] = sp.Rational(sgn_sigma)
        
        # 2. On even generators:
        # f(J) = 0
        # On sp(2n) generators:
        # Every sp(2n) generator is bilinear in bosonic oscillators.
        # Let's inspect the action:
        # For each bosonic oscillator b_i: [B, b_i] in V_0.
        # Notice what we saw in the explicit f tables:
        # For H_k:
        #   if k == k_0:
        #     f(H_k) = - F_{opp_sigma, opp_s0, k}
        # For E_2d_k:
        #   if k == k_0 and s_0 == 'p':
        #     f(E_2d_k) = - F_{opp_sigma, 'p', k}
        # For F_2d_k:
        #   if k == k_0 and s_0 == 'm':
        #     f(F_2d_k) = - F_{opp_sigma, 'm', k}
        # For cross terms E_{s1, s2}_{j}_{k}:
        #   if j == k_0:
        #     if s1 == s_0:
        #       f(E) = - F_{opp_sigma, s2, k}
        #   if k == k_0:
        #     if s2 == s_0:
        #       f(E) = - F_{opp_sigma, s1, j}
        opp_s0 = 'm' if s_0 == 'p' else 'p'
        
        # H_k:
        f_map[f'H_{k_0}'][f'F_{opp_sigma}{opp_s0}_{k_0}'] = sp.Rational(-1)
        
        # E_2d, F_2d:
        if s_0 == 'p':
            f_map[f'E_2d_{k_0}'][f'F_{opp_sigma}p_{k_0}'] = sp.Rational(-1)
        else:
            f_map[f'F_2d_{k_0}'][f'F_{opp_sigma}m_{k_0}'] = sp.Rational(-1)
            
        # Cross terms:
        for j in range(1, n + 1):
            for k in range(j + 1, n + 1):
                for s1 in ['p', 'm']:
                    for s2 in ['p', 'm']:
                        gen_name = f'E_{s1}{s2}_{j}_{k}'
                        if j == k_0 and s1 == s_0:
                            f_map[gen_name][f'F_{opp_sigma}{s2}_{k}'] = sp.Rational(-1)
                        if k == k_0 and s2 == s_0:
                            f_map[gen_name][f'F_{opp_sigma}{s1}_{j}'] = sp.Rational(-1)
                            
        return f_map

    # Test universal formula against gamma for ALL parameters:
    print(f"\n--- Testing Universal Analytic Formula for n={n} ---")
    all_passed = True
    
    for param in gb_list:
        parts = param.split('_')
        sigma = parts[1]
        k = int(parts[2])
        s = parts[3]
        
        bp = 2 * k if s == 'p' else 2 * k + 1
        fa = 0 if sigma == 'p' else 1
        c1_dict = { (bp, fa): sp.Rational(-1), (fa, bp): sp.Rational(1) }
        
        f_map = get_analytic_f(sigma, k, s)
        
        # Check delta(f)(X, Y) == gamma(X, Y) for all pairs
        param_passed = True
        num_checked = 0
        for X in gen_list:
            for Y in gen_list:
                num_checked += 1
                # compute gamma(X, Y)
                t1, _, _ = generators[X]
                t2, _, _ = generators[Y]
                tot1 = {}
                for u1, u2, co1 in t1:
                    for w1, w2, co2 in t2:
                        _, r1 = superbracket_monomial(u1, u2, w1, w2, c1_dict)
                        for p, v in r1.items():
                            tot1[p] = tot1.get(p, sp.Rational(0)) + co1 * co2 * v
                gam, _ = normal_order(tot1)
                
                # compute delta(f)(X, Y)
                pX = generators[X][2]
                pY = generators[Y][2]
                
                # term 1: (-1)^pX [X, f(Y)]
                fY = f_map[Y]
                t1_res = compute_bracket_linear({X: 1}, fY)
                
                # term 2: - (-1)^{(pX+1)pY} [Y, f(X)]
                fX = f_map[X]
                t2_res = compute_bracket_linear({Y: 1}, fX)
                
                # term 3: - f([X, Y]_0)
                br_XY = br_0[(X, Y)]
                f_XY = {g: sp.Rational(0) for g in gen_list}
                for z, cz in br_XY.items():
                    if cz != 0:
                        for tg, v in f_map[z].items():
                            f_XY[tg] += cz * v
                            
                sign1 = (-1)**pX
                sign2 = - ((-1)**((pX + 1) * pY))
                
                # compare delta_f with gam
                for g in gen_list:
                    val_df = sign1 * t1_res.get(g, 0) + sign2 * t2_res.get(g, 0) - f_XY.get(g, 0)
                    val_gam = gam.get(g, 0)
                    if sp.simplify(val_df - val_gam) != 0:
                        print(f"FAILED on param {param}, pair ({X}, {Y}), component {g}: delta_f={val_df}, gamma={val_gam}")
                        param_passed = False
                        all_passed = False
                        break
                if not param_passed:
                    break
            if not param_passed:
                break
                
        print(f"Parameter {param:12s}: Verified delta(f) == gamma across {num_checked} pairs? {param_passed}")
        
    print(f"\nFinal Result for n={n}: Analytic formula exact for all parameters: {all_passed}")
    return all_passed

if __name__ == '__main__':
    for n in [1, 2, 3]:
        ok = test_analytic_formula(n)
        if not ok:
            print(f"Error at n={n}")
            break
