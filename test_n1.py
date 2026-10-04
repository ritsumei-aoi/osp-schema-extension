from oscillator_algebra import OscillatorAlgebra
import sympy as sp

def test_n1():
    alg = OscillatorAlgebra(1)
    print(f"Dimension of g: {alg.dim} (even: {alg.dim_even}, odd: {alg.dim_odd})")
    print("Basis elements:")
    for idx, (b, p) in enumerate(alg.basis):
        print(f"  {idx}: parity={p}, {b}")
        
    # Compute all brackets
    # [X_i, X_j] = [X_i, X_j]_0 + kappa * gamma(X_i, X_j)
    # We store structure constants C_{ij}^k and gamma_{ij}^k
    C = {}
    gamma = {}
    
    print("\nComputing brackets...")
    for i in range(alg.dim):
        b1, p1 = alg.basis[i]
        for j in range(alg.dim):
            b2, p2 = alg.basis[j]
            bracket_dict = alg.superbracket(b1, p1, b2, p2)
            c_k0, c_k1 = alg.decompose_in_basis(bracket_dict)
            for k in range(alg.dim):
                if c_k0[k] != 0:
                    C[(i, j, k)] = c_k0[k]
                if c_k1[k] != 0:
                    gamma[(i, j, k)] = c_k1[k]
                    
    print(f"Non-zero structure constants count: {len(C)}")
    print(f"Non-zero gamma coefficients count: {len(gamma)}")
    
    print("\nSample gamma non-zero entries:")
    for (i, j, k), val in list(gamma.items())[:10]:
        print(f"gamma({alg.basis[i][0]}, {alg.basis[j][0]}) -> {alg.basis[k][0]} : {val}")
        
    # Now let's test coboundary operator delta f:
    # f is an odd linear map f: g -> g.
    # f reverses parity:
    # f(even) in g_odd, f(odd) in g_even.
    # So f is parameterized by:
    # phi_{k, j} for j in even, k in odd (dim_odd * dim_even parameters)
    # phi_{k, j} for j in odd, k in even (dim_even * dim_odd parameters)
    # Total parameters in f = 2 * dim_even * dim_odd.
    
    phi = {}
    for j in range(alg.dim):
        pj = alg.basis[j][1]
        for k in range(alg.dim):
            pk = alg.basis[k][1]
            if pk == 1 - pj:
                phi[(k, j)] = sp.Symbol(f"phi_{k}_{j}")
                
    print(f"\nNumber of parameters in f: {len(phi)}")
    
    # delta f formula:
    # (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    # Let X = e_i, Y = e_j.
    # f(e_j) = sum_k phi_{k, j} e_k
    # [X, f(Y)] = sum_k phi_{k, j} [e_i, e_k]_0 = sum_k phi_{k, j} sum_m C_{ik}^m e_m
    # [Y, f(X)] = sum_k phi_{k, i} [e_j, e_k]_0 = sum_k phi_{k, i} sum_m C_{jk}^m e_m
    # f([X, Y]) = f( sum_k C_{ij}^k e_k ) = sum_k C_{ij}^k f(e_k) = sum_k C_{ij}^k sum_m phi_{m, k} e_m
    
    # So (delta f)(e_i, e_j)_m =
    # (-1)^{p_i} sum_k phi_{k, j} C_{ik}^m
    # - (-1)^{(p_i + 1) p_j} sum_k phi_{k, i} C_{jk}^m
    # - sum_k C_{ij}^k phi_{m, k}
    
    delta_f = {}
    for i in range(alg.dim):
        pi = alg.basis[i][1]
        for j in range(alg.dim):
            pj = alg.basis[j][1]
            for m in range(alg.dim):
                val = sp.Integer(0)
                sgn1 = -1 if pi == 1 else 1
                sgn2 = -1 if ((pi + 1) * pj % 2 == 1) else 1
                
                # Term 1: (-1)^{p(X)} [X, f(Y)]
                for k in range(alg.dim):
                    if (k, j) in phi and (i, k, m) in C:
                        val += sgn1 * phi[(k, j)] * C[(i, k, m)]
                        
                # Term 2: - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
                for k in range(alg.dim):
                    if (k, i) in phi and (j, k, m) in C:
                        val -= sgn2 * phi[(k, i)] * C[(j, k, m)]
                        
                # Term 3: - f([X, Y])
                for k in range(alg.dim):
                    if (i, j, k) in C and (m, k) in phi:
                        val -= C[(i, j, k)] * phi[(m, k)]
                        
                val = sp.simplify(val)
                if val != 0:
                    delta_f[(i, j, m)] = val
                    
    print(f"Non-zero delta_f entries: {len(delta_f)}")
    
    # Now let's set up the system: gamma_{ij}^m = (delta f)_{ij}^m for all i, j, m
    equations = []
    all_pairs = set(gamma.keys()).union(set(delta_f.keys()))
    for (i, j, m) in all_pairs:
        g_val = gamma.get((i, j, m), sp.Integer(0))
        df_val = delta_f.get((i, j, m), sp.Integer(0))
        equations.append(g_val - df_val)
        
    print(f"Total equations to solve: {len(equations)}")
    
    # Unknowns: all phi symbols + gb symbols
    unknowns = list(phi.values())
    gb_vars = list(alg.gb.values())
    
    # Solve for phi in terms of gb
    sol = sp.solve(equations, unknowns)
    print(f"Solvable for phi in terms of gb? {bool(sol)}")
    if sol:
        print("Found solution for phi in terms of gb!")
        # Let's check remaining equations if any
        remaining = []
        for eq in equations:
            subbed = sp.simplify(eq.subs(sol))
            if subbed != 0:
                remaining.append(subbed)
        print(f"Remaining constraints on gb: {len(remaining)}")
        if remaining:
            print("Remaining constraints:", remaining)
        else:
            print("ALL gb parameters are completely unconstrained! That means FOR ANY gb, gamma is a coboundary!")
    else:
        # Check linear system with both phi and gb
        print("Testing if gb must be zero...")
        sol_all = sp.solve(equations, unknowns + gb_vars)
        print("Solution for all:", sol_all)

if __name__ == "__main__":
    test_n1()
