import sympy as sp
import itertools

def main():
    print("Solving C(2) triviality...")
    # We want to represent elements as polynomials in a+, a-, b+, b-, k
    # with relations:
    # a+ a+ = 0, a- a- = 0, a- a+ = 1 - a+ a-
    # b- b+ = b+ b- + 1
    # b+ a+ = a+ b+ - g_{++} k
    # b+ a- = a- b+ - g_{-+} k
    # b- a+ = a+ b- - g_{+-} k
    # b- a- = a- b- - g_{--} k
    # k is central, k^2 = 0
    # Also k a = - a k, k b = b k
    
    # We can write a normal ordering function:
    # Order: k, a+, a-, b+, b-
    def normal_order(terms):
        # terms is a dict of tuple of strings -> coefficient
        # e.g. {('a+', 'b+'): 1}
        changed = True
        while changed:
            changed = False
            new_terms = {}
            for term, coeff in terms.items():
                if coeff == 0:
                    continue
                # find first out-of-order pair
                # desired order: 'k', 'ap', 'am', 'bp', 'bm'
                order_map = {'k': 0, 'ap': 1, 'am': 2, 'bp': 3, 'bm': 4}
                out_of_order_idx = -1
                for i in range(len(term)-1):
                    if order_map[term[i]] > order_map[term[i+1]]:
                        out_of_order_idx = i
                        break
                
                if out_of_order_idx == -1:
                    # check for simplifications
                    # ap ap -> 0, am am -> 0, k k -> 0
                    if any(term[i] == term[i+1] and term[i] in ['ap', 'am', 'k'] for i in range(len(term)-1)):
                        continue # becomes 0
                    new_terms[term] = new_terms.get(term, 0) + coeff
                else:
                    changed = True
                    i = out_of_order_idx
                    A, B = term[i], term[i+1]
                    prefix = term[:i]
                    suffix = term[i+2:]
                    
                    if A == 'am' and B == 'ap':
                        # am ap = 1 - ap am
                        new_terms[prefix + suffix] = new_terms.get(prefix + suffix, 0) + coeff
                        new_terms[prefix + ('ap', 'am') + suffix] = new_terms.get(prefix + ('ap', 'am') + suffix, 0) - coeff
                    elif A == 'bm' and B == 'bp':
                        # bm bp = bp bm + 1
                        new_terms[prefix + suffix] = new_terms.get(prefix + suffix, 0) + coeff
                        new_terms[prefix + ('bp', 'bm') + suffix] = new_terms.get(prefix + ('bp', 'bm') + suffix, 0) + coeff
                    elif A == 'bp' and B == 'ap':
                        # bp ap = ap bp - g_{++} k
                        new_terms[prefix + ('ap', 'bp') + suffix] = new_terms.get(prefix + ('ap', 'bp') + suffix, 0) + coeff
                        new_terms[prefix + ('k',) + suffix] = new_terms.get(prefix + ('k',) + suffix, 0) - coeff * sp.Symbol('g_pp')
                    elif A == 'bp' and B == 'am':
                        # bp am = am bp - g_{-+} k
                        new_terms[prefix + ('am', 'bp') + suffix] = new_terms.get(prefix + ('am', 'bp') + suffix, 0) + coeff
                        new_terms[prefix + ('k',) + suffix] = new_terms.get(prefix + ('k',) + suffix, 0) - coeff * sp.Symbol('g_mp')
                    elif A == 'bm' and B == 'ap':
                        # bm ap = ap bm - g_{+-} k
                        new_terms[prefix + ('ap', 'bm') + suffix] = new_terms.get(prefix + ('ap', 'bm') + suffix, 0) + coeff
                        new_terms[prefix + ('k',) + suffix] = new_terms.get(prefix + ('k',) + suffix, 0) - coeff * sp.Symbol('g_pm')
                    elif A == 'bm' and B == 'am':
                        # bm am = am bm - g_{--} k
                        new_terms[prefix + ('am', 'bm') + suffix] = new_terms.get(prefix + ('am', 'bm') + suffix, 0) + coeff
                        new_terms[prefix + ('k',) + suffix] = new_terms.get(prefix + ('k',) + suffix, 0) - coeff * sp.Symbol('g_mm')
                    elif A in ['ap', 'am'] and B == 'k': # wait, k is 0, so A > B means A is ap/am/bp/bm and B is k
                        # k is odd, so ap k = - k ap, am k = - k am
                        # k is central for bos? No, k commutes with b.
                        if A in ['ap', 'am']:
                            new_terms[prefix + ('k', A) + suffix] = new_terms.get(prefix + ('k', A) + suffix, 0) - coeff
                        else:
                            new_terms[prefix + ('k', A) + suffix] = new_terms.get(prefix + ('k', A) + suffix, 0) + coeff
                    elif A in ['bp', 'bm'] and B in ['ap', 'am', 'k']:
                        # already handled ap, am. if B == k handled above.
                        pass # wait, I handled all out of order pairs!
                        
            terms = {t: c for t, c in new_terms.items() if c != 0}
            
        return terms

    def mul(t1, t2):
        res = {}
        for term1, c1 in t1.items():
            for term2, c2 in t2.items():
                res[term1 + term2] = c1 * c2
        return normal_order(res)

    def add(t1, t2, sign=1):
        res = dict(t1)
        for term, c in t2.items():
            res[term] = res.get(term, 0) + sign * c
        return {t: c for t, c in res.items() if c != 0}
        
    def scalar_mul(t, s):
        return {term: c * s for term, c in t.items()}

    def bracket(t1, t2, parity1, parity2):
        # superbracket
        sign = -1 if (parity1 == 1 and parity2 == 1) else 1
        term1 = mul(t1, t2)
        term2 = mul(t2, t1)
        return add(term1, term2, -sign) # X Y - (-1)^{p1 p2} Y X
        
    # Basis definitions
    basis_even = {
        'E_pp': {('bp', 'bp'): 1},
        'E_mm': {('bm', 'bm'): 1},
        'E_pm': {('bp', 'bm'): 1, (): sp.Rational(1, 2)},
        'E_a': {('ap', 'am'): 1, (): sp.Rational(-1, 2)}
    }
    
    basis_odd = {
        'F_pp': {('ap', 'bp'): 1},
        'F_pm': {('ap', 'bm'): 1},
        'F_mp': {('am', 'bp'): 1},
        'F_mm': {('am', 'bm'): 1}
    }
    
    # Compute gamma for all pairs
    def extract_gamma(expr):
        # gamma is the coefficient of k * basis_element
        # We know gamma(X, Y) lies in the algebra. 
        # But wait, our normal ordering gives terms like k * something.
        # Since k commutes with b and anticommutes with a, k is just k.
        gamma_terms = {}
        for term, coeff in expr.items():
            if len(term) > 0 and term[0] == 'k':
                rem = term[1:]
                gamma_terms[rem] = gamma_terms.get(rem, 0) + coeff
        return gamma_terms

    print("Computing gamma...")
    gammas = {}
    basis_all = list(basis_even.items()) + list(basis_odd.items())
    parities = {k: 0 for k in basis_even}
    parities.update({k: 1 for k in basis_odd})
    
    for (name1, expr1) in basis_all:
        for (name2, expr2) in basis_all:
            b = bracket(expr1, expr2, parities[name1], parities[name2])
            g = extract_gamma(b)
            gammas[(name1, name2)] = g
            
    # Now setup the linear map f: g -> g (odd)
    # f(E) = sum c_{E, F} F
    # f(F) = sum d_{F, E} E
    
    # Let's parameterize f
    f_vars = {}
    for e in basis_even:
        for o in basis_odd:
            f_vars[(e, o)] = sp.Symbol(f"f_{e}_{o}")
            f_vars[(o, e)] = sp.Symbol(f"f_{o}_{e}")
            
    def apply_f(name):
        res = {}
        if name in basis_even:
            for o in basis_odd:
                res[o] = f_vars[(name, o)]
        else:
            for e in basis_even:
                res[e] = f_vars[(name, e)]
        return res
        
    def to_expr(f_dict):
        res = {}
        for name, coeff in f_dict.items():
            expr = basis_even[name] if name in basis_even else basis_odd[name]
            res = add(res, scalar_mul(expr, coeff))
        return res

    # Compute delta f(X, Y) = [X, f(Y)] - (-1)^{p(X) p(Y)} [Y, f(X)] - f([X, Y]_0)
    # wait, the formula is:
    # (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    
    print("Setting up linear system...")
    equations = []
    
    # We will match coefficients of basis elements
    def extract_basis_coeffs(expr, expected_parity):
        coeffs = {}
        if expected_parity == 0:
            # Match with E_pp, E_mm, E_pm, E_a
            coeffs['E_pp'] = expr.get(('bp', 'bp'), 0)
            coeffs['E_mm'] = expr.get(('bm', 'bm'), 0)
            coeffs['E_pm'] = expr.get(('bp', 'bm'), 0)
            coeffs['E_a'] = expr.get(('ap', 'am'), 0)
            # check consistency with constant term
            c_term = expr.get((), 0)
            expected_c = coeffs['E_pm'] * sp.Rational(1, 2) - coeffs['E_a'] * sp.Rational(1, 2)
            if sp.simplify(c_term - expected_c) != 0:
                print("WARNING:", sp.simplify(c_term - expected_c))
        else:
            coeffs['F_pp'] = expr.get(('ap', 'bp'), 0)
            coeffs['F_pm'] = expr.get(('ap', 'bm'), 0)
            coeffs['F_mp'] = expr.get(('am', 'bp'), 0)
            coeffs['F_mm'] = expr.get(('am', 'bm'), 0)
        return coeffs

    # To avoid double counting, use combinations_with_replacement? No, gammas is for all pairs.
    for i, (name1, expr1) in enumerate(basis_all):
        for j, (name2, expr2) in enumerate(basis_all):
            if i > j: continue # symmetric/antisymmetric anyway
            
            p1 = parities[name1]
            p2 = parities[name2]
            
            # compute [X, Y]_0
            b0 = bracket(expr1, expr2, p1, p2)
            # remove gamma part from b0
            b0_pure = {t: c for t, c in b0.items() if not (len(t) > 0 and t[0] == 'k')}
            
            # express b0_pure in basis
            b0_coeffs = extract_basis_coeffs(b0_pure, (p1 + p2) % 2)
            
            # f([X, Y]_0)
            f_b0 = {}
            for b_name, b_c in b0_coeffs.items():
                f_res = apply_f(b_name)
                for k, v in f_res.items():
                    f_b0[k] = f_b0.get(k, 0) + b_c * v
            
            f_b0_expr = to_expr(f_b0)
            
            # [X, f(Y)]
            f_Y = apply_f(name2)
            f_Y_expr = to_expr(f_Y)
            term1 = bracket(expr1, f_Y_expr, p1, (p2 + 1) % 2)
            term1_pure = {t: c for t, c in term1.items() if not (len(t) > 0 and t[0] == 'k')}
            
            # [Y, f(X)]
            f_X = apply_f(name1)
            f_X_expr = to_expr(f_X)
            term2 = bracket(expr2, f_X_expr, p2, (p1 + 1) % 2)
            term2_pure = {t: c for t, c in term2.items() if not (len(t) > 0 and t[0] == 'k')}
            
            # (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
            sign1 = (-1)**p1
            sign2 = - (-1)**((p1 + 1)*p2)
            
            delta_f_expr = add(scalar_mul(term1_pure, sign1), scalar_mul(term2_pure, sign2))
            delta_f_expr = add(delta_f_expr, f_b0_expr, sign=-1)
            
            # Match with gamma
            gamma_expr = gammas[(name1, name2)]
            
            expected_p = (p1 + p2 + 1) % 2
            delta_coeffs = extract_basis_coeffs(delta_f_expr, expected_p)
            gamma_coeffs = extract_basis_coeffs(gamma_expr, expected_p)
            
            for k in delta_coeffs.keys():
                eq = sp.simplify(delta_coeffs.get(k, 0) - gamma_coeffs.get(k, 0))
                if eq != 0:
                    equations.append(eq)

    print(f"Generated {len(equations)} equations.")
    
    # We want to know if there exists f for ANY non-zero gb.
    # So we solve the homogeneous system where f_vars and gb_vars are all unknowns!
    # It's a linear system in both f and gb.
    all_vars = list(f_vars.values()) + [sp.Symbol('g_pp'), sp.Symbol('g_pm'), sp.Symbol('g_mp'), sp.Symbol('g_mm')]
    
    matrix, rhs = sp.linear_eq_to_matrix(equations, all_vars)
    print("Matrix shape:", matrix.shape)
    
    # Nullspace will give all valid assignments of (f, gb)
    ns = matrix.nullspace()
    print(f"Nullspace dimension: {len(ns)}")
    
    import json
    results = {}
    if len(ns) == 0:
        print("Triviality condition is NOT satisfiable for any non-zero gb!")
        results['conclusion'] = 'Non-trivial'
    else:
        # Check if gb can be non-zero
        gb_indices = [-4, -3, -2, -1] # The last 4 variables
        gb_solutions = []
        for vec in ns:
            gb_vals = [vec[i] for i in gb_indices]
            if any(v != 0 for v in gb_vals):
                gb_solutions.append(gb_vals)
        if len(gb_solutions) > 0:
            print("Triviality condition IS satisfiable for some non-zero gb!")
            results['conclusion'] = 'Trivial'
            results['gb_solutions'] = [str(x) for x in gb_solutions]
        else:
            print("Triviality condition is NOT satisfiable for any non-zero gb! (Only gb=0 works)")
            results['conclusion'] = 'Non-trivial'
            
    with open('results.json', 'w') as f:
        json.dump(results, f)

if __name__ == '__main__':
    main()
