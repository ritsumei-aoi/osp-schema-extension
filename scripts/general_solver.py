"""
General solver for C(n+1) triviality for n=1, 2, 3.
"""
import sympy as sp
from general_algebra import setup_algebra

def run_verification(n):
    alg = setup_algebra(n)
    parities = alg['parities']
    c0 = alg['c0']
    gb_list = alg['gb_list']
    generators = alg['generators']
    gen_list = alg['gen_list']
    even_gens = alg['even_gens']
    odd_gens = alg['odd_gens']
    normal_order = alg['normal_order']
    
    # Precompute [u, w]_0 for all pairs of oscillators
    # For deformed brackets, we will compute basis cocycles gamma^{(param)} for each param in gb_list
    
    # Monomial bracket function:
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
        
        res0 = {}
        res1 = {}
        def add0(p, v): res0[p] = res0.get(p, sp.Rational(0)) + v
        def add1(p, v): res1[p] = res1.get(p, sp.Rational(0)) + v
        
        # Term 1: u1 [u2, w1] w2
        if c0_u2_w1 != 0: add0((u1, w2), c0_u2_w1)
        if c1_u2_w1 != 0: add1((u1, w2), c1_u2_w1 * (-1)**pu1)
        
        # Term 2: (-1)^{pu2 * pw1} u1 w1 [u2, w2]
        sign2 = (-1)**(pu2 * pw1)
        if c0_u2_w2 != 0: add0((u1, w1), sign2 * c0_u2_w2)
        if c1_u2_w2 != 0: add1((u1, w1), sign2 * c1_u2_w2 * (-1)**(pu1 + pw1))
        
        # Term 3: (-1)^{pu2 * pY} [u1, w1] w2 u2
        sign3 = (-1)**(pu2 * pY)
        if c0_u1_w1 != 0: add0((w2, u2), sign3 * c0_u1_w1)
        if c1_u1_w1 != 0: add1((w2, u2), sign3 * c1_u1_w1)
        
        # Term 4: (-1)^{pu2 * pY + pu1 * pw1} w1 [u1, w2] u2
        sign4 = (-1)**(pu2 * pY + pu1 * pw1)
        if c0_u1_w2 != 0: add0((w1, u2), sign4 * c0_u1_w2)
        if c1_u1_w2 != 0: add1((w1, u2), sign4 * c1_u1_w2 * (-1)**pw1)
        
        return res0, res1

    # 1. Compute undeformed brackets [X, Y]_0 for all pairs
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

    # 2. Setup coboundary operator delta: C^1(g, g) -> C^2(g, g)
    # C^1(g, g)_{odd}:
    # f_even: even_gens -> odd_gens (dim = len(even_gens) * len(odd_gens))
    # f_odd: odd_gens -> even_gens (dim = len(odd_gens) * len(even_gens))
    
    # We enumerate basis elements of C^1_{odd}:
    c1_basis = []
    # (src, tgt)
    for src in even_gens:
        for tgt in odd_gens:
            c1_basis.append((src, tgt))
    for src in odd_gens:
        for tgt in even_gens:
            c1_basis.append((src, tgt))
            
    c1_dim = len(c1_basis)
    c1_idx = {b: i for i, b in enumerate(c1_basis)}
    print(f"dim C^1(g, g)_odd = {c1_dim}")
    
    # Independent pairs for C^2(g, g)_{odd}:
    # (X, Y) pairs such that p(X) + p(Y) + 1 = 1 mod 2 (i.e. p(X) + p(Y) = 0 mod 2)
    # OR p(X) + p(Y) + 1 = 0 mod 2 (i.e. p(X) + p(Y) = 1 mod 2).
    # Since gamma is an ODD cochain:
    # Parity of gamma(X, Y) is p(X) + p(Y) + 1 mod 2!
    # So if X, Y are even: p(gamma) = 1 (odd)
    # If X, Y are odd: p(gamma) = 1 (odd)
    # If one even, one odd: p(gamma) = 0 (even).
    
    # Let's list independent pairs (X, Y):
    # For (even, even): X < Y
    # For (odd, odd): X <= Y
    # For (even, odd): all (X, Y)
    c2_pairs = []
    for i, g1 in enumerate(even_gens):
        for j, g2 in enumerate(even_gens):
            if i < j:
                c2_pairs.append((g1, g2))
    for i, g1 in enumerate(odd_gens):
        for j, g2 in enumerate(odd_gens):
            if i <= j:
                c2_pairs.append((g1, g2))
    for g1 in even_gens:
        for g2 in odd_gens:
            c2_pairs.append((g1, g2))
            
    # For each pair (X, Y), the output space is either odd_gens (if pX=pY) or even_gens (if pX!=pY).
    c2_target_eqs = []
    for (X, Y) in c2_pairs:
        pX = generators[X][2]
        pY = generators[Y][2]
        out_parity = (pX + pY + 1) % 2
        out_gens = odd_gens if out_parity == 1 else even_gens
        for Z in out_gens:
            c2_target_eqs.append(((X, Y), Z))
            
    num_eqs = len(c2_target_eqs)
    c2_eq_idx = {eq: i for i, eq in enumerate(c2_target_eqs)}
    print(f"Total independent equations in C^2(g, g)_odd = {num_eqs}")
    
    # Helper to compute [X, Y]_0 between two elements:
    def br(X, Y):
        return br_0[(X, Y)]
        
    # Build Coboundary Matrix M_delta of shape (num_eqs, c1_dim):
    # For each basis element e_{src, tgt} of C^1:
    # delta(e_{src, tgt})(X, Y) = (-1)^{pX} [X, e(Y)] - (-1)^{(pX+1)pY} [Y, e(X)] - e([X, Y])
    
    M_delta = sp.zeros(num_eqs, c1_dim)
    
    print("Assembling coboundary matrix M_delta...")
    for col, (src, tgt) in enumerate(c1_basis):
        p_src = generators[src][2]
        p_tgt = generators[tgt][2]
        
        for (X, Y) in c2_pairs:
            pX = generators[X][2]
            pY = generators[Y][2]
            out_parity = (pX + pY + 1) % 2
            out_gens = odd_gens if out_parity == 1 else even_gens
            
            # term 1: (-1)^pX [X, e(Y)]
            # e(Y) is tgt if Y == src, else 0
            if Y == src:
                sign1 = (-1)**pX
                br_X_tgt = br(X, tgt)
                for Z in out_gens:
                    coeff = br_X_tgt.get(Z, sp.Rational(0))
                    if coeff != 0:
                        row = c2_eq_idx[((X, Y), Z)]
                        M_delta[row, col] += sign1 * coeff
                        
            # term 2: - (-1)^{(pX+1)pY} [Y, e(X)]
            # e(X) is tgt if X == src, else 0
            if X == src:
                sign2 = - ((-1)**((pX + 1) * pY))
                br_Y_tgt = br(Y, tgt)
                for Z in out_gens:
                    coeff = br_Y_tgt.get(Z, sp.Rational(0))
                    if coeff != 0:
                        row = c2_eq_idx[((X, Y), Z)]
                        M_delta[row, col] += sign2 * coeff
                        
            # term 3: - e([X, Y])
            # [X, Y]_0 component of src
            coeff_src = br(X, Y).get(src, sp.Rational(0))
            if coeff_src != 0:
                # e(src) = tgt
                if tgt in out_gens:
                    row = c2_eq_idx[((X, Y), tgt)]
                    M_delta[row, col] -= coeff_src

    rank_delta = M_delta.rank()
    print(f"Rank of M_delta = {rank_delta} (out of {c1_dim} cols, {num_eqs} rows)")
    
    # 3. Test each gb basis parameter
    all_trivial = True
    solutions = {}
    
    print("\nTesting each deformation parameter:")
    for param in gb_list:
        # Build c1_dict for this single parameter
        # param is e.g. 'gb_p_1_p' -> sigma='p', k=1, s='p'
        parts = param.split('_')
        sigma = parts[1]
        k = int(parts[2])
        s = parts[3]
        
        bp = 2 * k if s == 'p' else 2 * k + 1
        fa = 0 if sigma == 'p' else 1
        
        # [b, a] = -1 * kappa, [a, b] = 1 * kappa
        c1_dict = { (bp, fa): sp.Rational(-1), (fa, bp): sp.Rational(1) }
        
        # Compute gamma^{(param)}(X, Y) for all c2_pairs:
        gamma_vec = sp.zeros(num_eqs, 1)
        for (X, Y) in c2_pairs:
            t1, _, _ = generators[X]
            t2, _, _ = generators[Y]
            tot1 = {}
            for u1, u2, co1 in t1:
                for w1, w2, co2 in t2:
                    _, r1 = superbracket_monomial(u1, u2, w1, w2, c1_dict)
                    for p, v in r1.items():
                        tot1[p] = tot1.get(p, sp.Rational(0)) + co1 * co2 * v
            dec1, _ = normal_order(tot1)
            
            pX = generators[X][2]
            pY = generators[Y][2]
            out_parity = (pX + pY + 1) % 2
            out_gens = odd_gens if out_parity == 1 else even_gens
            
            for Z in out_gens:
                val = dec1.get(Z, sp.Rational(0))
                if val != 0:
                    row = c2_eq_idx[((X, Y), Z)]
                    gamma_vec[row, 0] = val
                    
        # Check if gamma_vec is in column space of M_delta
        # Augmented matrix [M_delta | gamma_vec]
        aug = M_delta.row_join(gamma_vec)
        rank_aug = aug.rank()
        
        is_coboundary = (rank_aug == rank_delta)
        print(f"Parameter {param:12s}: rank(aug)={rank_aug}, rank(M)={rank_delta} -> Trivial (coboundary)? {is_coboundary}")
        
        if not is_coboundary:
            all_trivial = False
        else:
            # Solve M_delta * f = gamma_vec
            f_sol = sp.linsolve((M_delta, gamma_vec))
            # pick one representative solution
            # replace free parameters with 0
            sol_tuple = list(f_sol)[0]
            concrete_f = {}
            for i, b in enumerate(c1_basis):
                val = sol_tuple[i]
                # substitute any remaining FreeSymbols with 0
                if hasattr(val, 'free_symbols') and val.free_symbols:
                    val = val.subs({s: 0 for s in val.free_symbols})
                if val != 0:
                    concrete_f[b] = val
            solutions[param] = concrete_f
            
    print(f"\nSummary for n={n}: All {len(gb_list)} basis deformations trivial: {all_trivial}")
    return {
        'n': n,
        'dim_g': len(gen_list),
        'c1_dim': c1_dim,
        'rank_delta': rank_delta,
        'num_eqs': num_eqs,
        'all_trivial': all_trivial,
        'solutions': solutions
    }

if __name__ == '__main__':
    res1 = run_verification(1)
    res2 = run_verification(2)
    # res3 will be run if res1 and res2 pass
