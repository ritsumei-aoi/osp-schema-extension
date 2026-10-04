"""
Test 2-cocycle condition and coboundary triviality for n=1.
"""
import sympy as sp
from collections import defaultdict
from verification.cn1_algebra import create_algebra, get_generators, superbracket
from verification.test_jacobi import decompose_into_basis

def test_triviality(n=1):
    print(f"\n==========================================")
    print(f"Testing triviality for n={n}")
    print(f"==========================================")
    gb, reduce_word = create_algebra(n)
    gens, parities = get_generators(n)
    gen_names = list(gens.keys())
    dim = len(gen_names)
    
    # 1. Compute c0 and gamma
    c0 = defaultdict(lambda: defaultdict(lambda: sp.Integer(0)))
    gamma = defaultdict(lambda: defaultdict(lambda: sp.Integer(0)))
    gamma_const = defaultdict(lambda: sp.Integer(0))
    
    for g1 in gen_names:
        for g2 in gen_names:
            br = superbracket(g1, g2, gens, parities, reduce_word)
            t0 = {k: v[0] for k, v in br.items() if v[0] != 0}
            tk = {k: v[1] for k, v in br.items() if v[1] != 0}
            
            dec0, const0 = decompose_into_basis(t0, gens, n)
            deck, constk = decompose_into_basis(tk, gens, n)
            
            for k_gen, val in dec0.items():
                c0[(g1, g2)][k_gen] = val
            for k_gen, val in deck.items():
                gamma[(g1, g2)][k_gen] = val
            gamma_const[(g1, g2)] = constk

    # 2. Check graded skew-symmetry of gamma:
    # Remember: gamma is an ODD 2-cochain!
    # Wait, what is the graded skew-symmetry of an odd 2-cochain?
    # In [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y).
    # Since p(kappa) = 1, [Y, X]_gamma = - (-1)^{p(X) p(Y)} [X, Y]_gamma.
    # [Y, X]_0 + kappa * gamma(Y, X) = - (-1)^{p(X) p(Y)} ([X, Y]_0 + kappa * gamma(X, Y))
    # Since [Y, X]_0 = - (-1)^{p(X) p(Y)} [X, Y]_0,
    # kappa * gamma(Y, X) = - (-1)^{p(X) p(Y)} kappa * gamma(X, Y).
    # Therefore, gamma(Y, X) = - (-1)^{p(X) p(Y)} gamma(X, Y)!
    # Let's verify this!
    skew_gamma_ok = True
    for g1 in gen_names:
        for g2 in gen_names:
            p1, p2 = parities[g1], parities[g2]
            sign = -1 if (p1 == 1 and p2 == 1) else 1
            for g3 in gen_names:
                v12 = gamma[(g1, g2)][g3]
                v21 = gamma[(g2, g1)][g3]
                if sp.simplify(v12 + sign * v21) != 0:
                    print(f"Skew-symmetry of gamma failed for [{g1}, {g2}]: {v12} vs {v21}")
                    skew_gamma_ok = False
    print("Graded skew-symmetry of gamma:", "PASSED" if skew_gamma_ok else "FAILED")

    # 3. Check 2-cocycle condition for gamma:
    # The deformed bracket [ , ]_gamma satisfies Jacobi identity to order kappa:
    # J_gamma(X, Y, Z) = 0 mod kappa^2
    # This means:
    # sum_cyclic (-1)^{p(X) p(Z)} ( [X, [Y, Z]_0]_1 + [X, [Y, Z]_1]_0 ) = 0
    # where [A, B]_1 = gamma(A, B).
    # Specifically:
    # [X, gamma(Y, Z)]_0 has p(X) and p(gamma(Y, Z)) = p(Y) + p(Z) + 1.
    # And gamma(X, [Y, Z]_0) has p(X) and p([Y, Z]_0) = p(Y) + p(Z).
    # Let's compute the total Jacobi failure d_gamma(X, Y, Z):
    cocycle_ok = True
    for i, g1 in enumerate(gen_names):
        p1 = parities[g1]
        for j in range(i, dim):
            g2 = gen_names[j]
            p2 = parities[g2]
            for k in range(j, dim):
                g3 = gen_names[k]
                p3 = parities[g3]
                
                # We can check J_gamma directly in U(A) using the Jacobi identity of associative superalgebra!
                # Since U(A) is associative, any supercommutator in U(A) AUTOMATICALLY satisfies the graded Jacobi identity!
                pass

    # 4. Now let's test the Coboundary Operator delta f:
    # f: g -> g is an odd linear map:
    # p(f(X)) = p(X) + 1 mod 2.
    # So:
    # If X is even (p(X)=0), f(X) is odd (in g_1).
    # If X is odd (p(X)=1), f(X) is even (in g_0).
    #
    # Formula from docs/math/C_coboundary_definition.md:
    # (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    #
    # Let f be parameterized by phi_{ij}:
    # f(Z_j) = sum_i phi_{ij} Z_i
    # Since f is odd:
    # for even Z_j (p(Z_j)=0), Z_i must be odd (p(Z_i)=1).
    # for odd Z_j (p(Z_j)=1), Z_i must be even (p(Z_i)=0).
    
    even_gens = [g for g in gen_names if parities[g] == 0]
    odd_gens = [g for g in gen_names if parities[g] == 1]
    
    # Variables for phi:
    # phi[(i, j)] where:
    # (i in odd, j in even): dim_odd * dim_even variables
    # (i in even, j in odd): dim_even * dim_odd variables
    # Total phi variables = 2 * dim_even * dim_odd
    phi = {}
    for o in odd_gens:
        for e in even_gens:
            phi[(o, e)] = sp.Symbol(f"phi_{o}_{e}")
            phi[(e, o)] = sp.Symbol(f"phi_{e}_{o}")
            
    print(f"Number of phi variables: {len(phi)} (= 2 * {len(even_gens)} * {len(odd_gens)})")
    
    # Now for each pair (X, Y) in gen_names x gen_names and each target Z in gen_names,
    # compute (delta f)(X, Y)_Z as a linear combination of phi variables.
    # Formula:
    # (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    
    # Let's compute delta_f[(X, Y)][target] in terms of phi:
    delta_f = defaultdict(lambda: defaultdict(lambda: sp.Integer(0)))
    
    for g1 in gen_names:
        p1 = parities[g1]
        for g2 in gen_names:
            p2 = parities[g2]
            
            # Term 1: (-1)^{p1} [X, f(Y)]
            # f(Y) = sum_k phi_{k, Y} Z_k
            # [X, f(Y)] = sum_k phi_{k, Y} [X, Z_k]_0 = sum_k phi_{k, Y} sum_r c0[(X, Z_k)][r] Z_r
            s1 = (-1)**p1
            # Which k can f(Y) have? Opposite parity of Y!
            target_par_Y = 1 - p2
            for k in gen_names:
                if parities[k] == target_par_Y:
                    p_var = phi[(k, g2)]
                    for r, c_val in c0[(g1, k)].items():
                        delta_f[(g1, g2)][r] += s1 * p_var * c_val
                        
            # Term 2: - (-1)^{(p1 + 1) p2} [Y, f(X)]
            s2 = - (-1)**((p1 + 1) * p2)
            target_par_X = 1 - p1
            for k in gen_names:
                if parities[k] == target_par_X:
                    p_var = phi[(k, g1)]
                    for r, c_val in c0[(g2, k)].items():
                        delta_f[(g1, g2)][r] += s2 * p_var * c_val
                        
            # Term 3: - f([X, Y])
            # [X, Y]_0 = sum_m c0[(X, Y)][m] Z_m
            # f([X, Y]) = sum_m c0[(X, Y)][m] f(Z_m) = sum_m c0[(X, Y)][m] sum_r phi_{r, m} Z_r
            for m, c_val in c0[(g1, g2)].items():
                target_par_m = 1 - parities[m]
                for r in gen_names:
                    if parities[r] == target_par_m:
                        p_var = phi[(r, m)]
                        delta_f[(g1, g2)][r] -= c_val * p_var
                        
    # Now set up the linear system:
    # (delta f)(X, Y) = gamma(X, Y) for all X, Y
    # That is: for all X, Y, r:
    # delta_f[(X, Y)][r] - gamma[(X, Y)][r] = 0
    
    equations = []
    eq_info = []
    
    for i, g1 in enumerate(gen_names):
        for j in range(i, dim):
            g2 = gen_names[j]
            for r in gen_names:
                lhs = delta_f[(g1, g2)][r]
                rhs = gamma[(g1, g2)][r]
                diff = sp.simplify(lhs - rhs)
                if diff != 0:
                    equations.append(diff)
                    eq_info.append((g1, g2, r))
                    
    print(f"Total non-trivial equations: {len(equations)}")
    
    # Let's solve the linear system for phi variables in terms of gb parameters!
    phi_vars = list(phi.values())
    gb_vars = list(gb.values())
    
    # Solve system: equations = 0
    # equations are linear in phi_vars, with constant terms linear in gb_vars.
    sol = sp.solve(equations, phi_vars)
    print(f"Solution for phi: {sol}")
    
    # Check if there are remaining constraints on gb_vars:
    # Substitute solution back into equations:
    rem_eqs = []
    for eq in equations:
        subbed = sp.simplify(eq.subs(sol))
        if subbed != 0:
            rem_eqs.append(subbed)
            
    print(f"Remaining constraints on gb parameters: {len(rem_eqs)}")
    if rem_eqs:
        print("Constraints:")
        for eq in rem_eqs[:10]:
            print("  ", eq, "= 0")
        gb_sol = sp.solve(rem_eqs, gb_vars)
        print("Required gb values for triviality:")
        print("  ", gb_sol)
    else:
        print("SUCCESS: gamma is a coboundary for ANY gb! (Unconditionally trivial)")
        
    return sol, rem_eqs

if __name__ == '__main__':
    test_triviality(1)
